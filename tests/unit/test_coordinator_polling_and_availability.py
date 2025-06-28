"""Test rate limiting, polling intervals, state management, and availability for Eastron SDM DataUpdateCoordinator."""

import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant

from custom_components.eastron_sdm.coordinator import EastronSDMDataUpdateCoordinator

@pytest.mark.asyncio
async def test_rate_limiting_and_polling_interval(hass: HomeAssistant):
    """Test that the coordinator respects the polling interval."""
    mock_client = AsyncMock()
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
            polling_interval=5,
        )
        assert coordinator.update_interval == 5

@pytest.mark.asyncio
async def test_coordinator_state_management_and_availability(hass: HomeAssistant):
    """Test coordinator state management and availability status updates."""
    mock_client = AsyncMock()
    # First call: success, second call: error
    mock_client.read_holding_registers.side_effect = [
        AsyncMock(isError=AsyncMock(return_value=False), registers=[23012, 0]),
        AsyncMock(isError=AsyncMock(return_value=True), registers=[]),
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
        # First update: available
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert coordinator.data.get("voltage") == pytest.approx(230.12, rel=1e-2)
        # Second update: unavailable
        await coordinator.async_refresh()
        assert not coordinator.last_update_success

@pytest.mark.asyncio
async def test_partial_failure_scenarios(hass: HomeAssistant):
    """Test partial failure scenarios (some registers fail, others succeed)."""
    mock_client = AsyncMock()
    # Simulate: voltage read fails, current read succeeds
    def side_effect(address, count=1, unit=1):
        if address == 0x0000:
            # Voltage register: error
            response = AsyncMock()
            response.isError.return_value = True
            response.registers = []
            return response
        elif address == 0x0006:
            # Current register: success
            response = AsyncMock()
            response.isError.return_value = False
            response.registers = [1005, 0]
            return response
        else:
            response = AsyncMock()
            response.isError.return_value = False
            response.registers = [0, 0]
            return response

    mock_client.read_holding_registers.side_effect = side_effect

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
        # Voltage should be missing or None, current should be present
        assert "voltage" not in coordinator.data or coordinator.data.get("voltage") is None
        assert coordinator.data.get("current") == pytest.approx(1.005, rel=1e-3)
