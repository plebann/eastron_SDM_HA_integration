# Common Failures
- Timeouts with retries: typically wrong device_id or address, or device busy; confirm unit id and function code.
- Extra data / framing errors: RTU-over-TCP gateways leaving bytes in buffer; missing flush/reset; mixed framer.
- Duplicate or zero values: endian mismatch or reading wrong register type (input vs holding).
- Write failures: using unit/slave kwargs on pymodbus 3.11+, or FC06 used for multi-register payload.
- Unavailable entities: coordinator not caching last good data; polling stopped after repeated failures.
