from typing import TypedDict


class WebHit(TypedDict, total=False):
    title: str
    url: str
    content: str


class PaperHit(TypedDict, total=False):
    title: str
    authors: str
    year: str
    abstract: str
    url: str
    paper_id: str


class ResearchState(TypedDict, total=False):
    topic: str
    web_results: list[WebHit]
    papers: list[PaperHit]
    source_index: str
    draft_report: str
    critique_json: str
    critique_summary: str
    revision_guidance: str
    iteration: int
    max_iterations: int
    final_report: str
    error: str
