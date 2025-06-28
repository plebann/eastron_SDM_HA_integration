"""Mock pymodbus client for Eastron SDM integration tests."""

from unittest.mock import AsyncMock

class MockPymodbusClient:
    """A simple mock for pymodbus ModbusTcpClient."""

    def __init__(self, responses=None, fail_connect=False, error_reads=None, timeout_reads=None):
        self.responses = responses or {}
        self.fail_connect = fail_connect
        self.connected = False
        self.error_reads = error_reads or set()
        self.timeout_reads = timeout_reads or set()

    async def connect(self):
        if self.fail_connect:
            self.connected = False
            return False
        self.connected = True
        return True

    async def close(self):
        self.connected = False

    async def read_holding_registers(self, address, count=1, unit=1):
        """Return a mock response for holding register reads."""
        key = (address, count, unit)
        if key in self.timeout_reads:
            raise TimeoutError("Mock timeout for read_holding_registers")
        if key in self.error_reads:
            mock_response = AsyncMock()
            mock_response.isError.return_value = True
            mock_response.registers = []
            return mock_response
        if key in self.responses:
            return self.responses[key]
        # Default: return a mock with .registers attribute as zeros
        mock_response = AsyncMock()
        mock_response.registers = [0] * count
        mock_response.isError.return_value = False
        return mock_response

    async def write_register(self, address, value, unit=1):
        """Mock write register operation."""
        mock_response = AsyncMock()
        mock_response.isError.return_value = False
        return mock_response

    async def write_registers(self, address, values, unit=1):
        """Mock write multiple registers operation."""
        mock_response = AsyncMock()
        mock_response.isError.return_value = False
        return mock_response
