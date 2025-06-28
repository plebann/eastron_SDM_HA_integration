"""Configuration test data sets for Eastron SDM integration."""

# Valid configurations
VALID_CONFIGS = [
    {
        "host": "192.168.1.100",
        "port": 4196,
        "unit_id": 1,
        "name": "SDM120 Living Room",
        "model": "sdm120",
    },
    {
        "host": "192.168.1.101",
        "port": 4196,
        "unit_id": 2,
        "name": "SDM630 Main Panel",
        "model": "sdm630",
    },
]

# Invalid configurations
INVALID_CONFIGS = [
    # Missing host
    {
        "port": 4196,
        "unit_id": 1,
        "name": "No Host",
        "model": "sdm120",
    },
    # Invalid port
    {
        "host": "192.168.1.102",
        "port": "not_a_port",
        "unit_id": 1,
        "name": "Bad Port",
        "model": "sdm120",
    },
    # Invalid unit_id
    {
        "host": "192.168.1.103",
        "port": 4196,
        "unit_id": -1,
        "name": "Bad Unit",
        "model": "sdm120",
    },
    # Name with special characters
    {
        "host": "192.168.1.104",
        "port": 4196,
        "unit_id": 1,
        "name": "Bad@Name!",
        "model": "sdm120",
    },
    # Unsupported model
    {
        "host": "192.168.1.105",
        "port": 4196,
        "unit_id": 1,
        "name": "Unknown Model",
        "model": "sdm999",
    },
]
