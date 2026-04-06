from research_system.agent_runtime.guardrails import GuardrailViolation, register_input, register_output


def _has_topic(payload: dict) -> None:
    if not (payload.get("topic") or "").strip():
        raise GuardrailViolation("finalize: missing topic")


def _output_report(output: dict) -> None:
    if not isinstance(output, dict):
        raise GuardrailViolation("finalize: output must be dict")
    fr = output.get("final_report")
    if not isinstance(fr, str) or len(fr.strip()) < 20:
        raise GuardrailViolation("finalize: final_report missing or too small")
    if len(fr) > 600_000:
        raise GuardrailViolation("finalize: final_report too large")


register_input("finalize", _has_topic)
register_output("finalize", _output_report)
