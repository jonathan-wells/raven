import os
from pathlib import Path


class Config:
    def __init__(self) -> None:
        self.sugra_api_key: str = self._load_env_var("SUGRA_API_KEY")
        self.duckdb: Path | str = Path(self._load_env_var("RAVEN_DUCKDB"))

    @staticmethod
    def _load_env_var(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"{key} environment variable not set.")
        return value


config = Config()
