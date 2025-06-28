"""Button entities for Eastron SDM integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SDMMultiTierCoordinator
from .device_models import get_button_entities_for_model

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eastron SDM button entities from a config entry."""
    multi_tier_coordinator: SDMMultiTierCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_model = entry.data.get("model", "SDM120")

    # Get button entity definitions from device_models.py
    button_entities = get_button_entities_for_model(device_model)
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

    device_info = getattr(multi_tier_coordinator, "device_info", None)
    entities = [
        SDMButtonEntity(
            multi_tier_coordinator.coordinators[get_tier_for_category(getattr(entity_def, "category", "normal"))],
            entry,
            entity_def,
            device_name,
            device_info,
        )
        for entity_def in button_entities
    ]

    async_add_entities(entities, update_before_add=True)

class SDMButtonEntity(ButtonEntity):
    """Representation of a button entity for Eastron SDM."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        entity_def: Any,
        device_name: str,
        device_info: Any,
    ) -> None:
        """Initialize the button entity."""
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
        # Map string category to EntityCategory enum if needed
        category = getattr(entity_def, "category", None)
        if category == "Config":
            self._attr_entity_category = EntityCategory.CONFIG
        elif category == "Diagnostic":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        else:
            self._attr_entity_category = None
        self._attr_device_info = device_info
        # Defensive: ensure required attributes for ButtonEntity are not None
        if hasattr(entity_def, "confirmation") and getattr(entity_def, "confirmation", None) is None:
            self._attr_confirmation = False
        # Enable by default only for Basic category
        self._attr_entity_registry_enabled_default = (getattr(entity_def, "category", None) == "Basic")
    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_press_button(self.entity_def)
        await self.coordinator.async_request_refresh()
