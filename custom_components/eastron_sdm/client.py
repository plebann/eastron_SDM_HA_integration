"""Per-meter Modbus client sending requests through a shared endpoint."""
from __future__ import annotations

from dataclasses import dataclass

from pymodbus.exceptions import ModbusIOException

from .endpoint import ModbusEndpoint

@dataclass(slots=True)
class ReadResult:
    address: int
    count: int
    registers: list[int]

class SdmModbusClient:
    """Reads and writes registers of one Unit ID over a Modbus endpoint shared with other meters."""

    def __init__(self, endpoint: ModbusEndpoint, unit_id: int) -> None:
        self._endpoint = endpoint
        self._unit_id = unit_id

    def set_unit_id(self, unit_id: int) -> None:
        """Address subsequent requests to a different Unit ID; the shared connection is untouched."""
        self._unit_id = unit_id

    def _current_unit_id(self) -> int:
        # Resolved by the endpoint once it holds the lock, so a queued request follows a Unit ID change.
        return self._unit_id

    async def read_input_registers(self, address: int, count: int) -> ReadResult:
        return await self._read_registers("read_input_registers", address, count)

    async def read_holding_registers(self, address: int, count: int) -> ReadResult:
        return await self._read_registers("read_holding_registers", address, count)

    async def write_holding_register(self, address: int, value: int) -> None:
        await self._write_registers("write_register", address, [value])

    async def write_holding_registers(self, address: int, values: list[int]) -> None:
        await self._write_registers("write_registers", address, values)

    async def _read_registers(self, method_name: str, address: int, count: int) -> ReadResult:
        rr = await self._endpoint.request(method_name, self._current_unit_id, address=address, count=count)
        if rr.isError():  # type: ignore[attr-defined]
            raise ModbusIOException(f"Modbus read error @ {address} len {count}: {rr}")
        return ReadResult(address=address, count=count, registers=rr.registers)  # type: ignore[attr-defined]

    async def _write_registers(self, method_name: str, address: int, values: list[int]) -> None:
        if not values:
            raise ValueError("No values provided for write")
        if method_name == "write_register":
            rr = await self._endpoint.request(method_name, self._current_unit_id, address=address, value=values[0])
        else:
            rr = await self._endpoint.request(method_name, self._current_unit_id, address=address, values=values)
        if rr.isError():  # type: ignore[attr-defined]
            raise ModbusIOException(f"Modbus write error @ {address} len {len(values)}: {rr}")
