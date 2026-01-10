"""Number platform for writable SDM config registers."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SdmCoordinator, DecodedValue, _encode_value
from .models.sdm120 import RegisterSpec, get_register_specs
from .shared_base import SdmBaseEntity


class SdmConfigNumber(SdmBaseEntity, NumberEntity):
    """Writable number entity for SDM config registers."""

    _attr_should_poll = False
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.AUTO

    def __init__(self, coordinator: SdmCoordinator, entry: ConfigEntry, spec: RegisterSpec) -> None:
        unique_id = coordinator.build_unique_id(spec.key)
        # Suggest object_id to avoid "none" suffix if translations are late
        self._attr_suggested_object_id = spec.key
        super().__init__(coordinator, entry, unique_id=unique_id, translation_key=spec.key)
        self._spec = spec
        self._attr_entity_registry_enabled_default = spec.enabled_default
        self._attr_native_unit_of_measurement = spec.unit
        self._attr_native_min_value = spec.min_value
        self._attr_native_max_value = spec.max_value
        self._attr_native_step = spec.step
        self._attr_mode = spec.mode or NumberMode.AUTO

    def _current_value(self) -> float | int | None:
        data: dict[str, DecodedValue] = self.coordinator.data or {}
        dv: DecodedValue | None = data.get(self._spec.key)
        if not dv:
            return None
        return dv.value

    @property
    def native_value(self) -> float | int | None:  # type: ignore[override]
        return self._current_value()

    async def async_set_native_value(self, value: float) -> None:  # type: ignore[override]
        if self._spec.min_value is not None and value < self._spec.min_value:
            raise ValueError("Value below allowed minimum")
        if self._spec.max_value is not None and value > self._spec.max_value:
            raise ValueError("Value above allowed maximum")
        encoded_value = _encode_value(self._spec, value)
        await self.coordinator.async_write_register(self._spec, encoded_value, raw_value=value)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SdmCoordinator = data["coordinator"]

    specs = get_register_specs()
    entities = [
        SdmConfigNumber(coordinator, entry, spec)
        for spec in specs
        if spec.category == "config" and spec.control == "number"
    ]
    if entities:
        async_add_entities(entities)
