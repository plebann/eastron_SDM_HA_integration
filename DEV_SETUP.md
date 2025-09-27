# Development Setup Guide

## Prerequisites
- Docker Desktop
- VS Code with Dev Containers extension
- Git

## Setup Steps

1. **Clone Home Assistant Core**:
```bash
git clone https://github.com/home-assistant/core.git ha-core
cd ha-core
```

2. **Copy your integration**:
```bash
cp -r /path/to/eastron_SDM_HA_integration/custom_components/eastron_sdm config/custom_components/
```

3. **Open in VS Code**:
- Open the `ha-core` folder in VS Code
- When prompted, reopen in Dev Container
- This creates a full HA development environment

4. **Run Home Assistant**:
```bash
# Inside the container
python -m homeassistant --config config
```

Your integration will be available at `http://localhost:8123`

## Benefits
- Full HA environment with all dependencies
- Debugger support
- Real-time code changes
- Access to HA logs and development tools