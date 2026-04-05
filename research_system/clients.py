import os
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


def semantic_scholar_search(query: str, limit: int = 10) -> list[PaperHit]:
    fields = "title,authors,year,abstract,url,externalIds"
    params = {"query": query, "limit": limit, "fields": fields}
    headers = {}
    # Optional S2 API key increases rate limits: https://www.semanticscholar.org/product/api
    s2_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if s2_key:
        headers["x-api-key"] = s2_key

    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    with httpx.Client(timeout=60.0) as client:
        r = client.get(url, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()

    out: list[PaperHit] = []
    for p in data.get("data") or []:
        authors = p.get("authors") or []
        author_names = ", ".join(
            a.get("name", "") for a in authors[:12] if isinstance(a, dict)
        )
        pid = ""
        ext = p.get("externalIds") or {}
        if isinstance(ext, dict):
            pid = ext.get("DOI") or ext.get("ArXiv") or ext.get("PubMed") or ""
        paper_url = p.get("url") or ""
        raw_id = p.get("paperId")
        if not paper_url and raw_id:
            paper_url = f"https://www.semanticscholar.org/paper/{raw_id}"

        out.append(
            {
                "title": (p.get("title") or "")[:500],
                "authors": author_names[:500],
                "year": str(p.get("year") or ""),
                "abstract": ((p.get("abstract") or "")[:3500]),
                "url": paper_url,
                "paper_id": pid or (p.get("paperId") or ""),
            }
        )
    return out
