"""Config flow for Eastron SDM integration."""

from __future__ import annotations

from typing import Any
import voluptuous as vol
import json
import re
import asyncio
import logging

try:
    from pymodbus.client import AsyncModbusTcpClient
except ImportError:
    AsyncModbusTcpClient = None

from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CATEGORY_BASIC, CATEGORY_ADVANCED, CATEGORY_DIAGNOSTIC
from .exceptions import SDMConnectionError
from .device_models import async_detect_device_model

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow handler for Eastron SDM integration.

    Guides the user through connection setup, device naming, entity category selection,
    and polling interval customization. Supports configuration import/export and robust error handling.
    """

    VERSION = 1

    async def async_step_import(self, user_input: dict[str, Any] | None = None):
        """Step 0: Optional configuration import.

        Allows the user to paste a JSON config to pre-fill the setup flow.
        """
        errors = {}
        data_schema = vol.Schema(
            {
                vol.Optional("import_json"): str,
            }
        )
        if user_input is not None and user_input.get("import_json"):
            try:
                imported = json.loads(user_input["import_json"])
                # Pre-fill context and jump to user step
                self.context["imported"] = imported
                return await self.async_step_user(imported)
            except Exception as exc:
                _LOGGER.error("Failed to import configuration JSON: %s", exc)
                errors["import_json"] = "invalid_json"
        return self.async_show_form(
            step_id="import",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}
        data_schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Required("port", default=4196): int,
                vol.Required("unit_id", default=1): int,
            }
        )
        if user_input is not None:
            # Validate host
            host = user_input.get("host", "").strip()
            port = user_input.get("port", 4196)
            unit_id = user_input.get("unit_id", 1)
            if not host:
                errors["host"] = "host_required"
            elif not re.match(r"^[a-zA-Z0-9\.\-]+$", host):
                errors["host"] = "host_invalid"
            # Validate port
            if not isinstance(port, int) or not (1 <= port <= 65535):
                errors["port"] = "port_invalid"
            # Validate unit_id
            if not isinstance(unit_id, int) or not (1 <= unit_id <= 247):
                errors["unit_id"] = "unit_id_invalid"
            # Device conflict detection: prevent duplicate (host, unit_id)
            existing_entries = self._async_current_entries()
            for entry in existing_entries:
                if (
                    entry.data.get("host") == host
                    and entry.data.get("unit_id") == unit_id
                ):
                    errors["base"] = "duplicate_device"
                    break
            if not errors:
                try:
                    client = await self._async_validate_connection(
                        host, port, unit_id
                    )
                    model = await async_detect_device_model(
                        client, unit_id
                    )
                    await client.close()
                    if not model:
                        errors["base"] = "cannot_detect_model"
                    else:
                        # Store connection and model info, proceed to naming step
                        self.context["connection"] = dict(user_input)
                        self.context["connection"]["model"] = model
                        return await self.async_step_name()
                except SDMConnectionError as exc:
                    _LOGGER.error("Connection error: %s", exc)
                    errors["base"] = "cannot_connect"
                except Exception as exc:
                    _LOGGER.exception("Unknown error during connection validation: %s", exc)
                    errors["base"] = "unknown"
        description = "Step 1 of 4: Connection Setup"
        if user_input is not None and not errors:
            description = "Connecting to device..."
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )

    async def async_step_name(self, user_input: dict[str, Any] | None = None):
        """Handle device naming step with validation."""
        errors = {}
        data_schema = vol.Schema(
            {
                vol.Required("device_name"): str,
            }
        )
        if user_input is not None:
            name = user_input["device_name"].strip()
            if not name or not name.replace("_", "").replace("-", "").isalnum():
                errors["device_name"] = "invalid_name"
            elif len(name) > 32:
                errors["device_name"] = "name_too_long"
            else:
                # Store name in context and proceed to category selection
                self.context["connection"]["device_name"] = name
                return await self.async_step_categories()
        return self.async_show_form(
            step_id="name",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )

    async def async_step_categories(self, user_input: dict[str, Any] | None = None):
        """Handle entity category selection step."""
        errors = {}
        data_schema = vol.Schema(
            {
                vol.Required(
                    CATEGORY_BASIC, default=True
                ): bool,
                vol.Optional(
                    CATEGORY_ADVANCED, default=False
                ): bool,
                vol.Optional(
                    CATEGORY_DIAGNOSTIC, default=False
                ): bool,
            }
        )
        if user_input is not None:
            categories = []
            if user_input.get(CATEGORY_BASIC, True):
                categories.append(CATEGORY_BASIC)
            if user_input.get(CATEGORY_ADVANCED, False):
                categories.append(CATEGORY_ADVANCED)
            if user_input.get(CATEGORY_DIAGNOSTIC, False):
                categories.append(CATEGORY_DIAGNOSTIC)
            self.context["connection"]["categories"] = categories
            return await self.async_step_polling()
        return self.async_show_form(
            step_id="categories",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )

    async def async_step_polling(self, user_input: dict[str, Any] | None = None):
        """Handle polling interval customization step."""
        errors = {}
        data_schema = vol.Schema(
            {
                vol.Required("poll_fast", default=5): int,
                vol.Required("poll_normal", default=30): int,
                vol.Required("poll_slow", default=300): int,
            }
        )
        if user_input is not None:
            poll_fast = user_input["poll_fast"]
            poll_normal = user_input["poll_normal"]
            poll_slow = user_input["poll_slow"]
            if poll_fast < 1 or poll_normal < 1 or poll_slow < 1:
                errors["base"] = "invalid_poll"
            else:
                entry_data = dict(self.context["connection"])
                entry_data["poll_fast"] = poll_fast
                entry_data["poll_normal"] = poll_normal
                entry_data["poll_slow"] = poll_slow
                return self.async_create_entry(
                    title=f"{entry_data['device_name']} ({entry_data['model']})", data=entry_data
                )
        return self.async_show_form(
            step_id="polling",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )

    async def _async_validate_connection(self, host: str, port: int, unit_id: int):
        """Validate connection to the SDM device and return client, with retries."""
        if AsyncModbusTcpClient is None:
            raise SDMConnectionError("pymodbus not installed")

        last_exc = None
        for attempt in range(3):
            try:
                client = AsyncModbusTcpClient(host=host, port=port)
                await client.connect()
                result = await client.read_holding_registers(0x0000, 2, unit_id)
                if not hasattr(result, "registers") or result.isError():
                    await client.close()
                    raise SDMConnectionError("No response or error from device")
                return client
            except Exception as exc:
                last_exc = exc
                _LOGGER.warning("Connection attempt %d failed: %s", attempt + 1, exc)
                await asyncio.sleep(1)
        raise SDMConnectionError(f"Connection failed after retries: {last_exc}") from last_exc

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return EastronSDMOptionsFlowHandler(config_entry)

class EastronSDMOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Eastron SDM."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options (device management UI)."""
        errors = {}
        current_name = self.config_entry.data.get("device_name", "")
        options = self.config_entry.options
        fast_default = options.get("poll_fast", 5)
        normal_default = options.get("poll_normal", 30)
        slow_default = options.get("poll_slow", 300)
        data_schema = vol.Schema(
            {
                vol.Required("device_name", default=current_name): str,
                vol.Required("poll_fast", default=fast_default): int,
                vol.Required("poll_normal", default=normal_default): int,
                vol.Required("poll_slow", default=slow_default): int,
                vol.Optional("export_config"): bool,
            }
        )
        if user_input is not None:
            if user_input.get("export_config"):
                return await self.async_step_export()
            name = user_input["device_name"].strip()
            poll_fast = user_input["poll_fast"]
            poll_normal = user_input["poll_normal"]
            poll_slow = user_input["poll_slow"]
            if not name or not name.replace("_", "").replace("-", "").isalnum():
                errors["device_name"] = "invalid_name"
            elif len(name) > 32:
                errors["device_name"] = "name_too_long"
            elif poll_fast < 1 or poll_normal < 1 or poll_slow < 1:
                errors["base"] = "invalid_poll"
            else:
                # Save new name and polling intervals to options
                return self.async_create_entry(
                    title=name,
                    data={
                        "device_name": name,
                        "poll_fast": poll_fast,
                        "poll_normal": poll_normal,
                        "poll_slow": poll_slow,
                    },
                )
        # Diagnostic info
        model = self.config_entry.data.get("model", "Unknown")
        firmware = self.config_entry.data.get("firmware", "Unknown")
        diag_desc = (
            f"Device model: {model}\n"
            f"Firmware: {firmware}\n\n"
            "Edit configuration or export current config as JSON."
        )
        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )

    async def async_step_export(self, user_input: dict[str, Any] | None = None):
        """Export current configuration as JSON."""
        config = dict(self.config_entry.data)
        config.update(self.config_entry.options)
        export_json = json.dumps(config, indent=2)
        return self.async_show_form(
            step_id="export",
            data_schema=vol.Schema({}),
            description_placeholders={"export_json": export_json},
        )
