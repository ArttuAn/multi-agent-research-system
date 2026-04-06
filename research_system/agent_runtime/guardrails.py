from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

GuardIn = Callable[[dict[str, Any]], None]
GuardOut = Callable[[Any], None]

_input_guards: dict[str, list[GuardIn]] = defaultdict(list)
_output_guards: dict[str, list[GuardOut]] = defaultdict(list)


class GuardrailViolation(Exception):
    """Raised when an input or output fails a guard."""


def register_input(agent_id: str, *guards: GuardIn) -> None:
    _input_guards[agent_id].extend(guards)


def register_output(agent_id: str, *guards: GuardOut) -> None:
    _output_guards[agent_id].extend(guards)


def run_input(agent_id: str, payload: dict[str, Any]) -> None:
    for g in _input_guards.get(agent_id, []):
        g(payload)


def run_output(agent_id: str, output: Any) -> None:
    for g in _output_guards.get(agent_id, []):
        g(output)
