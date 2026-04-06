from research_system.agent_runtime.guardrails import GuardrailViolation, register_input, register_output


def _topic_nonempty(payload: dict) -> None:
    t = (payload.get("topic") or "").strip()
    if len(t) < 2:
        raise GuardrailViolation("web_research: topic must be at least 2 characters")


def _topic_max_len(payload: dict) -> None:
    t = (payload.get("topic") or "").strip()
    if len(t) > 2000:
        raise GuardrailViolation("web_research: topic exceeds 2000 characters")


def _output_shape(output: dict) -> None:
    if not isinstance(output, dict):
        raise GuardrailViolation("web_research: output must be a dict state update")
    if "web_results" not in output:
        raise GuardrailViolation("web_research: missing web_results key")


register_input("web_research", _topic_nonempty, _topic_max_len)
register_output("web_research", _output_shape)
