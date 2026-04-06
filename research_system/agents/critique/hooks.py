from research_system.agent_runtime.hooks import register
from research_system.agents.critique import memory as mem
from research_system.agents.critique.types import CritiqueResult


def _post(ctx: dict) -> None:
    inp = ctx.get("input") or {}
    out = ctx.get("output")
    topic = str(inp.get("topic") or "")
    if not topic or not isinstance(out, CritiqueResult):
        return
    mem.append_verdict(topic, out.approved, out.hallucination_risk)


register("critique", post=[_post])
