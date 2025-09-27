"""Async Modbus RTU-over-TCP client wrapper."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from dataclasses import dataclass
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.framer.rtu_framer import ModbusRtuFramer
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
        self._connected = False

    async def ensure_connected(self) -> None:
        async with self._lock:
            if self._connected and self._client and self._client.connected:  # type: ignore[attr-defined]
                return
            # Close previous if any
            if self._client:
                with suppress(Exception):
                    await self._client.close()
            self._client = AsyncModbusTcpClient(
                self._host,
                port=self._port,
                timeout=self._timeout,
                framer=ModbusRtuFramer,
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

    async def read_input_registers(self, address: int, count: int) -> ReadResult:
        await self.ensure_connected()
        assert self._client is not None
        rr = await self._client.read_input_registers(address=address, count=count, unit=self._unit_id)
        if rr.isError():  # type: ignore[attr-defined]
            raise ModbusIOException(f"Modbus read error @ {address} len {count}: {rr}")
        # rr.registers is a list[int]
        return ReadResult(address=address, count=count, registers=rr.registers)  # type: ignore[attr-defined]
