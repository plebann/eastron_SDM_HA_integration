"""Eastron SDM integration init."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import entity_registry as er

from .const import (
    DOMAIN,
    CONF_ENABLE_ADVANCED,
    CONF_ENABLE_DIAGNOSTIC,
    CONF_ENABLE_TWO_WAY,
    CONF_ENABLE_CONFIG,
)
from .coordinator import SdmCoordinator
from .models.sdm120 import get_register_specs

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "number", "select"]

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
    await _sync_entity_registry_enabled_state(hass, entry)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by syncing registry defaults then reloading."""
    await _sync_entity_registry_enabled_state(hass, entry)
    await hass.config_entries.async_reload(entry.entry_id)


async def _sync_entity_registry_enabled_state(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Mass enable/disable entities based on options flags."""
    registry = er.async_get(hass)
    data = {**entry.data, **entry.options}

    category_flags = {
        "basic": True,
        "advanced": data.get(CONF_ENABLE_ADVANCED, False),
        "diagnostic": data.get(CONF_ENABLE_DIAGNOSTIC, False),
        "two-way": data.get(CONF_ENABLE_TWO_WAY, False),
        "config": data.get(CONF_ENABLE_CONFIG, False),
    }

    specs = get_register_specs()
    entries = er.async_entries_for_config_entry(registry, entry.entry_id)

    for reg_entry in entries:
        spec = next((s for s in specs if reg_entry.unique_id.endswith(f"_{s.key}")), None)
        if not spec:
            continue

        flag = category_flags.get(spec.category)
        if flag is None:
            continue

        desired_enabled = bool(flag)

        if reg_entry.disabled_by == er.RegistryEntryDisabler.USER:
            continue

        if desired_enabled and reg_entry.disabled_by == er.RegistryEntryDisabler.INTEGRATION:
            await registry.async_update_entity(reg_entry.entity_id, disabled_by=None)
        elif not desired_enabled and reg_entry.disabled_by is None:
            await registry.async_update_entity(reg_entry.entity_id, disabled_by=er.RegistryEntryDisabler.INTEGRATION)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = hass.data[DOMAIN].pop(entry.entry_id, {})
    coord: SdmCoordinator | None = data.get("coordinator")
    if coord:
        await coord.async_close()
    return unload_ok
