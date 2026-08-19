import json
from io import StringIO
from pathlib import Path
import requests

from prefect import task
from prefect.logging import get_run_logger
from prefect.cache_policies import NO_CACHE
from prefect_dbt import PrefectDbtRunner, PrefectDbtSettings
import duckdb

from orchestration.config import config
from orchestration.utils import ticker_to_cik

REPO_ROOT = Path(__file__).resolve().parent.parent
DBT_PROJECT_DIR = REPO_ROOT / "transforms"

TICKER_TO_CIK = ticker_to_cik()

EDGAR_CONCEPT_TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "SalesRevenueServicesNet",
        "SalesRevenueGoodsGross",
    ],
    "cost_of_revenue": [
        "CostOfRevenue",
        "CostOfGoodsAndServicesSold",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "operating_expense": [
        "OperatingExpenses",
        "CostsAndExpenses",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "net_income": [
        "NetIncomeLoss",
    ],
    "total_assets": [
        "Assets",
    ],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
    ],
    "total_liabilities": [
        "Liabilities",
    ],
    "long_term_debt": [
        "LongTermDebtNoncurrent",
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


@task(retries=3, retry_delay_seconds=5)
def call_edgar_api(ticker: str) -> dict:
    logger = get_run_logger()
    headers = {"User-Agent": config.edgar_header}
    cik = TICKER_TO_CIK.get(ticker)
    if not cik:
        logger.warn(f"Ticker '{ticker}' not found")
        return {}
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    return request_url(url, headers)


@task(retries=2, retry_delay_seconds=5)
def populate_edgar_raw(json_data: dict, ticker: str) -> None:
    logger = get_run_logger()
    if not json_data:
        return
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


@task(cache_policy=NO_CACHE)
def invoke_dbt(command: list[str]) -> None:
    """Run a dbt command via PrefectDbtRunner."""
    logger = get_run_logger()
    logger.info(f"Invoking dbt: {' '.join(command)}")

    runner = PrefectDbtRunner(
        settings=PrefectDbtSettings(
            project_dir=DBT_PROJECT_DIR,
            profiles_dir=Path(DBT_PROJECT_DIR),
        )
    )
    runner.invoke([*command])
