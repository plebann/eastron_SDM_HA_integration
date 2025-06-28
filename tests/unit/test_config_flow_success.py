"""Test successful user configuration flow for Eastron SDM integration."""

import pytest
from unittest.mock import patch
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.eastron_sdm.const import DOMAIN

@pytest.mark.asyncio
async def test_successful_user_config_flow(hass: HomeAssistant):
    """Test a successful user configuration flow."""
    # Import valid config
    from tests.fixtures.config_test_data import VALID_CONFIGS
    valid_config = VALID_CONFIGS[0]

    # Patch the Modbus connection check to always succeed
    with patch(
        "custom_components.eastron_sdm.config_flow.validate_modbus_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == "form"
        assert result["step_id"] == "user"

        # Submit the form with valid config data
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "host": valid_config["host"],
                "port": valid_config["port"],
                "unit_id": valid_config["unit_id"],
                "name": valid_config["name"],
            },
        )
        # Should create the entry
        assert result2["type"] == "create_entry"
        assert result2["title"] == valid_config["name"]
        assert result2["data"]["host"] == valid_config["host"]
        assert result2["data"]["port"] == valid_config["port"]
        assert result2["data"]["unit_id"] == valid_config["unit_id"]
        assert result2["data"]["name"] == valid_config["name"]
