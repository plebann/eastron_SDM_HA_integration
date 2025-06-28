# SDM120 Register Inventory

This document provides a categorized inventory of all SDM120 Modbus registers for Home Assistant integration.

| Register | Address (Hex) | Parameter                | Length | Units   | Data Type | Scaling Factor | Access | HA Entity Type | Category   | Special Handling |
|----------|---------------|--------------------------|--------|---------|-----------|---------------|--------|---------------|------------|------------------|
| 30001    | 00 00         | Voltage                  | 4      | Volts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30007    | 00 06         | Current                  | 4      | Amps    | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30013    | 00 0C         | Active power             | 4      | Watts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30019    | 00 12         | Apparent power           | 4      | VA      | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30025    | 00 18         | Reactive power           | 4      | VAr     | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30031    | 00 1E         | Power factor             | 4      | None    | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30071    | 00 46         | Frequency                | 4      | Hz      | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30073    | 00 48         | Import active energy     | 4      | kWh     | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30075    | 00 4A         | Export active energy     | 4      | kWh     | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30077    | 00 4C         | Import reactive energy   | 4      | kvarh   | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30079    | 00 4E         | Export reactive energy   | 4      | kvarh   | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30085    | 00 54         | Total system power demand| 4      | W       | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30087    | 00 56         | Max total system power demand | 4 | W       | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30089    | 00 58         | Import system power demand | 4    | W       | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30091    | 00 5A         | Max import system power demand | 4 | W      | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30093    | 00 5C         | Export system power demand | 4    | W       | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30095    | 00 5E         | Max export system power demand | 4 | W      | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30259    | 01 02         | Current demand           | 4      | Amps    | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30265    | 01 08         | Max current demand       | 4      | Amps    | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30343    | 01 56         | Total active energy      | 4      | kWh     | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30345    | 01 58         | Total reactive energy    | 4      | kvarh   | Float     | 1.0           | RO     | sensor        | Advanced   | None             |

**Legend:**
- **Basic**: Core energy monitoring, enabled by default
- **Advanced**: Additional electrical parameters, disabled by default
- **Diagnostic**: Device diagnostics and demand, disabled by default

**Data Type:** All registers are 32-bit IEEE 754 floating point values (Float).
**Scaling Factor:** All values are direct, no scaling required (factor = 1.0).
**Access:** All 3xxxx registers are read-only (RO). 4xxxx holding registers (not shown here) may be read-write (RW).
**HA Entity Type:** Most input registers map to `sensor`. Writable holding registers may map to `number`, `button`, or `select` as appropriate.
**Special Handling:** None required for SDM120 input registers listed above. See device documentation for holding register bit fields or enums if implemented.

*This table can be expanded as more registers are mapped or as needed for the integration.*

**Validation:** This register map is based on official SDM120 documentation. Validate against actual device responses during integration testing.
