# CritiqueAgent (`critique`)

## Role

**Fact-check** the draft against the source index only; return structured approval, risk, issues, and revision guidance.

## Skills

See `skills.py`.

## Memory

Post-hook records `approved` and `risk` per topic (requires `topic` in the invoke payload — supplied from graph state in `nodes.py`).

## Hooks

- **Post:** verdict line in episodic store.

## Guardrails

- Requires `topic`, substantive `source_index` and `draft`.
- Output must be `CritiqueResult` with `hallucination_risk` ∈ {low, medium, high}.

## Runnable

`critique_agent` — structured LLM chain, wrapped.

## Types

`CritiqueResult` in `types.py`.
