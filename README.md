# Raven

Raven is a simple platform that aggregates SEC data from the EDGAR database
system and provides tools for quickly assessing the financial health of a
company.

## Prerequisites

Raven uses [uv](https://docs.astral.sh/uv/) for package management and runs in a
containerized environment through [docker](https://www.docker.com/). To simplify
data collection, Raven uses [Sugra API](https://sugra.systems/api), a data API
that aggregates across a wide variety of primary sources and domains, including
finance and economics. It is free to use for up to 50 API calls per day.

## Installation

```bash
git clone git@github.com:jonathan-wells/raven.git
cd raven
uv sync
./deploy.sh
```
