from research_system.agent_runtime.memory import get_memory_store

AGENT_ID = "web_research"


def append_retrieval_summary(topic: str, hit_count: int, had_error: bool) -> None:
    get_memory_store().append(
        AGENT_ID,
        topic,
        f"web_hits={hit_count}, error={had_error}",
        metadata={"hit_count": hit_count, "had_error": had_error},
    )
