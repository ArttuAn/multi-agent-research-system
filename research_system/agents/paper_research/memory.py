from research_system.agent_runtime.memory import get_memory_store

AGENT_ID = "paper_research"


def append_retrieval_summary(topic: str, work_count: int, had_error: bool) -> None:
    get_memory_store().append(
        AGENT_ID,
        topic,
        f"openalex_works={work_count}, error={had_error}",
        metadata={"work_count": work_count, "had_error": had_error},
    )
