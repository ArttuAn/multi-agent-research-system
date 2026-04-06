from research_system.agent_runtime.types import AgentSkill

SKILLS: list[AgentSkill] = [
    AgentSkill(
        id="openalex_work_search",
        name="OpenAlex scholarly search",
        description="Search OpenAlex works for the topic and return titles, authors, year, abstract, URL.",
        when_to_use="Need academic / grey-literature style records to complement web hits.",
        inputs="Graph state: `topic`, optional prior `error` from web agent.",
        outputs="State update: `papers` (list), may append to `error` on failure.",
        tools_or_sources="OpenAlex API (optional OPENALEX_MAILTO for polite pool)",
    ),
]
