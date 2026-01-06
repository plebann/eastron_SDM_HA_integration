"""Sensor platform for Eastron SDM integration."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .coordinator import SdmCoordinator
from .models.sdm120 import get_register_specs
from .sensors import SdmRegisterSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SdmCoordinator = data["coordinator"]
    specs = get_register_specs()
    entities = [
        SdmRegisterSensor(coordinator, entry, spec)
        for spec in specs
        if spec.category != "config"
    ]

    async_add_entities(entities)
    _LOGGER.debug("Added %d SDM sensors for entry %s", len(entities), entry.entry_id)
