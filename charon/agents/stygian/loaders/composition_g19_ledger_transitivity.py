"""Composition loader: EREBOS-G19-* (Proof-Obligation) via ledger
transitivity.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 4 + the G19
plugin's "Tier B-MVP path" loader_feasibility_note. The plugin emits
"composed claim C holds iff each parent obligation holds"; the
Tier B-MVP loader just verifies each parent's current verdict in
the live Stygian + Pollux + Erebos kill_ledgers:

- Any parent REJECTED -> kill_pattern = sub_claim_falsified (the
  macro claim is invalidated by transitivity).
- All parents PROMOTED -> verdict = PROMOTED (the conjunction
  holds at the ledger-evidence level).
- Mixed (some PROMOTED, some UNVERIFIED, none REJECTED) ->
  UNVERIFIED with kill_pattern = stygian_composition_obligation_unknown
  (cannot conclude until obligations are independently resolved).

Substrate-grade lift: G19 graduates from "unfalsifiable MVP" to
"empirical instrument" without needing Lean. The Tier C-HARD Lean
path (formal proof obligation extraction) stays deferred.

Per DNA P12 (falsification asymmetry): this is exactly the kind of
loader that makes a plugin earn its keep.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from charon.agents.stygian.loaders._composition import register

try:
    from harmonia.agents._base import REPO_ROOT
except Exception:
    REPO_ROOT = Path(__file__).resolve().parents[4]


LEDGER_PATHS = [
    REPO_ROOT / "charon" / "agents" / "stygian" / "state" / "kill_ledger.jsonl",
    REPO_ROOT / "charon" / "agents" / "pollux" / "state" / "kill_ledger.jsonl",
    REPO_ROOT / "charon" / "agents" / "erebos" / "state" / "kill_ledger.jsonl",
]


def _lookup_verdicts(parent_ids: list[str]) -> dict[str, dict]:
    """Read the union of Stygian/Pollux/Erebos ledgers and return
    the LATEST verdict per parent_record_id. Missing parents map
    to {verdict: 'NOT_FOUND'}."""
    out: dict[str, dict] = {pid: {"verdict": "NOT_FOUND"} for pid in parent_ids}
    want = set(parent_ids)
    if not want:
        return out
    # For each ledger, scan; keep the latest hit per id by emitted_at.
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
                    if rid not in want:
                        continue
                    ts = row.get("emitted_at") or ""
                    if ts >= latest_ts.get(rid, ""):
                        latest_ts[rid] = ts
                        out[rid] = {
                            "verdict": row.get("verdict") or "UNKNOWN",
                            "kill_pattern": row.get("kill_pattern"),
                            "emitted_at": ts,
                            "generator_id": row.get("generator_id"),
                        }
        except Exception:
            continue
    return out


def run_g19_transitivity(parent_ids: list[str]) -> dict:
    """Evaluate the conjunction-over-obligations using ledger
    transitivity. Returns the result block the executor consumes."""
    if not parent_ids:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_no_obligations",
            "notes": "G19 emission had zero parent obligations",
        }
    verdicts = _lookup_verdicts(parent_ids)
    rejected = [
        pid for pid, v in verdicts.items()
        if (v.get("verdict") or "").upper() == "REJECTED"
    ]
    promoted = [
        pid for pid, v in verdicts.items()
        if (v.get("verdict") or "").upper() == "PROMOTED"
    ]
    not_found = [
        pid for pid, v in verdicts.items()
        if (v.get("verdict") or "").upper() == "NOT_FOUND"
    ]
    n = len(parent_ids)

    if rejected:
        verdict = "REJECTED"
        kp = "sub_claim_falsified"
        notes = (
            f"{len(rejected)}/{n} parent obligations are REJECTED in "
            f"the live ledger ({rejected}); the conjunction is "
            f"falsified by transitivity."
        )
    elif not_found:
        verdict = "UNVERIFIED"
        kp = "stygian_composition_obligation_unknown"
        notes = (
            f"{len(not_found)}/{n} parent obligations were not found "
            f"in the live ledger ({not_found}); cannot evaluate the "
            f"conjunction. Either the parents were emitted under a "
            f"different record_id scheme or they haven't run yet."
        )
    elif len(promoted) == n:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"All {n} parent obligations are PROMOTED in the live "
            f"ledger; the conjunction holds at the ledger-evidence "
            f"level (substrate-grade weak evidence -- the conjunction "
            f"is consistent with what we know, not a Lean-grade proof)."
        )
    else:
        # Some UNVERIFIED, some PROMOTED, no REJECTED
        verdict = "UNVERIFIED"
        kp = "stygian_composition_obligation_unknown"
        notes = (
            f"{len(promoted)}/{n} parents PROMOTED, "
            f"{n - len(promoted) - len(rejected) - len(not_found)} "
            f"UNVERIFIED, none REJECTED. The conjunction is consistent "
            f"so far but cannot be confirmed until all obligations "
            f"resolve to PROMOTED."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_obligations": n,
        "n_rejected": len(rejected),
        "n_promoted": len(promoted),
        "n_not_found": len(not_found),
        "rejected_parent_ids": rejected,
        "verdict_lookup": {
            pid: verdicts[pid].get("verdict") for pid in parent_ids
        },
        "notes": notes,
    }


class G19LedgerTransitivityLoader:
    plugin_id = "g19_proof_obligation"
    composition_id = "g19_ledger_transitivity"
    description = (
        "Composition loader for EREBOS-G19-* claims. Tier B-MVP path: "
        "look up each obligation parent's latest verdict in the union "
        "of Stygian/Pollux/Erebos kill_ledgers; emit verdict by "
        "transitivity. Tier C-HARD Lean path stays deferred."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g19_proof_obligation":
            return False
        # Any G19 emission qualifies; the loader is domain-agnostic.
        return True

    def build_battery_input(self, queue_payload: dict) -> dict:
        parent_ids = queue_payload.get("parent_record_ids") or []
        # The composed_id's own ledger-row is in parent_record_ids[0]
        # per daemon.py:268; the real obligations are parent_record_ids[1:].
        # G19 emits parent_record_ids = [rid_self, *obligation_ids].
        obligation_ids = (
            parent_ids[1:] if len(parent_ids) > 1 else parent_ids
        )
        result = run_g19_transitivity(obligation_ids)
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G19 transitivity composition: the macro claim "
                f"is the conjunction over {len(obligation_ids)} parent "
                f"obligations; verdict resolved by latest-verdict "
                f"lookup across the live kill_ledgers."
            ),
            "data_source": (
                "Live read of charon/agents/{stygian,pollux,erebos}/"
                "state/kill_ledger.jsonl, latest emitted_at per "
                "parent_record_id."
            ),
            "result": result,
            "notes": (
                "G19 graduates to empirical instrument via ledger "
                "transitivity without needing Lean. Tier C-HARD Lean "
                "path stays deferred to v0.15+."
            ),
        }


register(G19LedgerTransitivityLoader())
