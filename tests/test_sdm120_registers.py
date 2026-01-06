from custom_components.eastron_sdm.models.sdm120 import get_register_specs


def test_all_specs_returned():
    specs = get_register_specs()
    keys = {s.key for s in specs}
    expected = {
        "voltage",
        "current",
        "active_power",
        "frequency",
        "import_active_energy",
        "export_active_energy",
        "total_active_energy",
        "apparent_power",
        "reactive_power",
        "power_factor",
        "network_parity_stop",
        "meter_id",
        "baud_rate",
        "time_of_scroll_display",
        "serial_number",
        "meter_code",
        "software_version",
        "total_system_power_demand",
    }
    assert keys == expected
