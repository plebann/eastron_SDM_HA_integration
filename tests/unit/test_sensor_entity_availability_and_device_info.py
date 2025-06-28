"""Test sensor availability, device info, unique ID, attributes, icon, and naming for Eastron SDM sensor entities."""

import pytest
from unittest.mock import MagicMock
from custom_components.eastron_sdm.sensor import EastronSDMSensor

@pytest.mark.asyncio
async def test_sensor_availability_determination():
    """Test that the sensor entity determines availability correctly."""
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
    assert sensor.available

    coordinator.last_update_success = False
    assert not sensor.available

def test_sensor_device_info_and_unique_id():
    """Test device info and unique ID assignment."""
    coordinator = MagicMock()
    coordinator.data = {"voltage": 230.12}
    sensor = EastronSDMSensor(
        coordinator=coordinator,
        name="SDM120 Voltage",
        unique_id="sdm120_1_voltage",
        device_class="voltage",
        unit_of_measurement="V",
        key="voltage",
    )
    assert sensor.unique_id == "sdm120_1_voltage"
    assert isinstance(sensor.device_info, dict)

def test_sensor_attributes_and_icon():
    """Test sensor attributes, icon, and naming conventions."""
    coordinator = MagicMock()
    coordinator.data = {"voltage": 230.12}
    sensor = EastronSDMSensor(
        coordinator=coordinator,
        name="SDM120 Voltage",
        unique_id="sdm120_1_voltage",
        device_class="voltage",
        unit_of_measurement="V",
        key="voltage",
    )
    # Attributes
    attrs = sensor.extra_state_attributes
    assert isinstance(attrs, dict)
    # Icon and device class
    assert sensor.icon is not None
    assert sensor.device_class == "voltage"
    # Naming
    assert "Voltage" in sensor.name
