---
name: ha-config-flow-options
description: Home Assistant ConfigFlow/OptionsFlow patterns—single-instance guard, schema validation, reload listeners, safe options handling without recursion.
license: Complete terms in LICENSE.txt
---

# HA Config Flow & Options

Use when adding or fixing config/option flows.

## Quick start
- Guard single instance in `async_step_user` when appropriate.
- Validate inputs (interval mins, divisor ordering) with clear errors.
- Use standard OptionsFlow; do not override async_create_entry recursively.
- Register update listener in setup to reload platforms on option change.

## References
- [references/patterns.md](references/patterns.md)
- [references/validation.md](references/validation.md)
- [references/reload-listener.md](references/reload-listener.md)
