# Register Priority Matrix

This matrix prioritizes SDM120 and SDM630 Modbus registers for polling, based on user value (importance for energy monitoring) and expected update frequency (how often the value changes). Use this to assign registers to fast, normal, or slow polling groups in Home Assistant.

| Register/Parameter         | Device   | Category    | User Value | Update Frequency | Polling Tier   |
|---------------------------|----------|-------------|------------|------------------|---------------|
| Voltage (L1/L2/L3)        | Both     | Basic       | High       | High             | Fast (5s)     |
| Current (L1/L2/L3)        | Both     | Basic       | High       | High             | Fast (5s)     |
| Active Power (L1/L2/L3)   | Both     | Basic       | High       | High             | Fast (5s)     |
| Apparent/Reactive Power   | Both     | Advanced    | Medium     | High             | Normal (30s)  |
| Power Factor              | Both     | Advanced    | Medium     | High             | Normal (30s)  |
| Frequency                 | Both     | Basic       | Medium     | Medium           | Normal (30s)  |
| Import/Export Energy      | Both     | Basic       | High       | Low              | Slow (300s)   |
| Demand/Max Demand         | Both     | Diagnostic  | Low        | Medium           | Slow (300s)   |
| THD (Voltage/Current)     | SDM630   | Advanced    | Medium     | Medium           | Normal (30s)  |
| Phase Angle               | SDM630   | Advanced    | Low        | Medium           | Slow (300s)   |
| Diagnostic/Config Params  | Both     | Diagnostic  | Low        | Low              | Slow (300s)   |

**Polling Tier Definitions:**
- **Fast (5s):** Critical real-time values for dashboards/automation (voltage, current, power)
- **Normal (30s):** Frequently changing but less critical values (apparent/reactive power, power factor, THD)
- **Slow (300s):** Slowly changing or diagnostic values (energy totals, demand, config, diagnostics)

*This matrix should be reviewed and adjusted based on user feedback and real-world usage patterns.*
