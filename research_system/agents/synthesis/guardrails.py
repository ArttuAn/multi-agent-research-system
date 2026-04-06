from research_system.agent_runtime.guardrails import GuardrailViolation, register_input, register_output


def _inputs(payload: dict) -> None:
    if len((payload.get("topic") or "").strip()) < 2:
        raise GuardrailViolation("synthesis: topic too short")
    si = payload.get("source_index")
    if not isinstance(si, str):
        raise GuardrailViolation("synthesis: source_index must be a string")
    if len(si) > 1_500_000:
        raise GuardrailViolation("synthesis: source_index too large")
    rn = payload.get("revision_notes") or ""
    if isinstance(rn, str) and len(rn) > 80_000:
        raise GuardrailViolation("synthesis: revision_notes too large")


def _output_markdown(text: str) -> None:
    if not isinstance(text, str):
        raise GuardrailViolation("synthesis: output must be markdown string")
    if len(text) < 20:
        raise GuardrailViolation("synthesis: draft too short")
    if len(text) > 400_000:
        raise GuardrailViolation("synthesis: draft exceeds size limit")


register_input("synthesis", _inputs)
register_output("synthesis", _output_markdown)
