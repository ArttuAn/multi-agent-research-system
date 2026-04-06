"""
Streamlit live demo for the Multi-Agent Research System.
Run locally: streamlit run app.py
Deploy: https://streamlit.io/cloud — set secrets TAVILY_API_KEY and OPENAI_API_KEY.
"""

from __future__ import annotations

import os
import re

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv(override=True)

try:
    import langsmith.utils as _ls_utils

    if hasattr(_ls_utils.get_env_var, "cache_clear"):
        _ls_utils.get_env_var.cache_clear()
    if hasattr(_ls_utils.get_tracer_project, "cache_clear"):
        _ls_utils.get_tracer_project.cache_clear()
except Exception:
    pass

_MERMAID_FLOW = r"""
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "system-ui, -apple-system, 'Segoe UI', sans-serif",
    "fontSize": "17px",
    "primaryColor": "#e8eaf6",
    "primaryTextColor": "#1e293b",
    "primaryBorderColor": "#5b6cf0",
    "secondaryColor": "#f1f5f9",
    "tertiaryColor": "#ffffff",
    "lineColor": "#7c8ced",
    "clusterBkg": "#f8fafc",
    "clusterBorder": "#cbd5e1",
    "titleColor": "#334155"
  },
  "flowchart": { "curve": "basis", "padding": 18, "nodeSpacing": 42, "rankSpacing": 52 }
}}%%
flowchart TB
    subgraph R[" Retrieval "]
        direction TB
        GW["Web search<br/><b>Tavily</b>"] --> GP["Scholarly works<br/><b>OpenAlex</b>"]
        GP --> PS["Prepare<br/>source index"]
    end
    subgraph W[" Draft & critique "]
        direction TB
        SY["Synthesis<br/><i>LLM</i>"] --> CR["Critique<br/><i>LLM</i>"]
        CR -->|revise| SY
        CR -->|finalize| FN["Finalize<br/>report"]
    end
    START([Start]) --> GW
    PS --> SY
    FN --> ENDN([Done])
"""


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

            html, body, [class*="css"] {
                font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
            }
            .stApp, .stApp p, .stApp li, .stApp label {
                font-size: 1.0625rem;
                line-height: 1.55;
            }
            section[data-testid="stSidebar"] {
                font-size: 1.05rem;
            }
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] .stMarkdown {
                font-size: 1.05rem;
            }
            section[data-testid="stSidebar"] [data-baseweb="slider"] label {
                font-size: 1rem !important;
            }
            .block-container {
                padding-top: 1.25rem;
                padding-bottom: 3rem;
                max-width: 1100px;
            }
            div[data-testid="stVerticalBlock"] > div:has(> div.hero-card) {
                margin-bottom: 0.5rem;
            }
            .hero-card {
                background: linear-gradient(135deg, #1e1b4b 0%, #312e81 45%, #4338ca 100%);
                border-radius: 16px;
                padding: 1.75rem 1.5rem 1.5rem;
                color: #eef2ff;
                box-shadow: 0 12px 40px -12px rgba(67, 56, 202, 0.55);
                border: 1px solid rgba(255,255,255,0.12);
                margin-bottom: 1.25rem;
            }
            .hero-card h1 {
                font-size: 2.15rem;
                font-weight: 700;
                letter-spacing: -0.02em;
                margin: 0 0 0.35rem 0;
                color: #fff !important;
            }
            .hero-card p {
                margin: 0;
                font-size: 1.08rem;
                opacity: 0.9;
                line-height: 1.5;
                color: #c7d2fe !important;
            }
            .section-label {
                font-size: 0.82rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #64748b;
                margin: 1.5rem 0 0.5rem 0;
            }
            [data-testid="stMetricValue"] {
                font-size: 1.95rem !important;
            }
            [data-testid="stMetricLabel"] {
                font-size: 1.05rem !important;
            }
            div[data-testid="stCaption"] {
                font-size: 0.98rem !important;
            }
            .stTextInput input, .stTextArea textarea {
                font-size: 1.05rem !important;
            }
            button[kind] {
                font-size: 1.02rem !important;
            }
            [data-baseweb="tab"] {
                font-size: 1.05rem !important;
            }
            div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary p {
                font-size: 1.05rem !important;
            }
            .muted-footer {
                font-size: 0.92rem;
                color: #94a3b8;
                line-height: 1.55;
                margin-top: 2rem;
                padding-top: 1.25rem;
                border-top: 1px solid #e2e8f0;
            }
            .muted-footer a { color: #6366f1; text-decoration: none; }
            .muted-footer a:hover { text-decoration: underline; }
            div[data-testid="stExpander"] {
                border: 1px solid #e2e8f0 !important;
                border-radius: 12px !important;
                overflow: hidden;
                margin-bottom: 0.5rem;
                background: #fafafa;
            }
            .stMarkdown pre, .stCodeBlock {
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 0.88rem !important;
                border-radius: 8px !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 14px !important;
                border-color: #e2e8f0 !important;
                background: #ffffff;
                box-shadow: 0 1px 3px rgba(15,23,42,0.04);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _secrets_to_env() -> None:
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
            "LANGSMITH_PROJECT_URL",
        ):
            if key in s and not os.environ.get(key):
                os.environ[key] = str(s[key])
    except Exception:
        pass


def _mermaid_embed_safe(diagram: str) -> str:
    """Allow Mermaid markup (<br/>, <b>) while breaking out of HTML script context."""
    return diagram.strip().replace("</script", "<\\/script").replace("</Script", "<\\/Script")


def _render_mermaid(diagram: str, height: int = 520) -> None:
    safe = _mermaid_embed_safe(diagram)
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
<style>
  html, body {{ margin: 0; height: 100%; background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); }}
  .wrap {{
    padding: 20px 24px 16px;
    box-sizing: border-box;
    min-height: 100%;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.8);
  }}
  .mermaid {{ display: flex; justify-content: center; align-items: flex-start; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="mermaid">{safe}</div>
</div>
<script>
  mermaid.initialize({{ startOnLoad: true, securityLevel: "loose", fontFamily: "system-ui, sans-serif" }});
</script>
</body></html>"""
    components.html(page, height=height, scrolling=False)


def _topic_slug(topic: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", (topic or "").strip())
    return (s[:60] or "trace").strip("_")


def _status_dot(ok: bool) -> str:
    return "🟢" if ok else "🔴"


def _render_step_trace(trace: list[dict]) -> None:
    st.markdown('<p class="section-label">Execution verification</p>', unsafe_allow_html=True)
    st.caption("Per-node inputs/outputs from the last LangGraph run.")
    for i, step in enumerate(trace, start=1):
        node = step.get("node", "?")
        with st.expander(f"**Step {i}** · `{node}`", expanded=(i <= 2)):
            in_col, out_col = st.columns(2, gap="medium")
            with in_col:
                st.markdown("##### Inputs")
                for k, v in (step.get("inputs") or {}).items():
                    st.caption(k.replace("_", " "))
                    st.code(v or "—", language=None)
            with out_col:
                st.markdown("##### Outputs")
                for k, v in (step.get("outputs") or {}).items():
                    st.caption(k.replace("_", " "))
                    st.code(v or "—", language=None)
            st.markdown("##### Checks")
            for ch in step.get("checks") or []:
                ok = ch.get("ok")
                name = ch.get("name", "")
                detail = ch.get("detail") or ""
                icon = "✅" if ok else "⚠️"
                line = f"{icon} **{name}**"
                if detail:
                    line += f" — {detail}"
                st.markdown(line)


@st.cache_data(ttl=90, show_spinner="Fetching LangSmith runs…")
def _cached_langsmith_runs(project: str, limit: int) -> tuple[list[dict], str | None]:
    from research_system.langsmith_feed import fetch_recent_root_runs

    return fetch_recent_root_runs(project_name=project, limit=limit)


def _render_langsmith_panel(project_override: str) -> None:
    from research_system.langsmith_feed import langsmith_api_configured, resolved_project_name

    st.markdown('<p class="section-label">LangSmith activity</p>', unsafe_allow_html=True)
    st.caption(
        "LangSmith does not publish embeddable live trace widgets for third-party pages. "
        "This panel uses the API for simple charts; use **Open** links for the full LangSmith UI."
    )
    env_proj = resolved_project_name()
    proj = (project_override or "").strip() or env_proj
    if not langsmith_api_configured():
        st.info(
            "Set **LANGSMITH_API_KEY** (or **LANGCHAIN_API_KEY**) and optional **LANGSMITH_PROJECT** "
            "to enable tracing; after you run the graph, latency and token summaries appear here."
        )
        return

    top, btn = st.columns([4, 1])
    with top:
        if proj == env_proj:
            st.caption(f"Project {proj!r} — from tracer env (override empty).")
        else:
            st.caption(f"Project {proj!r} — **sidebar override** (env has {env_proj!r}).")
    with btn:
        if st.button("Refresh", help="Drop cache and fetch latest root runs", use_container_width=True):
            _cached_langsmith_runs.clear()
            st.rerun()

    runs, err = _cached_langsmith_runs(proj, 24)
    if not runs:
        if err:
            el = err.lower()
            if "not found" in el or "api error" in el:
                st.error(err)
            else:
                st.warning(err)
        else:
            st.warning(
                "No runs returned. Turn tracing on (**LANGSMITH_TRACING=true** or **LANGCHAIN_TRACING_V2=true**), "
                "confirm the project name matches LangSmith (or use the sidebar override), then run the pipeline once."
            )
        return

    import pandas as pd

    df = pd.DataFrame(runs)
    df["short"] = df["id"].str[:8] + " · " + df["name"].str.slice(0, 32)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart_lat = df[["short", "latency_s"]].dropna()
        if not chart_lat.empty:
            st.markdown("**Latency (s)** — root traces")
            st.bar_chart(chart_lat, x="latency_s", y="short", horizontal=True)
        else:
            st.caption("No latency data on these runs.")
    with c2:
        chart_tok = df[["short", "total_tokens"]].dropna()
        chart_tok = chart_tok[chart_tok["total_tokens"].notna() & (chart_tok["total_tokens"] > 0)]
        if not chart_tok.empty:
            st.markdown("**Total tokens** — when reported")
            st.bar_chart(chart_tok, x="total_tokens", y="short", horizontal=True)
        else:
            st.caption("Token counts not available for these runs.")

    proj_url = (os.environ.get("LANGSMITH_PROJECT_URL") or "").strip()
    if proj_url:
        st.link_button("Open project in LangSmith", proj_url, use_container_width=False)

    show = df[["started_at", "short", "name", "status", "latency_s", "total_tokens"]].copy()
    show.columns = ["Started", "Run", "Name", "Status", "Latency (s)", "Tokens"]
    st.dataframe(
        show,
        column_config={
            "Started": st.column_config.TextColumn("Started"),
            "Run": st.column_config.TextColumn("Run"),
            "Name": st.column_config.TextColumn("Name"),
            "Status": st.column_config.TextColumn("Status"),
            "Latency (s)": st.column_config.NumberColumn("Latency (s)", format="%.3f"),
            "Tokens": st.column_config.NumberColumn("Tokens", format="%d"),
        },
        hide_index=True,
        use_container_width=True,
    )
    link_df = df[df["url"].notna() & (df["url"].astype(str).str.len() > 0)][["name", "url"]].head(12)
    if not link_df.empty:
        st.markdown("**Trace links**")
        for _, row in link_df.iterrows():
            st.markdown(f"- [{row['name'][:60]}]({row['url']})")


def _sidebar_settings() -> tuple[int, bool, bool, str]:
    st.sidebar.markdown("### Settings")
    st.sidebar.caption("Tune the pipeline and what you see after a run.")
    max_rounds = st.sidebar.slider(
        "Max synthesis rounds",
        1,
        4,
        3,
        help="How many times the writer may revise before the graph stops.",
    )
    show_trace = st.sidebar.toggle(
        "Show sources & critique JSON",
        value=True,
        help="Web hits, OpenAlex works, and raw critique JSON.",
    )
    show_step_io = st.sidebar.toggle(
        "Show step I/O panels",
        value=True,
        help="LangGraph node-by-node verification from the last run.",
    )
    st.sidebar.divider()
    st.sidebar.markdown("### Environment")
    t_ok = bool(os.environ.get("TAVILY_API_KEY"))
    o_ok = bool(os.environ.get("OPENAI_API_KEY"))
    ls_ok = bool(
        os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")
    )
    st.sidebar.markdown(f"{_status_dot(t_ok)} **Tavily** — {'configured' if t_ok else 'missing key'}")
    st.sidebar.markdown(f"{_status_dot(o_ok)} **OpenAI** — {'configured' if o_ok else 'missing key'}")
    st.sidebar.markdown(
        f"{_status_dot(ls_ok)} **LangSmith** — optional tracing"
        if ls_ok
        else "⚪ **LangSmith** — optional (not set)"
    )
    ls_panel_project = st.sidebar.text_input(
        "LangSmith project (panel)",
        value="",
        placeholder="blank = env / default",
        help="Leave blank to use LANGSMITH_PROJECT / LANGCHAIN_PROJECT / tracer default. "
        "Must match the project name in the LangSmith UI exactly.",
    )
    st.sidebar.divider()
    st.sidebar.caption("Docs: README · AGENTS.md · OpenAlex polite pool: `OPENALEX_MAILTO`")
    return max_rounds, show_trace, show_step_io, ls_panel_project


st.set_page_config(
    page_title="Research Graph · Demo",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

_secrets_to_env()
_inject_styles()

if "viz_result" not in st.session_state:
    st.session_state.viz_result = None
if "viz_trace" not in st.session_state:
    st.session_state.viz_trace = []

max_rounds, show_trace, show_step_io, ls_panel_project = _sidebar_settings()

st.markdown(
    """
    <div class="hero-card">
        <h1>Multi-agent research</h1>
        <p>LangGraph orchestration · LangChain agents · Tavily + OpenAlex · cited reports with a critique loop</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="section-label">Run</p>', unsafe_allow_html=True)
default_topic = "AI regulation in Europe 2026"
topic = st.text_input(
    "Research topic",
    value=default_topic,
    placeholder="e.g. EU AI Act implementation timeline 2026",
    help="This string is sent to Tavily, OpenAlex, and the synthesis model.",
)

c1, c2 = st.columns([1, 4], gap="medium")
with c1:
    run = st.button("Run pipeline", type="primary", use_container_width=True)
with c2:
    st.caption("Retrieves web + scholarly sources, builds a source index, writes a cited draft, then critiques and may revise.")

if run:
    if not os.environ.get("TAVILY_API_KEY"):
        st.error("Add **TAVILY_API_KEY** to `.env` or Streamlit secrets.")
        st.stop()
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("Add **OPENAI_API_KEY** to `.env` or Streamlit secrets.")
        st.stop()

    prog = st.progress(0, text="Starting graph…")
    try:
        from research_system.graph import run_research

        prog.progress(15, text="Gathering web & works…")
        raw = run_research(topic, max_iterations=max_rounds, collect_trace=True)
        prog.progress(85, text="Finalizing…")
        tr = raw.pop("execution_trace", [])
        st.session_state.viz_result = raw
        st.session_state.viz_trace = tr
        prog.progress(100, text="Done")
    finally:
        prog.empty()

result = st.session_state.viz_result
trace = st.session_state.viz_trace or []

if result is None:
    st.info(
        "Configure your keys in the sidebar, enter a topic, and press **Run pipeline**. "
        "Results, sources, and exports appear here after the first successful run."
    )
else:
    if result.get("error"):
        st.warning(result["error"])

    n_web = len(result.get("web_results") or [])
    n_pap = len(result.get("papers") or [])
    iters = int(result.get("iteration") or 0)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Web hits", n_web)
    with m2:
        st.metric("OpenAlex works", n_pap)
    with m3:
        st.metric("Synthesis passes", iters)
    with m4:
        st.metric("Has final report", "Yes" if (result.get("final_report") or "").strip() else "No")

    st.markdown('<p class="section-label">Report</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(result.get("final_report") or "_No report generated._")

    if show_trace:
        st.markdown('<p class="section-label">Evidence & critique</p>', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["Web results", "OpenAlex works", "Critique JSON"])
        with t1:
            if n_web:
                for i, w in enumerate(result.get("web_results") or [], start=1):
                    st.markdown(f"**[W{i}]** [{w.get('title', '')}]({w.get('url', '')})")
                    st.caption((w.get("content") or "")[:700] + ("…" if len(w.get("content") or "") > 700 else ""))
            else:
                st.caption("No web hits returned for this run.")
        with t2:
            if n_pap:
                for j, p in enumerate(result.get("papers") or [], start=1):
                    st.markdown(f"**[P{j}]** {p.get('title', '')}")
                    st.caption(
                        f"{p.get('authors', '')} · {p.get('year', '')} · "
                        f"[link]({p.get('url', '')})" if p.get("url") else ""
                    )
            else:
                st.caption("No works returned (rate limits or query).")
        with t3:
            st.code(result.get("critique_json") or "{}", language="json")

        ptr = result.get("prompt_trace") or []
        if ptr:
            st.markdown('<p class="section-label">Prompt audit</p>', unsafe_allow_html=True)
            with st.container(border=True):
                st.caption(
                    "PDF includes exact **system** / **human** strings for each LLM call, plus retrieval request shapes. "
                    "First export may download a Unicode font into `data/fonts/`."
                )
                cdl, cdr = st.columns([1, 2])
                with cdl:
                    try:
                        from research_system.prompt_trace_pdf import build_prompt_trace_pdf

                        pdf_bytes = build_prompt_trace_pdf(topic, ptr)
                        st.download_button(
                            label="Download prompt trace PDF",
                            data=pdf_bytes,
                            file_name=f"prompt_trace_{_topic_slug(topic)}.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.warning(f"Could not build PDF: {e}")
                with cdr:
                    with st.expander(f"Steps recorded ({len(ptr)})"):
                        for i, e in enumerate(ptr, start=1):
                            st.markdown(
                                f"**{i}.** `{e.get('step')}` · *{e.get('kind', '')}* — {e.get('title', '')}"
                            )

st.markdown('<p class="section-label">Pipeline map</p>', unsafe_allow_html=True)
st.caption("Critique may loop back to synthesis until approval or max rounds.")
_render_mermaid(_MERMAID_FLOW)

_render_langsmith_panel(ls_panel_project)

if trace and show_step_io:
    st.divider()
    _render_step_trace(trace)
elif not trace and show_step_io and result is not None:
    st.caption("Step I/O trace was empty for this run.")

st.markdown(
    """
    <div class="muted-footer">
        <strong>Flow:</strong>
        <code>gather_web</code> (Tavily) → <code>gather_papers</code> (OpenAlex) → <code>prepare_sources</code> →
        <code>synthesize</code> → <code>critique</code> → revise or <code>finalize</code>.
        <br/>
        APIs:
        <a href="https://tavily.com/" target="_blank" rel="noopener">Tavily</a> ·
        <a href="https://docs.openalex.org/" target="_blank" rel="noopener">OpenAlex</a>
    </div>
    """,
    unsafe_allow_html=True,
)
