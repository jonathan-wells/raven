import os
from pathlib import Path
import yaml


class Config:
    def __init__(self):

        with open(Path(__file__).parent.parent / "config.yaml") as yamlfile:
            self._config = yaml.safe_load(yamlfile)

        if "tickers" not in self._config.keys():
            raise RuntimeError("'tickers' not found in config.yaml")
        if "datasets" not in self._config.keys():
            raise RuntimeError("'tickers' not found in config.yaml")

        self._config["sugra_api_key"] = self._load_env_var("SUGRA_API_KEY")
        self._config["duckdb"] = self._load_env_var("RAVEN_DUCKDB")

    @staticmethod
    def _load_env_var(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"{key} environment variable not set.")
        return value

    def __getitem__(self, name: str):
        return self._config[name]


config = Config()
