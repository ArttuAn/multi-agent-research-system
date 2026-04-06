"""Execution trace rows and state merge (Streamlit verification panels)."""

from __future__ import annotations

from research_system.execution_trace import _merge_partial, _step_record


def test_step_record_gather_web() -> None:
    before = {"topic": "EU AI Act"}
    partial = {"web_results": [{"title": "t"}], "error": ""}
    row = _step_record("gather_web", before, partial)
    assert row["node"] == "gather_web"
    assert row["inputs"]["topic"] == "EU AI Act"
    assert row["outputs"]["web_results_count"] == "1"
    assert any(c["name"] == "Tavily returned ≥1 hit" and c["ok"] for c in row["checks"])


def test_step_record_critique_parses_json() -> None:
    before = {"draft_report": "x", "source_index": "y"}
    partial = {
        "critique_json": '{"approved": true, "hallucination_risk": "low"}',
        "critique_summary": "ok",
    }
    row = _step_record("critique", before, partial)
    assert row["outputs"]["parsed_approved"] == "True"
    assert row["outputs"]["parsed_risk"] == "low"


def test_merge_partial_concatenates_prompt_trace() -> None:
    running: dict = {"topic": "t", "prompt_trace": [{"step": "a"}]}
    _merge_partial(running, {"prompt_trace": [{"step": "b"}], "iteration": 1})
    assert len(running["prompt_trace"]) == 2
    assert running["prompt_trace"][0]["step"] == "a"
    assert running["prompt_trace"][1]["step"] == "b"
    assert running["iteration"] == 1


def test_merge_partial_overwrites_scalar() -> None:
    running = {"draft_report": "old"}
    _merge_partial(running, {"draft_report": "new"})
    assert running["draft_report"] == "new"
