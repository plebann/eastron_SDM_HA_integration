# Write Path Tests
- Encode float32/uint32 payloads into two registers in expected word order.
- Ensure writes pass device_id; assert no unit/slave kwargs.
- Confirm no immediate refresh after write; next scheduled poll should pick up changes.
