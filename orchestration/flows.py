from prefect import flow

from tasks import call_sugra_api, populate_duckdb


@flow
def load_sugra_api_data(tickers: list[str]) -> None:
    for ticker in tickers:
        response = call_sugra_api("fundamentals", ticker, "balance")
        populate_duckdb(response["data"], ticker)


if __name__ == "__main__":
    tickers = ["DNA", "VRTX", "NVO"]
    load_sugra_api_data(tickers)
