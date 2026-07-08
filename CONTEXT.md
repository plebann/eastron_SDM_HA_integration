# Eastron SDM Integration

This context names the domain concepts for an Eastron SDM Home Assistant integration that polls meter registers over Modbus.

## Language

**Meter polling**:
The recurring collection of register values from an Eastron SDM meter according to configured tiers and options.
_Avoid_: Refresh loop, update cycle

**Read plan**:
A planned set of register reads for one meter polling pass, selected from the meter model, enabled categories, tier divisors, and current polling cycle.
_Avoid_: Batch helper, polling wrapper

**Register batch**:
A contiguous group of Modbus registers that can be read through one Modbus function during meter polling.
_Avoid_: Block, chunk
