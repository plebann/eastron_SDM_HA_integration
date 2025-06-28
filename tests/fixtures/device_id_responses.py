"""Mock Modbus responses for device identification (model detection)."""

from unittest.mock import AsyncMock

def make_id_response(model_code):
    mock = AsyncMock()
    mock.registers = [model_code, 0]
    mock.isError.return_value = False
    return mock

# Example: SDM120 returns 0x0001, SDM630 returns 0x0002 at register 0x0040
DEVICE_ID_RESPONSES = {
    (0x0040, 2, 1): {
        "sdm120": make_id_response(0x0001),
        "sdm630": make_id_response(0x0002),
    }
}
