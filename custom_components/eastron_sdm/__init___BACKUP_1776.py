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

<<<<<<< HEAD
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # pragma: no cover - minimal
    """Set up via YAML (not supported) placeholder."""
=======
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eastron SDM integration from a config entry."""
    from .coordinator import SDMMultiTierCoordinator
    from .device_models import create_device_instance

    _LOGGER.debug("Setting up Eastron SDM integration for entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})
    # Extract config entry data
    host = entry.data.get("host")
    port = entry.data.get("port", 4196)
    unit_id = entry.data.get("unit_id", 1)
    model = entry.data.get("model")
    device_name = entry.data.get("device_name", f"SDM_{entry.entry_id}")
    timeout = entry.data.get("timeout", 10)

    # Create device instance (factory function must be implemented in device_models.py)
    device = create_device_instance(
        model=model,
        unit_id=unit_id,
        host=host,
        port=port,
        timeout=timeout,
        name=device_name,
    )
    # Set device_name attribute for device registry
    device.device_name = device_name

    # Set register_map based on model
    from .device_models import SDM120RegisterMap, SDM630RegisterMap
    if model == "SDM120":
        device.register_map = list(SDM120RegisterMap.REGISTERS)
    elif model == "SDM630":
        device.register_map = list(SDM630RegisterMap.REGISTERS)
    else:
        device.register_map = []

    # Initialize and connect pymodbus client
    try:
        from pymodbus.client import AsyncModbusTcpClient
        device.client = AsyncModbusTcpClient(host=host, port=port)
        await device.client.connect()
    except Exception as exc:
        _LOGGER.error("Failed to initialize Modbus client: %s", exc)
        return False

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

    # Forward setup to supported platforms
    PLATFORMS = ["sensor", "number", "button", "select"]
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

>>>>>>> main
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
<<<<<<< HEAD
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = hass.data[DOMAIN].pop(entry.entry_id, {})
    coord: SdmCoordinator | None = data.get("coordinator")
    if coord:
        await coord.async_close()
    return unload_ok
=======
    _LOGGER.debug("Unloading Eastron SDM integration for entry: %s", entry.entry_id)
    PLATFORMS = ["sensor", "number", "button", "select"]
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of a config entry."""
    _LOGGER.debug("Removing Eastron SDM integration for entry: %s", entry.entry_id)
    # Placeholder for any cleanup on removal
>>>>>>> main
