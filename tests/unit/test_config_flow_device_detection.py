"""Test device detection and identification in Eastron SDM config flow."""

import pytest
from unittest.mock import patch
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.eastron_sdm.const import DOMAIN

@pytest.mark.asyncio
async def test_device_detection_and_identification(hass: HomeAssistant):
    """Test device detection and identification step in config flow."""
    # Simulate device detection returning SDM120
    with patch(
        "custom_components.eastron_sdm.config_flow.detect_sdm_device_model",
        return_value="sdm120",
    ), patch(
        "custom_components.eastron_sdm.config_flow.validate_modbus_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == "form"
        assert result["step_id"] == "user"

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
        # Should create the entry and include model info
        assert result2["type"] == "create_entry"
        assert result2["data"]["model"] == "sdm120"
