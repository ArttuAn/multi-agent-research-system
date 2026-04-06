"""
LangChain-built agents (Runnable chains / lambdas) used as LangGraph node bodies.

Each agent is configured with ``run_name`` and ``tags`` so LangSmith shows clear
hierarchy: Project → LangGraph run → per-agent spans (retrieval vs LLM).
"""

from research_system.agents.critique_agent import critique_agent
from research_system.agents.finalize_agent import finalize_agent
from research_system.agents.paper_agent import paper_research_agent
from research_system.agents.source_bundler import source_bundler_agent
from research_system.agents.synthesis_agent import synthesis_agent
from research_system.agents.web_agent import web_research_agent

__all__ = [
    "web_research_agent",
    "paper_research_agent",
    "source_bundler_agent",
    "synthesis_agent",
    "critique_agent",
    "finalize_agent",
]
