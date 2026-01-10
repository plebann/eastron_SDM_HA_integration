"""Eastron SDM integration init."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import entity_registry as er, device_registry as dr

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
    await coordinator.async_ensure_serial_number()
    await _maybe_migrate_to_serial_identity(hass, entry, coordinator)
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
            registry.async_update_entity(reg_entry.entity_id, disabled_by=None)
        elif not desired_enabled and reg_entry.disabled_by is None:
            registry.async_update_entity(reg_entry.entity_id, disabled_by=er.RegistryEntryDisabler.INTEGRATION)


async def _maybe_migrate_to_serial_identity(hass: HomeAssistant, entry: ConfigEntry, coordinator: SdmCoordinator) -> None:
    """One-time migration from host+unit identifiers to serial-based identifiers."""
    migrated = entry.options.get("serial_identity_migrated")
    serial = coordinator.serial_identifier or await coordinator.async_ensure_serial_number()
    if migrated or not serial:
        return

    registry = er.async_get(hass)
    dev_registry = dr.async_get(hass)

    old_identifier = (DOMAIN, f"{coordinator.host}_{coordinator.unit_id}")
    new_identifier = (DOMAIN, serial)

    device = dev_registry.async_get_device({old_identifier})
    if device and old_identifier in device.identifiers:
        dev_registry.async_update_device(device.id, new_identifiers={new_identifier})

    entries = er.async_entries_for_config_entry(registry, entry.entry_id)
    old_prefix = f"eastron_sdm_{coordinator.host}_{coordinator.unit_id}_"
    for reg_entry in entries:
        if not reg_entry.unique_id.startswith(old_prefix):
            continue
        new_unique_id = f"eastron_sdm_{serial}_" + reg_entry.unique_id[len(old_prefix):]
        registry.async_update_entity(reg_entry.entity_id, new_unique_id=new_unique_id)
        if device and reg_entry.device_id != device.id:
            registry.async_update_entity(reg_entry.entity_id, device_id=device.id)

    # Mark migration done
    new_options = {**entry.options, "serial_identity_migrated": True}
    hass.config_entries.async_update_entry(entry, options=new_options)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = hass.data[DOMAIN].pop(entry.entry_id, {})
    coord: SdmCoordinator | None = data.get("coordinator")
    if coord:
        await coord.async_close()
    return unload_ok
