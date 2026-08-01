# ADR-NNNN: <short, present-tense decision title>

- **Status:** Accepted
- **Date:** 2026-08-01

## Decision

I will simplify the medallion architecture from three to two layers: raw and
aggregated.

## Context

The data being pulled off the API is cleaner than I expected, and has already
had some tidying and transformation carried out. Splitting into the traditional
three layers is somewhat arbitrary, as the raw layer is already clean and ready
to be aggregated.

## Consequences

- **Positive:** Simpler architecture, more obvious separation of concerns.
- **Negative:** Some upfront renaming work and a bit more thought about the
  grain of the data.

## Notes:
Supercedes [ADR-001](00000_basic_architecture.md).
