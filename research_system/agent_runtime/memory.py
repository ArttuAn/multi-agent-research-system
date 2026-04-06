from __future__ import annotations

import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Any


def _default_store_path() -> Path:
    root = os.environ.get("AGENT_MEMORY_DIR")
    if root:
        return Path(root) / "store.jsonl"
    return Path(__file__).resolve().parents[2] / "data" / "agent_memory" / "store.jsonl"


def _normalize_topic(topic: str) -> str:
    return re.sub(r"\s+", " ", (topic or "").strip().lower())


class AgentMemoryStore:
    """Append-only JSONL episodic memory shared across agents (topic-scoped recall)."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _default_store_path()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def append(
        self,
        agent_id: str,
        topic: str,
        summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        line = {
            "ts": time.time(),
            "agent_id": agent_id,
            "topic": topic,
            "topic_key": _normalize_topic(topic),
            "summary": summary[:2000],
            "metadata": metadata or {},
        }
        with self._lock:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

    def recent_for_topic(self, topic: str, max_entries: int = 8) -> list[dict[str, Any]]:
        key = _normalize_topic(topic)
        if not key or not self._path.is_file():
            return []
        rows: list[dict[str, Any]] = []
        with self._lock:
            try:
                text = self._path.read_text(encoding="utf-8")
            except OSError:
                return []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            tk = row.get("topic_key") or _normalize_topic(str(row.get("topic", "")))
            if tk == key or key in tk or tk in key:
                rows.append(row)
        rows.sort(key=lambda r: r.get("ts", 0), reverse=True)
        return rows[:max_entries]

    def format_context_for_prompt(self, topic: str, max_entries: int = 6) -> str:
        rows = self.recent_for_topic(topic, max_entries=max_entries)
        if not rows:
            return ""
        lines = []
        for r in rows:
            aid = r.get("agent_id", "?")
            summ = r.get("summary", "")
            lines.append(f"- [{aid}] {summ}")
        return "\n".join(lines)


_store: AgentMemoryStore | None = None


def get_memory_store() -> AgentMemoryStore:
    global _store
    if _store is None:
        _store = AgentMemoryStore()
    return _store
