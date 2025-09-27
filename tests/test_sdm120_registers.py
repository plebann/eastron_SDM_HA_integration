from custom_components.eastron_sdm.models.sdm120 import get_register_specs


def test_default_specs_basic_included():
    specs = get_register_specs(enable_advanced=False, enable_diagnostic=False)
    keys = {s.key for s in specs}
    assert {"voltage", "current", "active_power", "frequency", "import_active_energy", "total_active_energy"}.issubset(keys)
    assert "apparent_power" not in keys
    assert "total_system_power_demand" not in keys


def test_advanced_included_when_enabled():
    specs = get_register_specs(enable_advanced=True, enable_diagnostic=False)
    keys = {s.key for s in specs}
    assert "apparent_power" in keys
    assert "reactive_power" in keys
    assert "power_factor" in keys


def test_diagnostic_included_when_enabled():
    specs = get_register_specs(enable_advanced=False, enable_diagnostic=True)
    keys = {s.key for s in specs}
    assert "total_system_power_demand" in keys
