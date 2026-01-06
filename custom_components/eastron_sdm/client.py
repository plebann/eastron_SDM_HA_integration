"""Async Modbus TCP client with strict length reads."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from dataclasses import dataclass
from typing import Any

from pymodbus.exceptions import ModbusIOException

_LOGGER = logging.getLogger(__name__)

@dataclass(slots=True)
class ReadResult:
    address: int
    count: int
    registers: list[int]

class SdmModbusClient:
    """Wrapper managing a single Modbus TCP session with exact-length reads."""

    def __init__(self, host: str, port: int, unit_id: int, *, timeout: float = 5.0) -> None:
        self._host = host
        self._port = port
        self._unit_id = unit_id
        self._timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        self._io_lock = asyncio.Lock()
        self._connected = False
        self._tid = 0

    async def ensure_connected(self) -> None:
        async with self._lock:
            if self._connected and self._reader and self._writer:
                return
            # Close previous if any
            await self._close_stream()

            try:
                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(self._host, self._port), timeout=self._timeout
                )
            except Exception as exc:
                raise ConnectionError(f"Unable to connect Modbus client: {exc}") from exc

            self._connected = True
            _LOGGER.debug("Connected to %s:%s (unit %s)", self._host, self._port, self._unit_id)

    async def close(self) -> None:
        async with self._lock:
            await self._close_stream()
            self._connected = False

    async def read_input_registers(self, address: int, count: int) -> ReadResult:
        async with self._io_lock:
            await self.ensure_connected()
            assert self._reader is not None and self._writer is not None

            # Drain any stray bytes before issuing a new request.
            await self._drain_recv()

            # Build request ADU (MBAP + PDU) for FC04.
            self._tid = (self._tid + 1) & 0xFFFF
            pdu = self._build_read_input_pdu(address, count)
            adu = self._build_mbap(self._tid, pdu)

            try:
                await asyncio.wait_for(self._write(adu), timeout=self._timeout)
                header = await asyncio.wait_for(self._reader.readexactly(7), timeout=self._timeout)
                tid, pid, length, unit = self._parse_mbap(header)
                if tid != self._tid:
                    raise ModbusIOException(f"Transaction mismatch (expected {self._tid}, got {tid})")
                if unit != self._unit_id:
                    raise ModbusIOException(f"Unit mismatch (expected {self._unit_id}, got {unit})")
                if pid != 0:
                    raise ModbusIOException(f"Protocol id mismatch (expected 0, got {pid})")
                remaining = length - 1  # exclude unit id already read
                resp_pdu = await asyncio.wait_for(self._reader.readexactly(remaining), timeout=self._timeout)
                registers = self._parse_read_input_pdu(resp_pdu, count)
            except Exception as exc:
                await self._reset_connection()
                raise

            # Optionally flush any trailing bytes to keep the next transaction clean.
            await self._drain_recv()

            return ReadResult(address=address, count=count, registers=registers)

    async def _write(self, data: bytes) -> None:
        assert self._writer is not None
        self._writer.write(data)
        await self._writer.drain()

    def _build_mbap(self, tid: int, pdu: bytes) -> bytes:
        length = 1 + len(pdu)  # unit id + pdu
        return tid.to_bytes(2, "big") + b"\x00\x00" + length.to_bytes(2, "big") + bytes([self._unit_id]) + pdu

    @staticmethod
    def _build_read_input_pdu(address: int, count: int) -> bytes:
        return b"\x04" + address.to_bytes(2, "big") + count.to_bytes(2, "big")

    @staticmethod
    def _parse_mbap(header: bytes) -> tuple[int, int, int, int]:
        tid = int.from_bytes(header[0:2], "big")
        pid = int.from_bytes(header[2:4], "big")
        length = int.from_bytes(header[4:6], "big")
        unit = header[6]
        return tid, pid, length, unit

    @staticmethod
    def _parse_read_input_pdu(pdu: bytes, expected_count: int) -> list[int]:
        if not pdu:
            raise ModbusIOException("Empty PDU")
        function = pdu[0]
        if function & 0x80:
            code = pdu[1] if len(pdu) > 1 else None
            raise ModbusIOException(f"Modbus exception {code}")
        if function != 0x04:
            raise ModbusIOException(f"Unexpected function {function}")
        if len(pdu) < 2:
            raise ModbusIOException("Malformed response PDU")
        byte_count = pdu[1]
        expected_bytes = expected_count * 2
        if byte_count != expected_bytes:
            raise ModbusIOException(f"Unexpected byte count {byte_count} (expected {expected_bytes})")
        data = pdu[2: 2 + byte_count]
        if len(data) != expected_bytes:
            raise ModbusIOException("Incomplete register payload")
        return list(int.from_bytes(data[i:i + 2], "big") for i in range(0, expected_bytes, 2))

    async def _drain_recv(self) -> None:
        if not self._reader:
            return
        # Non-blocking drain of any buffered bytes.
        while True:
            try:
                chunk = await asyncio.wait_for(self._reader.read(1024), timeout=0.01)
            except asyncio.TimeoutError:
                break
            if not chunk:
                break

    async def _reset_connection(self) -> None:
        async with self._lock:
            await self._close_stream()
            self._connected = False

    async def _close_stream(self) -> None:
        if self._writer:
            with suppress(Exception):
                self._writer.close()
                await self._writer.wait_closed()
        self._reader = None
        self._writer = None
