"""Build human-readable execution traces from LangGraph stream updates."""

from __future__ import annotations

import json
from typing import Any


def _clip(s: str, n: int = 280) -> str:
    s = (s or "").strip()
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _step_record(node: str, before: dict[str, Any], partial: dict[str, Any]) -> dict[str, Any]:
    """One row for the UI: inputs / outputs / verification checks."""
    inputs: dict[str, str] = {}
    outputs: dict[str, str] = {}
    checks: list[dict[str, Any]] = []

    def add_check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    if node == "gather_web":
        inputs["topic"] = str(before.get("topic") or "")
        wr = partial.get("web_results") or []
        err = (partial.get("error") or "").strip()
        outputs["web_results_count"] = str(len(wr))
        if err:
            outputs["node_error"] = _clip(err, 400)
        add_check("Input `topic` non-empty", bool(inputs["topic"]), inputs["topic"][:80] or "(empty)")
        add_check("Tavily returned ≥1 hit", len(wr) >= 1, f"{len(wr)} hits" if wr else err or "0 hits")
        if err and not wr:
            add_check("Tavily call succeeded", False, _clip(err, 200))

    elif node == "gather_papers":
        inputs["topic"] = str(before.get("topic") or "")
        papers = partial.get("papers") or []
        err = (partial.get("error") or "").strip()
        outputs["papers_count"] = str(len(papers))
        if err:
            outputs["state_error_note"] = _clip(err, 400)
        add_check("Input `topic` non-empty", bool(inputs["topic"]), "")
        add_check("OpenAlex returned ≥1 work", len(papers) >= 1, f"{len(papers)} works")

    elif node == "prepare_sources":
        wr = before.get("web_results") or []
        papers = before.get("papers") or []
        inputs["web_results_count"] = str(len(wr))
        inputs["papers_count"] = str(len(papers))
        idx = partial.get("source_index") or ""
        outputs["source_index_chars"] = str(len(idx))
        outputs["source_index_preview"] = _clip(idx, 320)
        add_check("Has web or paper rows to index", len(wr) + len(papers) > 0, f"{len(wr)} web, {len(papers)} papers")
        add_check("Built non-empty source index", bool(idx.strip()), f"{len(idx)} chars")

    elif node == "synthesize":
        inputs["topic"] = str(before.get("topic") or "")
        inputs["iteration_before"] = str(before.get("iteration") or 0)
        inputs["source_index_chars"] = str(len(before.get("source_index") or ""))
        rg = (before.get("revision_guidance") or "").strip()
        if rg:
            inputs["revision_guidance"] = _clip(rg, 240)
        draft = partial.get("draft_report") or ""
        outputs["iteration_after"] = str(partial.get("iteration"))
        outputs["draft_chars"] = str(len(draft))
        outputs["draft_preview"] = _clip(draft, 360)
        add_check("Source index present", bool((before.get("source_index") or "").strip()), "")
        add_check("Draft non-empty", bool(draft.strip()), f"{len(draft)} chars")

    elif node == "critique":
        inputs["draft_chars"] = str(len(before.get("draft_report") or ""))
        inputs["source_index_chars"] = str(len(before.get("source_index") or ""))
        cj = partial.get("critique_json") or ""
        outputs["critique_summary"] = _clip(partial.get("critique_summary") or "", 400)
        outputs["critique_json_preview"] = _clip(cj, 320)
        approved = False
        risk = ""
        try:
            data = json.loads(cj) if cj else {}
            approved = bool(data.get("approved"))
            risk = str(data.get("hallucination_risk") or "")
        except json.JSONDecodeError:
            data = {}
        outputs["parsed_approved"] = str(approved)
        outputs["parsed_risk"] = risk or "—"
        add_check("Critique JSON parses", bool(data), "")
        add_check("Hallucination risk recorded", bool(risk), risk or "missing")

    elif node == "finalize":
        inputs["draft_chars"] = str(len(before.get("draft_report") or ""))
        inputs["critique_summary_present"] = str(bool((before.get("critique_summary") or "").strip()))
        final = partial.get("final_report") or ""
        outputs["final_report_chars"] = str(len(final))
        outputs["final_preview"] = _clip(final, 360)
        add_check("Final report non-empty", bool(final.strip()), f"{len(final)} chars")

    else:
        inputs["(state keys)"] = ", ".join(sorted(partial.keys())) if partial else "—"
        outputs["raw_partial_keys"] = ", ".join(sorted(partial.keys()))

    return {"node": node, "inputs": inputs, "outputs": outputs, "checks": checks}


def merge_trace_from_stream(
    graph: Any,
    initial: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Stream graph updates; return final merged state and trace rows."""
    running: dict[str, Any] = dict(initial)
    trace: list[dict[str, Any]] = []
    for update in graph.stream(initial, stream_mode="updates"):
        if not isinstance(update, dict):
            continue
        for node_name, partial in update.items():
            if not isinstance(partial, dict):
                continue
            trace.append(_step_record(str(node_name), running, partial))
            running.update(partial)
    return running, trace
