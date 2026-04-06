"""Non-LLM agents: source index and final report assembly."""

from __future__ import annotations

import json

from research_system.agents.finalize.agent import finalize_agent
from research_system.agents.source_bundler.agent import source_bundler_agent


def test_source_bundler_builds_index() -> None:
    state = {
        "topic": "t",
        "web_results": [
            {"title": "W1", "url": "https://w1", "content": "web body"},
        ],
        "papers": [
            {
                "title": "P1",
                "authors": "A",
                "year": "2020",
                "url": "https://p1",
                "abstract": "abs",
            },
        ],
    }
    out = source_bundler_agent.invoke(state)
    idx = out.get("source_index") or ""
    assert "[W1]" in idx and "WEB" in idx
    assert "[P1]" in idx and "PAPER" in idx


def test_finalize_appends_critique_block() -> None:
    state = {
        "topic": "t",
        "draft_report": "## Report\nBody.",
        "critique_summary": "Risk: low",
        "critique_json": json.dumps({"approved": True, "issues": ["minor"]}),
    }
    out = finalize_agent.invoke(state)
    final = out.get("final_report") or ""
    assert "## Report" in final
    assert "Critique agent" in final
    assert "Risk: low" in final
    assert "minor" in final
