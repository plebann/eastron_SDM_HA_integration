"""Pytest fixture for a mock Home Assistant instance."""

import pytest
from pytest_homeassistant_custom_component.common import get_test_home_assistant

@pytest.fixture
async def hass():
    """Return a mock Home Assistant instance."""
    hass = await get_test_home_assistant()
    yield hass
    await hass.async_stop()
