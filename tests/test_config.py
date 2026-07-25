import pytest

from orchestration.config import Config


@pytest.fixture
def config(monkeypatch):
    monkeypatch.setenv("SUGRA_API_KEY", "test")
    monkeypatch.setenv("RAVEN_DUCKDB", "db/test.duckdb")
    monkeypatch.setattr(
        "orchestration.config.yaml.safe_load",
        lambda _: {"tickers": ["AAPL"], "datasets": ["balance"]},
    )
    return Config()


def test_config_get_attr(config):
    assert config.sugra_api_key == "test"
    assert isinstance(config.tickers, list)


def test_config_get_item(config):
    assert config["sugra_api_key"] == "test"
    assert isinstance(config["tickers"], list)
