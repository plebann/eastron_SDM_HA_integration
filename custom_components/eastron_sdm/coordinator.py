"""DataUpdateCoordinator for Eastron SDM meters."""
from __future__ import annotations

import asyncio
import logging
import struct
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Any, Iterable

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
    CONF_NORMAL_DIVISOR,
    CONF_SLOW_DIVISOR,
    CONF_DEBUG,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NORMAL_DIVISOR,
    DEFAULT_SLOW_DIVISOR,
)
from .client import SdmModbusClient
from .models.sdm120 import get_register_specs, RegisterSpec

_LOGGER = logging.getLogger(__name__)

@dataclass(slots=True)
class DecodedValue:
    key: str
    value: float | int | None
    updated: datetime

@dataclass(slots=True)
class _Batch:
    start: int
    length: int
    function: str
    specs: list[RegisterSpec]

class SdmCoordinator(DataUpdateCoordinator[dict[str, DecodedValue]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        data = {**entry.data, **entry.options}
        self.host: str = data[CONF_HOST]
        self.port: int = data.get(CONF_PORT, 502)
        self.unit_id: int = data.get(CONF_UNIT_ID, 1)
        self.scan_interval: int = data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self.normal_divisor: int = data.get(CONF_NORMAL_DIVISOR, DEFAULT_NORMAL_DIVISOR)
        self.slow_divisor: int = data.get(CONF_SLOW_DIVISOR, DEFAULT_SLOW_DIVISOR)
        self.enable_advanced: bool = data.get(CONF_ENABLE_ADVANCED, False)
        self.enable_diagnostic: bool = data.get(CONF_ENABLE_DIAGNOSTIC, False)
        self.debug: bool = data.get(CONF_DEBUG, False)

        self._client = SdmModbusClient(self.host, self.port, self.unit_id)
        self._cycle = 0
        self._failure_count = 0
        self._specs = get_register_specs(
            enable_advanced=self.enable_advanced,
            enable_diagnostic=self.enable_diagnostic,
        )
        self._fast = [s for s in self._specs if s.tier == "fast"]
        self._normal = [s for s in self._specs if s.tier == "normal"]
        self._slow = [s for s in self._specs if s.tier == "slow"]
        super().__init__(
            hass,
            _LOGGER,
            name=f"SDM {self.host}:{self.port} unit {self.unit_id}",
            update_interval=timedelta(seconds=self.scan_interval),
        )

    async def _async_update_data(self) -> dict[str, DecodedValue]:  # type: ignore[override]
        self._refresh_from_entry()
        try:
            specs_to_read = list(self._fast)
            if self._cycle % self.normal_divisor == 0:
                specs_to_read.extend(self._normal)
            if self._cycle % self.slow_divisor == 0:
                specs_to_read.extend(self._slow)
            self._cycle = (self._cycle + 1) % (self.normal_divisor * self.slow_divisor)

            decoded: dict[str, DecodedValue] = {**(self.data or {})}

            for batch in _build_batches(specs_to_read):
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

    def _refresh_from_entry(self) -> None:
        """Refresh coordinator settings from the latest entry data/options."""
        data = {**self.entry.data, **self.entry.options}
        self.enable_advanced = data.get(CONF_ENABLE_ADVANCED, self.enable_advanced)
        self.enable_diagnostic = data.get(CONF_ENABLE_DIAGNOSTIC, self.enable_diagnostic)
        self.normal_divisor = data.get(CONF_NORMAL_DIVISOR, self.normal_divisor)
        self.slow_divisor = data.get(CONF_SLOW_DIVISOR, self.slow_divisor)
        scan_interval = data.get(CONF_SCAN_INTERVAL, self.scan_interval)
        if scan_interval != self.scan_interval:
            self.scan_interval = scan_interval
            self.update_interval = timedelta(seconds=self.scan_interval)


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


def _build_batches(specs: Iterable[RegisterSpec]) -> list[_Batch]:
    # Sort by function then address for grouping
    ordered = sorted(specs, key=lambda s: (s.function, s.address))
    batches: list[_Batch] = []
    current: _Batch | None = None
    for spec in ordered:
        if current is None:
            current = _Batch(start=spec.address, length=spec.length, function=spec.function, specs=[spec])
            continue
        end = current.start + current.length
        gap = spec.address - end
        if spec.function == current.function and gap <= 0:  # only merge contiguous blocks per function
            current.length = (spec.address + spec.length) - current.start
            current.specs.append(spec)
        else:
            batches.append(current)
            current = _Batch(start=spec.address, length=spec.length, function=spec.function, specs=[spec])
    if current:
        batches.append(current)
    return batches
