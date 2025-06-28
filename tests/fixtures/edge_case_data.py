"""Edge case register values for SDM models (min/max values, error conditions)."""

EDGE_CASE_REGISTERS = {
    # Minimum possible values
    "min_voltage": [0, 0],           # 0.00 V
    "min_current": [0, 0],           # 0.000 A
    "min_power": [0, 0],             # 0.0 W
    "min_energy": [0, 0],            # 0.00 kWh

    # Maximum possible values (simulate 16-bit unsigned max for each register)
    "max_voltage": [65535, 65535],   # Unrealistically high, for overflow test
    "max_current": [65535, 65535],
    "max_power": [65535, 65535],
    "max_energy": [65535, 65535],

    # Negative values (simulate signed error, if applicable)
    "neg_voltage": [0xFFFF, 0xFFFF], # -1 (if interpreted as signed)
    "neg_current": [0xFFFF, 0xFFFF],
    "neg_power": [0xFFFF, 0xFFFF],
    "neg_energy": [0xFFFF, 0xFFFF],

    # Error condition: device returns error (simulate Modbus error)
    "error_response": None,
}
