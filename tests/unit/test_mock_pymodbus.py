import pytest
from tests.utils.mock_pymodbus import MockPymodbusClient

@pytest.mark.asyncio
async def test_mock_pymodbus_connect_success():
    client = MockPymodbusClient()
    result = await client.connect()
    assert result is True
    assert client.connected

@pytest.mark.asyncio
async def test_mock_pymodbus_connect_failure():
    client = MockPymodbusClient(fail_connect=True)
    result = await client.connect()
    assert result is False
    assert not client.connected
