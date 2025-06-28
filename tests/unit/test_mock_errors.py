import pytest
from tests.utils.mock_pymodbus import MockPymodbusClient

@pytest.mark.asyncio
async def test_read_holding_registers_timeout():
    client = MockPymodbusClient(timeout_reads={(10, 2, 1)})
    with pytest.raises(TimeoutError):
        await client.read_holding_registers(10, 2, 1)

@pytest.mark.asyncio
async def test_read_holding_registers_error_response():
    client = MockPymodbusClient(error_reads={(20, 2, 1)})
    result = await client.read_holding_registers(20, 2, 1)
    assert result.isError()
    assert result.registers == []
