from research_system.agent_runtime.guardrails import GuardrailViolation, register_input, register_output


def _topic_nonempty(payload: dict) -> None:
    t = (payload.get("topic") or "").strip()
    if len(t) < 2:
        raise GuardrailViolation("paper_research: topic must be at least 2 characters")


def _output_shape(output: dict) -> None:
    if not isinstance(output, dict):
        raise GuardrailViolation("paper_research: output must be a dict state update")
    if "papers" not in output:
        raise GuardrailViolation("paper_research: missing papers key")


register_input("paper_research", _topic_nonempty)
register_output("paper_research", _output_shape)
