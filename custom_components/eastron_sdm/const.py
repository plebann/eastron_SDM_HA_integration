"""Constants for Eastron SDM integration."""
from __future__ import annotations

DOMAIN = "eastron_sdm"
VERSION = "0.1.0"

DEFAULT_SCAN_INTERVAL = 10  # seconds
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 3600
DEFAULT_NORMAL_DIVISOR = 3   # every 3 base cycles
DEFAULT_SLOW_DIVISOR = 30    # every 30 base cycles
MAX_DIVISOR = 3600

CONF_HOST = "host"
CONF_PORT = "port"
CONF_UNIT_ID = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ENABLE_ADVANCED = "enable_advanced"
CONF_ENABLE_DIAGNOSTIC = "enable_diagnostic"
CONF_NORMAL_DIVISOR = "normal_divisor"
CONF_SLOW_DIVISOR = "slow_divisor"
CONF_DEBUG = "debug"

ATTR_LAST_UPDATE = "last_update"
