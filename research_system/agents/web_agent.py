from typing import Any, TypedDict

from langchain_core.runnables import RunnableLambda

from research_system.clients import tavily_search


class _WebIn(TypedDict, total=False):
    topic: str


def _gather_web(state: _WebIn) -> dict[str, Any]:
    topic = state.get("topic") or ""
    try:
        results = tavily_search(topic, max_results=8)
        return {"web_results": results, "error": ""}
    except Exception as e:
        return {"web_results": [], "error": f"Web search failed: {e}"}


web_research_agent = RunnableLambda(_gather_web).with_config(
    run_name="WebResearchAgent",
    tags=["multi-agent", "agent", "retrieval", "tavily"],
)
