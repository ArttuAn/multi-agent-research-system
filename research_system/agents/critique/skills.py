from research_system.agent_runtime.types import AgentSkill

SKILLS: list[AgentSkill] = [
    AgentSkill(
        id="structured_hallucination_critique",
        name="Structured hallucination critique",
        description="Compare draft report to source index only; emit structured verdict and revision guidance.",
        when_to_use="After each synthesis pass, before routing to revise or finalize.",
        inputs="`source_index`, `draft` (markdown).",
        outputs="`CritiqueResult` (Pydantic) → serialized to state as critique_json + summary fields.",
        tools_or_sources="OpenAI structured output",
    ),
]
