"""Measurement sensors for SDM120 - fast-tier real-time electrical measurements."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import SdmBaseSensor

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from ..coordinator import SdmCoordinator
    from ..models.sdm120 import RegisterSpec


class SdmMeasurementSensor(SdmBaseSensor):
    """Base class for fast-tier real-time measurement sensors.
    
    Includes voltage, current, and active power sensors that update
    every scan interval for real-time monitoring.
    """

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry, spec: RegisterSpec) -> None:
        """Initialize measurement sensor."""
        super().__init__(coordinator, entry, spec)


class SdmVoltageSensor(SdmMeasurementSensor):
    """Voltage sensor (V)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize voltage sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("voltage")
        super().__init__(coordinator, entry, spec)


class SdmCurrentSensor(SdmMeasurementSensor):
    """Current sensor (A)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize current sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("current")
        super().__init__(coordinator, entry, spec)


class SdmActivePowerSensor(SdmMeasurementSensor):
    """Active power sensor (W)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize active power sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("active_power")
        super().__init__(coordinator, entry, spec)
