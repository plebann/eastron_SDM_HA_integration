"""Realistic register values for SDM120 model for test scenarios."""

SDM120_REGISTERS = {
    # Voltage L-N (0x0000): 230.12 V
    0x0000: [23012, 0],
    # Current (0x0006): 1.005 A
    0x0006: [1005, 0],
    # Active Power (0x000C): 230.0 W
    0x000C: [23000, 0],
    # Apparent Power (0x0012): 240.0 VA
    0x0012: [24000, 0],
    # Reactive Power (0x0018): 50.0 VAR
    0x0018: [5000, 0],
    # Power Factor (0x001E): 0.98
    0x001E: [980, 0],
    # Frequency (0x0046): 50.00 Hz
    0x0046: [5000, 0],
    # Total Energy Import (0x0156): 1234.56 kWh
    0x0156: [123456, 0],
    # Total Energy Export (0x015C): 12.34 kWh
    0x015C: [1234, 0],
    # Diagnostic: Device address (0x00F8): 1
    0x00F8: [1, 0],
}
