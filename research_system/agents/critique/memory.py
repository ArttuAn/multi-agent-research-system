from research_system.agent_runtime.memory import get_memory_store

AGENT_ID = "critique"


def append_verdict(topic: str, approved: bool, risk: str) -> None:
    get_memory_store().append(
        AGENT_ID,
        topic,
        f"approved={approved}, risk={risk}",
        metadata={"approved": approved, "risk": risk},
    )
