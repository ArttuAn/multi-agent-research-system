import json
from typing import Any

from research_system.agent_runtime.memory import get_memory_store
from research_system.agents import (
    CritiqueResult,
    critique_agent,
    finalize_agent,
    paper_research_agent,
    source_bundler_agent,
    synthesis_agent,
    web_research_agent,
)
from research_system.prompt_formatters import format_critique_prompts, format_synthesis_prompts
from research_system.state import ResearchState


def node_gather_web(state: ResearchState) -> dict[str, Any]:
    topic = str(state.get("topic") or "")
    out = web_research_agent.invoke(dict(state))
    n = len(out.get("web_results") or [])
    err = (out.get("error") or "").strip()
    titles = [((r.get("title") or "")[:100]) for r in (out.get("web_results") or [])[:5]]
    trace = [
        {
            "step": "gather_web",
            "title": "Web retrieval — Tavily request → response",
            "kind": "retrieval_api",
            "before_processing": {
                "request": (
                    f"Search query: {topic}\n"
                    f"API: Tavily POST https://api.tavily.com/search\n"
                    f"Parameters: search_depth=advanced, max_results=8"
                ),
            },
            "after_processing": {
                "hits": str(n),
                "error": err or "(none)",
                "sample_titles": "\n".join(f"- {t}" for t in titles) if titles else "(none)",
            },
        }
    ]
    return {**out, "prompt_trace": trace}


def node_gather_papers(state: ResearchState) -> dict[str, Any]:
    topic = str(state.get("topic") or "")
    out = paper_research_agent.invoke(dict(state))
    n = len(out.get("papers") or [])
    err = (out.get("error") or "").strip()
    titles = [((p.get("title") or "")[:100]) for p in (out.get("papers") or [])[:5]]
    trace = [
        {
            "step": "gather_papers",
            "title": "Works retrieval — OpenAlex request → response",
            "kind": "retrieval_api",
            "before_processing": {
                "request": (
                    f"Search query: {topic}\n"
                    f"API: OpenAlex GET /works?search=…&per-page=8\n"
                    f"(optional OPENALEX_MAILTO for polite pool)"
                ),
            },
            "after_processing": {
                "works": str(n),
                "error": err or "(none)",
                "sample_titles": "\n".join(f"- {t}" for t in titles) if titles else "(none)",
            },
        }
    ]
    return {**out, "prompt_trace": trace}


def node_prepare_sources(state: ResearchState) -> dict[str, Any]:
    topic = str(state.get("topic") or "")
    wb = len(state.get("web_results") or [])
    pb = len(state.get("papers") or [])
    out = source_bundler_agent.invoke(dict(state))
    idx = out.get("source_index") or ""
    cap = 30_000
    trace = [
        {
            "step": "prepare_sources",
            "title": "Source index — state before bundle → combined index text",
            "kind": "transform",
            "before_processing": {
                "context": f"Topic: {topic}\nweb_results count: {wb}\npapers count: {pb}",
            },
            "after_processing": {
                "source_index_chars": str(len(idx)),
                "source_index_body": idx[:cap] + ("… [truncated]" if len(idx) > cap else ""),
            },
        }
    ]
    return {**out, "prompt_trace": trace}


def node_synthesize(state: ResearchState) -> dict[str, Any]:
    topic = state["topic"]
    src = state.get("source_index") or ""
    prior = (state.get("revision_guidance") or "").strip()
    revision_notes = (
        f"\n\nRevise the previous draft using this critique feedback:\n{prior}\n" if prior else ""
    )
    mem_lines = get_memory_store().format_context_for_prompt(topic, max_entries=8)
    episodic_block = ""
    if mem_lines.strip():
        episodic_block = (
            "## Episodic memory (prior agent notes for this topic)\n" + mem_lines + "\n\n"
        )
    payload = {
        "topic": topic,
        "source_index": src,
        "revision_notes": revision_notes,
        "episodic_memory_block": episodic_block,
    }
    pairs = format_synthesis_prompts(payload)
    sys_t = pairs[0][1] if pairs else ""
    hum_t = pairs[1][1] if len(pairs) > 1 else ""
    text = synthesis_agent.invoke(payload)
    new_iter = int(state.get("iteration") or 0) + 1
    prev_len = len(state.get("draft_report") or "")
    cap_out = 14_000
    trace = [
        {
            "step": "synthesize",
            "title": f"Synthesis LLM — pass {new_iter} (prompts sent → markdown draft)",
            "kind": "llm_chat",
            "before_processing": {
                "system": sys_t,
                "human": hum_t,
                "extra": f"Previous draft length (chars) before this pass: {prev_len}",
            },
            "after_processing": {
                "draft_chars": str(len(text)),
                "draft_markdown": text[:cap_out] + ("… [truncated]" if len(text) > cap_out else ""),
            },
        }
    ]
    return {"draft_report": text, "iteration": new_iter, "prompt_trace": trace}


def node_critique(state: ResearchState) -> dict[str, Any]:
    src = state.get("source_index") or ""
    draft = state.get("draft_report") or ""
    pairs = format_critique_prompts(src, draft)
    sys_t = pairs[0][1] if pairs else ""
    hum_t = pairs[1][1] if len(pairs) > 1 else ""
    result: CritiqueResult = critique_agent.invoke(
        {
            "topic": state["topic"],
            "source_index": src,
            "draft": draft,
        }
    )
    payload = result.model_dump_json()
    summary = (
        f"Risk: {result.hallucination_risk}; approved={result.approved}. "
        + ("; ".join(result.issues[:5]) if result.issues else "No issues listed.")
    )
    cap_j = 10_000
    trace = [
        {
            "step": "critique",
            "title": f"Critique LLM — after synthesis pass {state.get('iteration')}",
            "kind": "llm_structured",
            "before_processing": {
                "system": sys_t,
                "human": hum_t,
            },
            "after_processing": {
                "summary": summary,
                "approved": str(result.approved),
                "hallucination_risk": result.hallucination_risk,
                "critique_json": payload[:cap_j] + ("… [truncated]" if len(payload) > cap_j else ""),
            },
        }
    ]
    return {
        "critique_json": payload,
        "critique_summary": summary,
        "revision_guidance": result.revision_guidance if not result.approved else "",
        "prompt_trace": trace,
    }


def node_finalize(state: ResearchState) -> dict[str, Any]:
    draft = state.get("draft_report") or ""
    crit = state.get("critique_summary") or ""
    cj = state.get("critique_json") or ""
    out = finalize_agent.invoke(dict(state))
    fr = out.get("final_report") or ""
    cap_d, cap_f = 5000, 14_000
    trace = [
        {
            "step": "finalize",
            "title": "Finalize — inputs to assembler → final report",
            "kind": "transform",
            "before_processing": {
                "context": "Concatenate draft_report + critique block (+ issues list from JSON).",
                "draft_excerpt": draft[:cap_d] + ("… [truncated]" if len(draft) > cap_d else ""),
                "critique_summary": crit,
                "critique_json_excerpt": cj[:4000] + ("…" if len(cj) > 4000 else ""),
            },
            "after_processing": {
                "final_report_chars": str(len(fr)),
                "final_report": fr[:cap_f] + ("… [truncated]" if len(fr) > cap_f else ""),
            },
        }
    ]
    return {**out, "prompt_trace": trace}


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
