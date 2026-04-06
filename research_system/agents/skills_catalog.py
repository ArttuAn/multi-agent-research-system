"""Aggregate declarative skills across all agents (for UIs, routing, or docs)."""

from research_system.agent_runtime.types import AgentSkill
from research_system.agents.critique.skills import SKILLS as CRITIQUE_SKILLS
from research_system.agents.finalize.skills import SKILLS as FINALIZE_SKILLS
from research_system.agents.paper_research.skills import SKILLS as PAPER_SKILLS
from research_system.agents.source_bundler.skills import SKILLS as BUNDLER_SKILLS
from research_system.agents.synthesis.skills import SKILLS as SYNTH_SKILLS
from research_system.agents.web_research.skills import SKILLS as WEB_SKILLS


def all_skills_by_agent() -> dict[str, list[AgentSkill]]:
    return {
        "web_research": list(WEB_SKILLS),
        "paper_research": list(PAPER_SKILLS),
        "source_bundler": list(BUNDLER_SKILLS),
        "synthesis": list(SYNTH_SKILLS),
        "critique": list(CRITIQUE_SKILLS),
        "finalize": list(FINALIZE_SKILLS),
    }


def all_skills_flat() -> list[AgentSkill]:
    out: list[AgentSkill] = []
    for skills in all_skills_by_agent().values():
        out.extend(skills)
    return out
