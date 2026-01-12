# Patterns
- ConfigFlow async_step_user: abort if existing entry; create entry with title/data; avoid recursion.
- OptionsFlow async_step_init -> async_step_user (or other steps) returning async_create_entry with options.
- Keep schemas small; reuse base schema for config/options when possible.
- For multi-device support, one entry per device is simpler than nested device lists.
