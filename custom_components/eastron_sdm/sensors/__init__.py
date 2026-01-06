"""Sensor exports for Eastron SDM."""
from __future__ import annotations

from .base import SdmBaseSensor
from .register import SdmRegisterSensor

__all__ = ["SdmBaseSensor", "SdmRegisterSensor"]
