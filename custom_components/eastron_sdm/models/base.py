"""Shared model definitions."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterSpec:
    key: str
    address: int  # zero-based Modbus register address (Input Register base)
    length: int   # number of 16-bit registers
    function: str  # 'input' | 'holding'
    data_type: str  # 'float32' | 'uint32' | 'uint16' | 'hex16'
    unit: str | None
    device_class: str | None
    state_class: str | None
    category: str  # 'basic' | 'advanced' | 'diagnostic' | 'config' | 'two-way'
    tier: str  # 'fast' | 'normal' | 'slow'
    enabled_default: bool
    precision: int | None = None  # optional display precision
    control: str | None = None  # 'number' | 'select'
    options: tuple[int, ...] | None = None  # for select controls
    min_value: float | None = None  # for number controls
    max_value: float | None = None  # for number controls
    step: float | None = None  # for number controls
    mode: str | None = None  # for number controls: 'auto' | 'slider' | 'box'