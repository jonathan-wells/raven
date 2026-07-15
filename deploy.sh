docker compose --env-file .envrc up --build --remove-orphans -d
uv run prefect work-pool create raven-pool --type process --overwrite
uv run prefect deploy --all
