# Eastron SDM Energy Meter Integration - Development Plan

## Project Overview
Custom Home Assistant integration for Eastron SDM120/SDM630 energy meters via Modbus TCP.

## Phase 1: Foundation & Core Integration

### Repository Setup
- [x] Create HACS-compatible repository structure
- [x] Set up `manifest.json` with proper dependencies (pymodbus, homeassistant)
- [x] Create initial `__init__.py` with integration entry points
- [x] Set up version control and branching strategy
- [x] Create README.md with installation instructions

### Register Documentation Analysis
- [x] Read and analyze SDM120 PDF documentation for complete register map ('docs/SDM120-MODBUS_Protocol.pdf')
- [x] Read and analyze SDM630 PDF documentation for complete register map ('docs/SDM630_MODBUS_Protocol.pdf')
- [x] Create comprehensive register inventory with categories (Basic/Advanced/Diagnostic)
- [x] Document register addresses, data types, scaling factors, and units
- [x] Identify read-only vs read-write registers
- [x] Map registers to appropriate Home Assistant entity types (sensor/number/button/select)
- [x] Create register priority matrix based on user value and update frequency
- [x] Document any special handling requirements (bit fields, enums, calculations)
- [x] Validate register maps against actual device capabilities
- [x] Create `docs/registers-sdm120.md` and `docs/registers-sdm630.md` reference files

### Device Model Framework
- [x] Implement base `SDMDevice` class with common functionality
- [x] Create `SDM120RegisterMap` class with register definitions
- [x] Create `SDM630RegisterMap` class with register definitions
- [x] Implement register scaling and unit conversion logic
- [x] Add device detection mechanism via register reads

### Configuration Flow (Basic)
- [x] Implement `ConfigFlow` class structure
- [x] Create connection validation step (IP, port, unit_id)
- [x] Add device detection and model identification
- [x] Implement device naming input with validation
- [x] Add basic error handling and user feedback

### Data Coordinator
- [x] Implement `SDMDataUpdateCoordinator` base class
- [x] Create Modbus TCP connection management
- [x] Implement batch register reading for efficiency
- [x] Add connection error handling and retry logic
- [x] Create data parsing and validation methods

## Phase 2: Basic Sensors & Single Device

### Sensor Platform Implementation
- [x] Create `sensor.py` with platform setup
- [x] Read informations from RegistryMap 'device-models.py' for given type

### Numbers Platform Implementation
- [x] Create `number.py` with platform setup
- [x] Read informations from RegistryMap 'device-models.py' for given type

### Selects Platform Implementation
- [x] Create `select.py` with platform setup
- [x] Read informations from RegistryMap 'device-models.py' for given type

### Buttons Platform Implementation
- [x] Create `button.py` with platform setup
- [x] Read informations from RegistryMap 'device-models.py' for given type

### Entity Configuration
- [x] Set proper device classes for each sensor, number, select and button type
- [x] Configure state classes for energy dashboard integration
- [x] Implement proper unit of measurement assignment
- [x] Add entity naming with user-defined device prefix
- [x] Set default enabled/disabled states per category

### Device Registry Integration
- [x] Implement device info creation
- [x] Add model identification (SDM120/SDM630)
- [x] Create unique device identifiers
- [x] Add manufacturer and firmware information display

## Phase 3: Advanced Features & Multi-Device

### Multi-Device Support
- [x] Extend config flow for multiple device entries
- [x] Implement device-specific coordinators
- [x] Add device conflict detection (same IP/unit_id)
- [x] Create device management UI options
- [x] Test multiple device scenarios

### Polling Optimization
- [x] Implement multi-tier polling system (fast/normal/slow)
- [x] Create configurable polling intervals in config flow
- [x] Add polling group assignment for different entity types
- [x] Implement efficient coordinator scheduling
- [x] Add polling statistics and diagnostics

## Phase 4: Diagnostic Features & Control

### Number Entities
- [x] Create `number.py` platform
- [x] Implement baud rate configuration entity
- [x] Add parity setting configuration
- [x] Implement stop bits configuration
- [x] Add input validation and range checking

### Button Entities
- [x] Create `button.py` platform
- [x] Implement energy counter reset button
- [x] Add demand values reset button
- [x] Create confirmation dialog system
- [x] Set diagnostic entities as disabled by default

### Select Entities (if needed)
- [x] Create `select.py` platform for enumerated settings
- [x] Implement communication parameter selections
- [x] Add proper option validation

## Phase 5: User Experience & Polish

### Configuration Flow Enhancement
- [x] Add entity category selection checkboxes
- [x] Implement polling interval customization
- [x] Add configuration validation and testing
- [x] Create setup progress indicators
- [x] Implement configuration import/export

### Error Handling & Diagnostics
- [x] Implement comprehensive error logging
- [x] Add user-friendly error messages
- [x] Create connection status indicators
- [x] Add diagnostic information display
- [x] Implement automatic recovery mechanisms

### Translations & Documentation
- [x] Create `translations/en.json` with all UI strings
- [x] Add comprehensive inline code documentation
- [x] Create user documentation and examples
- [x] Add troubleshooting guide
- [x] Create configuration examples

## Phase 6: Testing & HACS Preparation

### Testing Framework
- [ ] Create unit tests for device models
- [ ] Add integration tests for coordinator
- [ ] Test multi-device scenarios
- [ ] Perform error condition testing
- [ ] Create automated test suite

### HACS Compatibility
- [ ] Create `hacs.json` configuration file
- [ ] Ensure proper versioning and releases
- [ ] Add integration to HACS store
- [ ] Create installation and update documentation
- [ ] Test HACS installation process

### Performance Optimization
- [ ] Profile and optimize register reading efficiency
- [ ] Minimize entity update frequency
- [ ] Optimize memory usage
- [ ] Test with multiple concurrent devices
- [ ] Benchmark against HA Modbus integration

## Phase 7: Release & Maintenance

### Release Preparation
- [ ] Create comprehensive changelog
- [ ] Tag stable release version
- [ ] Create release notes and documentation
- [ ] Submit to HACS default repository
- [ ] Announce release to community

### Post-Release Support
- [ ] Monitor issue reports and feedback
- [ ] Create bug fix and enhancement backlog
- [ ] Plan future feature additions
- [ ] Maintain compatibility with HA updates
- [ ] Build community support resources

## Dependencies & Prerequisites

### Required Skills/Knowledge
- Home Assistant integration development
- Python async programming
- Modbus TCP protocol understanding
- HACS integration packaging

### Development Environment
- Home Assistant development setup
- SDM120/SDM630 test meters or simulator
- Modbus TCP testing tools
- Version control system (Git)

### External Dependencies
- `pymodbus` library for Modbus communication
- Home Assistant core >= 2024.1.0
- Python >= 3.11

## Success Criteria
- [ ] Integration passes Home Assistant quality checklist
- [ ] Successfully manages multiple meter devices
- [ ] Provides reliable real-time energy monitoring
- [ ] Maintains stable HACS compatibility
- [ ] Receives positive community feedback
