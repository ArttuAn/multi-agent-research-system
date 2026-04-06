from research_system.agent_runtime.memory import get_memory_store

AGENT_ID = "finalize"


def append_delivery(topic: str, final_chars: int) -> None:
    get_memory_store().append(
        AGENT_ID,
        topic,
        f"delivered_report_chars={final_chars}",
        metadata={"final_chars": final_chars},
    )
