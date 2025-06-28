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
        """Parse and validate raw register values."""
        parsed = {}
        if raw_values is None or len(raw_values) < len(reg_defs):
            for reg in reg_defs:
                parsed[reg.name] = None
            return parsed
        for idx, reg in enumerate(reg_defs):
            try:
                value = reg.apply_scaling(raw_values[idx])
                parsed[reg.name] = value
            except Exception:
                parsed[reg.name] = None
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
        return await self._device.async_read_registers(address, count)

    async def _async_get_client(self):
        """Get or create the Modbus TCP client."""
        if self._client is not None:
            return self._client
        try:
            from pymodbus.client.async_tcp import AsyncModbusTCPClient
        except ImportError:
            raise UpdateFailed("pymodbus not installed")
        self._client = AsyncModbusTCPClient(
            host=self.device.host, port=self.device.port
        )
        await self._client.connect()
        return self._client

    async def _async_close_client(self):
        """Close the Modbus TCP client."""
        if self._client is not None:
            await self._client.close()
            self._client = None

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
                client = await self._async_get_client()
                self.device.client = client
                registers = getattr(self.device, "register_map", None)
                if registers is not None:
                    batches = self._group_registers_for_batch(registers)
                    results = {}
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
        # register_defs: tuple/list of SDM120Register
        sorted_regs = sorted(register_defs, key=lambda r: r.address)
        batches = []
        batch = []
        last_addr = None
        for reg in sorted_regs:
            if not batch:
                batch = [reg]
                last_addr = reg.address
                continue
            # Assume each register is 2 words (4 bytes)
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
        """Parse and validate raw register values."""
        parsed = {}
        if raw_values is None or len(raw_values) < len(reg_defs):
            for reg in reg_defs:
                parsed[reg.name] = None
            return parsed
        for idx, reg in enumerate(reg_defs):
            try:
                value = reg.apply_scaling(raw_values[idx])
                # Add further validation if needed (e.g., range checks)
                parsed[reg.name] = value
            except Exception:
                parsed[reg.name] = None
        return parsed
