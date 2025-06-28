"""Custom exceptions for Eastron SDM integration."""

from homeassistant.exceptions import HomeAssistantError

class SDMConnectionError(HomeAssistantError):
    """Error connecting to SDM device."""

class SDMDeviceNotFoundError(HomeAssistantError):
    """SDM device not found or not responding."""
