"""
Streamlit live demo for the Multi-Agent Research System.
Run locally: streamlit run app.py
Deploy: https://streamlit.io/cloud — set secrets TAVILY_API_KEY and OPENAI_API_KEY.
"""

from __future__ import annotations

import html
import os

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# override=True so edits to .env apply on each Streamlit rerun without restarting the server
load_dotenv(override=True)

# LangSmith caches env lookups; clear after reload so tracing toggles/project name updates apply without restarting Streamlit.
try:
    import langsmith.utils as _ls_utils

    if hasattr(_ls_utils.get_env_var, "cache_clear"):
        _ls_utils.get_env_var.cache_clear()
    if hasattr(_ls_utils.get_tracer_project, "cache_clear"):
        _ls_utils.get_tracer_project.cache_clear()
except Exception:
    pass

_MERMAID_FLOW = """
flowchart TB
    START([Start]) --> GW[gather_web]
    GW --> GP[gather_papers]
    GP --> PS[prepare_sources]
    PS --> SY[synthesize]
    SY --> CR[critique]
    CR -->|revise| SY
    CR -->|finalize| FN[finalize]
    FN --> ENDN([End])
"""


def _secrets_to_env() -> None:
    """Map Streamlit Cloud secrets to os.environ if present."""
    try:
        s = st.secrets
        for key in (
            "TAVILY_API_KEY",
            "OPENAI_API_KEY",
            "OPENAI_MODEL",
            "OPENALEX_MAILTO",
            "LANGSMITH_TRACING",
            "LANGSMITH_TRACING_V2",
            "LANGSMITH_API_KEY",
            "LANGSMITH_PROJECT",
            "LANGSMITH_ENDPOINT",
            "LANGCHAIN_TRACING_V2",
            "LANGCHAIN_API_KEY",
            "LANGCHAIN_PROJECT",
            "LANGCHAIN_ENDPOINT",
        ):
            if key in s and not os.environ.get(key):
                os.environ[key] = str(s[key])
    except Exception:
        pass


def _render_mermaid(diagram: str, height: int = 440) -> None:
    """Render Mermaid inside an isolated iframe (Streamlit component)."""
    safe = html.escape(diagram.strip())
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
</head>
<body style="margin:0;background:#f8fafc;">
<div class="mermaid">{safe}</div>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: "neutral", securityLevel: "loose" }});
</script>
</body></html>"""
    components.html(page, height=height, scrolling=False)


def _render_step_trace(trace: list[dict]) -> None:
    st.subheader("Step verification (last run)")
    st.caption("Inputs are read from graph state **before** each node; outputs are that node’s returned state update.")
    for i, step in enumerate(trace, start=1):
        node = step.get("node", "?")
        with st.expander(f"Step {i}: `{node}` — inputs / outputs / checks", expanded=(i <= 2)):
            in_col, out_col = st.columns(2)
            with in_col:
                st.markdown("**Inputs**")
                for k, v in (step.get("inputs") or {}).items():
                    st.markdown(f"*{k}*")
                    st.code(v or "—", language=None)
            with out_col:
                st.markdown("**Outputs**")
                for k, v in (step.get("outputs") or {}).items():
                    st.markdown(f"*{k}*")
                    st.code(v or "—", language=None)
            st.markdown("**Checks**")
            for ch in step.get("checks") or []:
                ok = ch.get("ok")
                name = ch.get("name", "")
                detail = ch.get("detail") or ""
                icon = "✅" if ok else "⚠️"
                line = f"{icon} **{name}**"
                if detail:
                    line += f" — {detail}"
                st.markdown(line)


st.set_page_config(
    page_title="Multi-Agent Research (LangGraph)",
    page_icon="🔬",
    layout="wide",
)

_secrets_to_env()

if "viz_result" not in st.session_state:
    st.session_state.viz_result = None
if "viz_trace" not in st.session_state:
    st.session_state.viz_trace = []

st.title("Multi-Agent Research System")
st.caption(
    "LangGraph orchestration · LangChain agents · Tavily + OpenAlex · "
    "LangSmith when tracing + API key are set (see README)"
)

default_topic = "AI regulation in Europe 2026"
topic = st.text_input("Research topic", value=default_topic, help="Edit and run a full multi-agent research pass.")

col_a, col_b, col_c = st.columns(3)
with col_a:
    max_rounds = st.slider("Max synthesis rounds", 1, 4, 3)
with col_b:
    show_trace = st.checkbox("Show source trace (web + papers)", value=True)
with col_c:
    show_step_io = st.checkbox("Show step I/O verification", value=True)

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

        raw = run_research(topic, max_iterations=max_rounds, collect_trace=True)
        tr = raw.pop("execution_trace", [])
        st.session_state.viz_result = raw
        st.session_state.viz_trace = tr

result = st.session_state.viz_result
trace = st.session_state.viz_trace or []

if result is not None:
    if result.get("error"):
        st.warning(result["error"])

    st.subheader("Final report")
    st.markdown(result.get("final_report") or "_No report_")

    if show_trace:
        with st.expander("Retrieved web results"):
            for i, w in enumerate(result.get("web_results") or [], start=1):
                st.markdown(f"**[W{i}]** [{w.get('title','')}]({w.get('url','')})")
                st.caption((w.get("content") or "")[:800] + "…")

        with st.expander("Retrieved works (OpenAlex)"):
            for j, p in enumerate(result.get("papers") or [], start=1):
                st.markdown(f"**[P{j}]** {p.get('title','')}")
                st.caption(f"{p.get('authors','')} — {p.get('year','')} — {p.get('url','')}")

        with st.expander("Critique JSON"):
            st.code(result.get("critique_json") or "", language="json")

st.divider()
st.subheader("Pipeline flowchart")
st.caption("Solid path: first pass. `critique` can loop back to `synthesize` (revise) until approve or max rounds.")
_render_mermaid(_MERMAID_FLOW)

if trace and show_step_io:
    st.divider()
    _render_step_trace(trace)
elif not trace and show_step_io:
    st.info("Run the graph once to populate **step I/O verification** (inputs/outputs per node).")

st.divider()
st.markdown(
    """
**Architecture:** `gather_web` (Tavily) → `gather_papers` (OpenAlex) → `prepare_sources` →
`synthesize` (LLM, inline [Wn]/[Pm] citations) → `critique` (structured hallucination check) →
conditional **revise** loop or **finalize** (append critique summary).

APIs: [Tavily](https://tavily.com/) · [OpenAlex API](https://docs.openalex.org/)
"""
)
