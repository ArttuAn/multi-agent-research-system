from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from research_system.agents.model import get_chat_model


class CritiqueResult(BaseModel):
    approved: bool = Field(description="True if no unsupported or contradictory claims")
    hallucination_risk: str = Field(description="low|medium|high")
    issues: list[str] = Field(default_factory=list, description="Specific problems with citations or claims")
    revision_guidance: str = Field(
        default="",
        description="Concrete edits if not approved; empty if approved",
    )


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


def _invoke_critique(payload: dict[str, Any]) -> CritiqueResult:
    return _critique_chain().invoke(payload)


critique_agent = RunnableLambda(_invoke_critique).with_config(
    run_name="CritiqueAgent",
    tags=["multi-agent", "agent", "llm", "quality", "hallucination"],
)
