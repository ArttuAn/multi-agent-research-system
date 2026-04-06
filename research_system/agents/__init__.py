"""
LangChain runnables per agent. Importing ``agent`` modules registers hooks and guardrails.
"""

from research_system.agents.critique.agent import critique_agent
from research_system.agents.critique.types import CritiqueResult
from research_system.agents.finalize.agent import finalize_agent
from research_system.agents.paper_research.agent import paper_research_agent
from research_system.agents.source_bundler.agent import source_bundler_agent
from research_system.agents.synthesis.agent import synthesis_agent
from research_system.agents.web_research.agent import web_research_agent

__all__ = [
    "CritiqueResult",
    "web_research_agent",
    "paper_research_agent",
    "source_bundler_agent",
    "synthesis_agent",
    "critique_agent",
    "finalize_agent",
]
