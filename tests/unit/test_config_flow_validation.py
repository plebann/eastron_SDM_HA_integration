"""Test invalid host/port input validation and connection failure scenarios for Eastron SDM config flow."""

import pytest
from unittest.mock import patch
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.eastron_sdm.const import DOMAIN

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_input,expected_error",
    [
        # Missing host
        ({"host": "", "port": 4196, "unit_id": 1, "name": "No Host"}, "host"),
        # Invalid port (string)
        ({"host": "192.168.1.10", "port": "not_a_port", "unit_id": 1, "name": "Bad Port"}, "port"),
        # Invalid port (out of range)
        ({"host": "192.168.1.10", "port": 70000, "unit_id": 1, "name": "Bad Port"}, "port"),
        # Invalid unit_id (negative)
        ({"host": "192.168.1.10", "port": 4196, "unit_id": -1, "name": "Bad Unit"}, "unit_id"),
        # Name with special characters
        ({"host": "192.168.1.10", "port": 4196, "unit_id": 1, "name": "Bad@Name!"}, "name"),
    ],
)
async def test_invalid_user_input_validation(hass: HomeAssistant, user_input, expected_error):
    """Test invalid host/port/unit_id/name input validation."""
    with patch(
        "custom_components.eastron_sdm.config_flow.validate_modbus_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == "form"
        assert result["step_id"] == "user"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=user_input,
        )
        assert result2["type"] == "form"
        assert expected_error in result2["errors"]

@pytest.mark.asyncio
async def test_connection_failure_scenario(hass: HomeAssistant):
    """Test connection failure scenario during config flow."""
    user_input = {
        "host": "192.168.1.200",
        "port": 4196,
        "unit_id": 1,
        "name": "Connection Fail",
    }
    with patch(
        "custom_components.eastron_sdm.config_flow.validate_modbus_connection",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == "form"
        assert result["step_id"] == "user"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=user_input,
        )
        assert result2["type"] == "form"
        assert "base" in result2["errors"]
