from research_system.agent_runtime.types import AgentSkill

SKILLS: list[AgentSkill] = [
    AgentSkill(
        id="assemble_final_markdown",
        name="Assemble final markdown",
        description="Append critique summary and issues block to the draft for delivery.",
        when_to_use="Terminal assembly step after critique approves or max iterations.",
        inputs="Full graph state: `draft_report`, `critique_summary`, `critique_json`.",
        outputs="State update: `final_report`.",
        tools_or_sources="Pure string assembly (no LLM).",
    ),
]
