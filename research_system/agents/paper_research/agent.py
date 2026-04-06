from typing import Any, TypedDict

from langchain_core.runnables import RunnableLambda

from research_system.agent_runtime.wrap import wrap_call
from research_system.agents.paper_research import guardrails as _g  # noqa: F401
from research_system.agents.paper_research import hooks as _h  # noqa: F401
from research_system.clients import openalex_work_search


class _PaperIn(TypedDict, total=False):
    topic: str
    error: str


def _core(state: _PaperIn) -> dict[str, Any]:
    topic = state.get("topic") or ""
    try:
        papers = openalex_work_search(topic, limit=8)
        return {"papers": papers}
    except Exception as e:
        return {
            "error": (state.get("error") or "") + f"\nOpenAlex search failed: {e}",
            "papers": [],
        }


paper_research_agent = RunnableLambda(wrap_call("paper_research", _core)).with_config(
    run_name="PaperResearchAgent",
    tags=["multi-agent", "agent", "retrieval", "openalex"],
)
