"""Charon swarm shared queues — typed pub/sub primitives.

The DESIGN doc (charon/agents/DESIGN_2026-05-19.md) specified Postgres
tables (`agora.attack_queue`, `agora.kill_ledger_entries`, etc.) as the
pub/sub fabric. v0.3 MVP: file-based JSONL queues, same row shapes, same
producer/consumer semantics. Cheaper to ship; upgradable to Postgres
when contention warrants.

Convention: each queue file is append-only JSONL. Each row has at minimum:
  - id (str — content-addressed or uuid4 hex)
  - ts (ISO-8601 UTC)
  - source (producer agent name, lowercase)
  - consumed (bool, default false)
  - consumed_at (ISO-8601 or null)
  - consumed_by (str or null)
  - <queue-specific payload>

Mark-consumed: O(N) rewrite of the JSONL with the consumed flag flipped.
Acceptable at MVP scale (≤10K rows / queue). Beyond that, swap to a sidecar
`<queue>.consumed.jsonl` index.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from harmonia.agents._base import REPO_ROOT

SHARED_QUEUES_DIR = REPO_ROOT / "charon" / "agents" / "_shared_queues"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class JsonlQueue:
    """Append-only JSONL queue with mark-consumed semantics.

    Not thread-safe across processes; relies on per-agent rotation
    (charon_loop.py fires one agent at a time) to avoid concurrent
    writes. If parallelism is introduced later, switch to file-locked
    writes or move to Postgres per the DESIGN doc.
    """

    def __init__(self, name: str):
        self.path = SHARED_QUEUES_DIR / f"{name}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, row: dict) -> str:
        """Append a row; auto-fills id/ts/consumed if missing. Returns id."""
        if "id" not in row:
            row["id"] = uuid.uuid4().hex
        row.setdefault("ts", _now_iso())
        row.setdefault("consumed", False)
        row.setdefault("consumed_at", None)
        row.setdefault("consumed_by", None)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row["id"]

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows: list[dict] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
        return rows

    def read_unconsumed(
        self, limit: int = 10, sort_key: Optional[str] = None, reverse: bool = True
    ) -> list[dict]:
        rows = [r for r in self.read_all() if not r.get("consumed")]
        if sort_key:
            rows.sort(key=lambda r: r.get(sort_key) or 0, reverse=reverse)
        return rows[:limit]

    def mark_consumed(self, row_id: str, by: str) -> bool:
        """Rewrite the JSONL flipping consumed=true for the given row. Returns True if found."""
        rows = self.read_all()
        found = False
        for r in rows:
            if r.get("id") == row_id and not r.get("consumed"):
                r["consumed"] = True
                r["consumed_at"] = _now_iso()
                r["consumed_by"] = by
                found = True
                break
        if not found:
            return False
        with self.path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return True

    def recent_keys(self, key_field: str, since_iso: str) -> set:
        """Return the set of `key_field` values seen in rows with ts >= since_iso.
        Used for producer-side dedup (avoid re-emitting the same kill_pattern in
        a tight window)."""
        return {
            r.get(key_field)
            for r in self.read_all()
            if r.get(key_field) is not None and (r.get("ts") or "") >= since_iso
        }


# Pre-built queue handles for the swarm's known producer/consumer pairs.
# Add new queue names here as the DESIGN tables come online.

def stygian_priority_queue() -> JsonlQueue:
    """Hecate (and any future producer) → Stygian. Highest-priority attack
    targets surfaced from the kill_ledger gradient archaeology. Stygian
    consumes from here before falling back to its static SEED_PROBLEMS rotation."""
    return JsonlQueue("stygian_priority")
