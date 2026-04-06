from research_system.agent_runtime.types import AgentSkill

SKILLS: list[AgentSkill] = [
    AgentSkill(
        id="cited_markdown_report",
        name="Cited research report",
        description="Produce structured markdown grounded strictly in the source index with [Wn]/[Pm] citations.",
        when_to_use="After `source_index` exists; may run multiple times when critique requests revision.",
        inputs="`topic`, `source_index`, `revision_notes`, optional `episodic_memory_block`.",
        outputs="Markdown string (draft report body).",
        tools_or_sources="OpenAI chat model via LangChain",
    ),
]
