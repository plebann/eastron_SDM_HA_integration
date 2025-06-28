"""Select entities for Eastron SDM integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import (
    SelectEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SDMMultiTierCoordinator
from .device_models import get_select_entities_for_model

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eastron SDM select entities from a config entry."""
    multi_tier_coordinator: SDMMultiTierCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_model = entry.data.get("model", "SDM120")

    # Get select entity definitions from device_models.py
    select_entities = get_select_entities_for_model(device_model)
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
        SDMSelectEntity(
            multi_tier_coordinator.coordinators[get_tier_for_category(getattr(entity_def, "category", "normal"))],
            entry,
            entity_def,
            device_name,
            device_info,
        )
        for entity_def in select_entities
    ]

    async_add_entities(entities, update_before_add=True)

class SDMSelectEntity(SelectEntity):
    """Representation of a configurable select entity for Eastron SDM."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        entity_def: Any,
        device_name: str,
        device_info: Any,
    ) -> None:
        """Initialize the select entity."""
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
        self._attr_options = entity_def.options if getattr(entity_def, "options", None) is not None else []
        # Map string category to EntityCategory enum if needed
        category = getattr(entity_def, "category", None)
        from homeassistant.helpers.entity import EntityCategory
        if category == "Config":
            self._attr_entity_category = EntityCategory.CONFIG
        elif category == "Diagnostic":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        else:
            self._attr_entity_category = None
        self._attr_device_info = device_info
        # Enable by default only for Basic category
        self._attr_entity_registry_enabled_default = (getattr(entity_def, "category", None) == "Basic")
    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self.coordinator.data.get(self.entity_def.key)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.async_write_select(self.entity_def, option)
        await self.coordinator.async_request_refresh()
