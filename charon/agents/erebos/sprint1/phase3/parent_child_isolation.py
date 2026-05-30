"""Phase 3.I — Parent-child structure isolation (ITER-64).

Today's 3 actionable deltas (ITER-58) were ALL parent-child
predictions (Erebos emission -> Stygian battery). The doctrine
claims general Layer-2 navigation, not hierarchical-prediction-only.

This test isolates the substrate's signal by structural type:
  - HIERARCHICAL signatures: input_signature equals parent_record_id
    of at least one row in the group (Erebos emission with Stygian
    downstream is the canonical case).
  - LATERAL signatures: input_signature shared by multiple rows
    but NOT in a parent-child relationship (sibling emissions on
    the same input).

If substrate produces actionable deltas on the LATERAL subset, the
architectural claim is general. If LATERAL produces 0 deltas, the
"Layer 2" value was specifically about hierarchical prediction --
narrower than the doctrine framed.
"""
from __future__ import annotations

from charon.agents.erebos._cross_cell_motif import (
    conditional_kp_recommendations,
    extract_cooccurrence_motifs,
    per_plugin_majority,
)
from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
    _load_real_rows,
)


MIN_COOCCURRENCE = 3
MIN_LIFT = 1.5


def _is_hierarchical_signature(rows_in_sig: list[dict]) -> bool:
    """A signature is hierarchical if any row's record_id matches
    another row's parent_record_id within the same signature group.
    """
    record_ids = {r.get("row_id") for r in rows_in_sig if r.get("row_id")}
    parent_ids = {r.get("parent_record_id") for r in rows_in_sig
                  if r.get("parent_record_id")}
    return bool(record_ids & parent_ids)


def _normalize_with_parent(row: dict) -> dict:
    """Normalize but preserve parent_record_id (which the standard
    _normalize_row drops)."""
    from charon.agents.erebos.sprint1.phase3.real_residue_smoke import _normalize_row
    norm = _normalize_row(row)
    if norm is None:
        return None  # type: ignore[return-value]
    norm["parent_record_id"] = row.get("parent_record_id")
    return norm


def _load_with_parent() -> list[dict]:
    import json
    from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
        REAL_LEDGER_PATHS, ENRICHED_LEDGER_PATH,
    )
    paths = list(REAL_LEDGER_PATHS) + [ENRICHED_LEDGER_PATH]
    rows = []
    for p in paths:
        if not p.exists():
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    continue
                norm = _normalize_with_parent(raw)
                if norm and norm.get("plugin_id"):
                    rows.append(norm)
    return rows


def _count_deltas(rows: list[dict]) -> int:
    counter = per_plugin_majority(rows)
    mr = extract_cooccurrence_motifs(
        rows, min_cooccurrence=MIN_COOCCURRENCE, min_lift=MIN_LIFT,
    )
    cr = conditional_kp_recommendations(rows, mr.motifs)
    return sum(1 for (p, _), c in cr.items()
                if counter.get(p) and counter[p] != c)


def run_parent_child_isolation() -> dict:
    rows = _load_with_parent()
    from collections import defaultdict
    by_sig: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        sig = r.get("input_signature")
        if sig:
            by_sig[sig].append(r)

    hierarchical_sigs = set()
    lateral_sigs = set()
    for sig, sig_rows in by_sig.items():
        if len(sig_rows) < 2:
            continue
        if _is_hierarchical_signature(sig_rows):
            hierarchical_sigs.add(sig)
        else:
            lateral_sigs.add(sig)

    hier_rows = [r for r in rows
                  if r.get("input_signature") in hierarchical_sigs]
    lat_rows = [r for r in rows
                 if r.get("input_signature") in lateral_sigs]

    hier_deltas = _count_deltas(hier_rows)
    lat_deltas = _count_deltas(lat_rows)

    return {
        "n_total_rows": len(rows),
        "n_signatures_with_2plus_rows": (
            len(hierarchical_sigs) + len(lateral_sigs)
        ),
        "n_hierarchical_signatures": len(hierarchical_sigs),
        "n_lateral_signatures": len(lateral_sigs),
        "n_rows_in_hierarchical": len(hier_rows),
        "n_rows_in_lateral": len(lat_rows),
        "hierarchical_actionable_deltas": hier_deltas,
        "lateral_actionable_deltas": lat_deltas,
        "verdict": (
            "GENERAL_SIGNAL" if lat_deltas > 0
            else "HIERARCHICAL_ONLY" if hier_deltas > 0
            else "NO_SIGNAL_EITHER_SIDE"
        ),
    }


if __name__ == "__main__":
    r = run_parent_child_isolation()
    print("=" * 72)
    print("Phase 3.I -- Parent-child structure isolation")
    print("=" * 72)
    for k, v in r.items():
        print(f"  {k:38s} = {v}")
