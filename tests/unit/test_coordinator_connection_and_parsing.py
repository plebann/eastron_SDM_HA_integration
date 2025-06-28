"""Test connection establishment, data parsing, error handling, and recovery for Eastron SDM DataUpdateCoordinator."""

import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant

from custom_components.eastron_sdm.coordinator import SDMDataUpdateCoordinator

@pytest.mark.asyncio
async def test_connection_establishment_and_management(hass: HomeAssistant):
    """Test that the coordinator establishes and manages the Modbus connection."""
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
            port=502,
            unit_id=1,
            model="sdm120",
            polling_interval=10,
        )
        await coordinator.async_refresh()
        mock_client.connect.assert_awaited()
        mock_client.close.assert_awaited()

@pytest.mark.asyncio
async def test_data_parsing_and_transformation(hass: HomeAssistant):
    """Test that the coordinator parses and transforms data correctly."""
    mock_client = AsyncMock()
    # Simulate voltage register returns 23012 (should be 230.12 V)
    mock_client.read_holding_registers.return_value.registers = [23012, 0]
    mock_client.read_holding_registers.return_value.isError.return_value = False

    with patch(
        "custom_components.eastron_sdm.coordinator.create_modbus_client",
        return_value=mock_client,
    ):
        coordinator = EastronSDMDataUpdateCoordinator(
            hass,
            host="192.168.1.100",
            port=502,
            unit_id=1,
            model="sdm120",
            polling_interval=10,
        )
        await coordinator.async_refresh()
        voltage = coordinator.data.get("voltage")
        assert voltage == pytest.approx(230.12, rel=1e-2)

@pytest.mark.asyncio
async def test_error_handling_and_recovery(hass: HomeAssistant):
    """Test error handling and recovery in the coordinator."""
    mock_client = AsyncMock()
    # Simulate error on first call, success on second
    mock_client.read_holding_registers.side_effect = [
        AsyncMock(isError=AsyncMock(return_value=True), registers=[]),
        AsyncMock(isError=AsyncMock(return_value=False), registers=[23012, 0]),
    ]

    with patch(
        "custom_components.eastron_sdm.coordinator.create_modbus_client",
        return_value=mock_client,
    ):
        coordinator = EastronSDMDataUpdateCoordinator(
            hass,
            host="192.168.1.100",
            port=502,
            unit_id=1,
            model="sdm120",
            polling_interval=10,
        )
        # First update fails
        await coordinator.async_refresh()
        assert not coordinator.last_update_success
        # Second update succeeds
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert coordinator.data.get("voltage") == pytest.approx(230.12, rel=1e-2)
