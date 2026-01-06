"""Async Modbus RTU-over-TCP client wrapper."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from dataclasses import dataclass
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusIOException

_LOGGER = logging.getLogger(__name__)

@dataclass(slots=True)
class ReadResult:
    address: int
    count: int
    registers: list[int]

class SdmModbusClient:
    """Wrapper managing a single RTU-over-TCP session."""

    def __init__(self, host: str, port: int, unit_id: int, *, timeout: float = 5.0) -> None:
        self._host = host
        self._port = port
        self._unit_id = unit_id
        self._timeout = timeout
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()
        self._io_lock = asyncio.Lock()  # serialize Modbus requests to avoid transaction-id interleave
        self._connected = False

    async def ensure_connected(self) -> None:
        async with self._lock:
            if self._connected and self._client and self._client.connected:  # type: ignore[attr-defined]
                return
            # Close previous if any
            if self._client:
                with suppress(Exception):
                    await self._client.close()
            # Attempt to import an RTU framer for better transaction id alignment when the
            # device expects RTU style encapsulation over TCP (common with SDM meters via gateways).
            framer = None
            with suppress(Exception):  # optional
                # pymodbus relocated framers across versions; try a few paths
                try:
                    from pymodbus.framer import ModbusRtuFramer as _Framer  # type: ignore
                except Exception:  # pragma: no cover
                    from pymodbus.transaction import ModbusRtuFramer as _Framer  # type: ignore
                framer = _Framer

            if framer:
                self._client = AsyncModbusTcpClient(
                    self._host,
                    port=self._port,
                    timeout=self._timeout,
                    framer=framer,
                )
            else:
                self._client = AsyncModbusTcpClient(
                    self._host,
                    port=self._port,
                    timeout=self._timeout,
                )
            await self._client.connect()
            self._connected = bool(self._client.connected)  # type: ignore[attr-defined]
            if not self._connected:
                raise ConnectionError("Unable to connect Modbus client")
            _LOGGER.debug("Connected to %s:%s (unit %s)", self._host, self._port, self._unit_id)

    async def close(self) -> None:
        async with self._lock:
            if self._client:
                with suppress(Exception):
                    await self._client.close()
            self._connected = False

    async def _reset_connection(self) -> None:
        """Close the client and mark it disconnected."""
        self._connected = False
        if self._client:
            with suppress(Exception):
                await self._client.close()
        self._client = None

    async def read_input_registers(self, address: int, count: int) -> ReadResult:
        max_attempts = 3
        last_exc: Exception | None = None

        for attempt in range(max_attempts):
            await self.ensure_connected()
            async with self._io_lock:  # keep transaction ids aligned and responses drained
                assert self._client is not None
                method = self._client.read_input_registers
                sig_exc: Exception | None = None
                attempts: list[tuple[str, dict[str, Any]]] = [
                    ("unit", {"unit": self._unit_id}),
                    ("slave", {"slave": self._unit_id}),
                    ("positional", {}),  # fallback: try without kw (some variants accept address,count,unit_id)
                ]

                try:
                    for mode, kw in attempts:
                        try:
                            if mode == "positional":
                                rr = await method(address=address, count=count)  # type: ignore[assignment]
                            else:
                                rr = await method(address=address, count=count, **kw)  # type: ignore[assignment]
                            break
                        except TypeError as exc:  # wrong signature
                            sig_exc = exc
                            continue
                    else:  # no break
                        if sig_exc:
                            raise sig_exc

                    if rr.isError():  # type: ignore[attr-defined]
                        raise ModbusIOException(f"Modbus read error @ {address} len {count}: {rr}")
                    if getattr(rr, "should_reconnect", False):  # pymodbus can signal reconnect necessity
                        raise ModbusIOException("Modbus response flagged reconnect")

                    return ReadResult(address=address, count=count, registers=rr.registers)  # type: ignore[attr-defined]
                except Exception as exc:
                    last_exc = exc

            await self._reset_connection()  # drop any buffered/extra data before retrying
            if attempt < max_attempts - 1:
                backoff = 0.2 * (attempt + 1)
                _LOGGER.debug(
                    "Retrying Modbus read @%s len %s after failure (%s), attempt %s/%s",
                    address,
                    count,
                    last_exc,
                    attempt + 1,
                    max_attempts,
                )
                await asyncio.sleep(backoff)

        raise ModbusIOException(
            f"Modbus read failed after {max_attempts} attempts @ {address} len {count}: {last_exc}"
        ) from last_exc
