"""The productivity signal and the freshness record (ARACHNE-06/07, base rule 8).

PRESENT is not ACTIVE is not PRODUCTIVE is not VALID. A tick that fires
and writes nothing new says so with an explicit no-op reason; a run's
freshness file is readable without running the loop.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable


def _landscape_of(node: str) -> str:
    return node.split(":", 1)[0] if ":" in node else "?"


def tick_productivity(new_edges: Iterable, new_nodes: Iterable[str], events: dict) -> dict:
    """Domain-level productivity of one tick, from the edges the store
    actually persisted (deduplicated) and the node ids it saw for the first
    time. null_discounted_new_nodes weights each new node by (1 - null_p) of
    the cheapest edge that introduced it: a node reached only through a
    generic edge counts for little (founding doc s3 rule 3 as fitness)."""
    edges = list(new_edges)
    nodes = list(new_nodes)
    best_null: dict = {}
    cross = 0
    ops: dict = {}
    for e in edges:
        null_p = float(e.null_p)
        ops[e.op] = ops.get(e.op, 0) + 1
        if _landscape_of(e.src) != _landscape_of(e.dst):
            cross += 1
        for n in (e.src, e.dst):
            if n not in best_null or null_p < best_null[n]:
                best_null[n] = null_p
    discounted = sum((1.0 - best_null.get(n, 1.0)) for n in nodes)
    out = {
        "new_edges": len(edges),
        "new_nodes": len(nodes),
        "null_discounted_new_nodes": round(float(discounted), 3),
        "cross_landscape_new_edges": cross,
        "ops": ops,
        "deaths": int(events.get("deaths", 0)),
        "branches": int(events.get("branches", 0)),
        "floor_revives": int(events.get("floor_revives", 0)),
        "no_op_reason": None,
    }
    if not edges and not nodes:
        out["no_op_reason"] = "no crawler persisted a new edge this tick"
    return out


def freshness_record(*, tick: int, started_at: str, last_success_at, landscape_report: dict,
                     workspace: dict, productivity: dict, alive: int) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "written_at": now,
        "tick": tick,
        "started_at": started_at,
        "last_input_at": now,                       # a tick consumed its landscapes now
        "last_success_at": last_success_at,         # last tick that persisted a new node or edge
        "alive": alive,
        "landscapes": {k: {kk: v[kk] for kk in ("available", "reason", "credential_source")}
                       for k, v in landscape_report.items()},
        "productivity": productivity,
        "workspace": {k: workspace.get(k) for k in ("base_sha", "branch", "worktree_path", "dirty", "main_worktree")},
        "state": "PRODUCTIVE" if (productivity.get("new_edges") or productivity.get("new_nodes")) else "ACTIVE_NO_OP",
    }
