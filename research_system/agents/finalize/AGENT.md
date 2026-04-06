# FinalizeAgent (`finalize`)

## Role

**Assemble** the user-facing markdown: draft + critique section + optional issues list.

## Skills

See `skills.py`.

## Memory

Post-hook records delivered report size for episodic context.

## Hooks

- **Post:** delivery stats.

## Guardrails

- Requires `topic` in state.
- `final_report` must be a non-trivial string under size cap.

## Runnable

`finalize_agent`.
