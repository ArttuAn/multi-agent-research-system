import os
import random
import time
from typing import Any

import httpx

from research_system.state import PaperHit, WebHit


def tavily_search(query: str, max_results: int = 8) -> list[WebHit]:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is not set")

    payload: dict[str, Any] = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False,
    }
    with httpx.Client(timeout=60.0) as client:
        r = client.post("https://api.tavily.com/search", json=payload)
        r.raise_for_status()
        data = r.json()

    out: list[WebHit] = []
    for item in data.get("results") or []:
        out.append(
            {
                "title": (item.get("title") or "")[:500],
                "url": item.get("url") or "",
                "content": (item.get("content") or "")[:4000],
            }
        )
    return out


def _http_retry_wait_s(response: httpx.Response, attempt: int) -> float:
    """Honor Retry-After when numeric; else exponential backoff with jitter."""
    ra = response.headers.get("Retry-After")
    if ra:
        try:
            return min(float(ra.strip()), 120.0)
        except ValueError:
            pass
    base = min(2.0**attempt, 45.0)
    return base + random.uniform(0.0, 1.5)


def _reconstruct_openalex_abstract(inv_index: Any) -> str:
    """OpenAlex stores abstracts as inverted index; rebuild plain text."""
    if not isinstance(inv_index, dict) or not inv_index:
        return ""
    positions_flat: list[int] = []
    for positions in inv_index.values():
        if not isinstance(positions, list):
            continue
        for pos in positions:
            if isinstance(pos, int):
                positions_flat.append(pos)
    if not positions_flat:
        return ""
    cap = max(positions_flat) + 1
    arr: list[str | None] = [None] * cap
    for word, positions in inv_index.items():
        if not isinstance(word, str) or not isinstance(positions, list):
            continue
        for pos in positions:
            if isinstance(pos, int) and 0 <= pos < cap:
                arr[pos] = word
    return " ".join(w for w in arr if w is not None)


def _openalex_work_url(work: dict[str, Any]) -> str:
    pl = work.get("primary_location")
    if isinstance(pl, dict):
        for key in ("landing_page_url", "pdf_url"):
            u = pl.get(key)
            if isinstance(u, str) and u.startswith("http"):
                return u
    doi = work.get("doi")
    if isinstance(doi, str) and doi:
        return doi if doi.startswith("http") else f"https://doi.org/{doi.lstrip('/')}"
    wid = work.get("id")
    return wid if isinstance(wid, str) else ""


def openalex_work_search(
    query: str,
    limit: int = 8,
    *,
    max_retries: int = 5,
) -> list[PaperHit]:
    """Search scholarly works via OpenAlex (no API key).

    Set ``OPENALEX_MAILTO`` to your email for the `polite pool` (better rate limits).
    Docs: https://docs.openalex.org/
    """
    mailto = os.environ.get("OPENALEX_MAILTO", "").strip()
    params: dict[str, Any] = {
        "search": query,
        "per-page": min(max(limit, 1), 25),
    }
    if mailto:
        params["mailto"] = mailto

    ua = "MultiAgentResearch/1.0 (+https://docs.openalex.org/)"
    if mailto:
        ua = f"MultiAgentResearch/1.0 (mailto:{mailto})"

    url = "https://api.openalex.org/works"
    last_response: httpx.Response | None = None
    data: dict[str, Any] = {}

    with httpx.Client(timeout=60.0) as client:
        for attempt in range(max_retries):
            r = client.get(url, params=params, headers={"User-Agent": ua})
            last_response = r
            if r.status_code == 429:
                time.sleep(_http_retry_wait_s(r, attempt))
                continue
            r.raise_for_status()
            data = r.json()
            break
        else:
            msg = (
                "OpenAlex rate limit (HTTP 429) after retries. "
                "Set OPENALEX_MAILTO in `.env` to your email (polite pool; see "
                "https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication) "
                "or wait and try again."
            )
            if last_response is not None:
                msg = f"{msg} Last status: {last_response.status_code}."
            raise RuntimeError(msg)

    out: list[PaperHit] = []
    for w in data.get("results") or []:
        if not isinstance(w, dict):
            continue
        title = (w.get("title") or w.get("display_name") or "")[:500]
        authorships = w.get("authorships") or []
        names: list[str] = []
        for a in authorships[:12]:
            if isinstance(a, dict):
                auth = a.get("author") or {}
                if isinstance(auth, dict):
                    n = auth.get("display_name")
                    if n:
                        names.append(str(n))
        author_str = ", ".join(names)[:500]
        year = w.get("publication_year")
        abstract = _reconstruct_openalex_abstract(w.get("abstract_inverted_index"))
        paper_url = _openalex_work_url(w)
        oid = ""
        raw_id = w.get("id")
        if isinstance(raw_id, str) and "openalex.org/" in raw_id:
            oid = raw_id.rsplit("/", 1)[-1]

        out.append(
            {
                "title": title,
                "authors": author_str,
                "year": str(year or ""),
                "abstract": abstract[:3500],
                "url": paper_url[:2000] if paper_url else "",
                "paper_id": oid,
            }
        )
    return out
