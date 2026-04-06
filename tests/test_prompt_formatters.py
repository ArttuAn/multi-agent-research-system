"""Prompt audit formatters (exact template text)."""

from __future__ import annotations

from research_system.prompt_formatters import format_critique_prompts, format_synthesis_prompts


def test_format_synthesis_prompts_roles_and_content() -> None:
    pairs = format_synthesis_prompts(
        {
            "topic": "Test topic",
            "source_index": "[W1] x",
            "revision_notes": "",
            "episodic_memory_block": "",
        }
    )
    roles = [p[0] for p in pairs]
    assert "system" in roles and "human" in roles
    blob = " ".join(p[1] for p in pairs)
    assert "Test topic" in blob
    assert "[W1]" in blob


def test_format_critique_prompts_includes_draft() -> None:
    pairs = format_critique_prompts("INDEX", "DRAFT")
    blob = " ".join(p[1] for p in pairs)
    assert "INDEX" in blob
    assert "DRAFT" in blob


def test_format_critique_prompts_two_messages() -> None:
    pairs = format_critique_prompts("s", "d")
    assert len(pairs) >= 2
