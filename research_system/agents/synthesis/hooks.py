from research_system.agent_runtime.hooks import register
from research_system.agents.synthesis import memory as mem


def _post(ctx: dict) -> None:
    inp = ctx.get("input") or {}
    out = ctx.get("output")
    topic = str(inp.get("topic") or "")
    if not topic or not isinstance(out, str):
        return
    phase = "revise" if (inp.get("revision_notes") or "").strip() else "first_draft"
    mem.append_draft_stats(topic, len(out), phase)


register("synthesis", post=[_post])
