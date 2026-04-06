import json
from typing import Any

from research_system.agents import (
    critique_agent,
    finalize_agent,
    paper_research_agent,
    source_bundler_agent,
    synthesis_agent,
    web_research_agent,
)
from research_system.agents.critique_agent import CritiqueResult
from research_system.state import ResearchState


def node_gather_web(state: ResearchState) -> dict[str, Any]:
    return web_research_agent.invoke(dict(state))


def node_gather_papers(state: ResearchState) -> dict[str, Any]:
    return paper_research_agent.invoke(dict(state))


def node_prepare_sources(state: ResearchState) -> dict[str, Any]:
    return source_bundler_agent.invoke(dict(state))


def node_synthesize(state: ResearchState) -> dict[str, Any]:
    topic = state["topic"]
    src = state.get("source_index") or ""
    prior = (state.get("revision_guidance") or "").strip()
    revision_notes = (
        f"\n\nRevise the previous draft using this critique feedback:\n{prior}\n" if prior else ""
    )
    text = synthesis_agent.invoke(
        {"topic": topic, "source_index": src, "revision_notes": revision_notes}
    )
    return {"draft_report": text, "iteration": int(state.get("iteration") or 0) + 1}


def node_critique(state: ResearchState) -> dict[str, Any]:
    src = state.get("source_index") or ""
    draft = state.get("draft_report") or ""
    result: CritiqueResult = critique_agent.invoke({"source_index": src, "draft": draft})
    payload = result.model_dump_json()
    summary = (
        f"Risk: {result.hallucination_risk}; approved={result.approved}. "
        + ("; ".join(result.issues[:5]) if result.issues else "No issues listed.")
    )
    return {
        "critique_json": payload,
        "critique_summary": summary,
        "revision_guidance": result.revision_guidance if not result.approved else "",
    }


def node_finalize(state: ResearchState) -> dict[str, Any]:
    return finalize_agent.invoke(dict(state))


def should_revise(state: ResearchState) -> str:
    if int(state.get("iteration") or 0) >= int(state.get("max_iterations") or 2):
        return "finalize"
    try:
        data = json.loads(state.get("critique_json") or "{}")
        if data.get("approved"):
            return "finalize"
    except json.JSONDecodeError:
        return "finalize"
    return "revise"
