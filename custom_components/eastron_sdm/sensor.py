"""Sensor platform for Eastron SDM integration."""
from __future__ import annotations

from typing import Any
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass

from .const import DOMAIN, CONF_ENABLE_ADVANCED, CONF_ENABLE_DIAGNOSTIC
from .coordinator import SdmCoordinator, DecodedValue
from .models.sdm120 import get_register_specs, RegisterSpec

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SdmCoordinator = data["coordinator"]

    specs = get_register_specs(
        enable_advanced=coordinator.enable_advanced,
        enable_diagnostic=coordinator.enable_diagnostic,
    )

    entities: list[SensorEntity] = []
    for spec in specs:
        entities.append(SdmSensor(coordinator, entry, spec))

    async_add_entities(entities)
    _LOGGER.debug("Added %d SDM sensors for entry %s", len(entities), entry.entry_id)


class SdmSensor(CoordinatorEntity[SdmCoordinator], SensorEntity):
    _attr_should_poll = False

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry, spec: RegisterSpec) -> None:
        super().__init__(coordinator)
        self._spec = spec
        self._entry_id = entry.entry_id
        base_name: str = entry.data.get("name", f"SDM120 {coordinator.host}")
        self._attr_name = f"{base_name} {self._friendly_part(spec.key)}"
        self._attr_unique_id = f"eastron_sdm_{coordinator.host}_{coordinator.unit_id}_{spec.key}"
        # Map spec.device_class/state_class strings to modern enums where possible
        if spec.device_class == "energy":
            self._attr_device_class = SensorDeviceClass.ENERGY
        elif spec.device_class == "power":
            self._attr_device_class = SensorDeviceClass.POWER
        elif spec.device_class == "voltage":
            self._attr_device_class = SensorDeviceClass.VOLTAGE
        elif spec.device_class == "current":
            self._attr_device_class = SensorDeviceClass.CURRENT
        elif spec.device_class == "frequency":
            self._attr_device_class = SensorDeviceClass.FREQUENCY
        else:
            self._attr_device_class = None

        self._attr_native_unit_of_measurement = spec.unit
        if spec.state_class == "total_increasing":
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif spec.state_class == "measurement":
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_state_class = None
        # Provide display precision hint if defined
        if getattr(spec, "precision", None) is not None:
            # Home Assistant uses suggested_display_precision to format UI
            self._attr_suggested_display_precision = spec.precision  # type: ignore[attr-defined]
        # Home Assistant built-ins for energy device class constant above is maintained for compatibility

    @staticmethod
    def _friendly_part(key: str) -> str:
        return key.replace("_", " ").title()

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        val = self._current_value()
        return val is not None

    def _current_value(self) -> float | int | None:
        data = self.coordinator.data or {}
        dv: DecodedValue | None = data.get(self._spec.key)  # type: ignore[arg-type]
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
            except Exception:  # pragma: no cover - defensive
                return val
        return val

    @property
    def device_info(self) -> dict[str, Any]:  # type: ignore[override]
        return {
            "identifiers": {(DOMAIN, f"{self.coordinator.host}_{self.coordinator.unit_id}")},
            "name": self.coordinator.entry.title,
            "manufacturer": "Eastron",
            "model": "SDM120",
        }
