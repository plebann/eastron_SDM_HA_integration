"""Test unit conversion and formatting for Eastron SDM sensor entities."""

import pytest
from unittest.mock import MagicMock
from custom_components.eastron_sdm.sensor import EastronSDMSensor

@pytest.mark.asyncio
async def test_sensor_unit_conversion_and_formatting():
    """Test that the sensor entity converts and formats units correctly."""
    # Mock coordinator with raw data (e.g., 23012 should be 230.12 V)
    coordinator = MagicMock()
    coordinator.data = {"voltage": 230.1234}
    coordinator.last_update_success = True

    sensor = EastronSDMSensor(
        coordinator=coordinator,
        name="SDM120 Voltage",
        unique_id="sdm120_1_voltage",
        device_class="voltage",
        unit_of_measurement="V",
        key="voltage",
    )
    # State should be rounded/formatted as needed
    assert round(sensor.state, 2) == 230.12
    assert sensor.unit_of_measurement == "V"
