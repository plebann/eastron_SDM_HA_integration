"""Button entities for Eastron SDM integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SDMDataUpdateCoordinator
from .device_models import get_button_entities_for_model

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eastron SDM button entities from a config entry."""
    coordinator: SDMDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_model = coordinator.device_model

    # Get button entity definitions from device_models.py
    button_entities = get_button_entities_for_model(device_model)
    device_name = entry.data.get("device_name", "eastron_sdm")

    entities = [
        SDMButtonEntity(coordinator, entry, entity_def, device_name)
        for entity_def in button_entities
    ]

    async_add_entities(entities, update_before_add=True)

class SDMButtonEntity(ButtonEntity):
    """Representation of a button entity for Eastron SDM."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SDMDataUpdateCoordinator,
        entry: ConfigEntry,
        entity_def: Any,
        device_name: str,
    ) -> None:
        """Initialize the button entity."""
        self.coordinator = coordinator
        self.entity_def = entity_def
        self._attr_unique_id = f"{device_name}_{entity_def.key}"
        self._attr_translation_key = entity_def.key
        self._attr_name = None  # Use translation
        self._attr_entity_category = entity_def.entity_category
        self._attr_device_info = coordinator.device_info
        # Enable by default only for Basic category
        self._attr_entity_registry_enabled_default = (getattr(entity_def, "category", None) == "Basic")
    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_press_button(self.entity_def)
        await self.coordinator.async_request_refresh()
