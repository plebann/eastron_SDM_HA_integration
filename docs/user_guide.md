# Eastron SDM Energy Meter Home Assistant Integration

## Overview

This integration allows Home Assistant to monitor Eastron SDM120 and SDM630 energy meters via Modbus TCP. It supports automatic device detection, category-based entity management, and advanced configuration options.

---

## Installation

1. **Via HACS (Recommended)**
   - Add this repository to HACS as a custom integration.
   - Search for "Eastron SDM Energy Meter" and install.
   - Restart Home Assistant.

2. **Manual**
   - Copy the `custom_components/eastron_sdm` directory to your Home Assistant `custom_components` folder.
   - Restart Home Assistant.

---

## Configuration

### Adding a Meter

1. Go to **Settings > Devices & Services > Add Integration**.
2. Search for **Eastron SDM Energy Meter**.
3. Enter the meter's IP address, port (default: 502), and unit ID (default: 1).
4. The integration will auto-detect the device model.
5. Enter a friendly name for the meter.
6. Select which entity categories to enable (Basic, Advanced, Diagnostic).
7. Set polling intervals for fast, normal, and slow data groups.
8. Complete the setup.

### Entity Categories

- **Basic**: Essential sensors (enabled by default)
- **Advanced**: Additional sensors (optional)
- **Diagnostic**: Configuration and reset entities (optional)

### Import/Export Configuration

- Use the import step to paste a JSON config for quick setup.
- Use the options menu to export the current configuration as JSON.

---

## Usage

- Entities will be created for each enabled sensor, number, button, and select.
- Entity names follow the pattern: `{device_name}_{parameter}` (e.g., `main_panel_voltage_l1`).
- Use the options menu to adjust polling intervals or export config.

---

## Troubleshooting

- **Cannot connect**: Check IP, port, unit ID, and network connectivity.
- **Model not detected**: Ensure the meter is powered and supports Modbus TCP.
- **Entities missing**: Check entity category selection and Home Assistant entity registry.
- **Reset buttons**: Use with caution; confirmation is required for destructive actions.

---

## Example Configuration Export

```json
{
  "host": "192.168.1.100",
  "port": 502,
  "unit_id": 1,
  "device_name": "main_panel",
  "model": "SDM630",
  "categories": ["basic", "advanced"],
  "poll_fast": 5,
  "poll_normal": 30,
  "poll_slow": 300
}
```

---

## Support

For issues or feature requests, open an issue on the GitHub repository or use the HACS community forums.
