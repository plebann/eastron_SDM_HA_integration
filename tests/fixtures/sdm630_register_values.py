"""Realistic register values for SDM630 three-phase model for test scenarios."""

SDM630_REGISTERS = {
    # Voltage L1-N (0x0000): 229.87 V
    0x0000: [22987, 0],
    # Voltage L2-N (0x0002): 230.15 V
    0x0002: [23015, 0],
    # Voltage L3-N (0x0004): 231.02 V
    0x0004: [23102, 0],
    # Current L1 (0x0006): 1.500 A
    0x0006: [1500, 0],
    # Current L2 (0x0008): 1.480 A
    0x0008: [1480, 0],
    # Current L3 (0x000A): 1.520 A
    0x000A: [1520, 0],
    # Active Power L1 (0x000C): 300.0 W
    0x000C: [30000, 0],
    # Active Power L2 (0x000E): 295.0 W
    0x000E: [29500, 0],
    # Active Power L3 (0x0010): 305.0 W
    0x0010: [30500, 0],
    # Frequency (0x0046): 50.00 Hz
    0x0046: [5000, 0],
    # Total Energy Import (0x0156): 6543.21 kWh
    0x0156: [654321, 0],
    # Total Energy Export (0x015C): 123.45 kWh
    0x015C: [12345, 0],
    # Diagnostic: Device address (0x00F8): 1
    0x00F8: [1, 0],
}
