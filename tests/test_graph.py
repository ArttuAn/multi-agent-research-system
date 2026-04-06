"""LangGraph wiring."""

from __future__ import annotations

from research_system.graph import build_graph


def test_build_graph_compiles() -> None:
    g = build_graph()
    assert g is not None


def test_build_graph_has_expected_nodes() -> None:
    g = build_graph()
    graph = g.get_graph()
    names = set(graph.nodes)
    for n in (
        "gather_web",
        "gather_papers",
        "prepare_sources",
        "synthesize",
        "critique",
        "finalize",
        "__start__",
        "__end__",
    ):
        assert n in names, f"missing node {n}"
