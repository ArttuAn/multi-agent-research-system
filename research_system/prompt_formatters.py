"""Render exact ChatPromptTemplate text as sent to the LLM (for audit PDFs)."""

from __future__ import annotations

from typing import Any

from research_system.agents.critique.agent import _critique_prompt
from research_system.agents.synthesis.agent import _synth_prompt


def _msg_role(msg: Any) -> str:
    t = getattr(msg, "type", None)
    if t in ("system", "human", "ai"):
        return str(t)
    name = msg.__class__.__name__
    if "System" in name:
        return "system"
    if "Human" in name:
        return "human"
    return name.lower()


def _msg_content(msg: Any) -> str:
    c = getattr(msg, "content", "")
    if isinstance(c, str):
        return c
    return str(c)


def format_synthesis_prompts(payload: dict[str, Any]) -> list[tuple[str, str]]:
    """Return (role, text) pairs exactly as formatted for the synthesis LLM call."""
    msgs = _synth_prompt.format_messages(**payload)
    return [(_msg_role(m), _msg_content(m)) for m in msgs]


def format_critique_prompts(source_index: str, draft: str) -> list[tuple[str, str]]:
    """Return (role, text) pairs for the critique LLM call."""
    msgs = _critique_prompt.format_messages(source_index=source_index, draft=draft)
    return [(_msg_role(m), _msg_content(m)) for m in msgs]
