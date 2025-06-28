"""Number entities for Eastron SDM integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import (
    NumberEntity,
    NumberDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN
from .coordinator import SDMMultiTierCoordinator
from .device_models import get_number_entities_for_model

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eastron SDM number entities from a config entry."""
    multi_tier_coordinator: SDMMultiTierCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_model = entry.data.get("model", "SDM120")

    # Get number entity definitions from device_models.py
    number_entities = get_number_entities_for_model(device_model)
    device_name = entry.data.get("device_name", "eastron_sdm")

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

    entities = [
        SDMNumberEntity(
            multi_tier_coordinator.coordinators[get_tier_for_category(getattr(entity_def, "category", "normal"))],
            entry,
            entity_def,
            device_name,
        )
        for entity_def in number_entities
    ]

    async_add_entities(entities, update_before_add=True)


class SDMNumberEntity(NumberEntity):
    """Representation of a configurable number entity for Eastron SDM."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        entity_def: Any,
        device_name: str,
    ) -> None:
        """Initialize the number entity."""
        self.coordinator = coordinator
        self.entity_def = entity_def
        key = getattr(entity_def, "parameter_key", None)
        if key is None:
            key = getattr(entity_def, "address", "unknown")
        self._attr_unique_id = f"{device_name}_{key}"
        translation_key = getattr(entity_def, "parameter_key", None)
        if translation_key is None:
            translation_key = str(getattr(entity_def, "address", "unknown"))
        self._attr_translation_key = translation_key
        self._attr_name = None  # Use translation
        self._attr_native_min_value = entity_def.min_value
        self._attr_native_max_value = entity_def.max_value
        self._attr_native_step = entity_def.step
        self._attr_native_unit_of_measurement = entity_def.unit
        self._attr_device_class = entity_def.device_class
        self._attr_entity_category = entity_def.entity_category
        self._attr_device_info = coordinator.device_info
        # Enable by default only for Basic category
        self._attr_entity_registry_enabled_default = (getattr(entity_def, "category", None) == "Basic")
    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self.entity_def.key)

    async def async_set_native_value(self, value: float) -> None:
        """Set a new value to the device."""
        await self.coordinator.async_write_number(self.entity_def, value)
        await self.coordinator.async_request_refresh()
