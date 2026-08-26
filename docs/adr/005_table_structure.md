# ADR-005: Structure of tables in raw-clean-presentation

- **Status:** Accepted
- **Date:** 2026-08-22

## Decision

1. Raw layer will contain single tables corresponding to each XBRL tag in Edgar.
   Each row contains a frame and value.
2. Clean layers will contain tables with clean, quarterly figures for each tag.
   A row contains a single quarter's report, either for the period or
   instantaneous. Q4 figures will be computed from the full year's value minus
   the sum of Q1-3. value minus the sum of Q1-3 value minus the sum of Q1-3
   value minus the sum of Q1-3.
3. Presentation layer will contain combined tables for balance and income, with
   partial reconciliation across metrics.

## Context

Been struggling to decide on the right grain (quarterly/yearly) and degree of
data cleaning and manipulation to do.

## Consequences

- **Positive:** Think this is a good middle ground, and provides enough detail
  to reconcile the most important figures, whilst not drowning in XBRL tags.
- **Negative:** Database tables need rebuilding.
