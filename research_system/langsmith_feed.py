"""Fetch recent LangSmith runs for lightweight in-app charts (not a full LangSmith UI embed)."""

from __future__ import annotations

import os
from typing import Any

from langsmith.utils import LangSmithNotFoundError


def resolved_project_name() -> str:
    """
    Project name where traces are sent — must match list_runs lookup.

    Uses the same default chain as the tracer (including ``default`` when unset),
    not ``return_default_value=False`` (which can disagree with actual tracing).
    """
    try:
        from langsmith.utils import get_tracer_project

        name = get_tracer_project(return_default_value=True)
        if name:
            return str(name)
    except Exception:
        pass
    return (
        os.environ.get("LANGSMITH_PROJECT")
        or os.environ.get("LANGCHAIN_PROJECT")
        or "default"
    )


def langsmith_api_configured() -> bool:
    return bool(os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY"))


def _run_to_row(r: Any) -> dict[str, Any]:
    lat = r.latency()
    url = getattr(r, "url", None)
    return {
        "id": str(r.id),
        "name": (r.name or "run")[:80],
        "status": (r.status or "unknown")[:32],
        "latency_s": round(lat, 3) if lat is not None else None,
        "total_tokens": r.total_tokens,
        "started_at": r.start_time.isoformat()[:19] if r.start_time else "",
        "url": url,
    }


def fetch_recent_root_runs(
    *,
    project_name: str | None = None,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Return (runs, error). ``error`` is set on API failures (e.g. unknown project name).

    ``list_runs`` resolves the project via ``read_project``; a wrong name raises
    ``LangSmithNotFoundError`` — previously swallowed as an empty list.
    """
    if not langsmith_api_configured():
        return [], None
    proj = (project_name or "").strip() or resolved_project_name()
    try:
        from langsmith import Client
    except ImportError:
        return [], "langsmith package is not installed."

    client = Client()
    out: list[dict[str, Any]] = []

    try:
        for r in client.list_runs(project_name=proj, is_root=True, limit=limit):
            out.append(_run_to_row(r))
    except LangSmithNotFoundError as e:
        return [], (
            f"LangSmith project {proj!r} was not found. "
            f"Create it in the LangSmith UI or set **LANGSMITH_PROJECT** / **LANGCHAIN_PROJECT** "
            f"to the exact project name. ({e})"
        )
    except Exception as e:
        return [], f"LangSmith API error: {e}"

    if out:
        return out, None

    # Some LangGraph / LC versions omit is_root; take recent runs with no parent.
    try:
        cap = min(limit * 4, 80)
        for r in client.list_runs(project_name=proj, limit=cap):
            if getattr(r, "parent_run_id", None) is None:
                out.append(_run_to_row(r))
            if len(out) >= limit:
                break
    except Exception:
        pass

    if out:
        return out, None

    def _truthy(key: str) -> bool:
        return os.environ.get(key, "").strip().lower() in ("1", "true", "yes", "on")

    tracing_on = (
        _truthy("LANGSMITH_TRACING")
        or _truthy("LANGSMITH_TRACING_V2")
        or _truthy("LANGCHAIN_TRACING_V2")
    )
    hint = (
        "No runs in this project yet. "
        + (
            "**LANGSMITH_TRACING** / **LANGCHAIN_TRACING_V2** is not set to true — tracing may be off."
            if not tracing_on
            else "Run **Run pipeline** once with tracing on; new traces can take a few seconds to appear."
        )
    )
    return [], hint
