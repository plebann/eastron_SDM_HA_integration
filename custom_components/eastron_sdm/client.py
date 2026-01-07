"""Async Modbus RTU-over-TCP client wrapper."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from dataclasses import dataclass

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

    async def read_input_registers(self, address: int, count: int) -> ReadResult:
        return await self._read_registers("read_input_registers", address, count)

    async def read_holding_registers(self, address: int, count: int) -> ReadResult:
        return await self._read_registers("read_holding_registers", address, count)

    async def write_holding_register(self, address: int, value: int) -> None:
        await self._write_registers("write_register", address, [value])

    async def write_holding_registers(self, address: int, values: list[int]) -> None:
        await self._write_registers("write_registers", address, values)

    async def _read_registers(self, method_name: str, address: int, count: int) -> ReadResult:
        async with self._io_lock:
            await self.ensure_connected()
            assert self._client is not None
            method = getattr(self._client, method_name)
            rr = await method(address=address, count=count, device_id=self._unit_id)
            if rr.isError():  # type: ignore[attr-defined]
                raise ModbusIOException(f"Modbus read error @ {address} len {count}: {rr}")
            return ReadResult(address=address, count=count, registers=rr.registers)  # type: ignore[attr-defined]

    async def _write_registers(self, method_name: str, address: int, values: list[int]) -> None:
        if not values:
            raise ValueError("No values provided for write")
        async with self._io_lock:
            await self.ensure_connected()
            assert self._client is not None
            method = getattr(self._client, method_name)
            if method_name == "write_register":
                rr = await method(address=address, value=values[0], device_id=self._unit_id)  # type: ignore[assignment]
            else:
                rr = await method(address=address, values=values, device_id=self._unit_id)  # type: ignore[assignment]
            if rr.isError():  # type: ignore[attr-defined]
                raise ModbusIOException(f"Modbus write error @ {address} len {len(values)}: {rr}")
