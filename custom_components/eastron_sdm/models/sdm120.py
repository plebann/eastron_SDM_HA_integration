"""SDM120 register specifications (Phase 1 Task 1.2)."""
from __future__ import annotations

from typing import Final

from .base import RegisterSpec

BASE_SDM120_SPECS: Final[list[RegisterSpec]] = [
    # FAST tier (every base cycle)
    RegisterSpec(
        key="voltage", address=0, length=2, function="input", data_type="float32", unit="V",
        device_class="voltage", state_class="measurement", category="basic", tier="fast", enabled_default=True, precision=1,
    ),
    RegisterSpec(
        key="current", address=6, length=2, function="input", data_type="float32", unit="A",
        device_class="current", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),
    RegisterSpec(
        key="active_power", address=12, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="basic", tier="fast", enabled_default=True,
    ),

    # NORMAL tier (every normal divisor cycles)
    RegisterSpec(
        key="frequency", address=70, length=2, function="input", data_type="float32", unit="Hz",
        device_class="frequency", state_class="measurement", category="basic", tier="normal", enabled_default=True, precision=2,
    ),

    # SLOW tier (every slow divisor cycles)
    RegisterSpec(
        key="import_active_energy", address=72, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="basic", tier="slow", enabled_default=True,
    ),
    RegisterSpec(
        key="export_active_energy", address=74, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="two-way", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="total_active_energy", address=342, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="two-way", tier="slow", enabled_default=False,
    ),

    # Advanced (disabled by default) - may be enabled later via options
    RegisterSpec(
        key="apparent_power", address=18, length=2, function="input", data_type="float32", unit="VA",
        device_class="apparent_power", state_class="measurement", category="advanced", tier="normal", enabled_default=False,
    ),
    RegisterSpec(
        key="reactive_power", address=24, length=2, function="input", data_type="float32", unit="var",
        device_class="reactive_power", state_class="measurement", category="advanced", tier="normal", enabled_default=False,
    ),
    RegisterSpec(
        key="power_factor", address=30, length=2, function="input", data_type="float32", unit=None,
        device_class="power_factor", state_class="measurement", category="advanced", tier="normal", enabled_default=False, precision=4,
    ),

    # Config (disabled by default)
    RegisterSpec(
        key="network_parity_stop", address=18, length=2, function="holding", data_type="float32", unit=None,
        device_class=None, state_class=None, category="config", tier="slow", enabled_default=False,
        control="select", options=(0, 1, 2, 3),
    ),
    RegisterSpec(
        key="meter_id", address=20, length=2, function="holding", data_type="float32", unit=None,
        device_class=None, state_class=None, category="config", tier="slow", enabled_default=False,
        precision=0, control="number", min_value=1, max_value=247, step=1, mode="box"
    ),
    RegisterSpec(
        key="baud_rate", address=28, length=2, function="holding", data_type="float32", unit=None,
        device_class=None, state_class=None, category="config", tier="slow", enabled_default=False,
        control="select", options=(0, 1, 2, 5),
    ),

    # Diagnostic identity (disabled by default) — holding registers per vendor map
    RegisterSpec(
        key="serial_number", address=64512, length=2, function="holding", data_type="uint32", unit=None,
        device_class=None, state_class=None, category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="meter_code", address=64514, length=1, function="holding", data_type="uint16", unit=None,
        device_class=None, state_class=None, category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="software_version", address=64515, length=1, function="holding", data_type="uint16", unit=None,
        device_class=None, state_class=None, category="diagnostic", tier="slow", enabled_default=False,
    ),

    # Diagnostic (disabled by default)
    RegisterSpec(
        key="total_system_power_demand", address=84, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="diagnostic", tier="slow", enabled_default=False,
    ),
]


def _get_spec_by_key(key: str) -> RegisterSpec:
    """Get a register spec by its key.
    
    Args:
        key: The register key to look up.
        
    Returns:
        RegisterSpec instance matching the key.
        
    Raises:
        ValueError: If no spec found for the given key.
    """
    for spec in BASE_SDM120_SPECS:
        if spec.key == key:
            return spec
    raise ValueError(f"No spec found for key: {key}")


def get_register_specs() -> list[RegisterSpec]:
    """Return all register specs; enabled_default drives registry enabled state."""
    return list(BASE_SDM120_SPECS)
