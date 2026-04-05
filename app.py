"""
Streamlit live demo for the Multi-Agent Research System.
Run locally: streamlit run app.py
Deploy: https://streamlit.io/cloud — set secrets TAVILY_API_KEY and OPENAI_API_KEY.
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _secrets_to_env() -> None:
    """Map Streamlit Cloud secrets to os.environ if present."""
    try:
        s = st.secrets
        for key in ("TAVILY_API_KEY", "OPENAI_API_KEY", "OPENAI_MODEL", "SEMANTIC_SCHOLAR_API_KEY"):
            if key in s and not os.environ.get(key):
                os.environ[key] = str(s[key])
    except Exception:
        pass


st.set_page_config(
    page_title="Multi-Agent Research (LangGraph)",
    page_icon="🔬",
    layout="wide",
)

_secrets_to_env()

st.title("Multi-Agent Research System")
st.caption("LangGraph · Tavily · Semantic Scholar · synthesis + hallucination critique")

default_topic = "AI regulation in Europe 2026"
topic = st.text_input("Research topic", value=default_topic, help="Edit and run a full multi-agent research pass.")

col_a, col_b = st.columns(2)
with col_a:
    max_rounds = st.slider("Max synthesis rounds", 1, 4, 3)
with col_b:
    show_trace = st.checkbox("Show source trace (web + papers)", value=True)

run = st.button("Run research graph", type="primary")

if run:
    if not os.environ.get("TAVILY_API_KEY"):
        st.error("Set `TAVILY_API_KEY` in `.env` or Streamlit secrets.")
        st.stop()
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("Set `OPENAI_API_KEY` in `.env` or Streamlit secrets.")
        st.stop()

    with st.spinner("Running LangGraph (web → papers → synthesize → critique loop)…"):
        from research_system.graph import run_research

        result = run_research(topic, max_iterations=max_rounds)

    if result.get("error"):
        st.warning(result["error"])

    st.subheader("Final report")
    st.markdown(result.get("final_report") or "_No report_")

    if show_trace:
        with st.expander("Retrieved web results"):
            for i, w in enumerate(result.get("web_results") or [], start=1):
                st.markdown(f"**[W{i}]** [{w.get('title','')}]({w.get('url','')})")
                st.caption((w.get("content") or "")[:800] + "…")

        with st.expander("Retrieved papers (Semantic Scholar)"):
            for j, p in enumerate(result.get("papers") or [], start=1):
                st.markdown(f"**[P{j}]** {p.get('title','')}")
                st.caption(f"{p.get('authors','')} — {p.get('year','')} — {p.get('url','')}")

        with st.expander("Critique JSON"):
            st.code(result.get("critique_json") or "", language="json")

st.divider()
st.markdown(
    """
**Architecture:** `gather_web` (Tavily) → `gather_papers` (Semantic Scholar) → `prepare_sources` →
`synthesize` (LLM, inline [Wn]/[Pm] citations) → `critique` (structured hallucination check) →
conditional **revise** loop or **finalize** (append critique summary).

APIs: [Tavily](https://tavily.com/) · [Semantic Scholar](https://www.semanticscholar.org/product/api)
"""
)
