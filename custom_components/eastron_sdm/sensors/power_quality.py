"""Power quality sensors for SDM120 - normal-tier secondary power measurements."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import SdmBaseSensor

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from ..coordinator import SdmCoordinator
    from ..models import RegisterSpec


class SdmPowerQualitySensor(SdmBaseSensor):
    """Base class for power quality measurement sensors.
    
    Includes apparent power, reactive power, power factor, and frequency
    sensors for detailed power quality monitoring.
    """

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry, spec: RegisterSpec) -> None:
        """Initialize power quality sensor."""
        super().__init__(coordinator, entry, spec)


class SdmApparentPowerSensor(SdmPowerQualitySensor):
    """Apparent power sensor (VA)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize apparent power sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("apparent_power")
        super().__init__(coordinator, entry, spec)


class SdmReactivePowerSensor(SdmPowerQualitySensor):
    """Reactive power sensor (var)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize reactive power sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("reactive_power")
        super().__init__(coordinator, entry, spec)


class SdmPowerFactorSensor(SdmPowerQualitySensor):
    """Power factor sensor (dimensionless)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize power factor sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("power_factor")
        super().__init__(coordinator, entry, spec)


class SdmFrequencySensor(SdmPowerQualitySensor):
    """Frequency sensor (Hz)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize frequency sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("frequency")
        super().__init__(coordinator, entry, spec)
