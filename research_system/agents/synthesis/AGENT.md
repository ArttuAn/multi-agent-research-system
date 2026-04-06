# SynthesisAgent (`synthesis`)

## Role

Turn the **source index** (+ optional critique feedback + episodic memory) into a **cited markdown** report.

## Skills

See `skills.py` — primary skill `cited_markdown_report`.

## Memory

Post-hook records draft length and whether this was a first draft or revision pass (inferred from `revision_notes`).

Episodic lines from other agents are injected via `episodic_memory_block` in the prompt (built in `nodes.py`).

## Hooks

- **Post:** draft statistics to shared memory store.

## Guardrails

- Topic length, `source_index` size caps, `revision_notes` size cap.
- Output must be markdown within min/max length.

## Runnable

`synthesis_agent` — `ChatPromptTemplate | ChatOpenAI | StrOutputParser` inside wrapped core.
