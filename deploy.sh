duckdb db/raven.duckdb -c "CREATE SCHEMA IF NOT EXISTS raw;"
duckdb db/raven.duckdb -c "CREATE SCHEMA IF NOT EXISTS clean;"

docker compose --env-file .envrc up --build --remove-orphans --force-recreate -d

uv run prefect work-pool create raven-pool --type process --overwrite
uv run prefect deploy --all
