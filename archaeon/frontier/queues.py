"""DEEP FRONTIER -- the three queues (directive s10) plus the permanent REVISIT queue (s11).

Each queue is an append-only JSONL of items; an item's latest state wins. Items reference a lineage
and one transformation; execution (after G6-0) pops by priority within the pool's allocation.

    q = Queues(); q.push("EXPLORATION", item); q.pop("EXPLORATION"); q.status()
item = {item_id, lineage_id, transformation_id, pool, priority (float, higher first), lane (provenance
        label of the generator that proposed it), budget_evaluations, created_at, state PENDING|
        CLAIMED|DONE|DROPPED, note}
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
Q_DIR = HERE / "queues"
POOLS = ("EXPLORATION", "EXPLOITATION", "AUDIT", "REVISIT")
LANES = ("HUMAN_DIRECTED", "LLM_PROPOSED", "PROCEDURAL", "EVOLUTION_GENERATED", "MIXED")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Queues:
    def __init__(self, root: Path = Q_DIR):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self.paths = {p: self.root / (p + ".jsonl") for p in POOLS}
        for p in self.paths.values():
            if not p.exists():
                p.write_text("", encoding="utf-8")
        self.items: Dict[str, Dict[str, dict]] = {p: {} for p in POOLS}
        for pool, path in self.paths.items():
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        it = json.loads(line); self.items[pool][it["item_id"]] = it

    def _append(self, pool: str, it: dict) -> None:
        with open(self.paths[pool], "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(it, sort_keys=True, separators=(",", ":"), default=str) + "\n")
        self.items[pool][it["item_id"]] = it

    def push(self, pool: str, *, lineage_id: str, transformation_id: str, priority: float, lane: str, budget_evaluations: int, note: str = "") -> str:
        assert pool in POOLS and lane in LANES
        iid = "Q-" + hashlib.sha256(json.dumps([pool, lineage_id, transformation_id], sort_keys=True).encode()).hexdigest()[:10]
        it = {"item_id": iid, "lineage_id": lineage_id, "transformation_id": transformation_id, "pool": pool, "priority": float(priority), "lane": lane,
              "budget_evaluations": int(budget_evaluations), "created_at": _now(), "state": "PENDING", "note": note}
        self._append(pool, it); return iid

    def set_state(self, pool: str, item_id: str, state: str, note: str = "") -> None:
        it = dict(self.items[pool][item_id]); it["state"] = state; it["updated_at"] = _now()
        if note:
            it["note"] = note
        self._append(pool, it)

    def pending(self, pool: str) -> List[dict]:
        return sorted([it for it in self.items[pool].values() if it["state"] == "PENDING"], key=lambda x: (-x["priority"], x["created_at"]))

    def pop(self, pool: str) -> Optional[dict]:
        p = self.pending(pool)
        if not p:
            return None
        self.set_state(pool, p[0]["item_id"], "CLAIMED"); return self.items[pool][p[0]["item_id"]]

    def status(self) -> dict:
        out = {}
        for pool in POOLS:
            its = list(self.items[pool].values())
            out[pool] = {"pending": sum(1 for i in its if i["state"] == "PENDING"), "claimed": sum(1 for i in its if i["state"] == "CLAIMED"),
                         "done": sum(1 for i in its if i["state"] == "DONE"), "dropped": sum(1 for i in its if i["state"] == "DROPPED"),
                         "pending_budget": sum(i["budget_evaluations"] for i in its if i["state"] == "PENDING"),
                         "lanes_pending": {l: sum(1 for i in its if i["state"] == "PENDING" and i["lane"] == l) for l in LANES}}
        return out
