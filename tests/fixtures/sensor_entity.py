"""Pytest fixture for a mock Home Assistant sensor entity."""

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_sensor_entity():
    """Return a mock sensor entity."""
    entity = MagicMock()
    entity.entity_id = "sensor.sdm120_voltage"
    entity.unique_id = "sdm120_1_voltage"
    entity.state = 230.12
    entity.device_class = "voltage"
    entity.unit_of_measurement = "V"
    entity.available = True
    entity.extra_state_attributes = {"test_attr": "value"}
    return entity
