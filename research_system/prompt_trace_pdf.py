"""Build a PDF documenting prompts / requests at each pipeline step and outputs after processing."""

from __future__ import annotations

import datetime as _dt
import io
from pathlib import Path
from typing import Any

from fpdf import FPDF


_DEJAVU_CDN = (
    "https://cdn.jsdelivr.net/gh/dejavu-fonts/dejavu-fonts@v2.37/ttf/DejaVuSans.ttf"
)


def _ensure_dejavu() -> str | None:
    """fpdf2 wheels may omit fonts; download DejaVu once for Unicode PDFs."""
    base = Path(__file__).resolve().parents[1] / "data" / "fonts"
    dest = base / "DejaVuSans.ttf"
    if dest.is_file():
        return str(dest)
    try:
        import urllib.request

        base.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(_DEJAVU_CDN, dest)  # noqa: S310 — fixed CDN URL
        return str(dest) if dest.is_file() else None
    except Exception:
        return None


def _find_dejavu() -> str | None:
    p = _ensure_dejavu()
    if p:
        return p
    try:
        import fpdf

        root = Path(fpdf.__file__).resolve().parent
        for hit in root.rglob("DejaVuSans.ttf"):
            if hit.is_file():
                return str(hit)
    except Exception:
        pass
    return None


def _encode_for_font(font_name: str, text: str) -> str:
    """Helvetica is Latin-1 only; DejaVu supports full Unicode."""
    if font_name == "helvetica":
        return (text or "").encode("latin-1", "replace").decode("latin-1")
    return text or ""


class _TracePDF(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self.set_auto_page_break(auto=True, margin=14)
        path = _find_dejavu()
        if path:
            self.add_font("DejaVu", "", path)
            self._font = "DejaVu"
        else:
            self._font = "helvetica"

    def heading(self, text: str, level: int = 1) -> None:
        self.ln(4)
        size = 14 if level == 1 else 11
        self.set_font(self._font, "", size)
        self.multi_cell(0, 7, _encode_for_font(self._font, text))
        self.ln(2)
        self.set_font(self._font, "", 10)

    def subheading(self, text: str) -> None:
        self.set_font(self._font, "", 10)
        self.multi_cell(0, 6, _encode_for_font(self._font, text))
        self.set_font(self._font, "", 9)
        self.ln(1)

    def body(self, text: str) -> None:
        if not text.strip():
            self.multi_cell(0, 5, "(empty)")
            self.ln(2)
            return
        self.set_font(self._font, "", 9)
        self.multi_cell(0, 5, _encode_for_font(self._font, text))
        self.ln(2)


def build_prompt_trace_pdf(
    topic: str,
    prompt_trace: list[dict[str, Any]],
    *,
    title: str = "CiteGraph — prompt trace",
) -> bytes:
    pdf = _TracePDF()
    pdf.add_page()
    pdf.heading(title, level=1)
    pdf.set_font(pdf._font, "", 10)
    pdf.body(f"Topic: {topic}")
    pdf.body(
        f"Generated: {_dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )
    if pdf._font == "helvetica":
        pdf.body(
            "(Note: DejaVu font not found in fpdf2 package; non-ASCII characters may be stripped.)"
        )

    for i, entry in enumerate(prompt_trace, start=1):
        pdf.add_page()
        step_title = entry.get("title") or entry.get("step") or f"Step {i}"
        pdf.heading(f"Step {i}: {step_title}", level=1)

        kind = entry.get("kind", "")
        if kind:
            pdf.subheading(f"Kind: {kind}")

        before = entry.get("before_processing")
        if isinstance(before, dict):
            for key in ("system", "human", "request", "context"):
                if key in before and before[key]:
                    pdf.subheading(f"Before - {key}")
                    pdf.body(str(before[key]))
            if "extra" in before and before["extra"]:
                pdf.subheading("Before - additional")
                pdf.body(str(before["extra"]))
        elif before:
            pdf.subheading("Before processing (input / prompt)")
            pdf.body(str(before))

        after = entry.get("after_processing")
        if isinstance(after, dict):
            for key, val in after.items():
                if val:
                    pdf.subheading(f"After - {key}")
                    pdf.body(str(val)[:120_000])
        elif after:
            pdf.subheading("After processing (model or tool output)")
            pdf.body(str(after)[:120_000])

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
