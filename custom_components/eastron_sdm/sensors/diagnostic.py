"""Diagnostic sensors for SDM120 - slow-tier device identity and status."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import SdmBaseSensor

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from ..coordinator import SdmCoordinator
    from ..models import RegisterSpec


class SdmDiagnosticSensor(SdmBaseSensor):
    """Base class for diagnostic sensors.
    
    Includes power demand, serial number, meter code, and software version
    sensors for device identification and diagnostics.
    """

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry, spec: RegisterSpec) -> None:
        """Initialize diagnostic sensor."""
        super().__init__(coordinator, entry, spec)


class SdmPowerDemandSensor(SdmDiagnosticSensor):
    """Total system power demand sensor (W)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize power demand sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("total_system_power_demand")
        super().__init__(coordinator, entry, spec)


class SdmSerialNumberSensor(SdmDiagnosticSensor):
    """Serial number sensor."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize serial number sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("serial_number")
        super().__init__(coordinator, entry, spec)


class SdmMeterCodeSensor(SdmDiagnosticSensor):
    """Meter code sensor."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize meter code sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("meter_code")
        super().__init__(coordinator, entry, spec)


class SdmSoftwareVersionSensor(SdmDiagnosticSensor):
    """Software version sensor."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize software version sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("software_version")
        super().__init__(coordinator, entry, spec)
