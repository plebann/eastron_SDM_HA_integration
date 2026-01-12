---
name: modbus-troubleshooting
description: Diagnostics for Modbus in Home Assistant custom components—framing/extra-data errors, unit_id mismatches, pacing/timeouts, write contention, and logging patterns.
license: Complete terms in LICENSE.txt
---

# Modbus Troubleshooting

Use when Modbus IO misbehaves (timeouts, extra data, wrong values).

## Quick checks
- Verify device_id/unit_id on every call; wrong unit → timeouts.
- Add pacing (`message_wait_milliseconds`) and avoid immediate post-write polls.
- For RTU-over-TCP, flush/reset framer/buffer; reconnect on extra-data.
- Log address/unit/function and raw words to spot endian or offset issues.

## References
- [references/common-failures.md](references/common-failures.md)
- [references/logging-and-dumps.md](references/logging-and-dumps.md)
- [references/mitigations.md](references/mitigations.md)
