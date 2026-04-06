from research_system.agent_runtime.types import AgentSkill

SKILLS: list[AgentSkill] = [
    AgentSkill(
        id="tavily_web_search",
        name="Tavily web search",
        description="Run an advanced web search for the research topic and return normalized hits (title, URL, excerpt).",
        when_to_use="Need fresh web evidence, news, or policy pages for the user topic.",
        inputs="Graph state field `topic` (string).",
        outputs="State update: `web_results` (list of hits), `error` (string).",
        tools_or_sources="Tavily Search API",
    ),
]
