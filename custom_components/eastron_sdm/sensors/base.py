"""Sensor base classes for Eastron SDM integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass

from ..shared_base import SdmBaseEntity
from ..coordinator import SdmCoordinator, DecodedValue
from ..models.sdm120 import RegisterSpec

_DEVICE_CLASS_MAP = {
    "energy": SensorDeviceClass.ENERGY,
    "power": SensorDeviceClass.POWER,
    "voltage": SensorDeviceClass.VOLTAGE,
    "current": SensorDeviceClass.CURRENT,
    "frequency": SensorDeviceClass.FREQUENCY,
    "apparent_power": SensorDeviceClass.APPARENT_POWER,
    "reactive_power": SensorDeviceClass.REACTIVE_POWER,
    "power_factor": SensorDeviceClass.POWER_FACTOR,
}

_STATE_CLASS_MAP = {
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
    "measurement": SensorStateClass.MEASUREMENT,
}


class SdmBaseSensor(SdmBaseEntity, SensorEntity):
    """Base sensor backed by SDM register data."""

    _attr_should_poll = False

    def __init__(self, coordinator: SdmCoordinator, entry, spec: RegisterSpec) -> None:
        unique_id = coordinator.build_unique_id(spec.key)
        super().__init__(coordinator, entry, unique_id=unique_id, translation_key=spec.key)
        self._spec = spec
        self._attr_entity_registry_enabled_default = spec.enabled_default

        self._attr_device_class = _DEVICE_CLASS_MAP.get(spec.device_class)
        self._attr_state_class = _STATE_CLASS_MAP.get(spec.state_class)
        self._attr_native_unit_of_measurement = spec.unit
        if spec.precision is not None:
            self._attr_suggested_display_precision = spec.precision

    def _current_value(self) -> float | int | None:
        data: dict[str, DecodedValue] = self.coordinator.data or {}
        dv: DecodedValue | None = data.get(self._spec.key)
        if not dv:
            return None
        return dv.value

    @property
    def native_value(self) -> float | int | None:  # type: ignore[override]
        val = self._current_value()
        if val is None:
            return None
        precision = getattr(self._spec, "precision", None)
        if precision is not None and isinstance(val, (int, float)):
            try:
                return round(float(val), precision)
            except Exception:
                return val
        return val

    @property
    def available(self) -> bool:  # type: ignore[override]
        return super().available and self._current_value() is not None
