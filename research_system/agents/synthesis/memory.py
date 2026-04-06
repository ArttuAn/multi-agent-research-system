from research_system.agent_runtime.memory import get_memory_store

AGENT_ID = "synthesis"


def append_draft_stats(topic: str, char_len: int, iteration_hint: str) -> None:
    get_memory_store().append(
        AGENT_ID,
        topic,
        f"draft_chars={char_len}, phase={iteration_hint}",
        metadata={"char_len": char_len},
    )
