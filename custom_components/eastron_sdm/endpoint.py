"""Shared Modbus endpoint: one TCP connection and one I/O lock per host and port."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from pymodbus.client import AsyncModbusTcpClient

from .const import CONF_HOST, CONF_PORT, CONF_UNIT_ID, DEFAULT_PORT, DEFAULT_UNIT_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

ENDPOINTS_KEY = f"{DOMAIN}_endpoints"

EndpointKey = tuple[str, int]


def endpoint_key(host: str, port: int) -> EndpointKey:
    return (str(host).strip().lower(), int(port))


class ModbusEndpoint:
    """Owns the single TCP client for a Modbus endpoint and serializes every request through it."""

    def __init__(self, host: str, port: int, *, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.users = 0
        self._timeout = timeout
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()
        self._retired = False
        # Serializes Unit ID changes (conflict check, write, verify, persist) across the endpoint's meters.
        # Separate from the transport lock, which each request inside such a change takes itself.
        self.address_lock = asyncio.Lock()

    @property
    def key(self) -> EndpointKey:
        return endpoint_key(self.host, self.port)

    async def request(self, method_name: str, unit_id: Callable[[], int], **kwargs: Any) -> Any:
        """Send one request; no other request on this endpoint overlaps it.

        The Unit ID is resolved once the lock is held, so a request queued behind a Unit ID change
        is addressed to the meter's current ID.
        """
        async with self._lock:
            if self._retired:
                raise ConnectionError(f"Modbus endpoint {self.host}:{self.port} was released")
            await self._ensure_connected()
            assert self._client is not None
            method = getattr(self._client, method_name)
            return await method(device_id=unit_id(), **kwargs)

    async def retire_if_unused(self) -> bool:
        """Close the connection and refuse further requests unless a user acquired the endpoint again."""
        async with self._lock:
            if self.users > 0:
                return False
            self._retired = True
            self._close_client()
            return True

    async def _ensure_connected(self) -> None:
        if self._client is not None and self._client.connected:
            return
        self._close_client()
        self._client = AsyncModbusTcpClient(self.host, port=self.port, timeout=self._timeout)
        await self._client.connect()
        if not self._client.connected:
            raise ConnectionError("Unable to connect Modbus client")
        _LOGGER.debug("Connected to %s:%s", self.host, self.port)

    def _close_client(self) -> None:
        if self._client is not None:
            with suppress(Exception):
                self._client.close()
            self._client = None


def async_acquire_endpoint(hass: HomeAssistant, host: str, port: int) -> ModbusEndpoint:
    """Return the endpoint for host and port, creating it for the first user."""
    endpoints: dict[EndpointKey, ModbusEndpoint] = hass.data.setdefault(ENDPOINTS_KEY, {})
    key = endpoint_key(host, port)
    endpoint = endpoints.get(key)
    if endpoint is None:
        endpoint = endpoints[key] = ModbusEndpoint(host, port)
    endpoint.users += 1
    return endpoint


async def async_release_endpoint(hass: HomeAssistant, endpoint: ModbusEndpoint) -> None:
    """Drop one user and close the connection once the last user is gone.

    The endpoint stays registered until it holds its lock, so a meter set up meanwhile
    reuses it instead of opening a second connection to the same gateway.
    """
    endpoint.users -= 1
    if endpoint.users > 0:
        return
    if await endpoint.retire_if_unused():
        endpoints: dict[EndpointKey, ModbusEndpoint] = hass.data.get(ENDPOINTS_KEY, {})
        if endpoints.get(endpoint.key) is endpoint:
            del endpoints[endpoint.key]


def find_unit_id_conflict(
    hass: HomeAssistant,
    host: str,
    port: int,
    unit_id: int,
    *,
    exclude_entry_id: str | None = None,
) -> ConfigEntry | None:
    """Return another config entry already using this Unit ID on the same Modbus endpoint."""
    key = endpoint_key(host, port)
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.entry_id == exclude_entry_id:
            continue
        data = {**entry.data, **entry.options}
        entry_key = endpoint_key(data.get(CONF_HOST, ""), data.get(CONF_PORT, DEFAULT_PORT))
        if entry_key == key and int(data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)) == int(unit_id):
            return entry
    return None
