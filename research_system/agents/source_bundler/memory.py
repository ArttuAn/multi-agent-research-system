from research_system.agent_runtime.memory import get_memory_store

AGENT_ID = "source_bundler"


def append_bundle_summary(topic: str, web_n: int, paper_n: int, index_chars: int) -> None:
    get_memory_store().append(
        AGENT_ID,
        topic,
        f"indexed web={web_n}, works={paper_n}, chars={index_chars}",
        metadata={"web_n": web_n, "paper_n": paper_n, "index_chars": index_chars},
    )
