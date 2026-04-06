from research_system.agent_runtime.hooks import register
from research_system.agents.finalize import memory as mem


def _post(ctx: dict) -> None:
    inp = ctx.get("input") or {}
    out = ctx.get("output") or {}
    topic = str(inp.get("topic") or "")
    fr = out.get("final_report") if isinstance(out, dict) else ""
    if topic and isinstance(fr, str):
        mem.append_delivery(topic, len(fr))


register("finalize", post=[_post])
