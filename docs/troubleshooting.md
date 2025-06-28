# Eastron SDM Integration Troubleshooting Guide

This guide helps resolve common issues encountered when using the Eastron SDM Energy Meter integration for Home Assistant.

---

## Connection Issues

### Cannot connect to meter
- Verify the meter's IP address, port (default: 502), and unit ID (default: 1).
- Ensure the meter is powered on and connected to the network.
- Check for firewall or network restrictions blocking Modbus TCP (port 502).
- Try pinging the meter from your Home Assistant host.
- Confirm the meter supports Modbus TCP and is not in use by another client.

### Duplicate device error
- Each integration entry must have a unique combination of IP address and unit ID.
- Remove or update any existing entries with the same details.

---

## Device Detection

### Model not detected
- Ensure you are connecting to a supported SDM120 or SDM630 meter.
- Power cycle the meter and retry.
- Check wiring and network connectivity.

---

## Entity Issues

### Entities missing or unavailable
- Check which entity categories (Basic, Advanced, Diagnostic) are enabled.
- Look for disabled entities in Home Assistant's entity registry.
- Ensure the integration is not reporting connection errors.

### Reset buttons not working
- Confirm the meter supports remote reset operations.
- Ensure you confirm the reset action in the Home Assistant UI.

---

## Configuration & Options

### Import/export not working
- Ensure the JSON is valid and matches the expected format.
- Only import configurations exported from this integration.

### Polling intervals not updating
- Use the options menu to adjust polling intervals.
- Restart Home Assistant if changes do not take effect.

---

## General Tips

- Always restart Home Assistant after updating the integration.
- Check Home Assistant logs for detailed error messages.
- Update to the latest version of the integration for bug fixes and improvements.
- For advanced debugging, enable debug logging for `custom_components.eastron_sdm`.

---

## Getting Help

- Review the [user guide](user_guide.md) for setup and usage instructions.
- Search the HACS forums or GitHub issues for similar problems.
- If needed, open a new issue with detailed logs and configuration info.
