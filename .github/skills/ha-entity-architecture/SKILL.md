---
name: ha-entity-architecture
description: Layered Home Assistant custom entity architecture—CoordinatorEntity bases, platform/category bases, registry-only platform files, translation-backed naming, stable IDs, and options reload wiring.
license: Complete terms in LICENSE.txt
---

# HA Entity Architecture

Use when organizing entities for a custom component.

## Quick start
- Create shared base (CoordinatorEntity) for device_info/availability/data helpers.
- Add platform bases (sensor/binary_sensor/etc.) and optional category bases.
- Keep platform files as registries; concrete entities live in grouped modules.
- Set `_attr_has_entity_name=True` and `_attr_translation_key` for localization; avoid hardcoded names.
- Register options update listener to reload on change.

## References
- [references/layers-and-files.md](references/layers-and-files.md)
- [references/base-entity-patterns.md](references/base-entity-patterns.md)
- [references/options-reload.md](references/options-reload.md)
- [references/ids-and-uniqueness.md](references/ids-and-uniqueness.md)
