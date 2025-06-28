"""Eastron SDM Energy Meter integration entry point."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eastron SDM integration from a config entry."""
    _LOGGER.debug("Setting up Eastron SDM integration for entry: %s", entry.entry_id)
    # Placeholder for coordinator and platform setup
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Eastron SDM integration for entry: %s", entry.entry_id)
    # Placeholder for unloading platforms and cleanup
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of a config entry."""
    _LOGGER.debug("Removing Eastron SDM integration for entry: %s", entry.entry_id)
    # Placeholder for any cleanup on removal
