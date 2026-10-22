import asyncio
from contextlib import suppress
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from homeassistant.const import CONF_NAME
from homeassistant.exceptions import HomeAssistantError

from custom_components.eastron_sdm import endpoint as endpoint_module
from custom_components.eastron_sdm.config_flow import ConfigFlow, OptionsFlowHandler
from custom_components.eastron_sdm.const import (
    CONF_HOST,
    CONF_MODEL,
    CONF_NORMAL_DIVISOR,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SLOW_DIVISOR,
    CONF_UNIT_ID,
    DOMAIN,
    MODEL_SDM120M,
)
from custom_components.eastron_sdm.coordinator import SdmCoordinator, _encode_value
from custom_components.eastron_sdm.endpoint import (
    async_acquire_endpoint,
    async_release_endpoint,
    find_unit_id_conflict,
)
from custom_components.eastron_sdm.models import get_spec_by_key


class FakeModbusTcpClient:
    """Stands in for AsyncModbusTcpClient and records overlapping requests."""

    instances: list["FakeModbusTcpClient"] = []
    in_flight_all = 0
    max_in_flight_all = 0

    def __init__(self, host, port=502, **kwargs):
        self.host = host
        self.port = port
        self.kwargs = kwargs
        self.connected = False
        self.closed = False
        self.in_flight = 0
        self.max_in_flight = 0
        self.calls: list[tuple[str, int]] = []
        FakeModbusTcpClient.instances.append(self)

    async def connect(self):
        self.connected = True
        return True

    def close(self):
        self.closed = True
        self.connected = False

    async def _respond(self, method_name, device_id, count=1):
        self.calls.append((method_name, device_id))
        self.in_flight += 1
        cls = FakeModbusTcpClient
        cls.in_flight_all += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        cls.max_in_flight_all = max(cls.max_in_flight_all, cls.in_flight_all)
        try:
            await asyncio.sleep(0.01)
        finally:
            self.in_flight -= 1
            cls.in_flight_all -= 1
        response = MagicMock()
        response.isError.return_value = False
        response.registers = [0] * count
        return response

    async def read_input_registers(self, address, count=1, device_id=1):
        return await self._respond("read_input_registers", device_id, count)

    async def read_holding_registers(self, address, count=1, device_id=1):
        return await self._respond("read_holding_registers", device_id, count)

    async def write_register(self, address, value, device_id=1):
        return await self._respond("write_register", device_id)

    async def write_registers(self, address, values, device_id=1):
        return await self._respond("write_registers", device_id)


@pytest.fixture(autouse=True)
def fake_pymodbus(monkeypatch):
    FakeModbusTcpClient.instances = []
    FakeModbusTcpClient.in_flight_all = 0
    FakeModbusTcpClient.max_in_flight_all = 0
    monkeypatch.setattr(endpoint_module, "AsyncModbusTcpClient", FakeModbusTcpClient)


def _fake_hass(entries=()):
    hass = MagicMock()
    hass.data = {}
    with suppress(RuntimeError):
        hass.loop = asyncio.get_running_loop()
    hass.config_entries.async_entries.return_value = list(entries)
    return hass


def _entry(entry_id, host, port, meter_unit, **options):
    return SimpleNamespace(
        entry_id=entry_id,
        data={CONF_HOST: host, CONF_PORT: port, CONF_UNIT_ID: meter_unit, CONF_MODEL: MODEL_SDM120M},
        options=options,
    )


def _coordinator(hass, entry):
    coordinator = SdmCoordinator(hass, entry)
    return coordinator


@pytest.mark.asyncio
async def test_coordinators_sharing_an_endpoint_serialize_concurrent_refreshes():
    entries = [_entry(f"entry{unit}", "gateway", 4196, unit) for unit in (5, 6, 7)]
    hass = _fake_hass(entries)
    coordinators = [_coordinator(hass, entry) for entry in entries]

    await asyncio.gather(*(coordinator._async_update_data() for coordinator in coordinators))

    assert len(FakeModbusTcpClient.instances) == 1
    client = FakeModbusTcpClient.instances[0]
    assert client.max_in_flight == 1
    assert {device_id for _, device_id in client.calls} == {5, 6, 7}


@pytest.mark.asyncio
async def test_writes_and_reads_through_one_endpoint_do_not_overlap():
    hass = _fake_hass()
    endpoint = async_acquire_endpoint(hass, "gateway", 4196)

    await asyncio.gather(
        endpoint.request("read_input_registers", 5, address=0, count=2),
        endpoint.request("write_register", 6, address=20, value=1),
        endpoint.request("write_registers", 7, address=20, values=[1, 2]),
        endpoint.request("read_holding_registers", 5, address=0, count=2),
    )

    assert FakeModbusTcpClient.instances[0].max_in_flight == 1


@pytest.mark.asyncio
async def test_different_endpoints_stay_independently_pollable():
    hass = _fake_hass()
    first = async_acquire_endpoint(hass, "gateway-a", 4196)
    second = async_acquire_endpoint(hass, "gateway-b", 4196)
    third = async_acquire_endpoint(hass, "gateway-a", 4197)

    await asyncio.gather(
        first.request("read_input_registers", 1, address=0, count=2),
        second.request("read_input_registers", 1, address=0, count=2),
        third.request("read_input_registers", 1, address=0, count=2),
    )

    assert first is not second and first is not third
    assert len(FakeModbusTcpClient.instances) == 3
    assert all(client.max_in_flight == 1 for client in FakeModbusTcpClient.instances)
    assert FakeModbusTcpClient.max_in_flight_all == 3


@pytest.mark.asyncio
async def test_endpoint_is_released_only_after_its_last_entry_unloads():
    entries = [_entry(f"entry{unit}", "gateway", 4196, unit) for unit in (5, 6, 7)]
    hass = _fake_hass(entries)
    coordinators = [_coordinator(hass, entry) for entry in entries]
    await asyncio.gather(*(coordinator._async_update_data() for coordinator in coordinators))
    client = FakeModbusTcpClient.instances[0]

    await coordinators[0].async_close()
    await coordinators[1].async_close()
    assert not client.closed

    await coordinators[2].async_close()
    assert client.closed
    assert not hass.data[f"{DOMAIN}_endpoints"]


@pytest.mark.asyncio
async def test_closing_a_coordinator_twice_releases_its_endpoint_once():
    hass = _fake_hass()
    first = _coordinator(hass, _entry("a", "gateway", 4196, 5))
    second = _coordinator(hass, _entry("b", "gateway", 4196, 6))
    await first._async_update_data()

    await first.async_close()
    await first.async_close()

    assert not FakeModbusTcpClient.instances[0].closed
    await second.async_close()
    assert FakeModbusTcpClient.instances[0].closed


@pytest.mark.asyncio
async def test_released_endpoint_reconnects_with_a_fresh_client_on_next_acquire():
    hass = _fake_hass()
    endpoint = async_acquire_endpoint(hass, "gateway", 4196)
    await endpoint.request("read_input_registers", 5, address=0, count=2)
    await async_release_endpoint(hass, endpoint)

    again = async_acquire_endpoint(hass, "gateway", 4196)
    await again.request("read_input_registers", 5, address=0, count=2)

    assert again is not endpoint
    assert len(FakeModbusTcpClient.instances) == 2


@pytest.mark.asyncio
async def test_endpoint_uses_default_tcp_framing():
    hass = _fake_hass()
    endpoint = async_acquire_endpoint(hass, "gateway", 4196)
    await endpoint.request("read_input_registers", 5, address=0, count=2)

    assert "framer" not in FakeModbusTcpClient.instances[0].kwargs


@pytest.mark.asyncio
async def test_changing_a_unit_id_keeps_the_shared_connection_open():
    hass = _fake_hass()
    coordinator = _coordinator(hass, _entry("a", "gateway", 4196, 5))
    await coordinator._async_update_data()
    client = FakeModbusTcpClient.instances[0]

    coordinator._client.set_unit_id(9)
    await coordinator._async_update_data()

    assert not client.closed
    assert len(FakeModbusTcpClient.instances) == 1
    assert client.calls[-1][1] == 9


def test_unit_id_conflict_matches_same_endpoint_and_unit_id():
    entries = [_entry("a", "Gateway", 4196, 5), _entry("b", "gateway", 4196, 6)]
    hass = _fake_hass(entries)

    assert find_unit_id_conflict(hass, "gateway", 4196, 5) is entries[0]
    assert find_unit_id_conflict(hass, "gateway", 4196, 7) is None
    assert find_unit_id_conflict(hass, "gateway", 4197, 5) is None
    assert find_unit_id_conflict(hass, "other", 4196, 5) is None


def test_unit_id_conflict_ignores_the_excluded_entry_and_prefers_options():
    entries = [_entry("a", "gateway", 4196, 5, unit_id=8)]
    hass = _fake_hass(entries)

    assert find_unit_id_conflict(hass, "gateway", 4196, 5) is None
    assert find_unit_id_conflict(hass, "gateway", 4196, 8) is entries[0]
    assert find_unit_id_conflict(hass, "gateway", 4196, 8, exclude_entry_id="a") is None


@pytest.mark.asyncio
async def test_meter_id_write_is_refused_when_another_entry_uses_the_unit_id_on_the_endpoint():
    entries = [_entry("a", "gateway", 4196, 5), _entry("b", "gateway", 4196, 6)]
    hass = _fake_hass(entries)
    coordinator = _coordinator(hass, entries[0])
    spec = get_spec_by_key(MODEL_SDM120M, "meter_id")

    with pytest.raises(HomeAssistantError):
        await coordinator.async_write_register(spec, _encode_value(spec, 6), raw_value=6)

    assert FakeModbusTcpClient.instances == []


@pytest.mark.asyncio
async def test_meter_id_write_to_a_free_unit_id_reaches_the_meter():
    entries = [_entry("a", "gateway", 4196, 5), _entry("b", "gateway", 4196, 6)]
    hass = _fake_hass(entries)
    coordinator = _coordinator(hass, entries[0])
    spec = get_spec_by_key(MODEL_SDM120M, "meter_id")

    await coordinator.async_write_register(spec, _encode_value(spec, 8), raw_value=8)

    assert ("write_registers", 5) in FakeModbusTcpClient.instances[0].calls


def _config_flow(hass):
    flow = ConfigFlow()
    flow.hass = hass
    return flow


def _user_input(host, port, unit_id):
    return {
        CONF_NAME: "Meter",
        CONF_HOST: host,
        CONF_PORT: port,
        CONF_UNIT_ID: unit_id,
        CONF_MODEL: MODEL_SDM120M,
        CONF_SCAN_INTERVAL: 10,
        CONF_NORMAL_DIVISOR: 3,
        CONF_SLOW_DIVISOR: 30,
    }


@pytest.mark.asyncio
async def test_user_flow_rejects_a_unit_id_already_used_on_the_endpoint():
    hass = _fake_hass([_entry("a", "gateway", 4196, 5)])

    result = await _config_flow(hass).async_step_user(_user_input("gateway", 4196, 5))

    assert result["type"] == "form"
    assert result["errors"] == {CONF_UNIT_ID: "unit_id_in_use"}


def _options_input(host, port, unit_id):
    return {
        CONF_HOST: host,
        CONF_PORT: port,
        CONF_UNIT_ID: unit_id,
        CONF_SCAN_INTERVAL: 10,
        CONF_NORMAL_DIVISOR: 3,
        CONF_SLOW_DIVISOR: 30,
    }


def _options_flow(hass, entry):
    flow = OptionsFlowHandler(entry)
    flow.hass = hass
    return flow


@pytest.mark.asyncio
async def test_options_flow_rejects_moving_an_entry_onto_a_used_unit_id():
    entries = [_entry("a", "gateway", 4196, 5), _entry("b", "gateway", 4196, 6)]
    hass = _fake_hass(entries)

    result = await _options_flow(hass, entries[1]).async_step_init(_options_input("gateway", 4196, 5))

    assert result["type"] == "form"
    assert result["errors"] == {CONF_UNIT_ID: "unit_id_in_use"}


@pytest.mark.asyncio
async def test_options_flow_keeps_a_legacy_duplicate_editable_while_its_address_is_unchanged():
    entries = [_entry("a", "gateway", 4196, 5), _entry("b", "gateway", 4196, 5)]
    hass = _fake_hass(entries)

    result = await _options_flow(hass, entries[1]).async_step_init(_options_input("gateway", 4196, 5))

    assert result["type"] == "create_entry"
