"""Composition loader v2: EREBOS-G19-* recursive obligation walk.

The v1 loader (composition_g19_ledger_transitivity) only checks the
direct parents of a macro claim. If any direct parent is itself a
composed claim with sub-obligations, v1 misses transitive
falsifications: parent P1 might be PROMOTED, but P1's own sub-
parents Q1.1 and Q1.2 might be REJECTED — in which case P1's
PROMOTED status is suspect.

v2 walks the obligation tree to leaf level. A leaf is any row in
the ledger whose extras has no nested parent_record_ids or is a
non-erebos (Stygian/Pollux) primary verdict. The macro is killed
if ANY leaf in the obligation graph is REJECTED.

Cycle detection: track visited record_ids to avoid infinite loops.
Depth limit: MAX_RECURSION_DEPTH = 10 prevents pathological cases.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders.composition_g19_ledger_transitivity import (
    LEDGER_PATHS,
)


MAX_RECURSION_DEPTH = 10


def _load_ledger_rows_by_id() -> dict[str, dict]:
    """Read all three kill_ledgers; index by record_id (keep latest
    by emitted_at on duplicates)."""
    by_id: dict[str, dict] = {}
    latest_ts: dict[str, str] = {}
    for path in LEDGER_PATHS:
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except Exception:
                        continue
                    rid = row.get("record_id")
                    ts = row.get("emitted_at") or ""
                    if rid and ts >= latest_ts.get(rid, ""):
                        by_id[rid] = row
                        latest_ts[rid] = ts
        except Exception:
            continue
    return by_id


def _direct_parents(row: dict) -> list[str]:
    """Extract parent_record_ids from a row's extras / composition_payload."""
    extras = row.get("extras") or {}
    ids = (
        extras.get("parent_record_ids")
        or (extras.get("composition_payload") or {}).get("parent_record_ids")
        or []
    )
    if not isinstance(ids, (list, tuple)):
        return []
    return [str(i) for i in ids if i]


def _walk_obligations(
    root_ids: list[str],
    by_id: dict[str, dict],
    max_depth: int = MAX_RECURSION_DEPTH,
) -> dict:
    """BFS the obligation graph from root_ids to leaves. Returns:
    - visited: set of all record_ids touched
    - leaves: list of leaf row dicts (rows with no nested parents)
    - missing: list of record_ids referenced but not found in ledger
    - depth_reached: max depth visited
    - cycle_detected: bool
    """
    visited: set[str] = set()
    leaves: list[dict] = []
    missing: list[str] = []
    queue: list[tuple[str, int]] = [(rid, 0) for rid in root_ids]
    depth_reached = 0
    cycle_detected = False

    while queue:
        rid, depth = queue.pop(0)
        if rid in visited:
            cycle_detected = True
            continue
        visited.add(rid)
        depth_reached = max(depth_reached, depth)
        if depth >= max_depth:
            continue
        row = by_id.get(rid)
        if row is None:
            missing.append(rid)
            continue
        children = _direct_parents(row)
        # A leaf is a row with no nested obligations
        if not children:
            leaves.append(row)
            continue
        # Otherwise enqueue children for further walking
        for child_rid in children:
            queue.append((child_rid, depth + 1))

    return {
        "visited": visited,
        "leaves": leaves,
        "missing": missing,
        "depth_reached": depth_reached,
        "cycle_detected": cycle_detected,
    }


def run_g19_v2_recursive_obligations(parent_ids: list[str]) -> dict:
    """Walk obligation graph; classify by leaf verdicts."""
    if not parent_ids:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_no_obligations",
            "notes": "G19 v2 emission had zero parent obligations",
        }

    by_id = _load_ledger_rows_by_id()
    if not by_id:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "ledger load returned no rows",
        }

    walk = _walk_obligations(parent_ids, by_id)
    leaves = walk["leaves"]
    missing = walk["missing"]
    n_leaves = len(leaves)

    rejected_leaves = [
        l for l in leaves
        if (l.get("verdict") or "").upper() == "REJECTED"
    ]
    promoted_leaves = [
        l for l in leaves
        if (l.get("verdict") or "").upper() == "PROMOTED"
    ]
    unverified_leaves = [
        l for l in leaves
        if (l.get("verdict") or "").upper() not in {"REJECTED", "PROMOTED"}
    ]

    if rejected_leaves:
        verdict = "REJECTED"
        kp = "sub_claim_falsified"
        rejected_rids = [l.get("record_id") for l in rejected_leaves]
        notes = (
            f"v2 recursive walk found {len(rejected_leaves)}/{n_leaves} "
            f"leaf obligations REJECTED ({rejected_rids[:5]}); the "
            f"macro is falsified by DEEP transitivity (depth_reached="
            f"{walk['depth_reached']})."
        )
    elif missing:
        verdict = "UNVERIFIED"
        kp = "stygian_composition_obligation_unknown"
        notes = (
            f"v2 recursive walk found {len(missing)} obligation IDs "
            f"NOT in ledger; cannot conclude. Missing first 5: "
            f"{missing[:5]}."
        )
    elif unverified_leaves:
        verdict = "UNVERIFIED"
        kp = "stygian_composition_obligation_unknown"
        notes = (
            f"v2 recursive walk: {len(unverified_leaves)}/{n_leaves} "
            f"leaves remain UNVERIFIED; conjunction unresolved."
        )
    else:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"v2 recursive walk: all {n_leaves} leaves PROMOTED at "
            f"depth_reached={walk['depth_reached']}; the deep "
            f"obligation graph fully resolves to PROMOTED."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_root_obligations": len(parent_ids),
        "n_leaves": n_leaves,
        "n_visited": len(walk["visited"]),
        "depth_reached": walk["depth_reached"],
        "cycle_detected": walk["cycle_detected"],
        "n_rejected_leaves": len(rejected_leaves),
        "n_promoted_leaves": len(promoted_leaves),
        "n_unverified_leaves": len(unverified_leaves),
        "n_missing": len(missing),
        "rejected_leaf_ids": [l.get("record_id") for l in rejected_leaves[:5]],
        "notes": notes,
    }


class G19V2RecursiveObligationsLoader:
    plugin_id = "g19_proof_obligation"
    composition_id = "g19_v2_recursive_obligations"
    description = (
        "Composition loader v2 for EREBOS-G19-* claims. Walks the "
        "full obligation graph to leaf level (BFS, depth cap 10, "
        "cycle detection). Any REJECTED leaf kills the macro by "
        "DEEP transitivity. Complements v1 which only checks direct "
        "parents."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g19_proof_obligation":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        # v2 fires when composed_id mentions v2 or recursive
        return "v2" in composed_id.lower() or "recursive" in composed_id.lower()

    def build_battery_input(self, queue_payload: dict) -> dict:
        parent_ids = queue_payload.get("parent_record_ids") or []
        # Same convention as v1: parent_record_ids[0] is the macro's
        # own ledger row; obligations are [1:].
        obligation_ids = parent_ids[1:] if len(parent_ids) > 1 else parent_ids
        result = run_g19_v2_recursive_obligations(obligation_ids)
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G19 v2 recursive composition: walk obligation "
                "graph from macro to leaves (BFS, depth cap 10); any "
                "REJECTED leaf kills the macro by deep transitivity."
            ),
            "data_source": (
                "Live read of charon/agents/{stygian,pollux,erebos}/"
                "state/kill_ledger.jsonl; recursive obligation walk "
                "with cycle detection."
            ),
            "result": result,
            "notes": (
                "G19 v2 catches DEEP transitive falsifications that "
                "v1's direct-parent-only check misses. Complementary "
                "to v1; both registered."
            ),
        }


register(G19V2RecursiveObligationsLoader())
