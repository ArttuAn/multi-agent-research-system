from typing import Any

from langchain_core.runnables import RunnableLambda

from research_system.state import ResearchState


def _build_source_index(state: ResearchState) -> str:
    lines: list[str] = []
    for i, w in enumerate(state.get("web_results") or [], start=1):
        lines.append(
            f"[W{i}] WEB — {w.get('title','')}\n   URL: {w.get('url','')}\n   Excerpt: {w.get('content','')[:1200]}"
        )
    for j, p in enumerate(state.get("papers") or [], start=1):
        lines.append(
            f"[P{j}] PAPER — {p.get('title','')}\n"
            f"   Authors: {p.get('authors','')}; Year: {p.get('year','')}\n"
            f"   URL: {p.get('url','')}\n"
            f"   Abstract: {(p.get('abstract') or '')[:1500]}"
        )
    return "\n\n".join(lines) if lines else "(no sources retrieved)"


def _bundle(state: ResearchState) -> dict[str, Any]:
    return {"source_index": _build_source_index(state)}


source_bundler_agent = RunnableLambda(_bundle).with_config(
    run_name="SourceBundlerAgent",
    tags=["multi-agent", "agent", "prepare", "no-llm"],
)
