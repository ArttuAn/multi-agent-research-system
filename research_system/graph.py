from typing import Any

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from research_system.nodes import (
    node_critique,
    node_finalize,
    node_gather_papers,
    node_gather_web,
    node_prepare_sources,
    node_synthesize,
    should_revise,
)
from research_system.execution_trace import merge_trace_from_stream
from research_system.state import ResearchState

load_dotenv()


def build_graph() -> CompiledStateGraph:
    g = StateGraph(ResearchState)
    g.add_node("gather_web", node_gather_web)
    g.add_node("gather_papers", node_gather_papers)
    g.add_node("prepare_sources", node_prepare_sources)
    g.add_node("synthesize", node_synthesize)
    g.add_node("critique", node_critique)
    g.add_node("finalize", node_finalize)

    g.add_edge(START, "gather_web")
    g.add_edge("gather_web", "gather_papers")
    g.add_edge("gather_papers", "prepare_sources")
    g.add_edge("prepare_sources", "synthesize")
    g.add_edge("synthesize", "critique")
    g.add_conditional_edges(
        "critique",
        should_revise,
        {"revise": "synthesize", "finalize": "finalize"},
    )
    g.add_edge("finalize", END)
    return g.compile()


def run_research(
    topic: str,
    max_iterations: int = 3,
    *,
    collect_trace: bool = False,
) -> dict[str, Any]:
    """Run the full LangGraph pipeline and return the final state dict.

    If collect_trace is True, the returned dict includes ``execution_trace``: a list of
    per-node records with inputs, outputs, and verification checks for UI display.
    """
    graph = build_graph()
    initial: ResearchState = {
        "topic": topic,
        "web_results": [],
        "papers": [],
        "source_index": "",
        "draft_report": "",
        "critique_json": "",
        "critique_summary": "",
        "revision_guidance": "",
        "iteration": 0,
        "max_iterations": max_iterations,
        "final_report": "",
        "error": "",
    }
    if not collect_trace:
        return dict(graph.invoke(initial))
    running, trace = merge_trace_from_stream(graph, initial)
    out = dict(running)
    out["execution_trace"] = trace
    return out
