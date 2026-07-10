# ADR-002: Use Docker for containerization

- **Status:** Accepted
- **Date:** 2026-07-09

## Decision

Prefect and DuckDB will be served from Docker containers.

## Context

I would like this project to be capable of running locally, regardless of
operating system or hardware, or deployed on remote VMs with minimal extra work.
Containerization is the solution to this problem and Docker is a good choice as
the industry default - I have good familiarity with it, and it's composability
makes it straightforward to combine and orchestrate containers from different
sources.

## Alternatives considered

- **Podman** — Another popular option, with the ability to run without a daemon
  being a good security advantage. I am more familiar with Docker, and do not
  anticipate this project being used in a production environment, so Docker wins
  out based on speed of development.

## Consequences

- **Positive:** Cross-platform portability, predictable, unchanging environment.
  Long term persistence via background daemon.
- **Negative:** Finicky, slightly more setup than purely running locally.
