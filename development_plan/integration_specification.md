## Complete Integration Specification

**Integration Name**: `eastron_sdm`  
**Display Name**: "Eastron SDM Energy Meter"  
**Entity Naming**: `{user_device_name}_{parameter}` (e.g., `main_panel_voltage_l1`)

## Implementation Structure

**1. Repository Structure (HACS-compatible)**
```
custom_components/eastron_sdm/
├── __init__.py
├── manifest.json
├── config_flow.py
├── coordinator.py
├── device_models.py
├── sensor.py
├── number.py
├── button.py
├── select.py
└── translations/
    └── en.json
```

**2. Configuration Flow Steps**
- **Connection Setup**: IP, port (4196), unit_id (1), timeout (10s)
- **Device Detection**: Auto-detect via register 0x0040 read attempt
- **Device Naming**: User provides friendly name (validation: no special chars)
- **Entity Categories**: Checkboxes for Basic (default), Advanced, Diagnostic (unchecked)
- **Polling Intervals**: Fast (5s), Normal (30s), Slow (300s) - user adjustable

**3. Entity Categories & Default States**

**Basic (enabled by default)**:
- Sensors: voltage_l1/l2/l3, current_l1/l2/l3, frequency, total_energy_import, total_energy_export

**Advanced (disabled by default)**:
- Sensors: active_power_l1/l2/l3, reactive_power_l1/l2/l3, apparent_power_l1/l2/l3, power_factor_l1/l2/l3, thd_voltage_l1/l2/l3, thd_current_l1/l2/l3

**Diagnostic (disabled by default)**:
- Number entities: baud_rate, parity_setting, stop_bits
- Button entities: reset_energy_counters (requires confirmation), reset_demand_values (requires confirmation)
- Both reset buttons: `entity_registry_enabled_default: False`

**4. Device Model Abstraction**
- `SDM120RegisterMap`: ~25 basic registers, ~40 advanced, ~10 diagnostic
- `SDM630RegisterMap`: ~35 basic registers, ~80 advanced, ~15 diagnostic
- Auto-scaling for register values (V, A, W, kWh, etc.)
- Proper device classes and state classes for energy dashboard integration

**5. Multi-Device Support**
- Each config entry = one physical meter
- Independent coordinators and polling schedules
- Device registry integration with model info
- Unique device identifiers using MAC-like format from IP+unit_id

**6. Safety & UX Features**
- Confirmation dialogs for reset operations
- Connection validation during setup
- Automatic retry logic with exponential backoff
- Clear error messages for common issues (wrong unit_id, network problems)
- Proper device_info for grouping entities

## Development Phases

**Phase 1**: Core integration (config flow, basic sensors, single device)
**Phase 2**: Advanced entities and multi-device support  
**Phase 3**: Diagnostic entities and reset operations
**Phase 4**: HACS packaging and documentation