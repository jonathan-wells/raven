from io import StringIO
import requests

from prefect import task
import duckdb

from config import config


@task
def call_sugra_api(service: str, ticker: str, dataset: str) -> dict:
    header = {"x-api-key": config.sugra_api_key}
    url = f"https://sugra.ai/api/v1/{service}/{ticker}/{dataset}"
    tmax = 10
    try:
        response = requests.get(url, headers=header, timeout=tmax)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        # TODO: add prefect logging statement
        raise http_err
    except requests.exceptions.Timeout as timeout:
        # TODO: add prefect logging statement
        raise timeout
    else:
        return response.json()


def populate_duckdb(json_data: dict, ticker: str) -> None:
    conn = duckdb.connect(config.duckdb)
    for table, value in json_data.items():
        if not isinstance(value, list):
            # TODO: add prefect logging statement
            raise ValueError(f"Unexpected json format: {table} = {type(value)}")
        if len(value) == 0:
            # TODO: add prefect logging statement
            continue

        _json_data = conn.read_json(StringIO(json.dumps(value)))  # type: ignore
        conn.sql(
            f"CREATE TABLE IF NOT EXISTS {table} AS SELECT *, '{ticker}' AS ticker FROM _json_data;"
        )
        conn.sql(
            f"CREATE TEMPORARY TABLE new_{table} AS SELECT *, '{ticker}' AS ticker FROM _json_data;"
        )
        conn.sql(
            f"MERGE INTO {table} AS t USING new_{table} AS s ON t.accession_number == s.accession_number WHEN NOT MATCHED THEN INSERT BY NAME;"
        )


if __name__ == "__main__":
    import json

    ticker = "DNA"  # Followed by AAPL
    ticker = "AAPL"  # Followed by AAPL
    data = call_sugra_api("fundamentals", ticker, "balance")["data"]
    populate_duckdb(data, ticker)
