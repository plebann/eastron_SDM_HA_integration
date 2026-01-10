"""Select platform for writable SDM config registers."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SdmCoordinator, DecodedValue, _encode_value
from .models.sdm120 import RegisterSpec, get_register_specs
from .shared_base import SdmBaseEntity

_OPTION_LABELS = {
    "baud_rate": {
        0: "2400",
        1: "4800",
        2: "9600",
        5: "1200",
    },
    "network_parity_stop": {
        0: "1 stop / no parity",
        1: "1 stop / even",
        2: "1 stop / odd",
        3: "2 stop / no parity",
    },
}


class SdmConfigSelect(SdmBaseEntity, SelectEntity):
    """Writable select entity for SDM config registers."""

    _attr_should_poll = False
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry, spec: RegisterSpec) -> None:
        unique_id = f"eastron_sdm_{coordinator.host}_{coordinator.unit_id}_{spec.key}"
        # Suggest object_id to avoid "none" suffix if translations are late
        self._attr_suggested_object_id = spec.key
        super().__init__(coordinator, entry, unique_id=unique_id, translation_key=spec.key)
        self._spec = spec
        self._attr_entity_registry_enabled_default = spec.enabled_default
        option_values = spec.options or ()

        label_map = _OPTION_LABELS.get(spec.key)
        if label_map:
            # Preserve original ordering from spec.options
            self._options = [label_map.get(v, str(v)) for v in option_values]
            self._value_from_label = {label_map.get(v, str(v)): v for v in option_values}
            self._label_from_value = {v: label_map.get(v, str(v)) for v in option_values}
        else:
            self._options = [str(v) for v in option_values]
            self._value_from_label = {str(v): v for v in option_values}
            self._label_from_value = {v: str(v) for v in option_values}

        self._attr_options = self._options

    def _current_value(self) -> float | int | None:
        data: dict[str, DecodedValue] = self.coordinator.data or {}
        dv: DecodedValue | None = data.get(self._spec.key)
        if not dv:
            return None
        return dv.value

    @property
    def current_option(self) -> str | None:
        val = self._current_value()
        if val is None:
            return None
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        return self._label_from_value.get(val)

    async def async_select_option(self, option: str) -> None:
        if option not in self._options:
            raise ValueError("Invalid option")
        raw_value = self._value_from_label.get(option)
        if raw_value is None:
            raise ValueError("Invalid option")
        encoded_value = _encode_value(self._spec, raw_value)
        await self.coordinator.async_write_register(self._spec, encoded_value, raw_value=raw_value)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SdmCoordinator = data["coordinator"]

    specs = get_register_specs()
    entities = [
        SdmConfigSelect(coordinator, entry, spec)
        for spec in specs
        if spec.category == "config" and spec.control == "select"
    ]
    if entities:
        async_add_entities(entities)
