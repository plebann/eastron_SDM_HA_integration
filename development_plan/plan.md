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
- [ ] Implement base `SDMDevice` class with common functionality
- [ ] Create `SDM120RegisterMap` class with register definitions
- [ ] Create `SDM630RegisterMap` class with register definitions
- [ ] Implement register scaling and unit conversion logic
- [ ] Add device detection mechanism via register reads

### Configuration Flow (Basic)
- [ ] Implement `ConfigFlow` class structure
- [ ] Create connection validation step (IP, port, unit_id)
- [ ] Add device detection and model identification
- [ ] Implement device naming input with validation
- [ ] Add basic error handling and user feedback

### Data Coordinator
- [ ] Implement `SDMDataUpdateCoordinator` base class
- [ ] Create Modbus TCP connection management
- [ ] Implement batch register reading for efficiency
- [ ] Add connection error handling and retry logic
- [ ] Create data parsing and validation methods

## Phase 2: Basic Sensors & Single Device

### Sensor Platform Implementation
- [ ] Create `sensor.py` with platform setup
- [ ] Implement basic voltage sensors (L1, L2, L3)
- [ ] Implement basic current sensors (L1, L2, L3)
- [ ] Implement basic power sensor (L1, L2, L3)
- [ ] Implement basic total power sensor
- [ ] Add frequency sensor
- [ ] Add total energy import/export sensors

### Entity Configuration
- [ ] Set proper device classes for each sensor type
- [ ] Configure state classes for energy dashboard integration
- [ ] Implement proper unit of measurement assignment
- [ ] Add entity naming with user-defined device prefix
- [ ] Set default enabled/disabled states per category

### Device Registry Integration
- [ ] Implement device info creation
- [ ] Add model identification (SDM120/SDM630)
- [ ] Create unique device identifiers
- [ ] Add manufacturer and firmware information display

## Phase 3: Advanced Features & Multi-Device

### Advanced Sensors
- [ ] Implement power sensors (active, reactive, apparent)
- [ ] Add power factor sensors
- [ ] Implement THD sensors (voltage and current)
- [ ] Add phase angle measurements
- [ ] Create demand measurement sensors

### Multi-Device Support
- [ ] Extend config flow for multiple device entries
- [ ] Implement device-specific coordinators
- [ ] Add device conflict detection (same IP/unit_id)
- [ ] Create device management UI options
- [ ] Test multiple device scenarios

### Polling Optimization
- [ ] Implement multi-tier polling system (fast/normal/slow)
- [ ] Create configurable polling intervals in config flow
- [ ] Add polling group assignment for different entity types
- [ ] Implement efficient coordinator scheduling
- [ ] Add polling statistics and diagnostics

## Phase 4: Diagnostic Features & Control

### Number Entities
- [ ] Create `number.py` platform
- [ ] Implement baud rate configuration entity
- [ ] Add parity setting configuration
- [ ] Implement stop bits configuration
- [ ] Add input validation and range checking

### Button Entities
- [ ] Create `button.py` platform
- [ ] Implement energy counter reset button
- [ ] Add demand values reset button
- [ ] Create confirmation dialog system
- [ ] Set diagnostic entities as disabled by default

### Select Entities (if needed)
- [ ] Create `select.py` platform for enumerated settings
- [ ] Implement communication parameter selections
- [ ] Add proper option validation

## Phase 5: User Experience & Polish

### Configuration Flow Enhancement
- [ ] Add entity category selection checkboxes
- [ ] Implement polling interval customization
- [ ] Add configuration validation and testing
- [ ] Create setup progress indicators
- [ ] Implement configuration import/export

### Error Handling & Diagnostics
- [ ] Implement comprehensive error logging
- [ ] Add user-friendly error messages
- [ ] Create connection status indicators
- [ ] Add diagnostic information display
- [ ] Implement automatic recovery mechanisms

### Translations & Documentation
- [ ] Create `translations/en.json` with all UI strings
- [ ] Add comprehensive inline code documentation
- [ ] Create user documentation and examples
- [ ] Add troubleshooting guide
- [ ] Create configuration examples

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
