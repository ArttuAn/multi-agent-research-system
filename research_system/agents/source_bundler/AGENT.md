# SourceBundlerAgent (`source_bundler`)

## Role

Build the shared **source index** (`[Wn]`, `[Pm]`) from web + OpenAlex payloads.

## Skills

See `skills.py`.

## Memory

Logs index size (web count, work count, character length) for episodic context.

## Hooks

- **Post:** memory summary of bundle statistics.

## Guardrails

- Requires `topic` in state.
- `source_index` must be a string under size cap.

## Runnable

`source_bundler_agent`.
