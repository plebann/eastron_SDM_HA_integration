---
name: ha-translations-and-ids
description: Home Assistant translation_key and identifier practices—entity/device naming via translations, stable unique IDs, and migration tips.
license: Complete terms in LICENSE.txt
---

# HA Translations & IDs

Use when fixing names/IDs in a custom component.

## Quick start
- Set `_attr_translation_key` and `_attr_has_entity_name=True`; keep code names minimal.
- Provide names under `entity.<platform>.<translation_key>.name` in translations JSON.
- Keep unique_ids stable; prefer device serial/model over mutable unit_id.
- Device identifiers should not change across reloads; plan migrations if format changes.

## References
- [references/translations-json.md](references/translations-json.md)
- [references/ids-and-migrations.md](references/ids-and-migrations.md)
