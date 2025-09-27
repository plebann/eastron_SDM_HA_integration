# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-09-27
### Added
- Initial release with SDM120 support (read-only core + optional advanced / diagnostic sensors)
- Tiered polling (fast/normal/slow) with configurable divisors
- Async RTU-over-TCP Modbus client using pymodbus
- Dynamic sensor entity creation
- Options flow for enabling sensor groups & debug logging
- Batching of contiguous register reads
- Basic register spec tests

### Notes
- Energy export, reactive energy, and writable configuration registers deferred
- Future roadmap includes SDM630, reset services, diagnostics export
