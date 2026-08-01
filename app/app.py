from pathlib import Path
import duckdb
import streamlit as st

WORKDIR = Path(__file__).parent.parent


def load_duckdb_conn() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(f"{WORKDIR}/db/raven.duckdb")
    conn.execute("USE 'aggregated'")
    return conn


conn = load_duckdb_conn()
income_df = conn.query("SELECT * FROM income").df()

income_df["gross_profit_estimated"] = income_df.revenue - income_df.cost_of_revenue
income_df["gross_profit"] = income_df.gross_profit.combine_first(
    income_df.gross_profit_estimated
)
with st.container():
    tickers = st.multiselect(
        "Tickers",
        income_df.ticker.unique(),
        default=["VRTX", "REGN", "BNTX"],
    )

data_df = income_df.loc[income_df.ticker.isin(tickers)]
st.line_chart(data=data_df, x="end_date", y="net_income", color="ticker")
data_df
