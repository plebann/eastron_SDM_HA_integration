# Eastron SDM Integration

This context names the domain concepts for an Eastron SDM Home Assistant integration that polls meter registers over Modbus.

## Language

**SDM630**:
The supported three-phase Eastron SDM630 Modbus meter model.
_Avoid_: SDM630M, SDM630Modbus as the user-facing domain term

**Meter model**:
The meter family selected when an integration entry is created. The model determines the register map and entity set and is not changed in options; choosing a different model means creating a new integration entry.
_Avoid_: Treating model selection as a polling option

**SDM630 register source**:
The manufacturer SDM630 Modbus protocol PDF is the authoritative register map for SDM630 support. Derived Markdown inventories are convenience documents and must be checked against the PDF.
_Avoid_: Treating generated or hand-maintained Markdown inventories as authoritative

**Unit ID**:
The Modbus unit address of a meter. Use Unit ID in user-facing language; `meter_id` may remain an internal implementation key only.
_Avoid_: Calling the Modbus address Meter ID in UI or documentation

**Meter polling**:
The recurring collection of register values from an Eastron SDM meter according to configured tiers and options.
_Avoid_: Refresh loop, update cycle

**Read plan**:
A planned set of register reads for one meter polling pass, selected from the meter model, enabled categories, tier divisors, and current polling cycle.
_Avoid_: Batch helper, polling wrapper

**Register batch**:
A contiguous group of Modbus registers that can be read through one Modbus function during meter polling.
_Avoid_: Block, chunk
