from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentSkill:
    """Declarative capability card for an agent (documentation + routing hints)."""

    id: str
    name: str
    description: str
    when_to_use: str
    inputs: str
    outputs: str
    tools_or_sources: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
