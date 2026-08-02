import pytest
from unittest.mock import Mock
from pathlib import Path
import json
from requests.exceptions import InvalidURL, HTTPError, Timeout

import duckdb
from prefect.logging import disable_run_logger

from orchestration.tasks import (
    request_url,
    call_edgar_api,
    call_sugra_api,
    populate_duckdb,
)

DATA_DIR = Path(__file__).parent


@pytest.fixture
def dna_balance():
    return json.loads((DATA_DIR / "data" / "dna_balance.json").read_text())


@pytest.fixture
def vrtx_company_facts():
    return json.loads((DATA_DIR / "data" / "vertex_companyfacts.json").read_text())


@pytest.fixture
def get_dna_balance(monkeypatch, dna_balance):
    response = Mock()
    response.json.return_value = dna_balance
    get = Mock(return_value=response)
    monkeypatch.setattr("orchestration.tasks.requests.get", get)
    return get


@pytest.fixture
def get_vrtx_company_facts(monkeypatch, vrtx_company_facts):
    response = Mock()
    response.json.return_value = vrtx_company_facts
    get = Mock(return_value=response)
    monkeypatch.setattr("orchestration.tasks.requests.get", get)
    return get


def test_call_sugra_api_success(monkeypatch, get_dna_balance, dna_balance):
    monkeypatch.setattr("orchestration.tasks.config.sugra_api_key", "notakey")
    with disable_run_logger():
        data = call_sugra_api.fn("service", "ticker", "dataset")
    get_dna_balance.assert_called_once_with(
        "https://sugra.ai/api/v1/service/ticker/dataset",
        headers={"x-api-key": "notakey"},
        params={"period": 20, "usd": True, "form": "10-K"},
    )
    assert data == dna_balance


def test_call_edgar_api_success(
    monkeypatch, get_vrtx_company_facts, vrtx_company_facts
):
    monkeypatch.setattr("orchestration.tasks.config.edgar_header", "Jane Doe")
    with disable_run_logger():
        data = call_edgar_api.fn("VRTX")
    # VRTX's CIK is 875320
    get_vrtx_company_facts.assert_called_once_with(
        "https://data.sec.gov/api/xbrl/companyfacts/CIK0000875320.json",
        headers={"User-Agent": "Jane Doe"},
        params={},
    )
    assert data == vrtx_company_facts


def test_request_url_invalid(get_dna_balance):
    get_dna_balance.return_value.raise_for_status.side_effect = InvalidURL
    with disable_run_logger(), pytest.raises(InvalidURL):
        request_url("https://bad url", headers={}, params={})


def test_request_url_http_error(get_dna_balance):
    get_dna_balance.return_value.raise_for_status.side_effect = HTTPError
    with disable_run_logger(), pytest.raises(HTTPError):
        request_url("https://www.google.com", headers={}, params={})


def test_request_url_timeout(monkeypatch):
    monkeypatch.setattr("orchestration.tasks.requests.get", Mock(side_effect=Timeout()))
    with disable_run_logger(), pytest.raises(Timeout):
        request_url("https://www.google.com", headers={}, params={})


def test_populate_duckdb(monkeypatch, dna_balance):
    dbpath = Path("/tmp/tmp.duckdb")
    monkeypatch.setattr("orchestration.tasks.config.duckdb", dbpath)
    conn = duckdb.connect(dbpath)
    conn.sql("CREATE SCHEMA IF NOT EXISTS 'raw';")
    ticker = "ticker"
    dataset = "dataset"
    with disable_run_logger():
        populate_duckdb(dna_balance, ticker, dataset)

    for table, values in dna_balance.items():
        if len(values) == 0:
            # Skip because empty tables don't get created
            continue
        data = conn.sql("SET SCHEMA 'raw';")
        data = conn.sql(f"SELECT * FROM {dataset}_{table};")
        assert data.to_df().shape[0] == len(values)

    # If not unset this test could pass based on data saved in prior runs.
    dbpath.unlink(missing_ok=True)
