"""Concrete register-based sensors for Eastron SDM."""
from __future__ import annotations

from .base import SdmBaseSensor


class SdmRegisterSensor(SdmBaseSensor):
    """Sensor representing a single SDM register value."""

    # Inherits behavior from SdmBaseSensor; kept for future specializations
    pass
