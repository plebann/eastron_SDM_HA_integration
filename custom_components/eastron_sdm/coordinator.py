"""DataUpdateCoordinator for Eastron SDM meters."""
from __future__ import annotations

import asyncio
import logging
import struct
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Iterable

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_UNIT_ID,
    CONF_SCAN_INTERVAL,
    CONF_ENABLE_ADVANCED,
    CONF_ENABLE_DIAGNOSTIC,
    CONF_ENABLE_TWO_WAY,
    CONF_ENABLE_CONFIG,
    CONF_NORMAL_DIVISOR,
    CONF_SLOW_DIVISOR,
    CONF_DEBUG,
    CONF_MODEL,
    DEFAULT_MODEL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NORMAL_DIVISOR,
    DEFAULT_SLOW_DIVISOR,
)
from .client import SdmModbusClient
from .models import get_model_specs, get_spec_by_key, RegisterSpec
from .read_plan import ReadPlanOptions, build_read_plan

_LOGGER = logging.getLogger(__name__)

@dataclass(slots=True)
class DecodedValue:
    key: str
    value: float | int | None
    updated: datetime

class SdmCoordinator(DataUpdateCoordinator[dict[str, DecodedValue]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        data = {**entry.data, **entry.options}
        self.host: str = data[CONF_HOST]
        self.port: int = data.get(CONF_PORT, 502)
        self.unit_id: int = data.get(CONF_UNIT_ID, 1)
        self.model: str = data.get(CONF_MODEL, DEFAULT_MODEL)
        self.scan_interval: int = data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self.normal_divisor: int = data.get(CONF_NORMAL_DIVISOR, DEFAULT_NORMAL_DIVISOR)
        self.slow_divisor: int = data.get(CONF_SLOW_DIVISOR, DEFAULT_SLOW_DIVISOR)
        self.enable_advanced: bool = data.get(CONF_ENABLE_ADVANCED, False)
        self.enable_diagnostic: bool = data.get(CONF_ENABLE_DIAGNOSTIC, False)
        self.enable_two_way: bool = data.get(CONF_ENABLE_TWO_WAY, False)
        self.enable_config: bool = data.get(CONF_ENABLE_CONFIG, False)
        self.debug: bool = data.get(CONF_DEBUG, False)

        # Identity fields
        self._serial_number: int | None = None
        self.serial_identifier: str | None = None

        self._client = SdmModbusClient(self.host, self.port, self.unit_id)
        self._cycle = 0
        self._failure_count = 0
        self._specs = get_model_specs(self.model)
        super().__init__(
            hass,
            _LOGGER,
            name=f"SDM {self.host}:{self.port} unit {self.unit_id}",
            update_interval=timedelta(seconds=self.scan_interval),
        )

    def _read_plan_options(self) -> ReadPlanOptions:
        return ReadPlanOptions(
            enable_advanced=self.enable_advanced,
            enable_diagnostic=self.enable_diagnostic,
            enable_two_way=self.enable_two_way,
            enable_config=self.enable_config,
            normal_divisor=self.normal_divisor,
            slow_divisor=self.slow_divisor,
        )

    async def _async_update_data(self) -> dict[str, DecodedValue]:  # type: ignore[override]
        self._refresh_from_entry()
        try:
            read_plan = build_read_plan(self._specs, self._read_plan_options(), self._cycle)
            self._cycle = read_plan.next_cycle

            decoded: dict[str, DecodedValue] = {**(self.data or {})}

            for batch in read_plan.batches:
                if batch.function == "input":
                    raw = await self._client.read_input_registers(batch.start, batch.length)
                elif batch.function == "holding":
                    raw = await self._client.read_holding_registers(batch.start, batch.length)
                else:
                    raise UpdateFailed(f"Unsupported function {batch.function}")
                if self.debug:
                    _LOGGER.debug(
                        "Batch read start=%s len=%s specs=%s", batch.start, batch.length, [s.key for s in batch.specs]
                    )
                # Slice out per spec
                for spec in batch.specs:
                    offset = spec.address - batch.start
                    regs = raw.registers[offset: offset + spec.length]
                    value = _decode(spec, regs)
                    decoded[spec.key] = DecodedValue(key=spec.key, value=value, updated=datetime.utcnow())
                    if self.debug:
                        _LOGGER.debug("Decoded %s -> %s", spec.key, value)

            self._failure_count = 0
            return decoded
        except Exception as exc:  # broad to ensure coordinator handles availability
            self._failure_count += 1
            if self.data:
                _LOGGER.warning("Using cached SDM data after failure #%s: %s", self._failure_count, exc)
                return self.data
            raise UpdateFailed(str(exc)) from exc

    async def async_close(self) -> None:
        await self._client.close()

    async def async_write_register(
        self, spec: RegisterSpec, value: int | Iterable[int], *, raw_value: float | int | None = None
    ) -> None:
        """Write a holding register value and react to meter_id updates."""
        if spec.function != "holding":
            raise ValueError(f"Write attempted on non-holding register {spec.key}")
        if spec.length > 1:
            if isinstance(value, int):
                raise ValueError(f"Multi-register write for {spec.key} requires {spec.length} values")
            values = [int(v) for v in value]
            if len(values) != spec.length:
                raise ValueError(f"Value length {len(values)} does not match spec length {spec.length} for {spec.key}")
            await self._client.write_holding_registers(spec.address, values)
        else:
            await self._client.write_holding_register(spec.address, int(value))

        # Sync client/unit_id when the meter address changes to avoid breaking communications.
        if spec.key == "meter_id":
            new_unit = self._extract_unit_id(raw_value, value)
            if new_unit is not None:
                await self._handle_meter_id_change(new_unit)

    def _refresh_from_entry(self) -> None:
        """Refresh coordinator settings from the latest entry data/options."""
        data = {**self.entry.data, **self.entry.options}
        old_model = self.model
        
        self.enable_advanced = data.get(CONF_ENABLE_ADVANCED, self.enable_advanced)
        self.enable_diagnostic = data.get(CONF_ENABLE_DIAGNOSTIC, self.enable_diagnostic)
        self.enable_two_way = data.get(CONF_ENABLE_TWO_WAY, self.enable_two_way)
        self.enable_config = data.get(CONF_ENABLE_CONFIG, self.enable_config)
        self.normal_divisor = data.get(CONF_NORMAL_DIVISOR, self.normal_divisor)
        self.slow_divisor = data.get(CONF_SLOW_DIVISOR, self.slow_divisor)
        self.model = data.get(CONF_MODEL, self.model)
        scan_interval = data.get(CONF_SCAN_INTERVAL, self.scan_interval)
        if scan_interval != self.scan_interval:
            self.scan_interval = scan_interval
            self.update_interval = timedelta(seconds=self.scan_interval)
        
        if old_model != self.model:
            self._specs = get_model_specs(self.model)

    def _extract_unit_id(self, raw_value: float | int | None, encoded: int | Iterable[int]) -> int | None:
        """Best-effort extraction of the intended unit id after a meter_id write."""
        if raw_value is not None:
            try:
                return int(raw_value)
            except Exception:
                return None
        if isinstance(encoded, int):
            return int(encoded)
        try:
            lst = list(encoded)
        except Exception:
            return None
        if len(lst) == 1:
            return int(lst[0])
        return None

    async def _handle_meter_id_change(self, new_unit_id: int) -> None:
        """Update client/coordinator/unit_id persistence after meter_id changes."""
        if new_unit_id == self.unit_id:
            return
        old_unit = self.unit_id

        # Switch client to the new unit to validate the change on-device.
        await self._client.set_unit_id(new_unit_id)
        self.unit_id = new_unit_id

        try:
            spec = get_spec_by_key(self.model, "meter_id")
            raw = await self._client.read_holding_registers(spec.address, spec.length)
            confirmed = _decode(spec, raw.registers)
            if confirmed is None or int(confirmed) != int(new_unit_id):
                raise ValueError(f"Meter id verification failed (read back {confirmed})")

            # Persist into entry data/options to survive reloads.
            new_data = {**self.entry.data, CONF_UNIT_ID: new_unit_id}
            new_options = {**self.entry.options, CONF_UNIT_ID: new_unit_id}
            self.hass.config_entries.async_update_entry(self.entry, data=new_data, options=new_options)
        except Exception as exc:
            # Roll back to the previous unit id to avoid mismatched polls.
            _LOGGER.warning("Meter id change not verified; rolling back to unit %s: %s", old_unit, exc)
            await self._client.set_unit_id(old_unit)
            self.unit_id = old_unit
            self.hass.config_entries.async_update_entry(
                self.entry,
                data={**self.entry.data, CONF_UNIT_ID: old_unit},
                options={**self.entry.options, CONF_UNIT_ID: old_unit},
            )
        else:
            # Refresh to pick up the new addressing context.
            await self.async_request_refresh()

    async def async_ensure_serial_number(self) -> str | None:
        """Fetch and cache the meter serial number for stable identity."""
        if self.serial_identifier:
            return self.serial_identifier
        try:
            spec = get_spec_by_key(self.model, "serial_number")
            raw = await self._client.read_holding_registers(spec.address, spec.length)
            value = _decode(spec, raw.registers)
            if value is None:
                return None
            self._serial_number = int(value)
            self.serial_identifier = str(self._serial_number)
            return self.serial_identifier
        except Exception as exc:
            _LOGGER.warning("Unable to read serial_number: %s", exc)
            return None

    def build_unique_id(self, key: str) -> str:
        """Build a stable unique_id using serial_number when available."""
        base = self.serial_identifier or f"{self.host}_{self.unit_id}"
        return f"eastron_sdm_{base}_{key}"


def _decode(spec: RegisterSpec, registers: list[int]) -> float | int | None:
    if spec.data_type == "float32":
        if len(registers) < 2:
            return None
        combined = (registers[0] << 16) | registers[1]
        return struct.unpack(">f", combined.to_bytes(4, byteorder="big"))[0]
    if spec.data_type == "uint32":
        if len(registers) < 2:
            return None
        return (registers[0] << 16) | registers[1]
    if spec.data_type in {"uint16", "hex16"}:
        if not registers:
            return None
        return registers[0]
    return None


def _encode_value(spec: RegisterSpec, value: float | int) -> int | list[int]:
    """Encode a value into register format based on data type.
    
    Args:
        spec: Register specification containing data type and length
        value: The value to encode (numeric)
        
    Returns:
        For single register (length=1): int value
        For multiple registers (length>1): list of int values
    """
    if spec.data_type == "float32":
        # Encode as 32-bit float, split into 2 registers (big-endian)
        packed = struct.pack(">f", float(value))
        high_word = (packed[0] << 8) | packed[1]
        low_word = (packed[2] << 8) | packed[3]
        return [high_word, low_word]
    if spec.data_type == "uint32":
        # Encode as 32-bit unsigned int, split into 2 registers
        int_val = int(value)
        high_word = (int_val >> 16) & 0xFFFF
        low_word = int_val & 0xFFFF
        return [high_word, low_word]
    if spec.data_type in {"uint16", "hex16"}:
        # Single 16-bit register
        return int(value)
    # Default: single register
    return int(value)

