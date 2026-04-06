"""LangSmith panel helpers."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
import pytest

from research_system import langsmith_feed as lf


def test_latency_seconds_property_float() -> None:
    r = SimpleNamespace(latency=1.234)
    assert lf._latency_seconds(r) == pytest.approx(1.234)


def test_latency_seconds_callable() -> None:
    r = SimpleNamespace(latency=lambda: 2.5)
    assert lf._latency_seconds(r) == pytest.approx(2.5)


def test_latency_seconds_timedelta() -> None:
    r = SimpleNamespace(latency=timedelta(seconds=3, milliseconds=500))
    assert lf._latency_seconds(r) == pytest.approx(3.5)


def test_latency_seconds_none() -> None:
    r = SimpleNamespace(latency=None)
    assert lf._latency_seconds(r) is None


def test_resolved_project_name_prefers_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGSMITH_PROJECT", "my-proj")
    monkeypatch.delenv("LANGCHAIN_PROJECT", raising=False)
    # Clear langsmith util cache if present
    try:
        from langsmith.utils import get_tracer_project, get_env_var

        get_tracer_project.cache_clear()
        get_env_var.cache_clear()
    except Exception:
        pass
    name = lf.resolved_project_name()
    assert name == "my-proj"
