import json
from io import StringIO
import requests

from prefect import task
from prefect.logging import get_run_logger
import duckdb

from orchestration.config import config
from orchestration.utils import ticker_to_cik

TICKER_TO_CIK = ticker_to_cik()

EDGAR_CONCEPT_TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueGoodsNet",
        "SalesRevenueServicesNet",
        "SalesRevenueGoodsGross",
    ],
}


def request_url(url: str, headers: dict, params: dict = {}) -> dict:
    logger = get_run_logger()
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.InvalidURL as url_err:
        logger.error("InvalidURL: Failed to retrieve data.")
        raise url_err
    except requests.exceptions.HTTPError as http_err:
        logger.error("HTTPError: Failed to retrieve data.")
        raise http_err
    except requests.exceptions.Timeout as timeout:
        logger.error("Timeout: Failed to retrieve data.")
        raise timeout
    else:
        logger.info("Succesfully retrieved data.")
        return response.json()


# @task(retries=3, retry_delay_seconds=5)
# def call_sugra_api(service: str, ticker: str, dataset: str) -> dict:
#     headers = {"x-api-key": config.sugra_api_key}
#     params = {"period": 20, "usd": True, "form": "10-K"}
#     url = f"https://sugra.ai/api/v1/{service}/{ticker}/{dataset}"
#     return request_url(url, headers, params)


@task(retries=3, retry_delay_seconds=5)
def call_edgar_api(ticker: str) -> dict:
    headers = {"User-Agent": config.edgar_header}
    cik = TICKER_TO_CIK[ticker]
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    return request_url(url, headers)


@task(retries=2, retry_delay_seconds=5)
def populate_edgar_raw(json_data: dict, ticker: str) -> None:
    logger = get_run_logger()
    gaap = json_data.get("facts", {}).get("us-gaap", {})
    conn = duckdb.connect(config.duckdb)
    for concept, tags in EDGAR_CONCEPT_TAGS.items():
        rows = []
        for tag in tags:
            tag_data = gaap.get(tag)
            if tag_data is None:
                continue
            usd_facts = tag_data.get("units", {}).get("USD")
            if not usd_facts:
                continue
            for fact in usd_facts:
                if "frame" not in fact:
                    continue
                rows.append({**fact, "tag": tag, "ticker": ticker})

        table = f"edgar_{concept}"
        logger.info(f"Populating {ticker} {table} data.")
        if len(rows) == 0:
            continue

        _json_data = conn.read_json(StringIO(json.dumps(rows)))
        conn.sql("SET SCHEMA 'raw';")
        conn.sql(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM _json_data;")
        conn.sql(f"CREATE TEMPORARY TABLE new_{table} AS SELECT * FROM _json_data;")
        conn.sql(
            f"MERGE INTO {table} AS t USING new_{table} AS s "
            "ON t.ticker == s.ticker AND t.tag == s.tag AND t.accn == s.accn "
            "WHEN NOT MATCHED THEN INSERT BY NAME;"
        )


# @task(retries=2, retry_delay_seconds=5)
# def populate_duckdb(json_data: dict, ticker: str, dataset: str) -> None:
#     logger = get_run_logger()
#     conn = duckdb.connect(config.duckdb)
#     for table, value in json_data.items():
#         logger.info(f"Populating {ticker} {table} data.")
#         if not isinstance(value, list):
#             raise ValueError(f"Unexpected json format: {table} = {type(value)}")
#         if len(value) == 0:
#             continue
#
#         _json_data = conn.read_json(StringIO(json.dumps(value)))
#         conn.sql("SET SCHEMA 'raw';")
#         conn.sql(
#             f"CREATE TABLE IF NOT EXISTS {dataset}_{table} AS SELECT *, '{ticker}' AS ticker, '{dataset}' AS dataset FROM _json_data;"
#         )
#         conn.sql(
#             f"CREATE TEMPORARY TABLE new_{dataset}_{table} AS SELECT *, '{ticker}' AS ticker, '{dataset}' AS dataset FROM _json_data;"
#         )
#         conn.sql(
#             f"MERGE INTO {dataset}_{table} AS t USING new_{dataset}_{table} AS s ON t.accession_number == s.accession_number WHEN NOT MATCHED THEN INSERT BY NAME;"
#         )
