"""Config flow for Eastron SDM integration (skeleton)."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_UNIT_ID,
    CONF_SCAN_INTERVAL,
    CONF_ENABLE_ADVANCED,
    CONF_ENABLE_DIAGNOSTIC,
    CONF_NORMAL_DIVISOR,
    CONF_SLOW_DIVISOR,
    CONF_DEBUG,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NORMAL_DIVISOR,
    DEFAULT_SLOW_DIVISOR,
    MIN_SCAN_INTERVAL,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=502): int,
        vol.Required(CONF_UNIT_ID, default=1): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        vol.Optional(CONF_ENABLE_ADVANCED, default=False): bool,
        vol.Optional(CONF_ENABLE_DIAGNOSTIC, default=False): bool,
        vol.Optional(CONF_NORMAL_DIVISOR, default=DEFAULT_NORMAL_DIVISOR): int,
        vol.Optional(CONF_SLOW_DIVISOR, default=DEFAULT_SLOW_DIVISOR): int,
        vol.Optional(CONF_DEBUG, default=False): bool,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[misc]
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            # Basic validation
            if user_input[CONF_SCAN_INTERVAL] < MIN_SCAN_INTERVAL:
                errors[CONF_SCAN_INTERVAL] = "min_value"
            if user_input[CONF_NORMAL_DIVISOR] < 2:
                errors[CONF_NORMAL_DIVISOR] = "min_value"
            if user_input[CONF_SLOW_DIVISOR] <= user_input[CONF_NORMAL_DIVISOR]:
                errors[CONF_SLOW_DIVISOR] = "invalid"

            if not errors:
                title = f"{user_input[CONF_NAME]} (SDM120)"
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input[CONF_SCAN_INTERVAL] < MIN_SCAN_INTERVAL:
                errors[CONF_SCAN_INTERVAL] = "min_value"
            if user_input[CONF_NORMAL_DIVISOR] < 2:
                errors[CONF_NORMAL_DIVISOR] = "min_value"
            if user_input[CONF_SLOW_DIVISOR] <= user_input[CONF_NORMAL_DIVISOR]:
                errors[CONF_SLOW_DIVISOR] = "invalid"
            if not errors:
                # Save options
                return self.async_create_entry(title="Options", data=user_input)

        data = {**self._entry.data, **self._entry.options}
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int,
                vol.Required(CONF_ENABLE_ADVANCED, default=data.get(CONF_ENABLE_ADVANCED, False)): bool,
                vol.Required(CONF_ENABLE_DIAGNOSTIC, default=data.get(CONF_ENABLE_DIAGNOSTIC, False)): bool,
                vol.Required(CONF_NORMAL_DIVISOR, default=data.get(CONF_NORMAL_DIVISOR, DEFAULT_NORMAL_DIVISOR)): int,
                vol.Required(CONF_SLOW_DIVISOR, default=data.get(CONF_SLOW_DIVISOR, DEFAULT_SLOW_DIVISOR)): int,
                vol.Required(CONF_DEBUG, default=data.get(CONF_DEBUG, False)): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)

    async def async_create_entry(self, title: str, data: dict[str, Any]) -> dict[str, Any]:
        """Handle the creation of an entry."""
        # Update the config entry with the new options
        self.hass.config_entries.async_update(self._entry.entry_id, options=data)
        # Reload the entry to apply the new options
        await self.hass.config_entries.async_reload(self._entry.entry_id)
        return self.async_create_entry(title=title, data={**self._entry.data, **data})

async def async_get_options_flow(config_entry: config_entries.ConfigEntry):  # pragma: no cover - HA hook
    return OptionsFlowHandler(config_entry)
