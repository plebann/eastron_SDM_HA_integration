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
        self._io_lock = asyncio.Lock()
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
            framer: Any | None = None
            with suppress(Exception):
                from pymodbus.framer import FramerType  # type: ignore

                framer = FramerType.RTU

            if framer is None:  # fallback for older pymodbus layouts
                with suppress(Exception):  # optional
                    try:
                        from pymodbus.framer.rtu_framer import ModbusRtuFramer as _Framer  # type: ignore
                    except Exception:  # pragma: no cover
                        from pymodbus.transaction import ModbusRtuFramer as _Framer  # type: ignore
                    framer = _Framer

            kwargs: dict[str, Any] = {
                "host": self._host,
                "port": self._port,
                "timeout": self._timeout,
            }
            if framer:
                kwargs["framer"] = framer

            self._client = AsyncModbusTcpClient(**kwargs)
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

    async def read_input_registers(self, address: int, count: int) -> ReadResult:
        async with self._io_lock:
            await self.ensure_connected()
            assert self._client is not None
            # Clear any partial frames to avoid "extra data" errors on the next request.
            with suppress(Exception):
                framer = getattr(getattr(self._client, "protocol", None), "framer", None)
                if framer:
                    framer.resetFrame()

            method = self._client.read_input_registers
            last_exc: Exception | None = None
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
                        last_exc = exc
                        continue
                else:  # no break
                    if last_exc:
                        raise last_exc
            except Exception:
                # Drop the connection so the next attempt starts from a clean state.
                self._connected = False
                with suppress(Exception):
                    await self._client.close()
                raise

            if rr.isError():  # type: ignore[attr-defined]
                raise ModbusIOException(f"Modbus read error @ {address} len {count}: {rr}")
            # rr.registers is a list[int]
            return ReadResult(address=address, count=count, registers=rr.registers)  # type: ignore[attr-defined]
