"""Replay ONE H3 stream through Techne's pyribs adapter AND Archaeon's four policies.

    python -m techne.scripts.h3_compare_policies --candidates <records.json> \
        --edges-json <edges.json> --cap-items N --cap-bytes N [--stream-id ID]

Both sides consume the identical ordered stream under the IDENTICAL caps, and the report is
per-policy: the three bounds (count, bytes, grid cells) and the retained-id agreement against
the pyribs adapter.

Two things this deliberately does not do.

It does not tune. If the stream is degenerate on the objective axis -- Archaeon warns that most
C3 candidates score the same -- the report says what the archives DO with ties at that scale.
Changing a cap, an edge or a descriptor to make the numbers more interesting would be choosing
the result.

It does not treat disagreement as an error. Techne's adapter REFUSES a new cell at the count
cap; Archaeon's Archive EVICTS to make room (except behavioral and uniform, which pass
evict_choice=None and therefore refuse too). Where they differ, the difference is a real
semantic difference between two implementations of "retention", and naming it is the useful
output.
"""
from __future__ import annotations

import argparse
import importlib
import json
import pathlib
import sys

from techne.acquisition import budget as _budget
from techne.acquisition import receipt
from techne.h3_retention import adapter as A
from techne.h3_retention import archaeon_seam as SEAM


def _load_archaeon():
    """Archaeon's harness lives outside techne; import it from the repo root."""
    root = pathlib.Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("archaeon.producer.h3_replay")


def _bounds(policy_name: str, arch, cap_items: int, cap_bytes: int, grid_cells: int) -> dict:
    """The three bounds, per policy, with none_bound stated rather than implied."""
    ev = [e["event"] for e in arch.events]
    hit_count = sum(1 for e in ev if e in ("refused_full", "evicted"))
    hit_bytes = sum(1 for e in ev if e in ("refused_oversize", "refused_bytes_on_replace"))
    at_grid = policy_name in ("behavioral", "hybrid") and len(arch.items) >= grid_cells
    bound = "+".join([n for n, hit in (("COUNT", hit_count), ("BYTES", hit_bytes),
                                       ("GRID_CELLS", at_grid)) if hit]) or "NONE"
    return {
        "retained_n": len(arch.items), "retained_bytes": arch.bytes_used,
        "cap_items": cap_items, "cap_bytes": cap_bytes, "grid_cells": grid_cells,
        "count_pressure_events": hit_count, "byte_pressure_events": hit_bytes,
        "at_grid_capacity": at_grid,
        "binding": bound,
        "none_bound_note": (None if bound != "NONE" else
                            "no bound was operative for this policy on this stream; its "
                            "retained set is not evidence that its caps work"),
        "event_counts": {k: ev.count(k) for k in sorted(set(ev))},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True,
                    help="JSON list of Archaeon Candidate records")
    ap.add_argument("--edges-json", required=True,
                    help="JSON list of per-descriptor bin edges")
    ap.add_argument("--cap-items", type=int, required=True)
    ap.add_argument("--cap-bytes", type=int, required=True)
    ap.add_argument("--stream-id", default="h3-stream")
    ap.add_argument("--reserve", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--profile", default="offline_check")
    ap.add_argument("--label", default="")
    a = ap.parse_args(argv)

    records = json.loads(pathlib.Path(a.candidates).read_text(encoding="utf-8"))
    edges = json.loads(pathlib.Path(a.edges_json).read_text(encoding="utf-8"))

    rec = receipt.new("ADAPTER_QUALIFICATION", "pyribs", tool="ribs")
    rec["check"] = "h3_policy_comparison_on_one_stream"
    rec["consumer"] = "H3 retention replay (Archaeon)"
    rec["stream_source"] = {"candidates": str(a.candidates), "label": a.label}

    prof = _budget.get_profile(a.profile)
    rec["budget_profile"] = prof

    with _budget.Budget(profile=prof) as b:
        # --- the seam: Archaeon records -> Techne rows, weakenings named
        stream, seam = SEAM.from_candidates(records, edges=edges, stream_id=a.stream_id)
        rec["observations"] = {"seam": seam, "stream_validation": stream.validation}

        dims = seam["grid_dims"]
        caps = A.Caps(max_retained=a.cap_items, max_bytes=a.cap_bytes)
        mine = A.replay(stream, caps, dims=dims, verify_ties=True)
        rec["observations"]["techne_pyribs"] = {
            "caps": mine.caps, "counts": mine.counts, "binding": mine.binding_constraint,
            "grid_cells": mine.grid_cells, "retained_bytes": mine.retained_bytes,
            "retained_ids": mine.retained_ids, "tie_policy": mine.tie_policy["declared"],
            "tie_verified": mine.tie_policy.get("verified"),
            "emitter_guard": mine.emitter_guard, "notes": mine.notes,
        }
        mine_seqs = {int(cid.split("-")[1]) for cid in mine.retained_ids}

        # --- Archaeon's four policies, same stream, same caps
        H = _load_archaeon()
        # Fields prefixed with "_" are report-only carriers added by the stream builder
        # (label, arm, rule_hex). They are NOT part of Archaeon's record shape, so they are
        # dropped here rather than forced into its dataclass.
        _fields = {f for f in H.Candidate.__dataclass_fields__}
        cands = [H.Candidate(**{k: (tuple(v) if k in ("descriptors", "parent_ids") else v)
                                for k, v in r.items() if k in _fields}) for r in records]
        cands.sort(key=lambda c: c.stream_id)
        manifest = H.stream_manifest(cands)
        rec["observations"]["archaeon_stream_manifest"] = manifest

        grid_cells = 1
        for es in edges:
            grid_cells *= (len(es) + 1)

        policies = {}
        for name, fn in H.POLICIES.items():
            arch = fn(cands, a.cap_items, a.cap_bytes, edges=edges, reserve=a.reserve,
                      seed=a.seed)
            seqs = {c.stream_id for c in arch.retained()}
            policies[name] = {
                "policy_id": arch.policy_id,
                "bounds": _bounds(name, arch, a.cap_items, a.cap_bytes, grid_cells),
                "retained_stream_ids": sorted(seqs),
                "archive_digest": arch.digest(),
                "agreement_with_pyribs": {
                    "identical": seqs == mine_seqs,
                    "jaccard": round(len(seqs & mine_seqs) / max(1, len(seqs | mine_seqs)), 4),
                    "only_in_policy": sorted(seqs - mine_seqs)[:20],
                    "only_in_pyribs": sorted(mine_seqs - seqs)[:20],
                },
            }
        rec["observations"]["archaeon_policies"] = policies
        rec["resource_receipt"] = b.resource_receipt()

    deg = seam["objective_degeneracy"]
    rec["observations"]["degeneracy_reading"] = {
        "modal_score": deg["modal_score"], "modal_fraction": deg["modal_fraction"],
        "what_the_archives_do": (
            "Under FIRST_WRITER_WINS an exactly equal objective never displaces an incumbent. "
            "So for the modal mass, retention is decided by ARRIVAL ORDER and by which "
            "descriptor cell each candidate lands in -- not by quality, because on that mass "
            "there is no quality difference to act on. behavioral and hybrid therefore retain "
            "the FIRST candidate to reach each cell; top_k retains the earliest of the tied "
            "best; uniform is unaffected because it never reads the objective."),
        "not_tuned": ("no cap, edge or descriptor was adjusted to make this more interesting. "
                      "The degeneracy is a property of the stream and is reported as one."),
    }
    rec["status"] = "COMPARED"
    out = receipt.write(rec)

    print(f"=== H3 policy comparison: {a.label or a.stream_id} ===")
    print(f"stream          n={seam['n']} failed={seam['n_failed']} "
          f"dims={seam['grid_dims']} grid_cells={mine.grid_cells}")
    print(f"  assay         {seam['assay_ref_structured']['assay_id']}"
          f"@{seam['assay_ref_structured']['assay_version']}")
    print(f"  lineage       {seam['lineage_kind_derived_from_parent_ids']}")
    print(f"  degeneracy    modal score {deg['modal_score']} in {deg['modal_count']}/"
          f"{deg['n_scored']} scored ({deg['modal_fraction']}), "
          f"{deg['n_distinct_scores']} distinct")
    for w in seam["WEAKENED_AT_THE_SEAM"]:
        print(f"  {w['id']} weaker  {w['property']}: {w['lost']}")
    print(f"\ncaps            items={a.cap_items} bytes={a.cap_bytes}")
    print(f"techne/pyribs   retained={mine.caps['retained']} bytes={mine.retained_bytes} "
          f"BINDING={mine.binding_constraint} counts={mine.counts}")
    print(f"\n{'policy':<12} {'retained':>8} {'bytes':>10} {'binding':<14} "
          f"{'identical':>9} {'jaccard':>8}")
    for name, p in policies.items():
        bd, ag = p["bounds"], p["agreement_with_pyribs"]
        print(f"{name:<12} {bd['retained_n']:>8} {bd['retained_bytes']:>10} "
              f"{bd['binding']:<14} {str(ag['identical']):>9} {ag['jaccard']:>8}")
    print(f"\nreceipt         {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
