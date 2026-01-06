"""SDM120 register specifications (Phase 1 Task 1.2)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

@dataclass(frozen=True, slots=True)
class RegisterSpec:
    key: str
    address: int  # zero-based Modbus register address (Input Register base)
    length: int   # number of 16-bit registers
    function: str # 'input'
    data_type: str  # 'float32'
    unit: str | None
    device_class: str | None
    state_class: str | None
    category: str  # 'basic' | 'advanced' | 'diagnostic'
    tier: str  # 'fast' | 'normal' | 'slow'
    enabled_default: bool
    precision: int | None = None  # optional display precision

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
        device_class="energy", state_class="total_increasing", category="basic", tier="slow", enabled_default=True,
    ),
    RegisterSpec(
        key="total_active_energy", address=342, length=2, function="input", data_type="float32", unit="kWh",
        device_class="energy", state_class="total_increasing", category="basic", tier="slow", enabled_default=True,
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

    # Diagnostic identity (disabled by default)
    RegisterSpec(
        key="serial_number", address=0xFC00, length=2, function="input", data_type="uint32", unit=None,
        device_class=None, state_class=None, category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="meter_code", address=0xFC02, length=1, function="input", data_type="uint16", unit=None,
        device_class=None, state_class=None, category="diagnostic", tier="slow", enabled_default=False,
    ),
    RegisterSpec(
        key="software_version", address=0xFC03, length=1, function="input", data_type="uint16", unit=None,
        device_class=None, state_class=None, category="diagnostic", tier="slow", enabled_default=False,
    ),

    # Diagnostic (disabled by default)
    RegisterSpec(
        key="total_system_power_demand", address=84, length=2, function="input", data_type="float32", unit="W",
        device_class="power", state_class="measurement", category="diagnostic", tier="slow", enabled_default=False,
    ),
]


def get_register_specs(*, enable_advanced: bool, enable_diagnostic: bool) -> list[RegisterSpec]:
    """Return filtered register specs based on option flags."""
    specs: list[RegisterSpec] = []
    for spec in BASE_SDM120_SPECS:
        if spec.category == "advanced" and not enable_advanced:
            if not spec.enabled_default:
                continue
        if spec.category == "diagnostic" and not enable_diagnostic:
            if not spec.enabled_default:
                continue
        if spec.enabled_default or (spec.category == "advanced" and enable_advanced) or (spec.category == "diagnostic" and enable_diagnostic):
            specs.append(spec)
    return specs
