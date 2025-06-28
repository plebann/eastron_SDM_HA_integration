# Eastron SDM Integration Configuration Examples

This document provides example configurations for the Eastron SDM Energy Meter integration.

---

## Example 1: Basic Integration Setup (via UI)

No YAML required. Use the Home Assistant UI to add the integration and follow the prompts.

---

## Example 2: Example Exported Configuration (JSON)

This is an example of the configuration you can export and later import via the integration's import step.

```json
{
  "host": "192.168.1.50",
  "port": 502,
  "unit_id": 1,
  "device_name": "main_panel",
  "model": "SDM120",
  "categories": ["basic", "diagnostic"],
  "poll_fast": 5,
  "poll_normal": 30,
  "poll_slow": 300
}
```

---

## Example 3: Advanced Configuration (Multiple Devices)

You can add multiple meters by repeating the integration setup in the UI for each device.

- **Device 1:**  
  - Host: 192.168.1.50  
  - Unit ID: 1  
  - Name: main_panel

- **Device 2:**  
  - Host: 192.168.1.51  
  - Unit ID: 1  
  - Name: sub_panel

---

## Example 4: Custom Polling Intervals

Set custom polling intervals during setup or via the options menu:

- Fast: 2 seconds
- Normal: 15 seconds
- Slow: 120 seconds

---

## Example 5: Enabling Advanced and Diagnostic Entities

During setup, select "Advanced" and "Diagnostic" categories to enable all available entities.

---

## Notes

- All configuration is UI-driven; YAML is not required for setup.
- Use the import/export feature for backup and migration.
- For troubleshooting, see [troubleshooting.md](troubleshooting.md).
