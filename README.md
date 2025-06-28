# eastron_SDM_HA_integration

## Installation

### Prerequisites
- Home Assistant Core 2024.1.0 or newer
- Python 3.11 or newer
- `pymodbus` (installed automatically)

### Manual Installation
1. Download or clone this repository.
2. Copy the `custom_components/eastron_sdm` folder into your Home Assistant `custom_components` directory.
3. Restart Home Assistant.
4. Add the "Eastron SDM Energy Meter" integration via the Home Assistant UI.

### HACS Installation (when available)
1. Add this repository as a custom repository in HACS.
2. Install the "Eastron SDM Energy Meter" integration from HACS.
3. Restart Home Assistant.

See documentation for configuration and usage details.

## Version Control & Branching Strategy

- **main**: Stable, production-ready code. All releases are tagged from this branch.
- **develop**: Ongoing development and integration. All feature and bugfix branches are merged here first.
- **feature/\*** or **bugfix/\***: Short-lived branches for new features or fixes. Merge into develop when complete.

Always create pull requests for merging changes. Keep main branch deployable at all times.
