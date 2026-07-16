import json
from io import StringIO
import requests

from prefect import task
from prefect.logging import get_run_logger
import duckdb

from orchestration.config import config


@task(retries=3, retry_delay_seconds=5)
def call_sugra_api(service: str, ticker: str, dataset: str) -> dict:
    logger = get_run_logger()
    header = {"x-api-key": config.sugra_api_key}
    url = f"https://sugra.ai/api/v1/{service}/{ticker}/{dataset}"
    try:
        logger.info(f"Requesting {dataset} data from {ticker}.")
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTPError: Failed to retrieve {ticker} data.")
        raise http_err
    except requests.exceptions.Timeout as timeout:
        logger.error(f"Timeout: Failed to retrieve {ticker} data.")
        raise timeout
    else:
        logger.info(f"Retrieved {ticker} data.")
        return response.json()


def populate_duckdb(json_data: dict, ticker: str) -> None:
    logger = get_run_logger()
    conn = duckdb.connect(config.duckdb)
    for table, value in json_data.items():
        logger.info(f"Populating {ticker} {table} data.")
        if not isinstance(value, list):
            raise ValueError(f"Unexpected json format: {table} = {type(value)}")
        if len(value) == 0:
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
    print("hi")
