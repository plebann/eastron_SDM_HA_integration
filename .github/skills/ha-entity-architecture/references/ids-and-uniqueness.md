# IDs and Uniqueness
- Keep unique_id stable; avoid embedding mutable unit_id if possible (prefer serial/model identifiers). If migration needed, plan registry update.
- device_info identifiers should group entities under one device; avoid changing identifiers on reload.
- Use translation_key for naming; do not bake names into code.
