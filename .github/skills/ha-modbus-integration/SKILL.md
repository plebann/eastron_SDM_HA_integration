---
name: ha-modbus-integration
description: Patterns for building Home Assistant custom integrations that talk Modbus (TCP/RTU-over-TCP/serial): pymodbus device_id usage, safe polling/writing, pacing/backoff, encoding multi-register values, cached fallback, and translation-backed entities.
license: Complete terms in LICENSE.txt
---

# HA Modbus Integration

Use this when implementing or refactoring HA custom components that communicate with Modbus devices.

## Quick start
- Pick connection mode (tcp, rtuovertcp, serial); set timeout and message spacing.
- Always pass the correct unit id (device_id/slave) on every read/write.
- Batch contiguous reads, lock IO, and tier polling; cache last good data for availability.
- Encode multi-register writes (float32/uint32) and avoid immediate post-write refresh.
- Use translation_key + entity.sensor names and stable unique/device ids.

## References
- [references/connection-modes.md](references/connection-modes.md)
- [references/read-write-patterns.md](references/read-write-patterns.md)
- [references/resilience-and-pacing.md](references/resilience-and-pacing.md)
- [references/translations-and-ids.md](references/translations-and-ids.md)
