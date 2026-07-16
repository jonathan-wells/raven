import pytest
from unittest.mock import Mock
from pathlib import Path
import json
from requests.exceptions import HTTPError, Timeout

import duckdb
from prefect.logging import disable_run_logger


from orchestration.tasks import call_sugra_api, populate_duckdb

DATA_DIR = Path(__file__).parent


@pytest.fixture
def dna_balance():
    return json.loads((DATA_DIR / "data" / "dna_balance.json").read_text())


@pytest.fixture
def get(monkeypatch, dna_balance):
    response = Mock()
    response.json.return_value = dna_balance
    get = Mock(return_value=response)
    monkeypatch.setattr("orchestration.tasks.requests.get", get)
    return get


def test_call_sugra_api_success(monkeypatch, get, dna_balance):
    monkeypatch.setattr("orchestration.tasks.config.sugra_api_key", "notakey")
    with disable_run_logger():
        data = call_sugra_api.fn("service", "ticker", "dataset")
    get.assert_called_once_with(
        "https://sugra.ai/api/v1/service/ticker/dataset",
        headers={"x-api-key": "notakey"},
    )
    assert data == dna_balance


def test_call_sugra_api_http_error(get):
    get.return_value.raise_for_status.side_effect = HTTPError
    with disable_run_logger(), pytest.raises(HTTPError):
        call_sugra_api.fn("service", "ticker", "dataset")


def test_call_sugra_api_timeout(monkeypatch):
    monkeypatch.setattr("orchestration.tasks.requests.get", Mock(side_effect=Timeout()))
    with disable_run_logger(), pytest.raises(Timeout):
        call_sugra_api.fn("service", "ticker", "dataset")


def test_populate_duckdb(monkeypatch, dna_balance):
    dbpath = Path("/tmp/tmp.duckdb")
    monkeypatch.setattr("orchestration.tasks.config.duckdb", dbpath)
    with disable_run_logger():
        populate_duckdb(dna_balance, "ticker")

    conn = duckdb.connect(dbpath)
    for table, values in dna_balance.items():
        if len(values) == 0:
            # Skip because empty tables don't get created
            continue
        data = conn.sql(f"SELECT * FROM {table};")
        assert data.to_df().shape[0] == len(values)

    # If not unset this test could pass based on data saved in prior runs.
    dbpath.unlink(missing_ok=True)
