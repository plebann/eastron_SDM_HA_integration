# SDM630 Register Inventory

Source of truth: SDM630 Modbus protocol (docs/SDM630_MODBUS_Protocol.pdf). All measurement/config values are 4-byte IEEE 754 floats unless noted. Reset is a 2-byte Hex command; serial number is a 4-byte unsigned int32. Length column is bytes.

| Register | Address (Hex) | Parameter                                   | Length | Units   | Data Type | Scaling Factor | Access | HA Entity Type | Category   | Special Handling |
|----------|---------------|---------------------------------------------|--------|---------|-----------|----------------|--------|----------------|------------|------------------|
| 30001    | 00 00         | Phase 1 Voltage                         | 4      | Volts   | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30003    | 00 02         | Phase 2 Voltage                         | 4      | Volts   | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30005    | 00 04         | Phase 3 Voltage                         | 4      | Volts   | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30007    | 00 06         | Phase 1 Current                             | 4      | Amps    | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30009    | 00 08         | Phase 2 Current                             | 4      | Amps    | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30011    | 00 0A         | Phase 3 Current                             | 4      | Amps    | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30013    | 00 0C         | Phase 1 Power                               | 4      | Watts   | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30015    | 00 0E         | Phase 2 Power                               | 4      | Watts   | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30017    | 00 10         | Phase 3 Power                               | 4      | Watts   | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30049    | 00 30         | Sum of Line Currents                        | 4      | Amps    | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30053    | 00 34         | Total System Power                          | 4      | Watts   | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30057    | 00 38         | Total System Apparent Power                 | 4      | VA      | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30061    | 00 3C         | Total System Reactive Power                 | 4      | VAr     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30063    | 00 3E         | Total System Power Factor                   | 4      | None    | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30071    | 00 46         | Frequency                                   | 4      | Hz      | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30073    | 00 48         | Total Import kWh                            | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30075    | 00 4A         | Total Export kWh                            | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30077    | 00 4C         | Total Import kVArh                          | 4      | kVArh   | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30079    | 00 4E         | Total Export kVArh                          | 4      | kVArh   | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30081    | 00 50         | Total VAh                                   | 4      | kVAh    | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30085    | 00 54         | Total System Power Demand                   | 4      | Watts   | Float     | 1.0            | RO     | sensor         | Diagnostic | None             |
| 30087    | 00 56         | Maximum Total System Power Demand           | 4      | Watts   | Float     | 1.0            | RO     | sensor         | Diagnostic | None             |
| 30101    | 00 64         | Total System VA Demand                      | 4      | VA      | Float     | 1.0            | RO     | sensor         | Diagnostic | None             |
| 30105    | 00 68         | Neutral Current Demand                      | 4      | Amps    | Float     | 1.0            | RO     | sensor         | Diagnostic | None             |
| 30107    | 00 6A         | Maximum Neutral Current Demand              | 4      | Amps    | Float     | 1.0            | RO     | sensor         | Diagnostic | None             |
| 30225    | 00 E0         | Neutral Current                             | 4      | Amps    | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30343    | 01 56         | Total kWh                                   | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Basic      | None             |
| 30345    | 01 58         | Total kVArh                                 | 4      | kVArh   | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30347    | 01 5A         | L1 Import kWh                               | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30349    | 01 5C         | L2 Import kWh                               | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30351    | 01 5E         | L3 Import kWh                               | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30353    | 01 60         | L1 Export kWh                               | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30355    | 01 62         | L2 Export kWh                               | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30357    | 01 64         | L3 Export kWh                               | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30359    | 01 66         | L1 Total kWh                                | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30361    | 01 68         | L2 Total kWh                                | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 30363    | 01 6A         | L3 Total kWh                                | 4      | kWh     | Float     | 1.0            | RO     | sensor         | Advanced   | None             |
| 40019    | 00 12         | Network Parity / Stop                       | 4      | -       | Float     | 1.0            | RW     | select         | Config     | Enum: 0=1 stop/no parity, 1=1 stop/even, 2=1 stop/odd, 3=2 stop/no parity |
| 40021    | 00 14         | Network Node                                | 4      | -       | Float     | 1.0            | RW     | number         | Config     | Range: 1-247 (default 1) |
| 40029    | 00 1C         | Network Baud Rate                           | 4      | -       | Float     | 1.0            | RW     | select         | Config     | Enum: 0=2400, 1=4800, 2=9600 (default), 3=19200, 4=38400 |
6=total reactive, 8=export reactive |
| 64513    | FC 00         | Serial Number                               | 4      | -       | UInt32    | 1.0            | RO     | sensor         | Diagnostic | Read-only hardware serial |

**Legend:**
- **Basic**: Core energy monitoring, enabled by default.
- **Advanced**: Additional electrical parameters, disabled by default.
- **Diagnostic**: Demand/diagnostics, disabled by default.
- **Config**: Writable configuration registers; may require password or restart.

**Data Type:** 32-bit IEEE 754 floats unless noted (reset = Hex, serial = UInt32).
**Scaling Factor:** 1.0 (no scaling required).
**Access:** 3xxxx registers are RO; 4xxxx config are RW; reset is WO; serial is RO.
**Special Handling:** Apply enumerations/passwords where specified. Validate against device responses during integration testing.
