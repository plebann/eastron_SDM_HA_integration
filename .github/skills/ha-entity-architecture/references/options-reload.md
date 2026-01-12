# Options Reload
- In async_setup_entry: register `entry.async_on_unload(entry.add_update_listener(async_update_options))`.
- async_update_options: sync registry enablement if needed, then `await hass.config_entries.async_reload(entry.entry_id)`.
- Coordinator should read options on init and after reload to refresh intervals/flags.
