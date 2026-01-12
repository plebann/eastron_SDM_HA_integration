# Reload Listener
- In async_setup_entry: `entry.async_on_unload(entry.add_update_listener(async_update_options))`.
- async_update_options: perform any registry sync, then `await hass.config_entries.async_reload(entry.entry_id)`.
- Coordinator should re-read options on init to honor changes after reload.
