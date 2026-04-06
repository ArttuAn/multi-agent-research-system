from typing import Any, TypedDict

from langchain_core.runnables import RunnableLambda

from research_system.clients import openalex_work_search


class _PaperIn(TypedDict, total=False):
    topic: str
    error: str


def _gather_papers(state: _PaperIn) -> dict[str, Any]:
    topic = state.get("topic") or ""
    try:
        papers = openalex_work_search(topic, limit=8)
        return {"papers": papers}
    except Exception as e:
        return {
            "error": (state.get("error") or "") + f"\nPaper search failed: {e}",
            "papers": [],
        }


paper_research_agent = RunnableLambda(_gather_papers).with_config(
    run_name="PaperResearchAgent",
    tags=["multi-agent", "agent", "retrieval", "openalex"],
)
