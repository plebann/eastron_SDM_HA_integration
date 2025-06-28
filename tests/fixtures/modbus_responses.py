"""Realistic Modbus register response data for SDM120 and SDM630 models."""

from unittest.mock import AsyncMock

def make_mock_response(registers):
    mock = AsyncMock()
    mock.registers = registers
    mock.isError.return_value = False
    return mock

# Example: SDM120 voltage (register 0x0000), current (0x0006), total energy (0x0156)
SDM120_RESPONSES = {
    (0x0000, 2, 1): make_mock_response([23012, 0]),      # Voltage L-N: 230.12 V
    (0x0006, 2, 1): make_mock_response([1005, 0]),       # Current: 1.005 A
    (0x0156, 2, 1): make_mock_response([123456, 0]),     # Total energy: 1234.56 kWh
}

# Example: SDM630 voltage L1 (0x0000), current L1 (0x0006), total energy (0x0156)
SDM630_RESPONSES = {
    (0x0000, 2, 1): make_mock_response([22987, 0]),      # Voltage L1-N: 229.87 V
    (0x0006, 2, 1): make_mock_response([1500, 0]),       # Current L1: 1.500 A
    (0x0156, 2, 1): make_mock_response([654321, 0]),     # Total energy: 6543.21 kWh
}

# Combine for easy import in tests
ALL_RESPONSES = {
    "sdm120": SDM120_RESPONSES,
    "sdm630": SDM630_RESPONSES,
}
