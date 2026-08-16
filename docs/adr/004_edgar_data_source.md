# ADR-004: EDGAR API as source of truth for SEC financial statements

- **Status:** Accepted
- **Date:** 2026-08-16

## Decision

SEC statement information will preferentially be pulled from EDGAR over Sugra,
and revert back to 3-layer medallion architecture.

## Context

In the previous ADR, I stated that Sugra's API was producing cleaner data than
expected, and as a result I would reduce the number of medallion layers to two.
This was premature, as it turns out that Sugra only pulls revenue data with the
XBRL tag "Revenues". This is only used by a minority of companies, and to get a
more complete accounting of revenue and other financial metrics, Sugra is
probably not up to the task. There is also the matter of inconsistent reporting
periods and changes in SEC requirements across different dates, making EDGAR a
necessary choice for the greater detail it provides.

## Consequences

- **Positive:** Actually get reliable financial data.
- **Negative:** Reversing work from last time to simplify medallions, and need
  new Prefect tasks to handle EDGAR data structure.

## Notes:
Supercedes [ADR-003](./003_simplify_transformation_layers.md).
