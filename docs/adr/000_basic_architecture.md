# ADR-000: Build platform around a simple medallion-style architecture

- **Status:** Accepted
- **Date:** 2026-07-01

## Decision

The Raven platform will follow a simple medallion architecture, with ELT
pipelines that transfer data between raw, clean and presentation layers.

## Context

Intend to use very simple data sources that should already have undergone
significant cleaning, and data velocity will be very low. No need to think too
much about this for a toy project: data mesh, microservices, streaming lambda
architectures would all be a bad fit due to their inherent complexity. This
project will never scale to the sort of volumes or user base where they might be
a consideration.

## Consequences

- **Positive:** Buys simplicity and familiarity
- **Negative:** Will make it hard to adapt the project to more exciting and or
  challenging data sources, e.g. real-time forex data.
