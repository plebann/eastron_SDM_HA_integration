# Base Entity Patterns
- Common base: sets `_attr_has_entity_name=True`, `_attr_translation_key`, device_info, availability via coordinator.last_update_success and cached data presence.
- Platform base: add platform mixin (SensorEntity, BinarySensorEntity, etc.) and helper methods (value extraction, precision, state_class setup).
- Category base: shared unit/icon/state_class for similar sensors (e.g., stats/energy/diagnostic) to trim concrete classes.
