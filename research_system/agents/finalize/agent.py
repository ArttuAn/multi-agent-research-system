import json
from typing import Any

from langchain_core.runnables import RunnableLambda

from research_system.agent_runtime.wrap import wrap_call
from research_system.agents.finalize import guardrails as _g  # noqa: F401
from research_system.agents.finalize import hooks as _h  # noqa: F401
from research_system.state import ResearchState


def _core(state: ResearchState) -> dict[str, Any]:
    draft = state.get("draft_report") or ""
    crit = state.get("critique_summary") or ""
    block = f"\n\n---\n## Critique agent (hallucination check)\n{crit}\n"
    try:
        data = json.loads(state.get("critique_json") or "{}")
        if data.get("issues"):
            block += "\n**Issues flagged:**\n" + "\n".join(f"- {i}" for i in data["issues"][:12])
    except json.JSONDecodeError:
        pass
    return {"final_report": draft + block}


finalize_agent = RunnableLambda(wrap_call("finalize", _core)).with_config(
    run_name="FinalizeAgent",
    tags=["citegraph", "multi-agent", "agent", "assemble", "no-llm"],
)
