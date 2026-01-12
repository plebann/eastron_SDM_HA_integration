# Layers and Files
- shared_base.py: CoordinatorEntity subclass with device_info, availability, data helpers.
- Platform bases (sensors/base.py, binary_sensors/base.py): platform-specific helpers.
- Category/group modules: e.g., sensors/measurements.py, sensors/energy.py, sensors/diagnostic.py.
- Platform files (sensor.py etc.): registry/instantiation only; no business logic.
- __init__.py per group to export entities cleanly.
