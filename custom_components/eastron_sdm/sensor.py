"""Sensor platform for Eastron SDM integration."""
from __future__ import annotations

import logging
from typing import Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_MODEL, DEFAULT_MODEL
from .coordinator import SdmCoordinator
from .models import RegisterSpec, get_model_specs
from .sensors.base import SdmBaseSensor

_LOGGER = logging.getLogger(__name__)


def _iter_sensor_specs(specs: Iterable[RegisterSpec]) -> list[RegisterSpec]:
    """Filter specs to those represented as sensors (exclude config/control)."""

    return [
        spec
        for spec in specs
        if spec.category != "config" and spec.control is None
    ]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SdmCoordinator = data["coordinator"]

    entry_data = {**entry.data, **entry.options}
    model = entry_data.get(CONF_MODEL, DEFAULT_MODEL)
    specs = _iter_sensor_specs(get_model_specs(model))

    entities = [SdmBaseSensor(coordinator, entry, spec) for spec in specs]
    async_add_entities(entities)
    _LOGGER.debug("Added %d SDM sensors for entry %s (model=%s)", len(entities), entry.entry_id, model)

