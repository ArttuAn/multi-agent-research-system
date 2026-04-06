"""Structured critique schema."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from research_system.agents.critique.types import CritiqueResult


def test_critique_result_defaults() -> None:
    r = CritiqueResult(approved=False, hallucination_risk="high")
    assert r.issues == []
    assert r.revision_guidance == ""


def test_critique_result_roundtrip_json() -> None:
    r = CritiqueResult(
        approved=True,
        hallucination_risk="low",
        issues=["a"],
        revision_guidance="",
    )
    data = r.model_dump()
    r2 = CritiqueResult.model_validate(data)
    assert r2.approved is True


def test_critique_result_requires_risk() -> None:
    with pytest.raises(ValidationError):
        CritiqueResult(approved=True)  # type: ignore[call-arg]
