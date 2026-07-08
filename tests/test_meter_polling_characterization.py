from custom_components.eastron_sdm.models import get_model_specs
from custom_components.eastron_sdm.models.base import RegisterSpec
from custom_components.eastron_sdm.read_plan import ReadPlanOptions, build_read_plan, build_register_batches
from custom_components.eastron_sdm.const import MODEL_SDM120M, MODEL_SDM630M


def _keys(specs):
    return [spec.key for spec in specs]


def _plan_keys(model, options=None, cycle=0):
    plan = build_read_plan(get_model_specs(model), options or ReadPlanOptions(), cycle)
    return [spec.key for batch in plan.batches for spec in batch.specs]


def test_read_plan_categories_are_excluded_until_enabled():
    default_keys = set(_plan_keys(MODEL_SDM120M))

    assert default_keys == {"voltage", "current", "active_power", "frequency", "import_active_energy"}

    all_enabled_keys = set(
        _plan_keys(
            MODEL_SDM120M,
            ReadPlanOptions(
                enable_advanced=True,
                enable_diagnostic=True,
                enable_two_way=True,
                enable_config=True,
            ),
        )
    )

    assert all_enabled_keys == {
        "voltage",
        "current",
        "active_power",
        "frequency",
        "apparent_power",
        "reactive_power",
        "power_factor",
        "import_active_energy",
        "export_active_energy",
        "total_active_energy",
        "network_parity_stop",
        "meter_id",
        "baud_rate",
        "serial_number",
        "meter_code",
        "software_version",
        "total_system_power_demand",
    }


def test_read_plan_sdm630m_default_polling_shape_differs_from_sdm120m():
    assert _plan_keys(MODEL_SDM120M) == ["voltage", "current", "active_power", "frequency", "import_active_energy"]

    assert _plan_keys(MODEL_SDM630M) == [
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
        "frequency",
        "total_import_active_energy",
        "total_active_energy",
    ]


def test_read_plan_advances_cycle_and_selects_tiers_for_the_current_pass():
    options = ReadPlanOptions(normal_divisor=2, slow_divisor=5)

    first_plan = build_read_plan(get_model_specs(MODEL_SDM120M), options, cycle=0)
    fast_only_plan = build_read_plan(get_model_specs(MODEL_SDM120M), options, cycle=1)
    normal_plan = build_read_plan(get_model_specs(MODEL_SDM120M), options, cycle=2)
    slow_plan = build_read_plan(get_model_specs(MODEL_SDM120M), options, cycle=5)

    assert [spec.key for batch in first_plan.batches for spec in batch.specs] == [
        "voltage",
        "current",
        "active_power",
        "frequency",
        "import_active_energy",
    ]
    assert [spec.key for batch in fast_only_plan.batches for spec in batch.specs] == [
        "voltage",
        "current",
        "active_power",
    ]
    assert [spec.key for batch in normal_plan.batches for spec in batch.specs] == [
        "voltage",
        "current",
        "active_power",
        "frequency",
    ]
    assert [spec.key for batch in slow_plan.batches for spec in batch.specs] == [
        "voltage",
        "current",
        "active_power",
        "import_active_energy",
    ]
    assert first_plan.next_cycle == 1
    assert build_read_plan(get_model_specs(MODEL_SDM120M), options, cycle=9).next_cycle == 0


def test_register_batches_are_sorted_by_function_then_address_and_merge_only_contiguous_or_overlapping_specs():
    specs = [
        RegisterSpec("input_gap_start", 0, 2, "input", "uint16", None, None, None, "basic", "fast", True),
        RegisterSpec("holding_first", 20, 2, "holding", "uint16", None, None, None, "config", "slow", False),
        RegisterSpec("input_gap_after", 8, 2, "input", "uint16", None, None, None, "basic", "fast", True),
        RegisterSpec("input_contiguous", 2, 2, "input", "uint16", None, None, None, "basic", "fast", True),
        RegisterSpec("holding_contiguous", 22, 1, "holding", "uint16", None, None, None, "config", "slow", False),
        RegisterSpec("input_overlap", 9, 2, "input", "uint16", None, None, None, "basic", "fast", True),
    ]

    batches = build_register_batches(specs)

    assert [(batch.function, batch.start, batch.length, _keys(batch.specs)) for batch in batches] == [
        ("holding", 20, 3, ["holding_first", "holding_contiguous"]),
        ("input", 0, 4, ["input_gap_start", "input_contiguous"]),
        ("input", 8, 3, ["input_gap_after", "input_overlap"]),
    ]
