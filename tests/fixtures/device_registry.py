"""Pytest fixture for a mock Home Assistant device registry entry."""

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_device_entry():
    """Return a mock device registry entry."""
    entry = MagicMock()
    entry.id = "mock_device_id"
    entry.name = "SDM120 Test Device"
    entry.model = "SDM120"
    entry.manufacturer = "Eastron"
    entry.sw_version = "1.0"
    entry.hw_version = "A"
    entry.identifiers = {("eastron_sdm", "sdm120_1")}
    entry.via_device_id = None
    return entry
