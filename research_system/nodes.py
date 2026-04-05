import json
import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from research_system.clients import semantic_scholar_search, tavily_search
from research_system.state import ResearchState


def _model() -> ChatOpenAI:
    name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=name, temperature=0.2)


def _build_source_index(state: ResearchState) -> str:
    lines: list[str] = []
    for i, w in enumerate(state.get("web_results") or [], start=1):
        lines.append(f"[W{i}] WEB — {w.get('title','')}\n   URL: {w.get('url','')}\n   Excerpt: {w.get('content','')[:1200]}")
    for j, p in enumerate(state.get("papers") or [], start=1):
        lines.append(
            f"[P{j}] PAPER — {p.get('title','')}\n"
            f"   Authors: {p.get('authors','')}; Year: {p.get('year','')}\n"
            f"   URL: {p.get('url','')}\n"
            f"   Abstract: {(p.get('abstract') or '')[:1500]}"
        )
    return "\n\n".join(lines) if lines else "(no sources retrieved)"


def node_gather_web(state: ResearchState) -> dict[str, Any]:
    topic = state["topic"]
    try:
        results = tavily_search(topic, max_results=8)
    except Exception as e:
        return {"error": f"Web search failed: {e}", "web_results": []}
    return {"web_results": results, "error": ""}


def node_gather_papers(state: ResearchState) -> dict[str, Any]:
    topic = state["topic"]
    try:
        papers = semantic_scholar_search(topic, limit=10)
    except Exception as e:
        return {"error": (state.get("error") or "") + f"\nPaper search failed: {e}", "papers": []}
    return {"papers": papers}


def node_prepare_sources(state: ResearchState) -> dict[str, Any]:
    return {"source_index": _build_source_index(state)}


SYNTH_SYSTEM = """You are a senior policy and technology research analyst.
Write a structured report that ONLY uses facts supported by the provided sources.
Every non-trivial factual claim must include an inline citation using the exact tags [Wn] for web and [Pm] for papers.
If the sources are silent on a point, write "Not addressed in retrieved sources" instead of guessing.
Use clear markdown with these sections:
## Executive summary
## Key developments (bullet list with citations)
## Academic perspectives (from papers, with citations)
## Open questions / gaps
## Source list
At the end, repeat each [Wn] and [Pm] with title and URL from the source index."""


def node_synthesize(state: ResearchState) -> dict[str, Any]:
    topic = state["topic"]
    src = state.get("source_index") or ""
    prior = state.get("revision_guidance") or ""
    extra = ""
    if prior.strip():
        extra = f"\n\nRevise the previous draft using this critique feedback:\n{prior}\n"

    human = (
        f"Topic: {topic}\n\nSOURCE INDEX (only allowed evidence):\n{src}{extra}\n"
        "Produce the full markdown report now."
    )
    llm = _model()
    msg = llm.invoke(
        [SystemMessage(content=SYNTH_SYSTEM), HumanMessage(content=human)]
    )
    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    return {"draft_report": text, "iteration": int(state.get("iteration") or 0) + 1}


class CritiqueResult(BaseModel):
    approved: bool = Field(description="True if no unsupported or contradictory claims")
    hallucination_risk: str = Field(description="low|medium|high")
    issues: list[str] = Field(default_factory=list, description="Specific problems with citations or claims")
    revision_guidance: str = Field(
        default="",
        description="Concrete edits if not approved; empty if approved",
    )


CRITIQUE_SYSTEM = """You are an independent fact-checker and editor.
Compare the draft report to the SOURCE INDEX only.
Flag any factual claim not clearly entailed by a cited source, wrong citations, or invented details.
Respond with structured JSON matching the schema (approved, hallucination_risk, issues, revision_guidance)."""


def node_critique(state: ResearchState) -> dict[str, Any]:
    src = state.get("source_index") or ""
    draft = state.get("draft_report") or ""
    llm = _model().with_structured_output(CritiqueResult)
    human = f"SOURCE INDEX:\n{src}\n\nDRAFT REPORT:\n{draft}"
    result: CritiqueResult = llm.invoke(
        [SystemMessage(content=CRITIQUE_SYSTEM), HumanMessage(content=human)]
    )
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
    draft = state.get("draft_report") or ""
    crit = state.get("critique_summary") or ""
    block = f"\n\n---\n## Critique agent (hallucination check)\n{crit}\n"
    try:
        data = json.loads(state.get("critique_json") or "{}")
        if data.get("issues"):
            block += "\n**Issues flagged:**\n" + "\n".join(f"- {i}" for i in data["issues"][:12])
    except json.JSONDecodeError:
        pass
    return {"final_report": draft + block}


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
