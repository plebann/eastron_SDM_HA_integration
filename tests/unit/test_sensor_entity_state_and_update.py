"""Test sensor state calculation and updates for Eastron SDM sensor entities."""

import pytest
from unittest.mock import MagicMock
from custom_components.eastron_sdm.sensor import EastronSDMSensor

@pytest.mark.asyncio
async def test_sensor_state_calculation_and_update():
    """Test that the sensor entity calculates and updates its state correctly."""
    # Mock coordinator with voltage data
    coordinator = MagicMock()
    coordinator.data = {"voltage": 230.12}
    coordinator.last_update_success = True

    sensor = EastronSDMSensor(
        coordinator=coordinator,
        name="SDM120 Voltage",
        unique_id="sdm120_1_voltage",
        device_class="voltage",
        unit_of_measurement="V",
        key="voltage",
    )
    # State should reflect coordinator data
    assert sensor.state == 230.12

    # Simulate update
    coordinator.data["voltage"] = 231.00
    sensor.async_write_ha_state = MagicMock()
    await sensor.async_update()
    assert sensor.state == 231.00
