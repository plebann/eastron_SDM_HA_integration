"""SDM630M register specifications."""
from __future__ import annotations

from typing import Final, List

from .base import RegisterSpec

SDM630_SPECS: Final[List[RegisterSpec]] = [
    # FAST tier - per-phase measurements
    RegisterSpec(
        key="voltage_l1", address=0, length=2, function="input", data_type="float32", unit="V",
        device_class="voltage", state_class="measurement", category="basic", tier="fast", enabled_default=True,
        precision=1,
    ),
    RegisterSpec(
        key="voltage_l2", address=2, length=2, function="input", data_type="float32", unit="V",
        device_class="voltage", state_class="measurement", category="basic", tier="fast", enabled_default=True,
        precision=1,
    ),
    RegisterSpec(
        key="voltage_l3", address=4, length=2, function="input", data_type="float32", unit="V",
        device_class="voltage", state_class="measurement", category="basic", tier="fast", enabled_default=True,
        precision=1,
    ),
    RegisterSpec(
        key="current_l1", address=6, length=2, function="input", data_type="float32", unit="A",
        device_class="current", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),
    RegisterSpec(
        key="current_l2", address=8, length=2, function="input", data_type="float32", unit="A",
        device_class="current", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),
    RegisterSpec(
        key="current_l3", address=10, length=2, function="input", data_type="float32", unit="A",
        device_class="current", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),
    RegisterSpec(
        key="active_power_l1", address=12, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),
    RegisterSpec(
        key="active_power_l2", address=14, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),
    RegisterSpec(
        key="active_power_l3", address=16, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),
    RegisterSpec(
        key="sum_line_currents", address=48, length=2, function="input", data_type="float32", unit="A",
        device_class="current", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),
    RegisterSpec(
        key="total_system_power", address=52, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),

    # NORMAL tier - power quality
    RegisterSpec(
        key="total_system_apparent_power", address=56, length=2, function="input", data_type="float32", unit="VA",
        device_class="apparent_power", state_class="measurement", category="advanced", tier="normal", enabled_default=False,
    ),
    RegisterSpec(
        key="total_system_reactive_power", address=60, length=2, function="input", data_type="float32", unit="var",
        device_class="reactive_power", state_class="measurement", category="advanced", tier="normal", enabled_default=False,
    ),
    RegisterSpec(
        key="total_system_power_factor", address=62, length=2, function="input", data_type="float32", unit=None,
        device_class="power_factor", state_class="measurement", category="advanced", tier="normal", enabled_default=False,
        precision=4,
    ),
    RegisterSpec(
        key="frequency", address=70, length=2, function="input", data_type="float32", unit="Hz",
        device_class="frequency", state_class="measurement", category="basic", tier="normal", enabled_default=True,
        precision=2,
    ),

    # SLOW tier - energies and demand
    RegisterSpec(
        key="total_import_active_energy", address=72, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="basic", tier="slow", enabled_default=True,
    ),
    RegisterSpec(
        key="total_export_active_energy", address=74, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="two-way", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_import_reactive_energy", address=76, length=2, function="input", data_type="float32", unit="kVArh",
        device_class=None, state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_export_reactive_energy", address=78, length=2, function="input", data_type="float32", unit="kVArh",
        device_class=None, state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_apparent_energy", address=80, length=2, function="input", data_type="float32", unit="kVAh",
        device_class=None, state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_system_power_demand", address=84, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="max_total_system_power_demand", address=86, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_system_va_demand", address=100, length=2, function="input", data_type="float32", unit="VA",
        device_class="apparent_power", state_class="measurement", category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="neutral_current_demand", address=104, length=2, function="input", data_type="float32", unit="A",
        device_class="current", state_class="measurement", category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="max_neutral_current_demand", address=106, length=2, function="input", data_type="float32", unit="A",
        device_class="current", state_class="measurement", category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="neutral_current", address=224, length=2, function="input", data_type="float32", unit="A",
        device_class="current", state_class="measurement", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_active_energy", address=342, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="basic", tier="slow", enabled_default=True,
    ),
    RegisterSpec(
        key="total_reactive_energy", address=344, length=2, function="input", data_type="float32", unit="kVArh",
        device_class=None, state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="import_active_energy_l1", address=346, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="import_active_energy_l2", address=348, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="import_active_energy_l3", address=350, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="export_active_energy_l1", address=352, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="two-way", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="export_active_energy_l2", address=354, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="two-way", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="export_active_energy_l3", address=356, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="two-way", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_active_energy_l1", address=358, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_active_energy_l2", address=360, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_active_energy_l3", address=362, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="advanced", tier="slow", enabled_default=False,
    ),

    # Diagnostic identity
    RegisterSpec(
        key="serial_number", address=64513, length=2, function="holding", data_type="uint32", unit=None,
        device_class=None, state_class=None, category="diagnostic", tier="slow", enabled_default=False,
    ),

    # Config - writable
    RegisterSpec(
        key="network_parity_stop", address=18, length=2, function="holding", data_type="float32", unit=None,
        device_class=None, state_class=None, category="config", tier="slow", enabled_default=False,
        control="select", options=(0, 1, 2, 3),
    ),
    RegisterSpec(
        key="meter_id", address=20, length=2, function="holding", data_type="float32", unit=None,
        device_class=None, state_class=None, category="config", tier="slow", enabled_default=False,
        precision=0, control="number", min_value=1, max_value=247, step=1, mode="box",
    ),
    RegisterSpec(
        key="baud_rate", address=28, length=2, function="holding", data_type="float32", unit=None,
        device_class=None, state_class=None, category="config", tier="slow", enabled_default=False,
        control="select", options=(0, 1, 2, 3, 4),
    ),
]


def get_register_specs() -> List[RegisterSpec]:
    """Return all SDM630M register specs."""

    return list(SDM630_SPECS)