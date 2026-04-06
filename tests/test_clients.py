"""HTTP clients and OpenAlex helpers (mocked; no real API calls)."""

from __future__ import annotations

import pytest

from research_system.clients import (
    _http_retry_wait_s,
    _openalex_work_url,
    _reconstruct_openalex_abstract,
    openalex_work_search,
    tavily_search,
)


def test_reconstruct_openalex_abstract_empty() -> None:
    assert _reconstruct_openalex_abstract({}) == ""
    assert _reconstruct_openalex_abstract(None) == ""  # type: ignore[arg-type]


def test_reconstruct_openalex_abstract_rebuilds_order() -> None:
    inv = {"The": [0], "quick": [1], "fox": [2]}
    assert _reconstruct_openalex_abstract(inv) == "The quick fox"


def test_openalex_work_url_primary_location() -> None:
    w = {
        "primary_location": {"landing_page_url": "https://example.org/paper"},
        "doi": "ignored",
    }
    assert _openalex_work_url(w) == "https://example.org/paper"


def test_openalex_work_url_doi_string() -> None:
    w = {"doi": "10.1000/182"}
    assert _openalex_work_url(w) == "https://doi.org/10.1000/182"


def test_openalex_work_url_openalex_id() -> None:
    w = {"id": "https://openalex.org/W123456789"}
    assert _openalex_work_url(w) == "https://openalex.org/W123456789"


def test_tavily_search_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="TAVILY_API_KEY"):
        tavily_search("x")


def test_tavily_search_parses_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "results": [
                    {"title": "A", "url": "https://a.test", "content": "body a"},
                    {"title": "B", "url": "", "content": ""},
                ]
            }

    class FakeClient:
        def __init__(self, *a, **k) -> None:
            pass

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *a) -> None:
            pass

        def post(self, url: str, json: dict) -> FakeResponse:
            assert "tavily" in url
            return FakeResponse()

    monkeypatch.setattr("research_system.clients.httpx.Client", FakeClient)
    hits = tavily_search("climate", max_results=2)
    assert len(hits) == 2
    assert hits[0]["title"] == "A"
    assert hits[0]["url"] == "https://a.test"
    assert "body a" in hits[0]["content"]


def test_openalex_work_search_success(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "results": [
            {
                "title": "Quantum widgets",
                "authorships": [{"author": {"display_name": "Ada Lovelace"}}],
                "publication_year": 2024,
                "abstract_inverted_index": {"Hello": [0], "world": [1]},
                "id": "https://openalex.org/Wabc",
                "doi": "https://doi.org/10.1/2",
            }
        ]
    }

    class FakeResponse:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return payload

    class FakeClient:
        def __init__(self, *a, **k) -> None:
            pass

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *a) -> None:
            pass

        def get(self, url: str, params: dict | None = None, headers: dict | None = None) -> FakeResponse:
            assert "openalex.org/works" in url
            return FakeResponse()

    monkeypatch.setattr("research_system.clients.httpx.Client", FakeClient)
    monkeypatch.delenv("OPENALEX_MAILTO", raising=False)
    papers = openalex_work_search("widgets", limit=5, max_retries=2)
    assert len(papers) == 1
    assert papers[0]["title"] == "Quantum widgets"
    assert papers[0]["authors"] == "Ada Lovelace"
    assert papers[0]["year"] == "2024"
    assert papers[0]["abstract"] == "Hello world"
    assert papers[0]["paper_id"] == "Wabc"


def test_http_retry_wait_s_numeric_retry_after() -> None:
    class R:
        headers = {"Retry-After": "3"}

    assert _http_retry_wait_s(R(), 0) == 3.0


def test_http_retry_wait_s_backoff() -> None:
    class R:
        headers = {}

    w = _http_retry_wait_s(R(), 2)
    assert 4.0 <= w <= 47.0
