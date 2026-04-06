# PaperResearchAgent (`paper_research`)

## Role

Retrieve **scholarly works** from **OpenAlex** for the research topic.

## Skills

Declared in `skills.py` (`AgentSkill` list).

## Memory

Post-hook records work counts and error flag per topic for episodic recall during synthesis.

## Hooks

- **Post:** append OpenAlex retrieval summary.

## Guardrails

- Topic minimum length.
- Output must include `papers`.

## Runnable

`paper_research_agent` — wrapped core calling `openalex_work_search`.
