"""Malformed Modbus register data scenarios for error testing."""

MALFORMED_DATA_SCENARIOS = {
    # Too few registers returned (should be 2, got 1)
    "short_response": [12345],
    # Too many registers returned (should be 2, got 3)
    "long_response": [100, 200, 300],
    # Non-integer data (should be int, got str)
    "string_response": ["not_an_int", 0],
    # None as response
    "none_response": None,
    # Empty list
    "empty_response": [],
    # Corrupted data (random bytes)
    "corrupted_response": [b"\x00\xFF", b"\xAA\xBB"],
}
