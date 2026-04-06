from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from research_system.agents.model import get_chat_model

SYNTH_SYSTEM = """You are a senior policy and technology research analyst.
Write a structured report that ONLY uses facts supported by the provided sources.
Every non-trivial factual claim must include an inline citation using the exact tags [Wn] for web and [Pm] for papers.
If the sources are silent on a point, write "Not addressed in retrieved sources" instead of guessing.
Use clear markdown with these sections:
## Executive summary
## Key developments (bullet list with citations)
## Academic perspectives (from papers, with citations)
## Open questions / gaps
## Source list
At the end, repeat each [Wn] and [Pm] with title and URL from the source index."""

SYNTH_HUMAN = """Topic: {topic}

SOURCE INDEX (only allowed evidence):
{source_index}
{revision_notes}

Produce the full markdown report now."""

_synth_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYNTH_SYSTEM),
        ("human", SYNTH_HUMAN),
    ]
)

_chain = None


def _synthesis_chain():
    """Lazy build so importing the package does not require OPENAI_API_KEY."""
    global _chain
    if _chain is None:
        _chain = _synth_prompt | get_chat_model() | StrOutputParser()
    return _chain


def _invoke_synthesis(payload: dict) -> str:
    return _synthesis_chain().invoke(payload)


synthesis_agent = RunnableLambda(_invoke_synthesis).with_config(
    run_name="SynthesisAgent",
    tags=["multi-agent", "agent", "llm", "report"],
)
