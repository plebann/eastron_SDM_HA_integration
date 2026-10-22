# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Fixed
- Meters sharing a host and port now share one Modbus TCP connection, and all reads and writes through it are serialized, so a TCP-to-RS485 gateway no longer returns one meter's reply to another meter's request

### Changed
- Modbus TCP framing is always used; the RTU framer preference never applied with pymodbus 3.11 and is removed
- Adding or editing a meter is rejected when another entry already uses the same Unit ID on that host and port
- Writing a meter's Unit ID is refused when another entry on the same host and port already uses it

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
