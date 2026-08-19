from prefect import flow

from tasks import call_edgar_api, populate_edgar_raw, invoke_dbt
from config import config


@flow
def load_edgar_data(tickers: list[str] = config["tickers"]) -> None:
    for ticker in tickers:
        response = call_edgar_api(ticker)
        populate_edgar_raw(response, ticker)


@flow
def run_dbt():
    invoke_dbt(["deps"])
    invoke_dbt(["build"])
