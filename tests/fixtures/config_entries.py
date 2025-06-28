"""Pytest fixtures for mock Home Assistant ConfigEntry objects."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

SDM120_CONFIG = {
    "host": "192.168.1.100",
    "port": 502,
    "unit_id": 1,
    "name": "SDM120 Test",
    "model": "sdm120",
}

SDM630_CONFIG = {
    "host": "192.168.1.101",
    "port": 502,
    "unit_id": 1,
    "name": "SDM630 Test",
    "model": "sdm630",
}

@pytest.fixture
def sdm120_entry():
    """Return a mock ConfigEntry for SDM120."""
    return MockConfigEntry(domain="eastron_sdm", data=SDM120_CONFIG)

@pytest.fixture
def sdm630_entry():
    """Return a mock ConfigEntry for SDM630."""
    return MockConfigEntry(domain="eastron_sdm", data=SDM630_CONFIG)
