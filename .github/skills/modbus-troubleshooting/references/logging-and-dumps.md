# Logging and Dumps
- Enable debug: `homeassistant.components.modbus: debug`, `pymodbus: debug`.
- Log tuples: unit_id, function, address, count/len, raw words/bytes.
- Capture MBAP/RTU frames when seeing extra-data; check length vs bytecount.
- Note pacing/timeout in logs to correlate with gateway limits.
