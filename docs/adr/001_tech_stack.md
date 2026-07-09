# ADR-001: Commit to lightweight tech stack

- **Status:** Accepted
- **Date:** 2026-07-08

## Decision

Raven will be built on a lightweight, open-source stack that avoids reliance on
cloud infrastructure. It will be built around Prefect for orchestration, dbt for
data modelling and transformation, and DuckDB for in-memory OLAP database
backend. It will use the Sugra API as its primary source of data.

## Context

This is intended to be a data engineering portfolio project and therefore must
showcase best practice, but doesn't need to be heavily productionised. I would
also like this to be feasible for other people to run, should they so choose,
and therefore anything that requires

## Alternatives considered

- **Build on top of PaaS vendors such as Databricks or Snowflake.** — Rejected
  as this would require potential users to set up accounts and handle
  significant config setup, even on free tiers. Significantly overkill for a
  project that will likely just ingest Kb-sized datasets from one or two
  sources.
- **Implement everything from scratch with Python and SQL** — Would probably be
  fun, but doesn't really showcase data engineering skills.

## Consequences

- **Positive:** Lightweight, easy to maintain and runs locally.
- **Negative:** Significantly harder to scale if the project ever grows beyond a
  toy.
