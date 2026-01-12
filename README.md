# Eastron SDM Home Assistant Integration (Custom / HACS)

Version: 0.1

A Home Assistant custom integration providing tiered, efficient polling of **Eastron SDM120** (initially) energy meter values over **Modbus RTU-over-TCP** using an async `pymodbus` client.

> Phase 1 scope: SDM120 read-only core, advanced, and diagnostic measurement registers. Future phases may add SDM630, writable configuration registers, and reset services.

## Features

- Async Modbus RTU-over-TCP client (no dependency on built-in HA Modbus integration)
- Tiered polling strategy (fast / normal / slow) based on priority matrix
- Configurable scan interval + divisors for normal & slow tiers
- Optional enabling of advanced & diagnostic sensor groups
- Automatic multi-entry support (add multiple meters via UI)
- Dynamic entity generation from structured register map
- Debug mode for raw read value logging

### HACS
Once published:
1. In HACS → Integrations → Custom Repositories → Add this repository URL as type "Integration".
2. Install, then restart.
3. Go to Settings → Devices & services → Add integration → Search for "Eastron SDM Meter"

## Configuration (Config Flow)
| Field | Description | Default |
|-------|-------------|---------|
| Friendly Name | Base name for entities | (required) |
| Host | RTU-over-TCP gateway IP | (required) |
| Port | TCP port | 502 |
| Modbus Unit ID | Slave / device address | 1 |
| Base Scan Interval (s) | Fast tier period | 10 |
| Normal Tier Divisor | normal tier every N fast cycles | 3 |
| Slow Tier Divisor | slow tier every M fast cycles | 30 |
| Enable Advanced Sensors | Apparent / Reactive / Power Factor | off |
| Enable Diagnostic Sensors | Demand / internal diagnostics | off |
| Enable two-way energy sensors | Enable to track import/export | off |
| Enable configuration registers | Enable to controll basic meter options | off |
| Enable Debug Logging | Verbose raw read output | off |

Validation:
- Minimum scan interval: 5s
- Normal divisor ≥ 2
- Slow divisor > normal divisor

## Polling Model
```
Fast interval = scan_interval (e.g. 10s)
Normal reads every: scan_interval * normal_divisor (≈30s by default)
Slow reads every:   scan_interval * slow_divisor (≈300s by default)
```

## Sensors (Initial Set)
| Key | Tier | Unit | Device Class | State Class | Default |
|-----|------|------|--------------|-------------|---------|
| voltage | fast | V | voltage | measurement | yes |
| current | fast | A | current | measurement | yes |
| active_power | fast | W | power | measurement | yes |
| frequency | normal | Hz | frequency | measurement | yes |
| import_active_energy | slow | kWh | energy | total_increasing | yes |
| total_active_energy | slow | kWh | energy | total_increasing | yes |
| apparent_power | normal | VA | apparent_power | measurement | advanced (off) |
| reactive_power | normal | var | reactive_power | measurement | advanced (off) |
| power_factor | normal | — | power_factor | measurement | advanced (off) |
| total_system_power_demand | slow | W | power | measurement | diagnostic (off) |

## Debug Logging
Enable in Options to log each Modbus read:
```
[DEBUG] Read active_power addr=12 len=2 -> 754.32
```

## Design Notes
- Each register read currently issues a separate Modbus request (simple & reliable). Future optimization may batch contiguous ranges.
- Float decoding uses big-endian 32-bit IEEE 754 (high word first).
- Energy totals are exposed as `total_increasing` without internal correction; meter rollover handling (if any) is deferred.

## Roadmap
- [ ] Add SDM630 multi-phase model
- [ ] Add diagnostics panel export (raw blocks)
- [ ] Unit tests for coordinator batching & decode (partial in this repo forthcoming)

## Troubleshooting
| Issue | Possible Cause | Action |
|-------|----------------|-------|
| All sensors unavailable | Connection failed | Check gateway IP/port, unit ID |
| Some sensors never appear | Advanced/Diagnostic disabled | Enable in Options |
| Values slow to update | Divisors high | Adjust Normal/Slow divisors |
| High log volume | Debug on | Disable debug in Options |

Enable debug logging in `configuration.yaml` if needed:
```yaml
logger:
  default: info
  logs:
    custom_components.eastron_sdm: debug
    pymodbus: info
```

## License
See [LICENSE](LICENSE).

## Disclaimer
This is an independent community integration; not affiliated with or endorsed by Eastron.
