from prefect import flow

from tasks import call_edgar_api, populate_edgar_raw, invoke_dbt
from config import config


# @flow
# def load_sugra_api_data(
#     datasets: list[str] = config["datasets"], tickers: list[str] = config["tickers"]
# ) -> None:
#     for dataset in datasets:
#         for ticker in tickers:
#             response = call_sugra_api("fundamentals", ticker, dataset)
#             populate_duckdb(response["data"], ticker, dataset)
#


@flow
def load_edgar_data(tickers: list[str] = config["tickers"]) -> None:
    for ticker in tickers:
        response = call_edgar_api(ticker)
        populate_edgar_raw(response, ticker)


@flow
def run_dbt():
    invoke_dbt(["deps"])
    invoke_dbt(["build"])
