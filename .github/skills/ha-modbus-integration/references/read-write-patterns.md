# Read/Write Patterns
- Addressing: pymodbus 3.11+ requires device_id on every call (HA names it slave/device_address). Do not use unit/slave kwargs.
- Reads: choose function by register type (input vs holding). Batch contiguous addresses; respect word counts. Decode endianness consistently.
- Writes: FC06 for single value; FC16 for array. Encode float32/uint32 into two registers (network order words). Avoid duplicating a scalar across multiple registers unless protocol specifies.
- Post-write: do not trigger immediate coordinator refresh; let next scheduled poll confirm. Optionally add short delay if device needs settle time.
- Locking: wrap all IO in a client-level async lock; one in-flight transaction at a time.
- Examples (pseudocode):
  - read_input_registers(address, count, device_id=unit_id)
  - write_registers(address, values=[hi, lo], device_id=unit_id)
