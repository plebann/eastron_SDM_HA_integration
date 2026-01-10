"""Shared base entity for Eastron SDM integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class SdmBaseEntity(CoordinatorEntity):
    """Common coordinator-backed entity behavior."""

    def __init__(self, coordinator, entry: ConfigEntry, *, unique_id: str, translation_key: str | None = None) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_has_entity_name = True
        self._attr_unique_id = unique_id
        if translation_key:
            self._attr_translation_key = translation_key

    @property
    def device_info(self) -> dict[str, Any]:
        identifier = self.coordinator.serial_identifier or f"{self.coordinator.host}_{self.coordinator.unit_id}"
        return {
            "identifiers": {(DOMAIN, identifier)},
            "name": self.entry.title,
            "manufacturer": "Eastron",
            "model": "SDM120",
        }

    @property
    def available(self) -> bool:  # pragma: no cover - thin wrapper
        return bool(self.coordinator.last_update_success and self.coordinator.data)
