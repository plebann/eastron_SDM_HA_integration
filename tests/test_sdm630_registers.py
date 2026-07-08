import json
from pathlib import Path

from custom_components.eastron_sdm.const import MODEL_SDM630M
from custom_components.eastron_sdm.models import get_model_specs
from custom_components.eastron_sdm.read_plan import ReadPlanOptions, build_read_plan


def _specs_by_key():
    return {spec.key: spec for spec in get_model_specs(MODEL_SDM630M)}


def test_sdm630_first_support_register_subset_is_pinned():
    specs = _specs_by_key()

    assert set(specs) == {
        "voltage_l1",
        "voltage_l2",
        "voltage_l3",
        "current_l1",
        "current_l2",
        "current_l3",
        "active_power_l1",
        "active_power_l2",
        "active_power_l3",
        "sum_line_currents",
        "total_system_power",
        "total_system_apparent_power",
        "total_system_reactive_power",
        "total_system_power_factor",
        "frequency",
        "total_import_active_energy",
        "total_export_active_energy",
        "total_import_reactive_energy",
        "total_export_reactive_energy",
        "total_apparent_energy",
        "total_system_power_demand",
        "max_total_system_power_demand",
        "total_system_va_demand",
        "neutral_current_demand",
        "max_neutral_current_demand",
        "neutral_current",
        "total_active_energy",
        "total_reactive_energy",
        "import_active_energy_l1",
        "import_active_energy_l2",
        "import_active_energy_l3",
        "export_active_energy_l1",
        "export_active_energy_l2",
        "export_active_energy_l3",
        "total_active_energy_l1",
        "total_active_energy_l2",
        "total_active_energy_l3",
        "serial_number",
        "network_parity_stop",
        "meter_id",
        "baud_rate",
    }

    assert specs["voltage_l1"].address == 0
    assert specs["voltage_l2"].address == 2
    assert specs["voltage_l3"].address == 4
    assert specs["total_system_power"].address == 52
    assert specs["frequency"].address == 70
    assert specs["total_import_active_energy"].address == 72
    assert specs["total_active_energy"].address == 342
    assert specs["serial_number"].address == 64513


def test_sdm630_config_controls_are_limited_to_unit_id_and_port_settings():
    specs = _specs_by_key()

    config_specs = {key: spec for key, spec in specs.items() if spec.category == "config"}

    assert set(config_specs) == {"network_parity_stop", "meter_id", "baud_rate"}
    assert config_specs["network_parity_stop"].control == "select"
    assert config_specs["network_parity_stop"].options == (0, 1, 2, 3)
    assert config_specs["meter_id"].control == "number"
    assert config_specs["meter_id"].min_value == 1
    assert config_specs["meter_id"].max_value == 247
    assert config_specs["baud_rate"].control == "select"
    assert config_specs["baud_rate"].options == (0, 1, 2, 3, 4)


def test_sdm630_read_plan_exposes_only_allowed_config_controls_when_config_enabled():
    plan = build_read_plan(
        get_model_specs(MODEL_SDM630M),
        ReadPlanOptions(enable_config=True),
        cycle=0,
    )

    config_keys = {
        spec.key
        for batch in plan.batches
        for spec in batch.specs
        if spec.category == "config"
    }

    assert config_keys == {"network_parity_stop", "meter_id", "baud_rate"}


def test_unit_id_is_the_user_facing_config_name():
    translations = json.loads(Path("custom_components/eastron_sdm/translations/en.json").read_text())

    assert translations["config"]["step"]["user"]["data"]["unit_id"] == "Unit ID"
    assert translations["entity"]["number"]["meter_id"]["name"] == "Unit ID"