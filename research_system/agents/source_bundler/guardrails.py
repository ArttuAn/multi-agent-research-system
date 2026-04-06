from research_system.agent_runtime.guardrails import GuardrailViolation, register_input, register_output


def _has_topic(payload: dict) -> None:
    if not (payload.get("topic") or "").strip():
        raise GuardrailViolation("source_bundler: missing topic")


def _output_index(output: dict) -> None:
    if not isinstance(output, dict):
        raise GuardrailViolation("source_bundler: output must be dict")
    if "source_index" not in output:
        raise GuardrailViolation("source_bundler: missing source_index")
    s = output.get("source_index")
    if not isinstance(s, str):
        raise GuardrailViolation("source_bundler: source_index must be str")
    if len(s) > 1_500_000:
        raise GuardrailViolation("source_bundler: source_index too large")


register_input("source_bundler", _has_topic)
register_output("source_bundler", _output_index)
