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
from .coordinator import SDMDataUpdateCoordinator
from .device_models import get_number_entities_for_model

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eastron SDM number entities from a config entry."""
    coordinator: SDMDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_model = coordinator.device_model

    # Get number entity definitions from device_models.py
    number_entities = get_number_entities_for_model(device_model)
    device_name = entry.data.get("device_name", "eastron_sdm")

    entities = [
        SDMNumberEntity(coordinator, entry, entity_def, device_name)
        for entity_def in number_entities
    ]

    async_add_entities(entities, update_before_add=True)


class SDMNumberEntity(NumberEntity):
    """Representation of a configurable number entity for Eastron SDM."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SDMDataUpdateCoordinator,
        entry: ConfigEntry,
        entity_def: Any,
        device_name: str,
    ) -> None:
        """Initialize the number entity."""
        self.coordinator = coordinator
        self.entity_def = entity_def
        self._attr_unique_id = f"{device_name}_{entity_def.key}"
        self._attr_translation_key = entity_def.key
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
