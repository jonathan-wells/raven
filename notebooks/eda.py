import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import duckdb
    import seaborn as sns
    import matplotlib.pyplot as plt

    return duckdb, plt, sns


@app.cell
def _(duckdb):
    conn = duckdb.connect("db/raven.duckdb")
    conn.execute("SET SCHEMA = 'aggregated'")
    return (conn,)


@app.cell
def _(conn):
    income_df = conn.query("SELECT * FROM income WHERE form = '10-K'").df()

    return (income_df,)


@app.cell
def _(income_df, plt, sns):
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.lineplot(
        data=income_df, x="end_date", y="gross_profit", hue="ticker", marker="o"
    )
    # ax.set_yscale("log")
    sns.despine()
    plt.show()
    return


@app.cell
def _(income_df):
    income_df.loc[income_df.ticker == "JAZZ"].sort_values("end_date")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
