# Translations and IDs
- Set `_attr_translation_key` on entities and provide names under `entity.sensor` (or platform) in translations JSON to avoid generic labels.
- Prefer stable unique_id/device identifiers not tied to mutable unit_id; use meter serial where available. If unit_id must be used, migrate carefully to avoid duplicate devices.
- Keep `_attr_has_entity_name=True`; avoid hardcoded names in code.
