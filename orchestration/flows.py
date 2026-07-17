from prefect import flow

from tasks import call_sugra_api, populate_duckdb
from config import config


@flow
def load_sugra_api_data(
    datasets: list[str] = config["datasets"], tickers: list[str] = config["tickers"]
) -> None:
    for dataset in datasets:
        for ticker in tickers:
            response = call_sugra_api("fundamentals", ticker, dataset)
            populate_duckdb(response["data"], ticker)
