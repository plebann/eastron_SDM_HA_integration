"""Device model definitions for Eastron SDM integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Literal
import logging
import asyncio
from homeassistant.components.sensor import SensorDeviceClass

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class SDMRegister:
    """Definition of a single SDM120/630 register."""

    address: int
    use_registry: bool
    parameter_key: Optional[str]
    name: str
    length: int
    units: Optional[str]
    data_type: Literal["Float", "UInt32", "HEX"]
    scaling: float
    access: Literal["RO", "RW"]
    ha_entity_type: Literal["sensor", "number", "select", "button"]
    category: Literal["Basic", "Advanced", "Diagnostic", "Config"]
    device_class: SensorDeviceClass | None
    special: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: Optional[list[Any]] = None

    def apply_scaling(self, raw_value: float | int) -> float | int:
        """Apply scaling factor to raw register value."""
        return raw_value * self.scaling

    def convert_unit(self, value: float | int) -> float | int:
        """Convert value to target unit if needed (placeholder for future logic)."""
        # No unit conversion needed for SDM120/630, but method is here for extensibility.
        return value

@dataclass
class SDMDevice:
    """Base class for Eastron SDM devices."""

    host: str
    port: int
    unit_id: int
    model: Optional[str] = None
    timeout: int = 10

    # Placeholder for pymodbus client, to be set by coordinator or connection manager
    client: Any = field(default=None, repr=False, compare=False)
    _lock: Any = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if self._lock is None:
            object.__setattr__(self, "_lock", asyncio.Lock())

    async def async_read_registers(self, address: int, count: int = 1) -> Optional[list[float]]:
        """Read Modbus registers from the device asynchronously.

        Args:
            address: Register address to read from.
            count: Number of registers to read.

        Returns:
            List of register values, or None if read fails.
        """
        _LOGGER.debug(
            "SDMDevice: async_read_registers called for address 0x%04X, count %d, device %s:%s",
            address, count, self.host, self.port
        )
        if self.client is None:
            _LOGGER.error("Modbus client not initialized for device at %s:%s", self.host, self.port)
            return None

        try:
            _LOGGER.debug(
                "Diagnostic: Attempting to read %d registers at 0x%04X from %s:%s",
                count, address, self.host, self.port
            )
            async with self._lock:
                # Attempt reconnect if client is disconnected
                if hasattr(self.client, "connected") and not self.client.connected:
                    _LOGGER.warning("Modbus client disconnected, attempting reconnect to %s:%s", self.host, self.port)
                    await self.client.connect()
                # pymodbus 3.x+ expects only address, count as keyword argument
                result = await self.client.read_holding_registers(address=address, count=count)
            _LOGGER.debug(
                "Diagnostic: Raw Modbus result for address 0x%04X from %s:%s: %s",
                address, self.host, self.port, repr(result)
            )
            if not result.isError():
                _LOGGER.debug(
                    "Diagnostic: Read %d registers at 0x%04X from %s:%s, values: %s",
                    count, address, self.host, self.port, result.registers
                )
                return result.registers
            _LOGGER.error("Modbus error reading registers at 0x%04X from %s:%s", address, self.host, self.port)
        except Exception as exc:
            _LOGGER.error("Exception reading registers at 0x%04X from %s:%s: %s", address, self.host, self.port, exc)
            # Attempt reconnect on error
            try:
                if self.client is not None:
                    close_fn = getattr(self.client, "close", None)
                    connect_fn = getattr(self.client, "connect", None)
                    if close_fn is not None:
                        await close_fn()
                    if connect_fn is not None:
                        await connect_fn()
            except Exception as reconnect_exc:
                _LOGGER.error("Failed to reconnect Modbus client: %s", reconnect_exc)
        return None

    def device_info(self) -> Dict[str, Any]:
        """Return Home Assistant device info dictionary."""
        model_name = self.model if self.model in ("SDM120", "SDM630") else "Unknown"
        # Try to use device_name if present (set as attribute by integration)
        device_name = getattr(self, "device_name", None)
        info = {
            "identifiers": {(self.host, self.unit_id)},
            "name": device_name or self.model or "Eastron SDM",
            "manufacturer": "Eastron",
            "model": model_name,
        }
        # Optionally add firmware version if available
        if hasattr(self, "firmware_version") and self.firmware_version:
            info["sw_version"] = self.firmware_version
        return info


class SDM120RegisterMap:
    """Static register map for SDM120 meter."""

    REGISTERS: tuple[SDMRegister, ...] = (
        SDMRegister(0x0000, True, "voltage", "Voltage", 4, "Volts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.VOLTAGE),
        SDMRegister(0x0006, True, "current", "Current", 4, "Amps", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.CURRENT),
        SDMRegister(0x000C, True, "power", "Power", 4, "Watts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.POWER),
        SDMRegister(0x0012, True, "apparent_power", "Apparent power", 4, "VA", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.APPARENT_POWER),
        SDMRegister(0x0018, True, "reactive_power", "Reactive power", 4, "VAr", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.REACTIVE_POWER),
        SDMRegister(0x001E, True, "power_factor", "Power factor", 4, None, "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.POWER_FACTOR),
        SDMRegister(0x0046, True, "frequency", "Frequency", 4, "Hz", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.FREQUENCY),
        SDMRegister(0x0048, True, "import_energy", "Import energy", 4, "kWh", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.ENERGY),
        SDMRegister(0x004A, True, "export_energy", "Export energy", 4, "kWh", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.ENERGY),
        SDMRegister(0x004C, False, "import_reactive_energy", "Import reactive energy", 4, "kvarh", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.ENERGY),
        SDMRegister(0x004E, False, "export_reactive_energy", "Export reactive energy", 4, "kvarh", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.ENERGY),
        SDMRegister(0x0054, False, "total_system_power_demand", "Total system power demand", 4, "W", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.POWER),
        SDMRegister(0x0056, False, "max_total_system_power_demand", "Max total system power demand", 4, "W", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.POWER),
        SDMRegister(0x0058, False, "import_system_power_demand", "Import system power demand", 4, "W", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.POWER),
        SDMRegister(0x005A, False, "max_import_system_power_demand", "Max import system power demand", 4, "W", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.POWER),
        SDMRegister(0x005C, False, "export_system_power_demand", "Export system power demand", 4, "W", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.POWER),
        SDMRegister(0x005E, False, "max_export_system_power_demand", "Max export system power demand", 4, "W", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.POWER),
        SDMRegister(0x0102, False, "current_demand", "Current demand", 4, "Amps", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.CURRENT),
        SDMRegister(0x0108, False, "max_current_demand", "Max current demand", 4, "Amps", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.CURRENT),
        SDMRegister(0x0156, False, "total_energy", "Total energy", 4, "kWh", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.ENERGY),
        SDMRegister(0x0158, False, "total_reactive_energy", "Total reactive energy", 4, "kvarh", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.ENERGY),
        SDMRegister(0x000C, False, "relay_pulse_width", "Relay Pulse Width", 4, "ms", "Float", 1.0, "RW", "number", "Config", None, "Enum: 60, 100, 200 (default 100)"),
        SDMRegister(0x0012, False, "network_parity_stop", "Network Parity Stop", 4, None, "Float", 1.0, "RW", "select", "Config", None, "Enum: 0=1 stop/no parity, 1=1 stop/even, 2=1 stop/odd, 3=2 stop/no parity"),
        SDMRegister(
            0x0014, False, "meter_id", "Meter ID", 4, None, "Float", 1.0, "RW", "number", "Config", None,
            special="Range: 1-247, default 1",
            min_value=1, max_value=247, step=1
        ),
        SDMRegister(
            0x001C, False, "baud_rate", "Baud rate", 4, None, "Float", 1.0, "RW", "select", "Config", None,
            special="Enum: 0=2400, 1=4800, 2=9600, 5=1200 (default 0)",
            options=[0, 1, 2, 5]
        ),
        SDMRegister(
            0x0056, False, "pulse_1_output_mode", "Pulse 1 output mode", 4, None, "Float", 1.0, "RW", "select", "Config", None,
            special="Enum: 1=import, 2=import+export, 4=export, 5=import reactive, 6=import+export reactive, 8=export reactive (default 4)",
            options=[1, 2, 4, 5, 6, 8]
        ),
        SDMRegister(
            0xF900, False, "time_of_scroll_display", "Time of scroll display", 2, "s", "HEX", 1.0, "RW", "number", "Config", None,
            special="Range: 0-30, default 0",
            min_value=0, max_value=30, step=1
        ),
        SDMRegister(
            0xF910, False, "pulse_1_output", "Pulse 1 output", 2, None, "HEX", 1.0, "RW", "select", "Config", None,
            special="Enum: 0=0.001kWh/imp (default), 1=0.01, 2=0.1, 3=1",
            options=[0, 1, 2, 3]
        ),
        SDMRegister(
            0xF920, False, "measurement_mode", "Measurement mode", 2, None, "HEX", 1.0, "RW", "select", "Config", None,
            special="Enum: 1=total=import, 2=import+export (default), 3=import-export",
            options=[1, 2, 3]
        ),
        SDMRegister(0xFC00, False, "serial_number", "Serial number", 4, None, "UInt32", 1.0, "RO", "sensor", "Diagnostic", "Read only"),
        SDMRegister(0xFC02, False, "meter_code", "Meter code", 2, None, "HEX", 1.0, "RO", "sensor", "Diagnostic", "Read only"),
        SDMRegister(0xFC03, False, "software_version", "Software version", 2, None, "HEX", 1.0, "RO", "sensor", "Diagnostic", "Read only"),
    )

class SDM630RegisterMap:
    """Static register map for SDM630 meter."""

    REGISTERS: tuple[SDMRegister, ...] = (
        SDMRegister(0x0000, True, "phase_1_voltage_l1", "Phase 1 L-N Voltage", 4, "Volts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.VOLTAGE),
        SDMRegister(0x0002, True, "phase_2_voltage_l2", "Phase 2 L-N Voltage", 4, "Volts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.VOLTAGE),
        SDMRegister(0x0004, True, "phase_3_voltage_l3", "Phase 3 L-N Voltage", 4, "Volts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.VOLTAGE),
        SDMRegister(0x0006, True, "phase_1_current", "Phase 1 Current", 4, "Amps", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.CURRENT),
        SDMRegister(0x0008, True, "phase_2_current", "Phase 2 Current", 4, "Amps", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.CURRENT),
        SDMRegister(0x000A, True, "phase_3_current", "Phase 3 Current", 4, "Amps", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.CURRENT),
        SDMRegister(0x000C, True, "phase_1_power", "Phase 1 Power", 4, "Watts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.POWER),
        SDMRegister(0x000E, True, "phase_2_power", "Phase 2 Power", 4, "Watts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.POWER),
        SDMRegister(0x0010, True, "phase_3_power", "Phase 3 Power", 4, "Watts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.POWER),
        SDMRegister(0x0012, False, "phase_1_apparent_power", "Phase 1 Apparent Power", 4, "VA", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.APPARENT_POWER),
        SDMRegister(0x0014, False, "phase_2_apparent_power", "Phase 2 Apparent Power", 4, "VA", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.APPARENT_POWER),
        SDMRegister(0x0016, False, "phase_3_apparent_power", "Phase 3 Apparent Power", 4, "VA", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.APPARENT_POWER),
        SDMRegister(0x0018, True, "phase_1_reactive_power", "Phase 1 Reactive Power", 4, "VAr", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.REACTIVE_POWER),
        SDMRegister(0x001A, True, "phase_2_reactive_power", "Phase 2 Reactive Power", 4, "VAr", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.REACTIVE_POWER),
        SDMRegister(0x001C, True, "phase_3_reactive_power", "Phase 3 Reactive Power", 4, "VAr", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.REACTIVE_POWER),
        SDMRegister(0x001E, False, "phase_1_power_factor", "Phase 1 Power Factor", 4, None, "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.POWER_FACTOR),
        SDMRegister(0x0020, False, "phase_2_power_factor", "Phase 2 Power Factor", 4, None, "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.POWER_FACTOR),
        SDMRegister(0x0022, False, "phase_3_power_factor", "Phase 3 Power Factor", 4, None, "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.POWER_FACTOR),
        SDMRegister(0x0024, False, "phase_1_phase_angle", "Phase 1 Phase Angle", 4, "Degrees", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x0026, False, "phase_2_phase_angle", "Phase 2 Phase Angle", 4, "Degrees", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x0028, False, "phase_3_phase_angle", "Phase 3 Phase Angle", 4, "Degrees", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x002E, False, "average_line_current", "Average Line Current", 4, "Amps", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.CURRENT),
        SDMRegister(0x0030, False, "sum_of_line_currents", "Sum of Line Currents", 4, "Amps", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.CURRENT),
        SDMRegister(0x0034, False, "total_system_power", "Total System Power", 4, "Watts", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.POWER),
        SDMRegister(0x0038, False, "total_system_apparent_power", "Total System Apparent Power", 4, "VA", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.APPARENT_POWER),
        SDMRegister(0x003C, False, "total_system_reactive_power", "Total System Reactive Power", 4, "VAr", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.REACTIVE_POWER),
        SDMRegister(0x003E, False, "total_system_power_factor", "Total System Power Factor", 4, None, "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.POWER_FACTOR),
        SDMRegister(0x0042, False, "total_system_phase_angle", "Total System Phase Angle", 4, "Degrees", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x0046, True, "frequency", "Frequency", 4, "Hz", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.FREQUENCY),
        SDMRegister(0x0048, True, "total_import_kwh", "Total Import kWh", 4, "kWh", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.ENERGY),
        SDMRegister(0x004A, True, "total_export_kwh", "Total Export kWh", 4, "kWh", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.ENERGY),
        SDMRegister(0x004C, False, "total_import_kvarh", "Total Import kVArh", 4, "kVArh", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.ENERGY),
        SDMRegister(0x004E, False, "total_export_kvarh", "Total Export kVArh", 4, "kVArh", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.ENERGY),
        SDMRegister(0x0054, False, "total_system_power_demand", "Total System Power Demand", 4, "W", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.POWER),
        SDMRegister(0x0056, False, "max_total_system_power_demand", "Max Total System Power Demand", 4, "W", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.POWER),
        SDMRegister(0x0064, False, "total_system_va_demand", "Total System VA Demand", 4, "VA", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.APPARENT_POWER),
        SDMRegister(0x0066, False, "max_total_system_va_demand", "Max Total System VA Demand", 4, "VA", "Float", 1.0, "RO", "sensor", "Diagnostic", SensorDeviceClass.APPARENT_POWER),
        SDMRegister(0x00EA, False, "phase_1_l_n_volts_thd", "Phase 1 L/N Volts THD", 4, "%", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x00EC, False, "phase_2_l_n_volts_thd", "Phase 2 L/N Volts THD", 4, "%", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x00EE, False, "phase_3_l_n_volts_thd", "Phase 3 L/N Volts THD", 4, "%", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x00F0, False, "phase_1_current_thd", "Phase 1 Current THD", 4, "%", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x00F2, False, "phase_2_current_thd", "Phase 2 Current THD", 4, "%", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x00F4, False, "phase_3_current_thd", "Phase 3 Current THD", 4, "%", "Float", 1.0, "RO", "sensor", "Advanced", None),
        SDMRegister(0x0156, False, "total_kwh", "Total kWh", 4, "kWh", "Float", 1.0, "RO", "sensor", "Basic", SensorDeviceClass.ENERGY),
        SDMRegister(0x0158, False, "total_kvarh", "Total kVArh", 4, "kVArh", "Float", 1.0, "RO", "sensor", "Advanced", SensorDeviceClass.ENERGY),
        SDMRegister(0x0002, False, "demand_period", "Demand Period", 4, "min", "Float", 1.0, "RW", "select", "Config", "Enum: 0, 5, 8, 10, 15, 20, 30, 60 (default 60)"),
        SDMRegister(0x000A, False, "system_type", "System Type", 4, None, "Float", 1.0, "RW", "select", "Config", "Enum: 3p4w=3, 3p3w=2, 1p2w=1 (password protected)"),
        SDMRegister(0x000C, False, "pulse1_width", "Pulse1 Width", 4, "ms", "Float", 1.0, "RW", "number", "Config", "Enum: 60, 100, 200 (default 100)"),
        SDMRegister(0x000E, False, "password_lock", "Password Lock", 4, None, "Float", 1.0, "RW", "button", "Config", "Write any value to lock, read resets timeout"),
        SDMRegister(0x0012, False, "network_parity_stop", "Network Parity Stop", 4, None, "Float", 1.0, "RW", "select", "Config", "Enum: 0=1 stop/no parity, 1=1 stop/even, 2=1 stop/odd, 3=2 stop/no parity"),
        SDMRegister(0x0014, False, "network_node", "Network Node", 4, None, "Float", 1.0, "RW", "number", "Config", "Range: 1-247, default 1"),
        SDMRegister(0x0016, False, "pulse1_divisor1", "Pulse1 Divisor1", 4, None, "Float", 1.0, "RW", "select", "Config", "Enum: 0=0.0025, 1=0.01, 2=0.1, 3=1, 4=10, 5=100 kWh/imp"),
        SDMRegister(0x0018, False, "password", "Password", 4, None, "Float", 1.0, "RW", "number", "Config", "Enter password for protected registers"),
        SDMRegister(0x001C, False, "network_baud_rate", "Network Baud Rate", 4, None, "Float", 1.0, "RW", "select", "Config", "Enum: 0=2400, 1=4800, 2=9600 (default), 3=19200, 4=38400"),
        SDMRegister(0x0056, False, "pulse_1_energy_type", "Pulse 1 Energy Type", 4, None, "Float", 1.0, "RW", "select", "Config", "Enum: 1=import, 2=total, 4=export (default), 5=import reactive, 6=total reactive, 8=export reactive"),
        SDMRegister(0xF010, False, "reset", "Reset", 2, None, "HEX", 1.0, "RW", "button", "Config", "Write 0x0000 to reset max demand"),
        SDMRegister(0xFC00, False, "serial_number", "Serial number", 4, None, "UInt32", 1.0, "RO", "sensor", "Diagnostic", "Read only"),
    )

async def async_detect_device_model(client: Any, unit_id: int) -> Optional[str]:
    """Detect SDM device model by reading distinguishing registers.

    Args:
        client: Async pymodbus client.
        unit_id: Modbus unit ID.

    Returns:
        "SDM120", "SDM630", or None if detection failed.
    """
    try:
        # Try SDM630-specific register (Phase 2 L-N Voltage at 0x0002)
        result_630 = await client.read_holding_registers(0x0002)
        if hasattr(result_630, "registers") and not result_630.isError():
            val_630 = result_630.registers[0]
            # SDM630 should report a plausible voltage (e.g., > 50V), SDM120 will return 0 or nonsense
            if val_630 > 50:
                return "SDM630"
        # Try SDM120-specific register (Voltage at 0x0000)
        result_120 = await client.read_holding_registers(0x0000)
        if hasattr(result_120, "registers") and not result_120.isError():
            val_120 = result_120.registers[0]
            if val_120 > 50:
                return "SDM120"
    except Exception as exc:
        _LOGGER.error("Device detection failed: %s", exc)

def get_number_entities_for_model(model: str):
    """Return number entity definitions for the given SDM model."""
    if model == "SDM120":
        registers = SDM120RegisterMap.REGISTERS
    elif model == "SDM630":
        registers = SDM630RegisterMap.REGISTERS
    else:
        return []

    # Filter registers for number entities (ha_entity_type == "number")
    number_entities = [
        reg for reg in registers if getattr(reg, "ha_entity_type", None) == "number"
    ]
    return number_entities

def get_select_entities_for_model(model: str):
    """Return select entity definitions for the given SDM model."""
    if model == "SDM120":
        registers = SDM120RegisterMap.REGISTERS
    elif model == "SDM630":
        registers = SDM630RegisterMap.REGISTERS
    else:
        return []

    # Filter registers for select entities (ha_entity_type == "select")
    select_entities = [
        reg for reg in registers if getattr(reg, "ha_entity_type", None) == "select"
    ]
    return select_entities

def get_button_entities_for_model(model: str):
    """Return button entity definitions for the given SDM model."""
    if model == "SDM120":
        registers = SDM120RegisterMap.REGISTERS
    elif model == "SDM630":
        registers = SDM630RegisterMap.REGISTERS
    else:
        return []

    # Filter registers for button entities (ha_entity_type == "button")
    button_entities = [
        reg for reg in registers if getattr(reg, "ha_entity_type", None) == "button"
    ]
    return button_entities

def create_device_instance(model: str, host: str, port: int, unit_id: int, timeout: int = 10, **kwargs):
    """Factory for SDMDevice instances based on model."""
    if model == "SDM120":
        return SDMDevice(host=host, port=port, unit_id=unit_id, model="SDM120", timeout=timeout)
    elif model == "SDM630":
        return SDMDevice(host=host, port=port, unit_id=unit_id, model="SDM630", timeout=timeout)
    else:
        raise ValueError(f"Unknown SDM model: {model}")
