"""Test duplicate device prevention and configuration options flow for Eastron SDM config flow."""

import pytest
from unittest.mock import patch
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.eastron_sdm.const import DOMAIN

@pytest.mark.asyncio
async def test_duplicate_device_prevention(hass: HomeAssistant):
    """Test that duplicate device entries are prevented."""
    # Add an existing entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "host": "192.168.1.100",
            "port": 502,
            "unit_id": 1,
            "name": "SDM120 Test",
            "model": "sdm120",
        },
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.eastron_sdm.config_flow.validate_modbus_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == "form"
        assert result["step_id"] == "user"

        # Try to add the same device again
        user_input = {
            "host": "192.168.1.100",
            "port": 502,
            "unit_id": 1,
            "name": "SDM120 Test",
        }
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=user_input,
        )
        assert result2["type"] == "abort"
        assert result2["reason"] == "already_configured"

@pytest.mark.asyncio
async def test_configuration_options_flow(hass: HomeAssistant):
    """Test configuration options flow (e.g., polling interval)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "host": "192.168.1.101",
            "port": 502,
            "unit_id": 2,
            "name": "SDM630 Main Panel",
            "model": "sdm630",
        },
        options={"polling_interval": 30},
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.eastron_sdm.config_flow.validate_modbus_connection",
        return_value=True,
    ):
        # Start options flow
        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["type"] == "form"
        assert result["step_id"] == "init"

        # Change polling interval
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"polling_interval": 5},
        )
        assert result2["type"] == "create_entry"
        assert result2["data"]["polling_interval"] == 5
