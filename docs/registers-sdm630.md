# SDM630 Register Inventory

This document provides a categorized inventory of all SDM630 Modbus registers for Home Assistant integration.

| Register | Address (Hex) | Parameter                       | Length | Units   | Data Type | Scaling Factor | Access | HA Entity Type | Category   | Special Handling |
|----------|---------------|----------------------------------|--------|---------|-----------|---------------|--------|---------------|------------|------------------|
| 30001    | 00 00         | Phase 1 L-N Voltage             | 4      | Volts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30003    | 00 02         | Phase 2 L-N Voltage             | 4      | Volts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30005    | 00 04         | Phase 3 L-N Voltage             | 4      | Volts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30007    | 00 06         | Phase 1 Current                 | 4      | Amps    | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30009    | 00 08         | Phase 2 Current                 | 4      | Amps    | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30011    | 00 0A         | Phase 3 Current                 | 4      | Amps    | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30013    | 00 0C         | Phase 1 Power                   | 4      | Watts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30015    | 00 0E         | Phase 2 Power                   | 4      | Watts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30017    | 00 10         | Phase 3 Power                   | 4      | Watts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30019    | 00 12         | Phase 1 Apparent Power          | 4      | VA      | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30021    | 00 14         | Phase 2 Apparent Power          | 4      | VA      | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30023    | 00 16         | Phase 3 Apparent Power          | 4      | VA      | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30025    | 00 18         | Phase 1 Reactive Power          | 4      | VAr     | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30027    | 00 1A         | Phase 2 Reactive Power          | 4      | VAr     | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30029    | 00 1C         | Phase 3 Reactive Power          | 4      | VAr     | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30031    | 00 1E         | Phase 1 Power Factor            | 4      | None    | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30033    | 00 20         | Phase 2 Power Factor            | 4      | None    | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30035    | 00 22         | Phase 3 Power Factor            | 4      | None    | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30037    | 00 24         | Phase 1 Phase Angle             | 4      | Degrees | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30039    | 00 26         | Phase 2 Phase Angle             | 4      | Degrees | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30041    | 00 28         | Phase 3 Phase Angle             | 4      | Degrees | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30047    | 00 2E         | Average Line Current            | 4      | Amps    | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30049    | 00 30         | Sum of Line Currents            | 4      | Amps    | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30053    | 00 34         | Total System Power              | 4      | Watts   | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30057    | 00 38         | Total System Apparent Power     | 4      | VA      | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30061    | 00 3C         | Total System Reactive Power     | 4      | VAr     | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30063    | 00 3E         | Total System Power Factor       | 4      | None    | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30067    | 00 42         | Total System Phase Angle        | 4      | Degrees | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30071    | 00 46         | Frequency                       | 4      | Hz      | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30073    | 00 48         | Total Import kWh                | 4      | kWh     | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30075    | 00 4A         | Total Export kWh                | 4      | kWh     | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30077    | 00 4C         | Total Import kVArh              | 4      | kVArh   | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30079    | 00 4E         | Total Export kVArh              | 4      | kVArh   | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30085    | 00 54         | Total System Power Demand       | 4      | W       | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30087    | 00 56         | Max Total System Power Demand   | 4      | W       | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30101    | 00 64         | Total System VA Demand          | 4      | VA      | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30103    | 00 66         | Max Total System VA Demand      | 4      | VA      | Float     | 1.0           | RO     | sensor        | Diagnostic | None             |
| 30235    | 00 EA         | Phase 1 L/N Volts THD           | 4      | %       | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30237    | 00 EC         | Phase 2 L/N Volts THD           | 4      | %       | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30239    | 00 EE         | Phase 3 L/N Volts THD           | 4      | %       | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30241    | 00 F0         | Phase 1 Current THD             | 4      | %       | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30243    | 00 F2         | Phase 2 Current THD             | 4      | %       | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30245    | 00 F4         | Phase 3 Current THD             | 4      | %       | Float     | 1.0           | RO     | sensor        | Advanced   | None             |
| 30343    | 01 56         | Total kWh                       | 4      | kWh     | Float     | 1.0           | RO     | sensor        | Basic      | None             |
| 30345    | 01 58         | Total kVArh                     | 4      | kVArh   | Float     | 1.0           | RO     | sensor        | Advanced   | None             |

**Legend:**
- **Basic**: Core energy monitoring, enabled by default
- **Advanced**: Additional electrical parameters, disabled by default
- **Diagnostic**: Device diagnostics and demand, disabled by default

**Data Type:** All registers are 32-bit IEEE 754 floating point values (Float).
**Scaling Factor:** All values are direct, no scaling required (factor = 1.0).
**Access:** All 3xxxx registers are read-only (RO). 4xxxx holding registers (not shown here) may be read-write (RW).
**HA Entity Type:** Most input registers map to `sensor`. Writable holding registers may map to `number`, `button`, or `select` as appropriate.
**Special Handling:** None required for SDM630 input registers listed above. See device documentation for holding register bit fields or enums if implemented.

*This table can be expanded as more registers are mapped or as needed for the integration.*

**Validation:** This register map is based on official SDM630 documentation. Validate against actual device responses during integration testing.
