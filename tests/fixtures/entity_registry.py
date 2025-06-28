"""Pytest fixture for a mock Home Assistant entity registry."""

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_entity_registry():
    """Return a mock entity registry."""
    registry = MagicMock()
    registry.async_get_entity_id = MagicMock(return_value="sensor.sdm120_voltage")
    registry.async_get = MagicMock()
    registry.async_update_entity = MagicMock()
    registry.async_remove = MagicMock()
    return registry
