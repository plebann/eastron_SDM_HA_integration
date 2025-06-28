"""Sensor platform for Eastron SDM integration."""

from __future__ import annotations

from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from .coordinator import SDMMultiTierCoordinator
from .device_models import SDM120RegisterMap, SDMRegister, SDM630RegisterMap
import logging

_LOGGER = logging.getLogger(__name__)

# SDM630 and SDM120 sensor selection will be done dynamically from their register maps

class SDMSensorEntity(CoordinatorEntity, SensorEntity):
    """Generic Eastron SDM sensor entity."""

    def __init__(
        self,
        coordinator,
        register: SDMRegister,
        device_name: str,
    ):
        super().__init__(coordinator)
        self._register = register
        self._device_name = device_name
        self._attr_translation_key = register.parameter_key
        # Title-case entity name: "Eastron SDM {device_name} {register.name}"
        self._attr_name = f"Eastron SDM {device_name} {register.name}".title()
        self._attr_unique_id = f"{device_name}_{register.parameter_key}"
        self._attr_native_unit_of_measurement = register.units
        self._attr_device_class = register.device_class
        self._attr_state_class = getattr(register, "state_class", None)
        # Enable by default only for Basic category
        self._attr_entity_registry_enabled_default = (getattr(register, "category", None) == "Basic")

    @property
    def device_info(self):
        """Return device info for Home Assistant device registry."""
        # Use the same identifiers as in device_models.py
        return {
            "identifiers": {("eastron_sdm", self._device_name)},
            "name": f"Eastron SDM {self._device_name}",
            "manufacturer": "Eastron",
            "model": "SDM Meter",
        }

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self._register.name)

# Alias for backward compatibility with tests
EastronSDMSensor = SDMSensorEntity

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eastron SDM sensors from a config entry."""
    device_name = entry.data.get("device_name", "eastron_sdm")
    model = entry.data.get("model", "SDM120")
    multi_tier_coordinator: SDMMultiTierCoordinator = hass.data["eastron_sdm"][entry.entry_id]["coordinator"]
    entities = []

    if model == "SDM630":
        reg_map = SDM630RegisterMap.REGISTERS
    else:
        reg_map = SDM120RegisterMap.REGISTERS

    # Map register category to polling tier
    def get_tier_for_category(category: str) -> str:
        if category == "Basic":
            return "fast"
        elif category == "Advanced":
            return "normal"
        elif category == "Diagnostic":
            return "slow"
        else:
            return "normal"

    for reg in reg_map:
        if reg.ha_entity_type == "sensor" and reg.use_registry:
            tier = get_tier_for_category(getattr(reg, "category", "normal"))
            tier_coordinator = multi_tier_coordinator.coordinators[tier]
            entities.append(SDMSensorEntity(tier_coordinator, reg, device_name))

    async_add_entities(entities)
