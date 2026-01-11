"""Shared base entity for Eastron SDM integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_MODEL, DEFAULT_MODEL


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
        data = {**self.entry.data, **self.entry.options}
        model = data.get(CONF_MODEL, DEFAULT_MODEL)
        return {
            "identifiers": {(DOMAIN, identifier)},
            "name": self.entry.title,
            "manufacturer": "Eastron",
            "model": model,
        }

    @property
    def available(self) -> bool:  # pragma: no cover - thin wrapper
        return bool(self.coordinator.last_update_success and self.coordinator.data)
