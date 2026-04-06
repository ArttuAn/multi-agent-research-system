from research_system.agent_runtime.hooks import register
from research_system.agents.source_bundler import memory as mem


def _post(ctx: dict) -> None:
    inp = ctx.get("input") or {}
    out = ctx.get("output") or {}
    topic = str(inp.get("topic") or "")
    if not topic:
        return
    wr = inp.get("web_results") or []
    pp = inp.get("papers") or []
    idx = (out.get("source_index") or "") if isinstance(out, dict) else ""
    wn = len(wr) if isinstance(wr, list) else 0
    pn = len(pp) if isinstance(pp, list) else 0
    mem.append_bundle_summary(topic, wn, pn, len(idx))


register("source_bundler", post=[_post])
