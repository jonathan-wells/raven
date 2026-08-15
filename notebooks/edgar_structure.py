import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import requests
    import time
    from collections import Counter

    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    return Counter, pd, plt, requests, sns, time


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
def _(biotech_df, ticker_data):
    _i = 0
    for _ticker in biotech_df.index:
        if "us-gaap" not in ticker_data[_ticker]["facts"].keys():
            continue
        if "Revenues" not in ticker_data[_ticker]["facts"]["us-gaap"].keys():
            continue
        _val = ticker_data[_ticker]["facts"]["us-gaap"]["Revenues"]
        # print(_val.keys())
        # break
        # if "Cost" not in key:
        #     continue
        # if "units" not in val:
        #     continue
        if "USD" not in _val["units"]:
            continue
        _data = [
            item
            for item in _val["units"]["USD"]
            if item["form"] == "10-Q" and "frame" not in item.keys()
        ]
        if len(_data) == 0:
            continue
        print(_i, _ticker)
        print(_val["description"])
        print([(item["fy"], item["fp"], item["end"], item["val"]) for item in _data])
        print()
        _i += 1
    return


@app.cell
def _(Counter, biotech_df, ticker_data):
    _test = Counter()
    print(len(biotech_df.index))
    for _ticker in biotech_df.index:
        if "us-gaap" not in ticker_data[_ticker]["facts"].keys():
            continue
        for key in ticker_data[_ticker]["facts"]["us-gaap"].keys():
            _test[key] += 1
    for _key, _val in sorted(_test.items(), key=lambda x: -x[1]):
        # if _val < 100:
        #     continue
        print(_val, _key)
    return


@app.cell
def _():
    revenue_tags = [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueGoodsNet",
        "SalesRevenueServicesNet",
        "SalesRevenueGoodsGross",
    ]
    return (revenue_tags,)


@app.cell
def _(biotech_df, pd, revenue_tags, ticker_data):
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
            for col in ["start", "end", "filed", "fy"]:
                _df[col] = pd.to_datetime(_df[col])
            _df["tag"] = _tag
            _df["ticker"] = _ticker
            _dfs.append(_df)
    revenue_df = pd.concat(_dfs)
    return (revenue_df,)


@app.cell
def _(revenue_df):
    revenue_df2 = (
        revenue_df.drop("tag", axis=1)
        .groupby(
            ["start", "end", "accn", "fy", "fp", "form", "filed", "frame", "ticker"]
        )
        .max()
        .reset_index()
        .rename({"val": "EstimatedRevenue"}, axis=1)
    )
    revenue_df2["duration"] = revenue_df2["end"] - revenue_df2["start"]
    revenue_df2
    return (revenue_df2,)


@app.cell
def _(plt, revenue_df2, sns):
    _tickers = ["vrtx", "dna", "regn", "mrna", "kymr"]

    _fig, _ax = plt.subplots()
    sns.lineplot(
        data=revenue_df2.loc[
            (revenue_df2.duration > "80 days")
            & (revenue_df2.duration < "100 days")
            & (revenue_df2.ticker.isin(_tickers))
        ],
        x="end",
        y="EstimatedRevenue",
        hue="ticker",
    )
    _ax.set_yticks(range(0, int(7e9), int(1e9)))
    _ax.set_yticklabels(range(0, 7))
    _ax.set_ylabel("Estimated Quarterly Revenue")

    sns.despine()
    plt.show()
    return


@app.cell
def _(revenue_df2):
    revenue_df2.loc[
        (revenue_df2.duration > "80 days")
        & (revenue_df2.duration < "100 days")
        & (revenue_df2.ticker == "mrna")
    ]
    return


@app.cell
def _(biotech_df):
    biotech_df
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
