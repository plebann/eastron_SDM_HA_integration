# Resilience and Pacing
- Pacing: honor message_wait_milliseconds spacing between requests (e.g., 20–50 ms for RTU gateways). Keep a base scan interval; layer tiered polling (fast/normal/slow) instead of uniform reads.
- Fallback: on transient failures, return last good data to keep entities available; mark unavailable only after repeated failures.
- Buffer hygiene: for RTU-over-TCP gateways, reset/flush framer state before each transaction; reconnect on extra-data errors.
- Timeouts/retries: keep moderate timeout (~5s) and limited retries; log address/unit_id/function for diagnostics.
- Avoid contention: do not poll immediately after writes; let devices process changes.
