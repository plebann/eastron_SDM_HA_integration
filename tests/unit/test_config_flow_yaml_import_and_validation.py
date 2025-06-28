"""Test YAML import functionality and configuration validation logic for Eastron SDM config flow."""

import pytest
from unittest.mock import patch
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.eastron_sdm.const import DOMAIN

@pytest.mark.asyncio
async def test_yaml_import_functionality(hass: HomeAssistant):
    """Test YAML import functionality if supported."""
    # Simulate YAML import source
    yaml_config = {
        "host": "192.168.1.150",
        "port": 502,
        "unit_id": 3,
        "name": "SDM120 YAML",
    }
    with patch(
        "custom_components.eastron_sdm.config_flow.validate_modbus_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data=yaml_config
        )
        # Should create the entry
        assert result["type"] == "create_entry"
        assert result["title"] == yaml_config["name"]
        assert result["data"]["host"] == yaml_config["host"]
        assert result["data"]["unit_id"] == yaml_config["unit_id"]

@pytest.mark.asyncio
async def test_config_validation_logic(hass: HomeAssistant):
    """Test configuration validation logic for edge cases."""
    # Invalid config: missing host
    invalid_config = {
        "port": 502,
        "unit_id": 1,
        "name": "No Host",
    }
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
            user_input=invalid_config,
        )
        assert result2["type"] == "form"
        assert "host" in result2["errors"]
