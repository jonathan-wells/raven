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
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    plt.rcParams["font.sans-serif"] = "Futura"

    # FT palette
    plt.rcParams["figure.facecolor"] = "#fff1e5"
    plt.rcParams["axes.facecolor"] = "#fff1e5"
    PALETTE = [
        "#990f3d",  # Claret
        "#0d7680",  # Teal
        "#0f5499",  # Oxford Blue
        "#262a33",  # Slate
    ]
    return (
        PALETTE,
        PCA,
        Path,
        StandardScaler,
        duckdb,
        os,
        pl,
        plt,
        requests,
        sns,
    )


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

    return


@app.cell
def _(duckdb):
    conn = duckdb.connect("db/raven.duckdb")
    balance_df = conn.execute("SELECT * FROM presentation.balance_sheet").pl()
    conn.close()
    balance_df
    return (balance_df,)


@app.cell
def _(balance_df, pl):
    balance_df.filter((pl.col("assets").is_null()))
    return


@app.cell
def _(PCA, StandardScaler, balance_df, plt):
    _value_cols = balance_df.columns[4:11]
    _value_cols = [
        "assets",
        "liabilities",
        "stockholders_equity",
        "cash_and_cash_equivalents_at_carrying_value",
    ]
    _complete_df = balance_df[_value_cols].drop_nulls()
    print(_complete_df.shape)
    _pca = PCA(n_components=3)
    _scaler = StandardScaler()
    _x = _pca.fit_transform(_scaler.fit_transform(_complete_df))

    plt.scatter(_x[:, 0], _x[:, 1], alpha=0.4)
    return


@app.cell
def _(PALETTE, balance_df, pl, plt, sns):
    _concepts = [
        "assets",
        "stockholders_equity",
        "cash_and_cash_equivalents_at_carrying_value",
    ]
    _fig, _axes = plt.subplots(
        figsize=(12, 4),
        ncols=len(_concepts),
        sharex=True,
        sharey=True,
    )

    for _tag, _ax in zip(_concepts, _axes):
        sns.lineplot(
            data=balance_df.filter(pl.col("ticker").is_in(["MRNA", "VRTX", "DNA"])),
            x="quarter_end",
            y=_tag,
            hue="ticker",
            palette=PALETTE,
            ax=_ax,
        )
        _ax.set_xlabel("")
        _ax.set_ylabel("Value ($B)")
        _ax.set_title(" ".join(_tag.split("_")))
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
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
