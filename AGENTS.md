# AGENTS.md — CiteGraph

**CiteGraph** uses **LangGraph** for orchestration and **LangChain** runnables per agent. Each agent has its own folder under `research_system/agents/<agent_id>/` with:

| File | Purpose |
|------|---------|
| `AGENT.md` | Human-readable role, skills, memory, hooks, guardrails |
| `skills.py` | Declarative `AgentSkill` cards (`research_system/agent_runtime/types.py`) |
| `memory.py` | Agent-specific helpers writing to the shared episodic store |
| `hooks.py` | Pre/post hooks (`research_system/agent_runtime/hooks.py`) |
| `guardrails.py` | Input/output validators (`GuardrailViolation`) |
| `agent.py` | Core logic + `RunnableLambda(wrap_call(...))` export |

## Shared runtime (`research_system/agent_runtime/`)

- **`wrap.py`** — Runs `pre` hooks → input guardrails → core → output guardrails → `post` hooks.
- **`memory.py`** — Append-only JSONL store (default `data/agent_memory/store.jsonl`). Override with `AGENT_MEMORY_DIR`.
- **`hooks.py`** — Register per `agent_id`.
- **`guardrails.py`** — Register per `agent_id`.
- **`types.py`** — `AgentSkill` dataclass.

## Agent index

| ID | Runnable | Folder |
|----|----------|--------|
| `web_research` | `web_research_agent` | `agents/web_research/` |
| `paper_research` | `paper_research_agent` | `agents/paper_research/` |
| `source_bundler` | `source_bundler_agent` | `agents/source_bundler/` |
| `synthesis` | `synthesis_agent` | `agents/synthesis/` |
| `critique` | `critique_agent` | `agents/critique/` |
| `finalize` | `finalize_agent` | `agents/finalize/` |

## Episodic memory in synthesis

`nodes.py` loads `get_memory_store().format_context_for_prompt(topic)` and injects it as `episodic_memory_block` into the synthesis prompt so prior retrieval/critique/finalize notes inform the draft (same topic key).

## Skills catalog

`research_system/agents/skills_catalog.py` exposes `all_skills_by_agent()` and `all_skills_flat()` for tooling or a future UI.

## For contributors / AI assistants

- Extend **skills** by appending to `SKILLS` in the relevant `skills.py`.
- Add **hooks** with `register(agent_id, pre=[...], post=[...])` in `hooks.py`.
- Add **guardrails** with `register_input` / `register_output` in `guardrails.py`.
- Keep **`AGENT.md`** in sync when behavior changes.
