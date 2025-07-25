"""Data update coordinator for Eastron SDM integration."""

from __future__ import annotations

from typing import Any
from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class SDMDataUpdateCoordinator(DataUpdateCoordinator):
    """Base coordinator for Eastron SDM devices."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        update_interval: timedelta,
        device,
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )
        self.device = device
        self._client = None

    async def _async_update_data(self) -> Any:
        """Fetch data for this polling tier."""
        _LOGGER.debug("SDMDataUpdateCoordinator: _async_update_data called for device %s", getattr(self.device, "device_name", self.device))
        import time

        if not hasattr(self, "poll_stats"):
            self.poll_stats = {
                "success_count": 0,
                "failure_count": 0,
                "last_update": None,
                "last_error": None,
                "avg_duration": 0.0,
                "total_duration": 0.0,
                "total_polls": 0,
            }
        max_attempts = 3
        delay = 1
        for attempt in range(1, max_attempts + 1):
            start = time.monotonic()
            try:
                client = getattr(self.device, "client", None)
                registers = getattr(self.device, "register_map", None)
                results = {}
                if registers is not None:
                    batches = self._group_registers_for_batch(registers)
                    for start_addr, count, reg_defs in batches:
                        raw = await self.device.async_read_registers(start_addr, count)
                        parsed = self._parse_and_validate_registers(raw, reg_defs)
                        results.update(parsed)
                    duration = time.monotonic() - start
                    self.poll_stats["success_count"] += 1
                    self.poll_stats["last_update"] = time.time()
                    self.poll_stats["last_error"] = None
                    self.poll_stats["total_duration"] += duration
                    self.poll_stats["total_polls"] += 1
                    self.poll_stats["avg_duration"] = (
                        self.poll_stats["total_duration"] / self.poll_stats["total_polls"]
                    )
                    return results
                data = await self.device.async_read_registers(0x0000, 2)
                duration = time.monotonic() - start
                self.poll_stats["success_count"] += 1
                self.poll_stats["last_update"] = time.time()
                self.poll_stats["last_error"] = None
                self.poll_stats["total_duration"] += duration
                self.poll_stats["total_polls"] += 1
                self.poll_stats["avg_duration"] = (
                    self.poll_stats["total_duration"] / self.poll_stats["total_polls"]
                )
                return data
            except Exception as err:
                self.poll_stats["failure_count"] += 1
                self.poll_stats["last_error"] = str(err)
                if attempt == max_attempts:
                    raise UpdateFailed(f"Error updating data after {attempt} attempts: {err}") from err
                import asyncio
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

    def _group_registers_for_batch(self, register_defs):
        """Group register definitions into contiguous address batches."""
        sorted_regs = sorted(register_defs, key=lambda r: r.address)
        batches = []
        batch = []
        last_addr = None
        for reg in sorted_regs:
            if not batch:
                batch = [reg]
                last_addr = reg.address
                continue
            expected_next = last_addr + reg.length // 2
            if reg.address == expected_next:
                batch.append(reg)
                last_addr = reg.address
            else:
                start = batch[0].address
                count = sum(r.length // 2 for r in batch)
                batches.append((start, count, list(batch)))
                batch = [reg]
                last_addr = reg.address
        if batch:
            start = batch[0].address
            count = sum(r.length // 2 for r in batch)
            batches.append((start, count, list(batch)))
        return batches

    def _parse_and_validate_registers(self, raw_values, reg_defs):
        """Parse and validate raw register values with datatype and size support."""
        import struct
        parsed = {}
        if raw_values is None:
            for reg in reg_defs:
                parsed[reg.name] = None
            return parsed
        idx = 0
        for reg in reg_defs:
            try:
                reg_words = reg.length // 2
                if idx + reg_words > len(raw_values):
                    parsed[reg.name] = None
                    idx += reg_words
                    continue
                regs = raw_values[idx:idx + reg_words]
                _LOGGER.debug(
                    "Register debug: name=%s, address=0x%04X, raw_regs=%s, reg_words=%d",
                    reg.name, reg.address, regs, reg_words
                )
                if reg.data_type == "Float" and reg_words == 2:
                    # SDM meters require swapped word order for float32
                    swapped_val = struct.unpack(">f", struct.pack(">HH", regs[1], regs[0]))[0]
                    normal_val = struct.unpack(">f", struct.pack(">HH", regs[0], regs[1]))[0]
                    _LOGGER.debug(
                        "Register debug: name=%s, address=0x%04X, raw_regs=%s, swapped_regs=%s, float(swapped)=%s, float(normal)=%s",
                        reg.name, reg.address, regs, [regs[1], regs[0]], swapped_val, normal_val
                    )
                elif reg.data_type == "UInt32" and reg_words == 2:
                    val = (regs[0] << 16) | regs[1]
                elif reg.data_type == "HEX":
                    if reg_words == 2:
                        val = (regs[0] << 16) | regs[1]
                    else:
                        val = regs[0]
                else:
                    val = regs[0]
                value = reg.apply_scaling(val)
                parsed[reg.name] = value
                idx += reg_words
            except Exception:
                parsed[reg.name] = None
                idx += reg.length // 2
        return parsed

class SDMMultiTierCoordinator:
    """Coordinator managing fast/normal/slow polling tiers."""

    def __init__(self, hass: HomeAssistant, device, name_prefix: str = ""):
        from datetime import timedelta

        self.device = device
        self.hass = hass

        # Define register groups by polling tier
        self.tiers = {
            "fast": {
                "interval": timedelta(seconds=5),
                "registers": [r for r in getattr(device, "register_map", []) if getattr(r, "polling", "normal") == "fast"],
            },
            "normal": {
                "interval": timedelta(seconds=30),
                "registers": [r for r in getattr(device, "register_map", []) if getattr(r, "polling", "normal") == "normal"],
            },
            "slow": {
                "interval": timedelta(seconds=300),
                "registers": [r for r in getattr(device, "register_map", []) if getattr(r, "polling", "normal") == "slow"],
            },
        }

        self.coordinators = {}
        for tier, cfg in self.tiers.items():
            self.coordinators[tier] = SDMDataUpdateCoordinator(
                hass=hass,
                name=f"{name_prefix}{tier.capitalize()} Tier",
                update_interval=cfg["interval"],
                device=SDMTierDeviceProxy(device, cfg["registers"]),
            )

    async def async_refresh_all(self):
        """Refresh all tiers."""
        _LOGGER.debug("SDMMultiTierCoordinator: Starting async_refresh_all for all tiers")
        await self.coordinators["fast"].async_refresh()
        await self.coordinators["normal"].async_refresh()
        await self.coordinators["slow"].async_refresh()

    def get_data(self, tier: str):
        """Get latest data for a tier."""
        return self.coordinators[tier].data if tier in self.coordinators else {}

class SDMTierDeviceProxy:
    """Proxy device exposing only a subset of registers for a polling tier."""

    def __init__(self, device, registers):
        self._device = device
        self.register_map = registers

    def __getattr__(self, attr):
        return getattr(self._device, attr)

    @property
    def device_info(self):
        """Return device info for Home Assistant device registry."""
        return self.device.device_info() if self.device else None

    async def async_read_registers(self, address: int, count: int = 1):
        """Delegate register reads to the underlying device (ensures lock is used)."""
        _LOGGER.debug(
            "SDMTierDeviceProxy: async_read_registers called for address 0x%04X, count %d, device=%s",
            address, count, repr(self._device)
        )
        return await self._device.async_read_registers(address, count)


    async def _async_update_data(self) -> Any:
        """Fetch data from the device with retry logic and track polling statistics."""
        import time
        if not hasattr(self, "poll_stats"):
            self.poll_stats = {
                "success_count": 0,
                "failure_count": 0,
                "last_update": None,
                "last_error": None,
                "avg_duration": 0.0,
                "total_duration": 0.0,
                "total_polls": 0,
            }
        max_attempts = 3
        delay = 1
        for attempt in range(1, max_attempts + 1):
            start = time.monotonic()
            try:
                registers = getattr(self.device, "register_map", None)
                if registers is not None:
                    batches = self._group_registers_for_batch(registers)
                    results = {}
                    for start_addr, count, reg_defs in batches:
                        raw = await self.device.async_read_registers(start_addr, count)
                        _LOGGER.debug(
                            "SDMTierDeviceProxy: async_read_registers called for address 0x%04X, count %d, raw=%s",
                            start_addr, count, raw)
                        parsed = self._parse_and_validate_registers(raw, reg_defs)
                        results.update(parsed)
                    duration = time.monotonic() - start
                    self.poll_stats["success_count"] += 1
                    self.poll_stats["last_update"] = time.time()
                    self.poll_stats["last_error"] = None
                    self.poll_stats["total_duration"] += duration
                    self.poll_stats["total_polls"] += 1
                    self.poll_stats["avg_duration"] = (
                        self.poll_stats["total_duration"] / self.poll_stats["total_polls"]
                    )
                    return results
                data = await self.device.async_read_registers(0x0000, 2)
                duration = time.monotonic() - start
                self.poll_stats["success_count"] += 1
                self.poll_stats["last_update"] = time.time()
                self.poll_stats["last_error"] = None
                self.poll_stats["total_duration"] += duration
                self.poll_stats["total_polls"] += 1
                self.poll_stats["avg_duration"] = (
                    self.poll_stats["total_duration"] / self.poll_stats["total_polls"]
                )
                return data
            except Exception as err:
                await self._async_close_client()
                self.poll_stats["failure_count"] += 1
                self.poll_stats["last_error"] = str(err)
                if attempt == max_attempts:
                    raise UpdateFailed(f"Error updating data after {attempt} attempts: {err}") from err
                import asyncio
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

    def _group_registers_for_batch(self, register_defs):
        """Group register definitions into contiguous address batches."""
        sorted_regs = sorted(register_defs, key=lambda r: r.address)
        batches = []
        batch = []
        last_addr = None
        for reg in sorted_regs:
            if not batch:
                batch = [reg]
                last_addr = reg.address
                continue
            expected_next = last_addr + reg.length // 2
            if reg.address == expected_next:
                batch.append(reg)
                last_addr = reg.address
            else:
                start = batch[0].address
                count = sum(r.length // 2 for r in batch)
                batches.append((start, count, list(batch)))
                batch = [reg]
                last_addr = reg.address
        if batch:
            start = batch[0].address
            count = sum(r.length // 2 for r in batch)
            batches.append((start, count, list(batch)))
        return batches

    def _parse_and_validate_registers(self, raw_values, reg_defs):
        """Parse and validate raw register values with datatype and size support."""
        import struct
        parsed = {}
        if raw_values is None:
            for reg in reg_defs:
                parsed[reg.name] = None
            return parsed
        idx = 0
        for reg in reg_defs:
            try:
                reg_words = reg.length // 2
                if idx + reg_words > len(raw_values):
                    parsed[reg.name] = None
                    idx += reg_words
                    continue
                regs = raw_values[idx:idx + reg_words]
                if reg.data_type == "Float" and reg_words == 2:
                    val = struct.unpack(">f", struct.pack(">HH", regs[0], regs[1]))[0]
                elif reg.data_type == "UInt32" and reg_words == 2:
                    val = (regs[0] << 16) | regs[1]
                elif reg.data_type == "HEX":
                    if reg_words == 2:
                        val = (regs[0] << 16) | regs[1]
                    else:
                        val = regs[0]
                else:
                    val = regs[0]
                value = reg.apply_scaling(val)
                parsed[reg.name] = value
                idx += reg_words
            except Exception:
                parsed[reg.name] = None
                idx += reg.length // 2
        return parsed
