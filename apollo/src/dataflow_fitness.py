"""dataflow_fitness.py — slot-causal-load as a fitness term.

For Branch C Phase 1: every promoted organism must show that its declared
state-writes are LOAD-BEARING under data-flow ablation. This module
converts the 2026-05-25 null-slot ablation into a reusable fitness
function: `compute_dataflow_fitness(pipeline, tasks) -> dict`.

The function returns BOTH a scalar `dataflow_score` (for NSGA-III use)
AND a per-slot signature dict (for Doctrine #2 reading — what failed
and why). Selection consumes the scalar; logging + downstream analysis
consume the signatures.

Per the failure-signature doctrine, the score is a triage signal. The
signatures are the artifact.
"""
from __future__ import annotations
import copy
from pathlib import Path

from blackboard import BlackboardState, BlackboardOp, run_pipeline


# Default reset values per slot semantic type
SLOT_RESET = {
    "numbers": [], "names": [], "relations": [], "quantities": {},
    "question_target": "", "transitive_closure": {}, "ordered": [],
    "counts": {}, "evidence": [], "hypotheses": [], "probabilities": {},
    "confidence": None, "max_entity": "", "max_value": None,
    "rules": {}, "facts": set(), "derived_facts": set(),
    "comparison": None, "extreme_number": "",
    "candidate_scores": [], "selected_answer": "",
}


def _zeroer_op(slot_name: str) -> BlackboardOp:
    """Construct an op that resets the named slot to its default."""
    from blackboard import blackboard_op

    @blackboard_op(reads=[], writes=[slot_name], name=f"_zero_{slot_name}")
    def _zero(state):
        if slot_name in SLOT_RESET:
            setattr(state, slot_name, copy.deepcopy(SLOT_RESET[slot_name]))
        return state
    return _zero


def _insert_zeroer_after_first_write(pipeline, slot_name):
    out = []
    inserted = False
    for op in pipeline:
        out.append(op)
        if (not inserted) and (slot_name in op.writes):
            out.append(_zeroer_op(slot_name))
            inserted = True
    return out, inserted


def _evaluate_pipeline(pipeline, tasks):
    n_correct = 0
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            out = run_pipeline(pipeline, s)
            if out.selected_answer == t["correct"]:
                n_correct += 1
        except Exception:
            pass
    return n_correct / max(len(tasks), 1)


def _classify_signature(slot: str, accuracy_delta: float, op_writes_for_slot: list[str]) -> dict:
    """Map (slot, accuracy_delta, co-writes) to a signature classification."""
    LOAD_BEARING_THRESHOLD = 0.05
    if accuracy_delta >= LOAD_BEARING_THRESHOLD:
        return {"signature": "load-bearing", "delta": accuracy_delta,
                "lesson": "slot is causally necessary; keep"}
    if accuracy_delta >= 0.01:
        return {"signature": "marginally-load-bearing", "delta": accuracy_delta,
                "lesson": "slot contributes weakly; investigate whether contribution is genuine or noise"}
    # delta < 0.01 — classify by structural pattern
    co_writes = [w for w in op_writes_for_slot if w != slot]
    if co_writes:
        return {"signature": "side-output", "delta": accuracy_delta,
                "co_writes_on_same_op": co_writes,
                "lesson": f"slot is a side-output of an op that writes {co_writes}; only one is load-bearing"}
    # If slot is terminal scorer co-write, it's atomic-with-output
    if slot in ("candidate_scores", "selected_answer"):
        return {"signature": "atomic-with-output", "delta": accuracy_delta,
                "lesson": "slot is written atomically with the final answer; this instrument can't separate them"}
    # Default: recompute-bypass or redundant-encoding
    return {"signature": "decorative-or-recompute-bypass", "delta": accuracy_delta,
            "lesson": "slot zeroing has no impact; downstream likely recomputes from upstream or doesn't read"}


def compute_dataflow_fitness(pipeline: list[BlackboardOp],
                             tasks: list[dict],
                             tracked_slots: list[str] | None = None) -> dict:
    """Run null-slot ablation across the pipeline. Returns:

    {
        "baseline_acc": float,
        "dataflow_score": float,        # mean(deltas across slots), bounded [0, 1]
        "n_load_bearing": int,
        "n_total_slots": int,
        "load_bearing_ratio": float,    # the NSGA-III-usable scalar
        "per_slot_signatures": [        # per-slot Doctrine #2 reading
            {"slot": "...", "signature": "...", "delta": float, "lesson": "..."},
            ...
        ],
    }

    `dataflow_score` is intentionally a SCALAR for use as a Pareto axis,
    but it summarizes; the per-slot signatures are the load-bearing
    diagnostic information for any human or downstream analyzer.
    """
    if tracked_slots is None:
        # Derive from pipeline: every slot any op writes
        tracked_slots = []
        for op in pipeline:
            for w in op.writes:
                if w not in tracked_slots:
                    tracked_slots.append(w)

    baseline_acc = _evaluate_pipeline(pipeline, tasks)
    per_slot = []
    # Build co-write map: for each slot, which other slots does its writer also write
    co_write_map = {}
    for op in pipeline:
        for w in op.writes:
            co_write_map.setdefault(w, []).extend(other for other in op.writes if other != w)

    for slot in tracked_slots:
        modified, inserted = _insert_zeroer_after_first_write(pipeline, slot)
        if not inserted:
            per_slot.append({"slot": slot, "signature": "not-written-by-pipeline",
                             "delta": 0.0, "lesson": "no op in pipeline writes this slot"})
            continue
        zeroed_acc = _evaluate_pipeline(modified, tasks)
        delta = baseline_acc - zeroed_acc
        sig = _classify_signature(slot, delta, co_write_map.get(slot, []))
        sig["slot"] = slot
        per_slot.append(sig)

    n_load_bearing = sum(1 for s in per_slot if s["signature"] == "load-bearing")
    n_marginal = sum(1 for s in per_slot if s["signature"] == "marginally-load-bearing")
    n_tracked = len([s for s in per_slot if s["signature"] != "not-written-by-pipeline"])
    load_bearing_ratio = (n_load_bearing + 0.5 * n_marginal) / max(n_tracked, 1)
    avg_delta = sum(s["delta"] for s in per_slot if s["delta"] > 0) / max(n_tracked, 1)

    return {
        "baseline_acc": baseline_acc,
        "dataflow_score": float(load_bearing_ratio),
        "avg_positive_delta": float(avg_delta),
        "n_load_bearing": n_load_bearing,
        "n_marginal": n_marginal,
        "n_tracked_slots": n_tracked,
        "load_bearing_ratio": float(load_bearing_ratio),
        "per_slot_signatures": per_slot,
    }


# ── Integration hint for fitness.py ──────────────────────────────────
# When Branch C Phase 1 runs, fitness.compute_fitness() should accept an
# optional `dataflow_score` field (similar to ablation_delta in v2c) and
# the per-slot signatures should be logged at stage="dataflow_audit" in
# the structured log. The Pareto-array additions:
#   - ablation_delta (existing, accuracy-based per primitive)
#   - dataflow_score (new, slot-level load-bearingness per organism)
# These are correlated but distinct: ablation_delta says "this primitive
# contributes to correct answers"; dataflow_score says "this primitive's
# typed-state writes are causally read downstream." Both must be > 0 for
# a Pareto-front organism.
