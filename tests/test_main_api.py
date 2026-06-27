import json

import main


class FakeSerpClient:
    response = {}
    received_api_key = None
    received_search_kwargs = None

    def __init__(self, api_key):
        FakeSerpClient.received_api_key = api_key

    def search(self, **kwargs):
        FakeSerpClient.received_search_kwargs = kwargs
        return FakeSerpClient.response


def test_call_api_combines_successful_best_and_other_flights(tmp_path, monkeypatch):
    response_file = tmp_path / "search_flights_response.json"
    best_flight = {"price": 900, "kind": "best"}
    other_flight = {"price": 1200, "kind": "other"}
    FakeSerpClient.response = {
        "search_metadata": {"status": "Success"},
        "best_flights": [best_flight],
        "other_flights": [other_flight],
    }

    monkeypatch.setattr(main.serpapi, "Client", FakeSerpClient)
    monkeypatch.setattr(main.config, "SERPAPI_KEY", "test-api-key")
    monkeypatch.setattr(main, "PATHS", {"search_flights_response": str(response_file)})

    status, results = main.callAPI()

    assert status == "Success"
    assert results == [best_flight, other_flight]
    assert FakeSerpClient.received_api_key == "test-api-key"
    assert FakeSerpClient.received_search_kwargs == main.QUERYSTRING
    assert json.loads(response_file.read_text(encoding="utf-8")) == results


def test_call_api_returns_error_when_serpapi_response_has_error(monkeypatch, capsys):
    FakeSerpClient.response = {"error": "invalid key"}

    monkeypatch.setattr(main.serpapi, "Client", FakeSerpClient)

    status, results = main.callAPI()

    assert status == "Error"
    assert results == []
    assert "SerpAPI error: invalid key" in capsys.readouterr().out


def test_call_api_returns_empty_results_for_non_success_status(monkeypatch, capsys):
    FakeSerpClient.response = {"search_metadata": {"status": "Processing"}}

    monkeypatch.setattr(main.serpapi, "Client", FakeSerpClient)

    status, results = main.callAPI()

    assert status == "Processing"
    assert results == []
    assert "SerpAPI search failed. Status: Processing" in capsys.readouterr().out


def test_call_api_returns_empty_results_when_success_has_no_flights(monkeypatch, capsys):
    FakeSerpClient.response = {
        "search_metadata": {"status": "Success"},
        "best_flights": [],
        "other_flights": [],
    }

    monkeypatch.setattr(main.serpapi, "Client", FakeSerpClient)

    status, results = main.callAPI()

    assert status == "Success"
    assert results == []
    assert "no flights were returned" in capsys.readouterr().out
