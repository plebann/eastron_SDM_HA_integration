# IDs and Migrations
- Choose stable unique_id inputs (serial/model) to survive unit_id changes; avoid host/port where possible.
- If changing unique_id format, add migration to update entity registry entries; avoid creating duplicate devices.
- Device identifiers should be consistent; changing identifiers creates new devices. Migrate rather than replace when feasible.
