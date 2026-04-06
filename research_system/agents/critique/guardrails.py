from research_system.agent_runtime.guardrails import GuardrailViolation, register_input, register_output
from research_system.agents.critique.types import CritiqueResult


def _inputs(payload: dict) -> None:
    if len((payload.get("topic") or "").strip()) < 2:
        raise GuardrailViolation("critique: topic too short for memory correlation")
    si = payload.get("source_index") or ""
    if not isinstance(si, str) or len(si.strip()) < 5:
        raise GuardrailViolation("critique: source_index missing or too small")
    d = payload.get("draft") or ""
    if not isinstance(d, str) or len(d.strip()) < 20:
        raise GuardrailViolation("critique: draft missing or too small")
    if len(d) > 500_000:
        raise GuardrailViolation("critique: draft too large")


def _output_critique(result: CritiqueResult) -> None:
    if not isinstance(result, CritiqueResult):
        raise GuardrailViolation("critique: output must be CritiqueResult")
    risk = (result.hallucination_risk or "").lower()
    if risk not in ("low", "medium", "high"):
        raise GuardrailViolation("critique: hallucination_risk must be low|medium|high")


register_input("critique", _inputs)
register_output("critique", _output_critique)
