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
| 40013    | 00 0C         | Relay Pulse Width        | 4      | ms      | Float     | 1.0           | RW     | number        | Config     | Enum: 60, 100, 200 (default 100) |
| 40019    | 00 12         | Network Parity Stop      | 4      | -       | Float     | 1.0           | RW     | select        | Config     | Enum: 0=1 stop/no parity, 1=1 stop/even, 2=1 stop/odd, 3=2 stop/no parity |
| 40021    | 00 14         | Meter ID                 | 4      | -       | Float     | 1.0           | RW     | number        | Config     | Range: 1-247, default 1 |
| 40029    | 00 1C         | Baud rate                | 4      | -       | Float     | 1.0           | RW     | select        | Config     | Enum: 0=2400, 1=4800, 2=9600, 5=1200 (default 0) |
| 40087    | 00 56         | Pulse 1 output mode      | 4      | -       | Float     | 1.0           | RW     | select        | Config     | Enum: 1=import, 2=import+export, 4=export, 5=import reactive, 6=import+export reactive, 8=export reactive (default 4) |
| 463745   | F9 00         | Time of scroll display   | 2      | s       | UInt16    | 1.0           | RW     | number        | Config     | Range: 0-30, default 0 |
| 463761   | F9 10         | Pulse 1 output           | 2      | -       | HEX       | 1.0           | RW     | select        | Config     | Enum: 0=0.001kWh/imp (default), 1=0.01, 2=0.1, 3=1 |
| 463777   | F9 20         | Measurement mode         | 2      | -       | HEX       | 1.0           | RW     | select        | Config     | Enum: 1=total=import, 2=import+export (default), 3=import-export |
| 464513   | FC 00         | Serial number            | 4      | -       | UInt32    | 1.0           | RO     | sensor        | Diagnostic | Read only |
| 464515   | FC 02         | Meter code               | 2      | -       | HEX       | 1.0           | RO     | sensor        | Diagnostic | Read only |
| 464516   | FC 03         | Software version         | 2      | -       | HEX       | 1.0           | RO     | sensor        | Diagnostic | Read only |

**Legend:**
- **Basic**: Core energy monitoring, enabled by default
- **Advanced**: Additional electrical parameters, disabled by default
- **Diagnostic**: Device diagnostics and demand, disabled by default
- **Config**: Device configuration registers (writable, may require restart or confirmation)

**Data Type:** Most registers are 32-bit IEEE 754 floating point values (Float). Some config/diagnostic registers are HEX or UInt32.
**Scaling Factor:** All values are direct, no scaling required (factor = 1.0).
**Access:** 3xxxx registers are read-only (RO). 4xxxx/46xxxx holding/config registers may be read-write (RW).
**HA Entity Type:** Input registers map to `sensor`. Writable holding/config registers map to `number`, `select`, or `button` as appropriate.
**Special Handling:** Enum/bitfield mapping required for some config registers (see "Special Handling" column).

*This table can be expanded as more registers are mapped or as needed for the integration.*

**Validation:** This register map is based on official SDM120 documentation. Validate against actual device responses during integration testing.
