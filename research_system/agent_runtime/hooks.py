from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

HookFn = Callable[[dict[str, Any]], None]

_pre: dict[str, list[HookFn]] = defaultdict(list)
_post: dict[str, list[HookFn]] = defaultdict(list)


def register(agent_id: str, *, pre: list[HookFn] | None = None, post: list[HookFn] | None = None) -> None:
    if pre:
        _pre[agent_id].extend(pre)
    if post:
        _post[agent_id].extend(post)


def run_pre(agent_id: str, ctx: dict[str, Any]) -> None:
    for fn in _pre.get(agent_id, []):
        fn(ctx)


def run_post(agent_id: str, ctx: dict[str, Any]) -> None:
    for fn in _post.get(agent_id, []):
        fn(ctx)
