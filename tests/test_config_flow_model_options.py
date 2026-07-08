from custom_components.eastron_sdm.config_flow import _build_options_schema
from custom_components.eastron_sdm.const import CONF_MODEL, CONF_SCAN_INTERVAL


def test_meter_model_is_not_an_options_flow_setting():
    schema = _build_options_schema({})
    option_keys = {str(key.schema) for key in schema.schema}

    assert CONF_MODEL not in option_keys
    assert CONF_SCAN_INTERVAL in option_keys