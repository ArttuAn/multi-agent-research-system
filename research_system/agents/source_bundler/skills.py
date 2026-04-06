from research_system.agent_runtime.types import AgentSkill

SKILLS: list[AgentSkill] = [
    AgentSkill(
        id="build_source_index",
        name="Source index bundler",
        description="Merge web hits and OpenAlex works into a single numbered source index for writers and critics.",
        when_to_use="After retrieval; before any LLM synthesis.",
        inputs="Graph state: `web_results`, `papers`.",
        outputs="State update: `source_index` (markdown string).",
        tools_or_sources="Pure transformation (no external API).",
    ),
]
