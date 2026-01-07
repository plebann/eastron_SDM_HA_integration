"""Energy accumulator sensors for SDM120 - slow-tier total energy readings."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import SdmBaseSensor

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from ..coordinator import SdmCoordinator
    from ..models.sdm120 import RegisterSpec


class SdmEnergySensor(SdmBaseSensor):
    """Base class for energy accumulator sensors.
    
    Includes import, export, and total active energy sensors with
    total_increasing state class for cumulative energy tracking.
    """

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry, spec: RegisterSpec) -> None:
        """Initialize energy sensor."""
        super().__init__(coordinator, entry, spec)

    def _handle_energy_reset(self, new_value: float, old_value: float) -> float:
        """Detect and handle energy counter resets.
        
        Future enhancement for meter rollover detection.
        
        Args:
            new_value: Current energy reading.
            old_value: Previous energy reading.
            
        Returns:
            Adjusted energy value.
        """
        return new_value


class SdmImportEnergySensor(SdmEnergySensor):
    """Import active energy sensor (kWh)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize import energy sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("import_active_energy")
        super().__init__(coordinator, entry, spec)


class SdmExportEnergySensor(SdmEnergySensor):
    """Export active energy sensor (kWh)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize export energy sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("export_active_energy")
        super().__init__(coordinator, entry, spec)


class SdmTotalEnergySensor(SdmEnergySensor):
    """Total active energy sensor (kWh)."""

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry) -> None:
        """Initialize total energy sensor."""
        from ..models.sdm120 import _get_spec_by_key
        spec = _get_spec_by_key("total_active_energy")
        super().__init__(coordinator, entry, spec)
