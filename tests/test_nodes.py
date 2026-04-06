"""Graph routing logic (no LLM)."""

from __future__ import annotations

import json

import pytest

from research_system.nodes import should_revise


def _state(
    *,
    iteration: int = 0,
    max_iterations: int = 3,
    approved: bool | None = None,
    bad_json: bool = False,
) -> dict:
    if bad_json:
        cj = "not-json"
    elif approved is None:
        cj = "{}"
    else:
        cj = json.dumps({"approved": approved})
    return {
        "iteration": iteration,
        "max_iterations": max_iterations,
        "critique_json": cj,
    }


def test_should_revise_finalize_when_max_iterations_reached() -> None:
    assert should_revise(_state(iteration=3, max_iterations=3)) == "finalize"


def test_should_revise_finalize_when_approved() -> None:
    assert should_revise(_state(iteration=1, approved=True)) == "finalize"


def test_should_revise_finalize_on_bad_json() -> None:
    assert should_revise(_state(bad_json=True)) == "finalize"


def test_should_revise_revise_when_not_approved_under_cap() -> None:
    assert should_revise(_state(iteration=1, max_iterations=5, approved=False)) == "revise"


def test_should_revise_revise_when_missing_approved_key() -> None:
    assert should_revise(_state(approved=None)) == "revise"
