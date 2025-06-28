"""Pytest fixture for a mock DataUpdateCoordinator."""

import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_coordinator():
    """Return a mock DataUpdateCoordinator."""
    coordinator = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator.last_update_success = True
    coordinator.data = {}
    coordinator.update_interval = 30
    return coordinator
