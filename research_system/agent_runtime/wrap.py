from __future__ import annotations

from typing import Any, Callable

from research_system.agent_runtime import guardrails, hooks


def wrap_call(agent_id: str, core: Callable[[dict[str, Any]], Any]) -> Callable[[dict[str, Any]], Any]:
    """Pre/post hooks + input/output guardrails around a synchronous agent body."""

    def inner(state: dict[str, Any]) -> Any:
        ctx: dict[str, Any] = {"agent_id": agent_id, "input": dict(state)}
        hooks.run_pre(agent_id, ctx)
        guardrails.run_input(agent_id, state)
        out = core(state)
        ctx["output"] = out
        guardrails.run_output(agent_id, out)
        hooks.run_post(agent_id, ctx)
        return out

    return inner
