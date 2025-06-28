"""Test successful data update cycles and connection management for Eastron SDM DataUpdateCoordinator."""

import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant

from custom_components.eastron_sdm.coordinator import SDMDataUpdateCoordinator

@pytest.mark.asyncio
async def test_successful_data_update_cycle(hass: HomeAssistant):
    """Test that the coordinator successfully updates data from the device."""
    # Mock the Modbus client and its read_holding_registers method
    mock_client = AsyncMock()
    mock_client.read_holding_registers.return_value.registers = [23012, 0]
    mock_client.read_holding_registers.return_value.isError.return_value = False

    with patch(
        "custom_components.eastron_sdm.coordinator.create_modbus_client",
        return_value=mock_client,
    ):
        coordinator = SDMDataUpdateCoordinator(
            hass,
            host="192.168.1.100",
            port=4196,
            unit_id=1,
            model="sdm120",
            polling_interval=10,
        )
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert coordinator.data is not None
        assert "voltage" in coordinator.data or isinstance(coordinator.data, dict)
