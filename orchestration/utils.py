from pathlib import Path


def ticker_to_cik():
    ticker_file = Path(__file__).parent.parent / "assets" / "ticker.txt"
    tickers = {}
    with open(ticker_file) as file:
        for line in file:
            ticker, cik = line.strip().split("\t")
            tickers[ticker.upper()] = f"{cik:0>10}"
    return tickers
