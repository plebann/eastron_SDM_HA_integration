# Registry Stability
- Assert unique_id format remains unchanged across reloads/migrations; migrate if format changes.
- Device identifiers should stay stable; avoid creating duplicate devices on option changes (e.g., unit_id updates).
- Check that translation_key names resolve (no generic labels from missing translations).
