from custom_components.eastron_sdm.models.sdm120 import get_register_specs


def test_default_specs_basic_included():
    specs = get_register_specs(
        enable_advanced=False,
        enable_diagnostic=False,
        enable_two_way=False,
        enable_config=False,
    )
    keys = {s.key for s in specs}
    assert {"voltage", "current", "active_power", "frequency", "import_active_energy"}.issubset(keys)
    assert "export_active_energy" not in keys
    assert "total_active_energy" not in keys
    assert "apparent_power" not in keys
    assert "total_system_power_demand" not in keys
    assert "serial_number" not in keys
    assert "meter_code" not in keys
    assert "software_version" not in keys


def test_advanced_included_when_enabled():
    specs = get_register_specs(
        enable_advanced=True,
        enable_diagnostic=False,
        enable_two_way=False,
        enable_config=False,
    )
    keys = {s.key for s in specs}
    assert "apparent_power" in keys
    assert "reactive_power" in keys
    assert "power_factor" in keys


def test_diagnostic_included_when_enabled():
    specs = get_register_specs(
        enable_advanced=False,
        enable_diagnostic=True,
        enable_two_way=False,
        enable_config=False,
    )
    keys = {s.key for s in specs}
    assert "total_system_power_demand" in keys
    assert "serial_number" in keys
    assert "meter_code" in keys
    assert "software_version" in keys


def test_two_way_included_when_enabled():
    specs = get_register_specs(
        enable_advanced=False,
        enable_diagnostic=False,
        enable_two_way=True,
        enable_config=False,
    )
    keys = {s.key for s in specs}
    assert "export_active_energy" in keys
    assert "total_active_energy" in keys


def test_config_included_when_enabled():
    specs = get_register_specs(
        enable_advanced=False,
        enable_diagnostic=False,
        enable_two_way=False,
        enable_config=True,
    )
    keys = {s.key for s in specs}
    assert {"network_parity_stop", "meter_id", "baud_rate", "time_of_scroll_display"}.issubset(keys)
