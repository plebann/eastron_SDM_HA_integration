"""Sensor platform for Eastron SDM integration."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .coordinator import SdmCoordinator
from .sensors import (
    SdmVoltageSensor,
    SdmCurrentSensor,
    SdmActivePowerSensor,
    SdmImportEnergySensor,
    SdmExportEnergySensor,
    SdmTotalEnergySensor,
    SdmApparentPowerSensor,
    SdmReactivePowerSensor,
    SdmPowerFactorSensor,
    SdmFrequencySensor,
    SdmPowerDemandSensor,
    SdmSerialNumberSensor,
    SdmMeterCodeSensor,
    SdmSoftwareVersionSensor,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SdmCoordinator = data["coordinator"]
    
    # Explicitly instantiate each specialized sensor
    entities = [
        # Fast tier - Real-time measurements
        SdmVoltageSensor(coordinator, entry),
        SdmCurrentSensor(coordinator, entry),
        SdmActivePowerSensor(coordinator, entry),
        
        # Slow tier - Energy accumulators
        SdmImportEnergySensor(coordinator, entry),
        SdmExportEnergySensor(coordinator, entry),
        SdmTotalEnergySensor(coordinator, entry),
        
        # Normal tier - Power quality
        SdmApparentPowerSensor(coordinator, entry),
        SdmReactivePowerSensor(coordinator, entry),
        SdmPowerFactorSensor(coordinator, entry),
        SdmFrequencySensor(coordinator, entry),
        
        # Slow tier - Diagnostic
        SdmPowerDemandSensor(coordinator, entry),
        SdmSerialNumberSensor(coordinator, entry),
        SdmMeterCodeSensor(coordinator, entry),
        SdmSoftwareVersionSensor(coordinator, entry),
    ]

    async_add_entities(entities)
    _LOGGER.debug("Added %d SDM sensors for entry %s", len(entities), entry.entry_id)

