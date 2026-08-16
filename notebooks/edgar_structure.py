import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import re
    import requests
    import time

    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    return pd, plt, re, requests, sns, time


@app.cell
def _(pd):
    _ticker_df = pd.read_csv(
        "assets/ticker.txt", sep="\t", names=["ticker", "cik"], dtype=str
    )
    biotech_df = (
        pd.read_csv("assets/biotech.txt", sep="\t", names=["ticker", "company"])
        .merge(_ticker_df, on="ticker")
        .set_index("ticker")
    )
    biotech_df
    return (biotech_df,)


@app.cell
def _(err, printf, requests):
    def call_edgar(cik):
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:0>10}.json"
        headers = {"User-Agent": "Jonathan Wells jonwells90@gmail.com"}
        try:
            response = requests.get(url, headers=headers)
        except err:
            printf(f"Failed to retrieve CIK {cik}")
            raise err
        return response.json()

    def parse_edgar_gaap_keys(json_data):
        return json_data["facts"]["us-gaap"].keys()

    return (call_edgar,)


@app.cell
def _(biotech_df, call_edgar, time):
    ticker_data = {}
    for _ticker, _row in biotech_df.iterrows():
        print(_ticker)
        _cik = _row.cik
        _data = call_edgar(_cik)
        ticker_data[_ticker] = _data
        time.sleep(0.15)
    return (ticker_data,)


@app.cell
def _(ticker_data):
    for _key, _val in ticker_data["vrtx"]["facts"]["us-gaap"].items():
        if "Cost" not in _key:
            continue
        if "units" not in _val:
            continue
        if "USD" not in _val["units"]:
            continue
        _data = [
            item
            for item in _val["units"]["USD"]
            if item["form"] == "10-Q" and "frame" not in item.keys()
        ]
        if len(_data) == 0:
            continue
        print(_key)
        print(_val["description"])
        print([(item["fy"], item["fp"], item["end"], item["val"]) for item in _data])
        print()
    return


@app.cell
def _():
    revenue_tags = [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueGoodsGross",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "SalesRevenueServicesNet",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
    ]
    return (revenue_tags,)


@app.cell
def _(biotech_df, pd, re, revenue_tags, ticker_data):
    _dfs = []
    for _ticker in biotech_df.index:
        if "facts" not in ticker_data[_ticker]:
            continue
        if "us-gaap" not in ticker_data[_ticker]["facts"]:
            continue
        _data = ticker_data[_ticker]["facts"]["us-gaap"]
        for _tag in revenue_tags:
            if _tag not in _data:
                _fin_data = []
                continue
            _revenue_data = _data[_tag]
            if "units" not in _revenue_data:
                continue
            if "USD" not in _revenue_data["units"]:
                continue
            _fin_data = [
                item for item in _revenue_data["units"]["USD"] if "frame" in item
            ]
            if len(_fin_data) == 0:
                continue
            _df = pd.DataFrame(_fin_data)
            if _df.columns.to_list() != [
                "start",
                "end",
                "val",
                "accn",
                "fy",
                "fp",
                "form",
                "filed",
                "frame",
            ]:
                continue
            for col in ["start", "end", "filed"]:
                _df[col] = pd.to_datetime(_df[col])
            _df["tag"] = _tag
            _df["ticker"] = _ticker
            _df["tag"] = pd.Categorical(
                _df["tag"], categories=revenue_tags, ordered=True
            )
            _dfs.append(_df)

    revenue_df = (
        pd.concat(_dfs)
        .sort_values(["tag", "form"])
        .groupby(["ticker", "frame"])
        .first()
        .reset_index()
        .rename({"val": "EstimatedRevenue"}, axis=1)
        .sort_values(["ticker", "fy", "form", "end"])
    )

    revenue_df["frame_year"] = revenue_df.frame.apply(
        lambda x: int(re.match(r"CY(\d+)", x).group(1))
    )
    revenue_df["frame_quarter"] = revenue_df.frame.apply(
        lambda x: (
            re.match(r"CY\d+(Q\d)", x).group(1) if re.match(r"CY\d+(Q\d)", x) else "FY"
        )
    )
    revenue_df
    return (revenue_df,)


@app.cell
def _(biotech_df, pd, revenue_df):
    _wide_revenue_df = revenue_df.pivot_table(
        index=["ticker", "frame_year"],
        columns=["frame_quarter"],
        values="EstimatedRevenue",
        aggfunc="last",
    )

    _complete = _wide_revenue_df[["FY", "Q1", "Q2", "Q3"]].notna().all(axis=1)
    _wide_revenue_df["Q4"] = (
        _wide_revenue_df["FY"] - _wide_revenue_df[["Q1", "Q2", "Q3"]].sum(axis=1)
    ).where(_complete)
    _wide_revenue_df

    _date_dict = (
        revenue_df[["ticker", "frame_year", "frame_quarter", "end", "start"]]
        .set_index(["ticker", "frame_year", "frame_quarter"])
        .to_dict()
    )

    for (_ticker, _year, _quarter), _end_date in list(_date_dict["end"].items()):
        if _quarter == "FY":
            _date_dict["end"][(_ticker, _year, "Q4")] = _end_date
    for _ticker, _year, _quarter in list(_date_dict["start"].keys()):
        if _quarter == "FY":
            _q3_end = _date_dict["end"].get((_ticker, _year, "Q3"))
            if _q3_end:
                _date_dict["start"][(_ticker, _year, "Q4")] = _q3_end + pd.Timedelta(
                    days=1
                )

    sim_df = _wide_revenue_df.reset_index().melt(
        id_vars=["ticker", "frame_year"], value_name="estimated_revenue"
    )
    sim_df["start"] = sim_df.apply(
        lambda x: _date_dict["start"].get((x.ticker, x.frame_year, x.frame_quarter)),
        axis=1,
    )
    sim_df["end"] = sim_df.apply(
        lambda x: _date_dict["end"].get((x.ticker, x.frame_year, x.frame_quarter)),
        axis=1,
    )
    sim_df["duration"] = sim_df.end - sim_df.start

    sim_df = sim_df.dropna()
    sim_df = biotech_df[["company"]].merge(sim_df, left_index=True, right_on="ticker")
    return (sim_df,)


@app.cell
def _(plt, sim_df, sns):
    _tickers = sim_df.sample(5)["ticker"].unique()[:5]

    _fig, _ax = plt.subplots()
    sns.lineplot(
        data=sim_df.loc[
            (sim_df.frame_quarter != "FY") & (sim_df.ticker.isin(_tickers))
        ],
        x="end",
        y="estimated_revenue",
        hue="company",
    )
    _ax.set_ylabel("Estimated Quarterly Revenue")

    sns.despine()
    plt.show()
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
