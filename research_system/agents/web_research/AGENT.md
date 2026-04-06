# WebResearchAgent (`web_research`)

## Role

Retrieve **web evidence** via Tavily for the current research topic.

## Skills

See `skills.py` — declarative capability cards (`AgentSkill`) for routing and documentation.

## Memory

Post-run hook writes a short episodic line (`web_hits`, `error` flag) via `memory.append_retrieval_summary` into the shared JSONL store (`data/agent_memory/store.jsonl` by default). Used to prime synthesis with `format_context_for_prompt` on the same topic.

## Hooks

- **Post:** record retrieval summary for the topic (see `hooks.py`).

## Guardrails

- Topic length 2–2000 characters.
- Output must include `web_results`.

## Runnable

`web_research_agent` — LangChain `RunnableLambda` wrapped with `agent_runtime.wrap.wrap_call`.
