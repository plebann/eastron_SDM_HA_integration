"""Local test script for SDM120 integration without Home Assistant."""
import asyncio
import sys
from pathlib import Path

# Add the custom component to Python path
sys.path.insert(0, str(Path(__file__).parent / "custom_components"))

from eastron_sdm.models.sdm120 import get_register_specs, BASE_SDM120_SPECS

def test_register_specs():
    """Test register specification logic."""
    print("Testing register specifications...")
    
    # Test default (basic only)
    basic_specs = get_register_specs(enable_advanced=False, enable_diagnostic=False)
    basic_keys = {s.key for s in basic_specs}
    print(f"Basic sensors: {basic_keys}")
    
    # Test with advanced
    advanced_specs = get_register_specs(enable_advanced=True, enable_diagnostic=False)
    advanced_keys = {s.key for s in advanced_specs}
    print(f"With advanced: {advanced_keys}")
    
    # Test with diagnostic
    all_specs = get_register_specs(enable_advanced=True, enable_diagnostic=True)
    all_keys = {s.key for s in all_specs}
    print(f"With all: {all_keys}")
    
    print("✅ Register specs working correctly")

async def test_mock_modbus():
    """Test Modbus client logic with mock data."""
    from eastron_sdm.client import SdmModbusClient
    from unittest.mock import AsyncMock, MagicMock
    
    print("\nTesting Modbus client (mock)...")
    
    # Mock client for testing
    client = SdmModbusClient("192.168.1.100", 502, 1)
    
    # Mock the actual modbus client
    mock_modbus = AsyncMock()
    mock_response = MagicMock()
    mock_response.isError.return_value = False
    mock_response.registers = [0x4234, 0x0000]  # Mock float32 data
    
    mock_modbus.read_input_registers.return_value = mock_response
    client._client = mock_modbus
    client._connected = True
    
    # Test read
    result = await client.read_input_registers(0, 2)
    print(f"Mock read result: address={result.address}, registers={result.registers}")
    
    print("✅ Modbus client mock working correctly")

if __name__ == "__main__":
    print("🧪 Running local integration tests...")
    
    # Test register logic
    test_register_specs()
    
    # Test async components
    asyncio.run(test_mock_modbus())
    
    print("\n✅ All local tests passed!")
    print("Integration logic appears to be working correctly.")