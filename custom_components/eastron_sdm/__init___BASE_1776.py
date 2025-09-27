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
    from .coordinator import SDMMultiTierCoordinator
    from .device_models import create_device_instance

    _LOGGER.debug("Setting up Eastron SDM integration for entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})

    # Extract config entry data
    host = entry.data.get("host")
    port = entry.data.get("port", 502)
    unit_id = entry.data.get("unit_id", 1)
    model = entry.data.get("model")
    device_name = entry.data.get("device_name", f"SDM_{entry.entry_id}")

    # Create device instance (factory function must be implemented in device_models.py)
    device = create_device_instance(
        model=model,
        host=host,
        port=port,
        unit_id=unit_id,
        name=device_name,
    )

    # Instantiate multi-tier coordinator
    coordinator = SDMMultiTierCoordinator(
        hass=hass,
        device=device,
        name_prefix=f"{device_name} "
    )

    await coordinator.async_refresh_all()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "device": device,
    }

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
