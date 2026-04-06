from research_system.agent_runtime.hooks import register
from research_system.agents.web_research import memory as mem


def _post(ctx: dict) -> None:
    inp = ctx.get("input") or {}
    out = ctx.get("output") or {}
    topic = str(inp.get("topic") or "")
    hits = out.get("web_results") if isinstance(out, dict) else []
    n = len(hits) if isinstance(hits, list) else 0
    err = bool((out.get("error") or "").strip()) if isinstance(out, dict) else False
    if topic:
        mem.append_retrieval_summary(topic, n, err)


register("web_research", pre=[], post=[_post])
