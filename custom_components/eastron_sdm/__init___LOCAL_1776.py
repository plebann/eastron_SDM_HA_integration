"""Eastron SDM integration init."""
from __future__ import annotations

from typing import Any
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import SdmCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # pragma: no cover - minimal
    """Set up via YAML (not supported) placeholder."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eastron SDM from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = SdmCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = hass.data[DOMAIN].pop(entry.entry_id, {})
    coord: SdmCoordinator | None = data.get("coordinator")
    if coord:
        await coord.async_close()
    return unload_ok
