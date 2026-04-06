from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from research_system.agent_runtime.wrap import wrap_call
from research_system.agents.critique import guardrails as _g  # noqa: F401
from research_system.agents.critique import hooks as _h  # noqa: F401
from research_system.agents.critique.types import CritiqueResult
from research_system.agents.model import get_chat_model

CRITIQUE_SYSTEM = """You are an independent fact-checker and editor.
Compare the draft report to the SOURCE INDEX only.
Flag any factual claim not clearly entailed by a cited source, wrong citations, or invented details.
Respond with structured JSON matching the schema (approved, hallucination_risk, issues, revision_guidance)."""

_critique_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CRITIQUE_SYSTEM),
        ("human", "SOURCE INDEX:\n{source_index}\n\nDRAFT REPORT:\n{draft}"),
    ]
)

_chain = None


def _critique_chain():
    global _chain
    if _chain is None:
        _chain = _critique_prompt | get_chat_model().with_structured_output(CritiqueResult)
    return _chain


def _core(payload: dict[str, Any]) -> CritiqueResult:
    return _critique_chain().invoke(
        {"source_index": payload["source_index"], "draft": payload["draft"]}
    )


critique_agent = RunnableLambda(wrap_call("critique", _core)).with_config(
    run_name="CritiqueAgent",
    tags=["multi-agent", "agent", "llm", "quality", "hallucination"],
)
