# Coordinator Tests
- Test _async_update_data happy path, error path with cached fallback, and repeated failures marking unavailable.
- Verify tiered polling logic (fast/normal/slow triggers) and batching decisions.
- Ensure options changes propagate to intervals/divisors after reload.
