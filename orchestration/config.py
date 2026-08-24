import os
from pathlib import Path

from orchestration.utils import ticker_to_cik

TICKER_TO_CIK = ticker_to_cik()

EDGAR_CONCEPT_TAGS = {
    "income": {
        "revenue": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
            "SalesRevenueGoodsNet",
            "SalesRevenueServicesNet",
            "SalesRevenueGoodsGross",
        ],
        "cost_of_revenue": [
            "CostOfRevenue",
            "CostOfGoodsAndServicesSold",
        ],
        "gross_profit": [
            "GrossProfit",
        ],
        "operating_expense": [
            "OperatingExpenses",
            "CostsAndExpenses",
        ],
        "operating_income": [
            "OperatingIncomeLoss",
        ],
        "net_income": [
            "NetIncomeLoss",
        ],
    },
    "balance": {
        "total_assets": [
            "Assets",
            "LiabilitiesAndStockholdersEquity",
        ],
        "current_assets": [
            "AssetsCurrent",
        ],
        "cash": [
            "CashAndCashEquivalentsAtCarryingValue",
        ],
        "total_liabilities": [
            "Liabilities",
        ],
        "current_liabilities": [
            "LiabilitiesCurrent",
        ],
        "long_term_debt": [
            "LongTermDebtNoncurrent",
        ],
        "stockholders_equity": [
            "StockholdersEquity",
        ],
    },
}


class Config:
    def __init__(self):
        biotech_path = Path(__file__).parent.parent / "assets" / "biotech.txt"
        self._config = {}
        with open(biotech_path) as file:
            self._config["tickers"] = [line.split("\t")[0].upper() for line in file]
        self._config["sugra_api_key"] = self._load_env_var("SUGRA_API_KEY")
        self._config["edgar_header"] = self._load_env_var("EDGAR_HEADER")
        self._config["duckdb"] = self._load_env_var("RAVEN_DUCKDB")

    @staticmethod
    def _load_env_var(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"{key} environment variable not set.")
        return value

    def __getitem__(self, name: str):
        return self._config[name]

    def __getattr__(self, name: str):
        try:
            return self._config[name]
        except KeyError:
            raise AttributeError(name)


config = Config()
