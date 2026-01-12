# Validation
- Enforce min scan interval; ensure divisors/order constraints (e.g., normal_divisor >=2, slow_divisor > normal_divisor).
- Clamp options to sane ranges; provide descriptive error reasons.
- Coerce numeric fields to int/float early; avoid silent defaults.
