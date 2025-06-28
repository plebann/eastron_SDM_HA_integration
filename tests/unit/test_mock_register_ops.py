import pytest
from unittest.mock import AsyncMock
from tests.utils.mock_pymodbus import MockPymodbusClient

@pytest.mark.asyncio
async def test_read_holding_registers_returns_mocked_response():
    mock_response = AsyncMock()
    mock_response.registers = [42, 43]
    mock_response.isError.return_value = False
    responses = {(100, 2, 1): mock_response}
    client = MockPymodbusClient(responses=responses)
    result = await client.read_holding_registers(100, 2, 1)
    assert result.registers == [42, 43]
    assert not result.isError()

@pytest.mark.asyncio
async def test_read_holding_registers_default_response():
    client = MockPymodbusClient()
    result = await client.read_holding_registers(200, 3, 1)
    assert result.registers == [0, 0, 0]
    assert not result.isError()

@pytest.mark.asyncio
async def test_write_register_returns_success():
    client = MockPymodbusClient()
    result = await client.write_register(10, 123, 1)
    assert not result.isError()

@pytest.mark.asyncio
async def test_write_registers_returns_success():
    client = MockPymodbusClient()
    result = await client.write_registers(20, [1, 2, 3], 1)
    assert not result.isError()
