"""null_slot_ablation.py — DeepSeek/Gemini's data-flow ablation test.

For each typed slot the blackboard prototype writes, zero/reset that slot
RIGHT BEFORE the next operator reads it. Measure accuracy delta vs the
baseline-unmodified pipeline. If a slot can be zeroed without accuracy
drop, that slot is decorative — the prototype's +5pp lift over Apollo's
gen-3551 elite was achieved through a SHIFTED Goodhart channel, not
genuine compositional reasoning over typed state.

Gemini's framing: "If corrupting the read-state does not cause the final
accuracy to drop, then Slot X is a decorative dead-store. The organism
must be killed."

DeepSeek's threshold question: this script reports accuracy_delta per
slot; the policy is then "any slot with delta < 0.01 is decorative."

Usage:
    python null_slot_ablation.py [n_per_category=5]
"""
import sys
import copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src"))

from blackboard import blackboard_op, BlackboardState, run_pipeline
from blackboard_ops import (
    parse_numbers, parse_names_and_relations, parse_question_target,
    op_transitive_closure, op_numeric_argmax,
    score_by_max_entity, score_by_max_value,
)

# Same pipelines as branch_c_poc.py
PIPELINE_NUMERIC = [
    parse_numbers,
    parse_question_target,
    op_numeric_argmax,
    score_by_max_value,
]

PIPELINE_TRANSITIVITY = [
    parse_names_and_relations,
    op_transitive_closure,
    score_by_max_entity,
]


def pipeline_dispatch(state):
    probe = parse_names_and_relations(BlackboardState(
        problem_text=state.problem_text, candidates=state.candidates))
    if probe.relations:
        return run_pipeline(PIPELINE_TRANSITIVITY, state)
    return run_pipeline(PIPELINE_NUMERIC, state)


# ── Slot reset definitions ────────────────────────────────────────────


def _reset_slot(state: BlackboardState, slot_name: str) -> None:
    """Reset a slot to its default (empty container / None / empty string)."""
    DEFAULTS = {
        "numbers": [], "names": [], "relations": [], "quantities": {},
        "question_target": "", "transitive_closure": {}, "ordered": [],
        "counts": {}, "evidence": [], "hypotheses": [], "probabilities": {},
        "confidence": None, "max_entity": "", "max_value": None,
        "candidate_scores": [], "selected_answer": "",
    }
    if slot_name in DEFAULTS:
        setattr(state, slot_name, copy.deepcopy(DEFAULTS[slot_name]))


def make_zeroer(slot_name: str):
    """Return a BlackboardOp that zeros one slot. Inserted between the
    writer and the next reader."""
    @blackboard_op(reads=[], writes=[slot_name], name=f"_zero_{slot_name}")
    def _zero(state):
        _reset_slot(state, slot_name)
        return state
    return _zero


def insert_zeroer_after_first_write(pipeline, slot_name):
    """Insert a zeroer right after the first op that writes `slot_name`.
    This corrupts the slot before any downstream op can read it."""
    out = []
    inserted = False
    for op in pipeline:
        out.append(op)
        if (not inserted) and (slot_name in op.writes):
            out.append(make_zeroer(slot_name))
            inserted = True
    return out, inserted


# ── Evaluation ────────────────────────────────────────────────────────


def evaluate(fn, tasks):
    n_correct = 0
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            out = fn(s)
            ok = (out.selected_answer == t["correct"])
        except Exception:
            ok = False
        n_correct += int(ok)
    return n_correct / max(len(tasks), 1)


def test_pipeline(name, pipeline, tasks, slot_names):
    print(f"=== {name} ({len(pipeline)} ops) ===")
    baseline_acc = evaluate(lambda s: run_pipeline(pipeline, s), tasks)
    print(f"  baseline (no zeroing): acc = {baseline_acc:.3f}")
    print()
    print(f"  {'slot':30s}  {'zeroed_acc':>10s}  {'delta':>8s}  verdict")
    print(f"  {'-'*30}  {'-'*10}  {'-'*8}  {'-'*30}")
    rows = []
    for slot in slot_names:
        modified, inserted = insert_zeroer_after_first_write(pipeline, slot)
        if not inserted:
            print(f"  {slot:30s}  {'—':>10s}  {'—':>8s}  slot never written by pipeline")
            continue
        zeroed_acc = evaluate(lambda s: run_pipeline(modified, s), tasks)
        delta = baseline_acc - zeroed_acc
        if delta >= 0.10:
            verdict = "✓ load-bearing (≥10pp drop)"
        elif delta >= 0.05:
            verdict = "✓ load-bearing (≥5pp drop)"
        elif delta >= 0.01:
            verdict = "~ marginally load-bearing"
        else:
            verdict = "✗ DECORATIVE (no impact)"
        print(f"  {slot:30s}  {zeroed_acc:>10.3f}  {delta:>+8.3f}  {verdict}")
        rows.append((slot, baseline_acc, zeroed_acc, delta, verdict))
    return rows


def main():
    from trap_generator import generate_trap_battery
    n_per = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    tasks = generate_trap_battery(n_per_category=n_per, seed=42)
    print(f"Loaded {len(tasks)} trap-battery tasks ({n_per} per category)")
    print()

    numeric_slots = ["numbers", "question_target", "max_value", "candidate_scores"]
    transit_slots = ["names", "relations", "transitive_closure", "ordered", "max_entity", "candidate_scores"]

    numeric_rows = test_pipeline("PIPELINE_NUMERIC", PIPELINE_NUMERIC, tasks, numeric_slots)
    print()
    transit_rows = test_pipeline("PIPELINE_TRANSITIVITY", PIPELINE_TRANSITIVITY, tasks, transit_slots)

    # Also test the dispatch composition (the +5pp prototype)
    print()
    print(f"=== DISPATCH COMPOSITION (the +5pp claim) ===")
    baseline_acc = evaluate(pipeline_dispatch, tasks)
    print(f"  baseline dispatch acc: {baseline_acc:.3f}")
    print()
    # For dispatch, zero each slot by patching ONE of the underlying pipelines
    # (whichever path is active for each task). Easier: zero in both paths.
    dispatch_slots = ["numbers", "question_target", "max_value",
                      "names", "relations", "transitive_closure", "max_entity",
                      "candidate_scores"]
    print(f"  {'slot':30s}  {'zeroed_acc':>10s}  {'delta':>8s}  verdict")
    print(f"  {'-'*30}  {'-'*10}  {'-'*8}  {'-'*30}")
    dispatch_rows = []
    for slot in dispatch_slots:
        # Build a modified dispatch that zeroes this slot in both branches
        mod_numeric, _ = insert_zeroer_after_first_write(PIPELINE_NUMERIC, slot)
        mod_transit, _ = insert_zeroer_after_first_write(PIPELINE_TRANSITIVITY, slot)
        def modified_dispatch(state, _mn=mod_numeric, _mt=mod_transit):
            probe = parse_names_and_relations(BlackboardState(
                problem_text=state.problem_text, candidates=state.candidates))
            if probe.relations:
                return run_pipeline(_mt, state)
            return run_pipeline(_mn, state)
        zeroed_acc = evaluate(modified_dispatch, tasks)
        delta = baseline_acc - zeroed_acc
        if delta >= 0.10: verdict = "✓ load-bearing (≥10pp drop)"
        elif delta >= 0.05: verdict = "✓ load-bearing (≥5pp drop)"
        elif delta >= 0.01: verdict = "~ marginally load-bearing"
        else: verdict = "✗ DECORATIVE (no impact)"
        print(f"  {slot:30s}  {zeroed_acc:>10.3f}  {delta:>+8.3f}  {verdict}")
        dispatch_rows.append((slot, baseline_acc, zeroed_acc, delta, verdict))

    # ── Failure-signature reading (per Prometheus Doctrine #2) ─────
    # We do not collapse to PASS/FAIL/MIXED. The result is the per-slot
    # signature breakdown — what shape does each non-load-bearing slot
    # take, and what design correction does each shape imply?
    print()
    print("=" * 75)
    print("FAILURE-SIGNATURE READING (Doctrine #2 — gradient over verdict)")
    print("=" * 75)
    print()
    print("Per-slot signature + implied design correction:")
    print()
    SIGNATURE_LIBRARY = {
        # signature_id -> (description, lesson)
        "load-bearing": ("Causally necessary: zeroing the slot drops accuracy meaningfully.",
                         "Keep. Verify the operator that writes it remains stable across mutation."),
        "recompute-bypass": ("Declared read by downstream op, but downstream RECOMPUTES from upstream slot.",
                             "Wrapper protocol must enforce declared-reads-must-be-actual-reads (static verification at compile_check)."),
        "side-output": ("Op writes multiple slots; only one is downstream-load-bearing. The others are byproducts.",
                        "Split the op into atomic single-output ops. Make the data flow visible at the genome level."),
        "redundant-encoding": ("Same data is recoverable from another slot the same op writes.",
                               "Parser/producer ops must write CANONICAL representations. No two slots that encode the same content."),
        "atomic-with-output": ("Slot is written on the same step as the final output, so the data-flow test cannot separate them.",
                               "Methodological blind spot of this instrument. Need complementary mid-step corruption test."),
    }

    # Classify each non-load-bearing slot by which signature pattern it matches.
    # This is a hand-coded classification based on the prototype's structure;
    # for future runs over evolved organisms, the classifier should be derived
    # from the op-graph rather than hand-coded.
    PROTOTYPE_SIGNATURES = {
        "numbers": "load-bearing",
        "question_target": "load-bearing",
        "relations": "load-bearing",
        "max_entity": "load-bearing",
        "max_value": "recompute-bypass",
        "transitive_closure": "side-output",
        "names": "redundant-encoding",
        "candidate_scores": "atomic-with-output",
    }

    for slot, _, _, delta, _ in dispatch_rows:
        sig_id = PROTOTYPE_SIGNATURES.get(slot, "load-bearing" if delta >= 0.05 else "unknown")
        desc, lesson = SIGNATURE_LIBRARY.get(sig_id, ("(uncharacterized)", "(no recommendation)"))
        print(f"  [{sig_id:20s}] {slot:25s}  delta={delta:+.3f}")
        print(f"    signature: {desc}")
        print(f"    lesson:    {lesson}")
        print()

    # Triage signal (NOT a verdict — these are inputs to a decision, not the decision)
    print("Triage signal (input to next move, not a verdict):")
    by_sig = {}
    for slot, *_ in dispatch_rows:
        sig_id = PROTOTYPE_SIGNATURES.get(slot, "unknown")
        by_sig.setdefault(sig_id, []).append(slot)
    for sig_id, slots in sorted(by_sig.items()):
        print(f"  {sig_id:20s}: {len(slots)} slots ({', '.join(slots)})")
    print()
    print("Implied corrections for Branch C Phase 0:")
    for sig_id, slots in by_sig.items():
        if sig_id == "load-bearing":
            continue
        _, lesson = SIGNATURE_LIBRARY.get(sig_id, ("", ""))
        print(f"  - {lesson}")


if __name__ == "__main__":
    main()
