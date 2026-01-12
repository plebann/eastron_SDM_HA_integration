# Mitigations
- Pacing: add message_wait_milliseconds or small sleeps between requests; stagger tiers.
- Buffer hygiene: reset framer/buffer before each transaction; reconnect on extra-data or CRC mismatch.
- Addressing: ensure device_id correct; avoid deprecated unit/slave kwargs.
- Writes: choose FC16 for multi-register; encode float32/uint32 words in network order; avoid immediate refresh.
- Resilience: cache last good data; retry limited times; mark unavailable after threshold; backoff before reconnect.
