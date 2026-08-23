import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import requests
    from pathlib import Path

    import duckdb
    import polars as pl
    import seaborn as sns
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = "Futura"
    plt.rcParams["figure.facecolor"] = "#fff1e5"
    plt.rcParams["axes.facecolor"] = "#fff1e5"
    PALETTE = [
        "#990f3d",  # Claret
        "#0d7680",  # Teal
        "#0f5499",  # Oxford Blue
        "#262a33",  # Slate
    ]
    return PALETTE, Path, duckdb, os, pl, plt, requests, sns


@app.cell
def _(Path, logger, os, requests):
    def ticker_to_cik():
        ticker_file = Path(__file__).parent.parent / "assets" / "ticker.txt"
        tickers = {}
        with open(ticker_file) as file:
            for line in file:
                ticker, cik = line.strip().split("\t")
                tickers[ticker.upper()] = f"{cik:0>10}"
        return tickers

    def call_edgar_api(ticker: str) -> dict:
        headers = {"User-Agent": os.environ["EDGAR_HEADER"]}
        cik = ticker_to_cik().get(ticker)
        if not cik:
            logger.warn(f"Ticker '{ticker}' not found")
            return {}
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        return requests.get(url=url, headers=headers)

    return (call_edgar_api,)


@app.cell
def _(duckdb, pl):
    conn = duckdb.connect("db/raven.duckdb")
    assets_df = conn.execute("SELECT * FROM raw.edgar_total_assets;").pl()
    liabilities_df = conn.execute("SELECT * FROM raw.edgar_total_liabilities;").pl()
    equity_df = conn.execute("SELECT * FROM raw.edgar_stockholders_equity;").pl()

    equity_df = equity_df.with_columns(pl.col("val").cast(pl.Int64))

    df = pl.concat([assets_df, liabilities_df, equity_df]).pivot(
        on="tag", index=["end", "accn", "fy", "fp", "form", "filed", "frame", "ticker"]
    )
    df = df.with_columns((pl.col("Assets") - pl.col("Liabilities")).alias("CalcEquity"))
    df.filter(
        (~pl.col("StockholdersEquity").is_null()) & (~pl.col("CalcEquity").is_null())
    )
    return assets_df, df


@app.cell
def _(PALETTE, df, pl, plt, sns):
    _fig, _axes = plt.subplots(
        figsize=(12, 4),
        ncols=3,
        sharex=True,
        sharey=True,
    )

    for _tag, _ax in zip(["Assets", "Liabilities", "Equity"], _axes):
        sns.lineplot(
            data=df.filter(pl.col("ticker").is_in(["REGN", "VRTX", "MRNA", "DNA"])),
            x="end",
            y=_tag,
            hue="ticker",
            palette=PALETTE,
            ax=_ax,
        )
        _ax.set_xlabel("")
        _ax.set_ylabel("Value ($B)")
        _ax.set_title(_tag)
        _ax.grid(ls=":")
        _ax.set_xticklabels(
            [x._text.split("-")[0] for x in _ax.get_xticklabels()], rotation=45
        )
        _ax.set_yticklabels([-10, 0, 10, 20, 30, 40])
    _axes[2].legend().remove()
    _axes[1].legend().remove()
    _axes[0].legend(framealpha=0.4)

    sns.despine()
    plt.tight_layout()
    plt.show()

    return


@app.cell
def _(call_edgar_api):
    data = call_edgar_api("JAZZ")
    data
    return (data,)


@app.cell
def _(data):
    # list(data.json()["facts"]["us-gaap"]["Assets"]["units"]["USD"])
    [k for k in data.json()["facts"]["us-gaap"].keys() if "iabilities" in k]
    return


@app.cell
def _(assets_df, pl):
    assets_df.filter(pl.col("ticker") == "JAZZ")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
