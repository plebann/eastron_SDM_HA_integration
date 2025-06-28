"""Sensor platform for Eastron SDM integration."""

from __future__ import annotations

from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from .coordinator import SDMDataUpdateCoordinator
from .device_models import SDM120RegisterMap, SDMRegister, SDM630RegisterMap
import logging

_LOGGER = logging.getLogger(__name__)

# SDM630 and SDM120 sensor selection will be done dynamically from their register maps

class SDMSensorEntity(CoordinatorEntity, SensorEntity):
    """Generic Eastron SDM sensor entity."""

    def __init__(
        self,
        coordinator: SDMDataUpdateCoordinator,
        register: SDMRegister,
        device_name: str,
    ):
        super().__init__(coordinator)
        self._register = register
        self._attr_translation_key = register.parameter_key
        self._attr_name = None  # Use translation
        self._attr_unique_id = f"{device_name}_{register.parameter_key}"
        self._attr_native_unit_of_measurement = register.units
        self._attr_device_class = register.device_class
        self._attr_state_class = getattr(register, "state_class", None)
        # Enable by default only for Basic category
        self._attr_entity_registry_enabled_default = (getattr(register, "category", None) == "Basic")
    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self._register.name)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eastron SDM sensors from a config entry."""
    device_name = entry.data.get("device_name", "eastron_sdm")
    model = entry.data.get("model", "SDM120")
    coordinator: SDMDataUpdateCoordinator = hass.data["eastron_sdm"][entry.entry_id]["coordinator"]
    entities = []

    if model == "SDM630":
        reg_map = SDM630RegisterMap.REGISTERS
    else:
        reg_map = SDM120RegisterMap.REGISTERS

    for reg in reg_map:
        if reg.ha_entity_type == "sensor" and reg.use_registry:
            entities.append(SDMSensorEntity(coordinator, reg, device_name))

    async_add_entities(entities)
