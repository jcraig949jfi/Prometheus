"""phase0_validate.py — end-to-end Phase 0 validation.

Runs everything Phase 0 built and reports failure signatures (not pass/fail
verdicts, per Doctrine #2):

  1. Loads the clean canary suite (50 length-balanced tasks)
  2. Audits the prototype pipelines using the new wrapper-protocol checks
     (recompute-bypass, side-output, redundant-encoding)
  3. Evaluates the prototype on the canary AND on the original trap battery
     side by side — does the canary's length-balancing show different
     numbers than the trap-battery's longest-candidate-hack ceiling?
  4. Runs the data-flow fitness function on the prototype and reports
     per-slot signatures
  5. Tests the rewritten v2 primitives on synthetic state to confirm they
     produce typed-state outputs (not bare scalars)

Output is a structured report. The conclusion line is explicitly NOT a
verdict — it's a list of next moves with their implied signature.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src"))

from blackboard import (
    BlackboardState, run_pipeline, audit_pipeline,
    mid_step_corruption_test,
)
from blackboard_ops import (
    parse_numbers, parse_names_and_relations, parse_question_target,
    op_transitive_closure, op_numeric_argmax,
    score_by_max_entity, score_by_max_value,
)
from blackboard_ops_v2 import evidence_updater, entity_counter, distribution_reducer
from dataflow_fitness import compute_dataflow_fitness


PIPELINE_NUMERIC = [parse_numbers, parse_question_target, op_numeric_argmax, score_by_max_value]
PIPELINE_TRANSITIVITY = [parse_names_and_relations, op_transitive_closure, score_by_max_entity]


def _pipeline_dispatch(state):
    probe = parse_names_and_relations(BlackboardState(
        problem_text=state.problem_text, candidates=state.candidates))
    if probe.relations:
        return run_pipeline(PIPELINE_TRANSITIVITY, state)
    return run_pipeline(PIPELINE_NUMERIC, state)


def _evaluate(fn, tasks):
    n_correct = 0
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            out = fn(s)
            if out.selected_answer == t["correct"]:
                n_correct += 1
        except Exception:
            pass
    return n_correct / max(len(tasks), 1)


def _baseline_longest(tasks):
    n_correct = 0
    for t in tasks:
        cands = t["candidates"]
        if cands:
            pick = max(cands, key=len)
            if pick == t["correct"]:
                n_correct += 1
    return n_correct / max(len(tasks), 1)


def main():
    print("=" * 78)
    print("PHASE 0 VALIDATION REPORT — failure signatures, not verdicts")
    print("=" * 78)
    print()

    # ── 1. Load canary + original trap battery for side-by-side ──────
    canary_path = Path(__file__).parent.parent / "data" / "clean_canary_v01.json"
    with open(canary_path, "r", encoding="utf-8") as f:
        canary_data = json.load(f)
    canary_tasks = canary_data["tasks"]
    print(f"[1] Canary loaded: {len(canary_tasks)} tasks")
    print(f"    By category: {canary_data['by_category']}")
    print(f"    Length-audit: longest-is-correct in {canary_data['audit']['longest_candidate_chance_rate']:.0%}, "
          f"shortest-is-correct in {canary_data['audit']['shortest_candidate_chance_rate']:.0%}")
    print()

    # Original trap battery
    try:
        from trap_generator import generate_trap_battery
        trap_tasks = generate_trap_battery(n_per_category=5, seed=42)
        have_trap = True
        print(f"    Original trap battery loaded: {len(trap_tasks)} tasks")
    except Exception as e:
        trap_tasks = []
        have_trap = False
        print(f"    Original trap battery unavailable: {e}")
    print()

    # ── 2. Wrapper protocol audit on prototype pipelines ─────────────
    print("[2] Wrapper protocol audit (4 new static checks)")
    for name, pipe in [("PIPELINE_NUMERIC", PIPELINE_NUMERIC),
                       ("PIPELINE_TRANSITIVITY", PIPELINE_TRANSITIVITY)]:
        sigs = audit_pipeline(pipe)
        print(f"  {name}:")
        if sigs["compile_check_errors"]:
            for e in sigs["compile_check_errors"]:
                print(f"    [compile_check]   {e}")
        for w in sigs["recompute_bypass"]:
            print(f"    [recompute-bypass]   {w['op']}: declared read of '{w['slot']}' but source doesn't reference state.{w['slot']}")
        for w in sigs["side_output"]:
            sev = w.get("severity", "warn")
            print(f"    [side-output/{sev}]    {w['op']} writes {w['n_writes']} slots ({w['writes']})")
        for w in sigs["redundant_encoding"]:
            print(f"    [redundant-encoding] {w['op']} writes {w['slots']}; one likely recoverable from another")
        if not any(sigs[k] for k in ("recompute_bypass", "side_output", "redundant_encoding")):
            print(f"    (no protocol-level signatures)")
    print()

    # ── 3. Canary vs trap-battery side-by-side ──────────────────────
    print("[3] Side-by-side: prototype dispatch on canary vs original trap battery")
    canary_dispatch = _evaluate(_pipeline_dispatch, canary_tasks)
    canary_longest = _baseline_longest(canary_tasks)
    print(f"  CANARY (length-balanced, {len(canary_tasks)} tasks):")
    print(f"    longest-candidate baseline:    {canary_longest:.3f}")
    print(f"    prototype dispatch:            {canary_dispatch:.3f}")
    print(f"    delta over length hack:        {canary_dispatch - canary_longest:+.3f}")
    if have_trap:
        trap_dispatch = _evaluate(_pipeline_dispatch, trap_tasks)
        trap_longest = _baseline_longest(trap_tasks)
        print(f"  ORIGINAL TRAP BATTERY ({len(trap_tasks)} tasks):")
        print(f"    longest-candidate baseline:    {trap_longest:.3f}")
        print(f"    prototype dispatch:            {trap_dispatch:.3f}")
        print(f"    delta over length hack:        {trap_dispatch - trap_longest:+.3f}")
        print()
        print(f"  Signature reading: the trap battery rewards length-as-feature ({trap_longest:.0%}),")
        print(f"  while the canary does not ({canary_longest:.0%}). Branch C Phase 1 should be")
        print(f"  evaluated PRIMARILY against the canary; the trap battery is a secondary signal")
        print(f"  whose 'high score' may not reflect reasoning.")
    print()

    # ── 4. Data-flow ablation as fitness — per-slot signatures ───────
    print("[4] Data-flow fitness (per-slot signatures on the canary)")
    result = compute_dataflow_fitness(
        PIPELINE_NUMERIC + [parse_names_and_relations],  # union of all slots used in dispatch
        canary_tasks,
        tracked_slots=["numbers", "question_target", "max_value", "names", "relations",
                       "transitive_closure", "max_entity", "candidate_scores"],
    )
    print(f"  baseline canary acc:           {result['baseline_acc']:.3f}")
    print(f"  load_bearing_ratio (scalar):   {result['load_bearing_ratio']:.3f}")
    print(f"  avg positive delta:            {result['avg_positive_delta']:.3f}")
    print()
    print(f"  Per-slot signatures:")
    for sig in result["per_slot_signatures"]:
        print(f"    [{sig['signature']:35s}] {sig['slot']:25s}  delta={sig['delta']:+.3f}")
        print(f"      lesson: {sig['lesson']}")
    print()

    # ── 5. v2 primitive sanity test ──────────────────────────────────
    print("[5] v2 primitive rewrites — typed-state output sanity")
    # entity_counter
    s = BlackboardState(problem_text="test", candidates=[])
    s.names = ["Alice", "Bob", "Carol"]
    s.relations = [("Alice", "Bob"), ("Bob", "Carol")]
    out = entity_counter(s)
    print(f"  entity_counter: writes counts={list(out.counts.keys())}, evidence len={len(out.evidence)}")
    print(f"    state.counts['names'] = {out.counts.get('names', {})}")
    # evidence_updater
    s2 = BlackboardState(problem_text="test", candidates=[])
    s2.hypotheses = ["H1", "H2"]
    s2.probabilities = {"H1": 0.5, "H2": 0.5}
    s2.evidence = [{"hypothesis": "H1", "likelihood": 0.9, "false_positive": 0.1}]
    out2 = evidence_updater(s2)
    print(f"  evidence_updater: updated probabilities = {out2.probabilities}, confidence = {out2.confidence}")
    # distribution_reducer
    s3 = BlackboardState(problem_text="test", candidates=[])
    s3.probabilities = {"A": 0.7, "B": 0.2, "C": 0.1}
    out3 = distribution_reducer(s3)
    last = out3.evidence[-1] if out3.evidence else {}
    print(f"  distribution_reducer: summary mode={last.get('mode_hypothesis')}, "
          f"entropy={last.get('entropy', 0):.3f}, confidence={out3.confidence}")
    print()

    # ── 6. Mid-step corruption test (the new instrument for atomic-with-output) ──
    print("[6] Mid-step corruption test (closes the atomic-with-output blind spot)")
    # Test score_by_max_value: does it actually read `numbers`?
    s4 = BlackboardState(problem_text="test", candidates=["1", "5", "10"])
    s4.numbers = [1.0, 5.0, 10.0]
    s4.question_target = "larger"
    r = mid_step_corruption_test(score_by_max_value, s4, "numbers", corrupted_value=[])
    print(f"  score_by_max_value with corrupted numbers (corrupted before read):")
    print(f"    signature: {r['signature']}")
    print(f"    lesson:    {r['lesson']}")
    # Test the same op corrupting `max_value` (which the v1 scorer ignores)
    s5 = BlackboardState(problem_text="test", candidates=["1", "5", "10"])
    s5.numbers = [1.0, 5.0, 10.0]
    s5.max_value = 999.0  # deliberately wrong
    s5.question_target = "larger"
    # Note: max_value isn't in the op's declared reads; this just confirms
    # the scorer is recompute-bypassing
    r2 = mid_step_corruption_test(score_by_max_value, s5, "max_value", corrupted_value=999.0)
    print(f"  score_by_max_value with corrupted max_value (the recompute-bypass slot):")
    print(f"    signature: {r2['signature']}")
    print(f"    lesson:    {r2['lesson']}")
    print()

    # ── 7. Triage signal (next moves) — explicitly not a verdict ─────
    print("=" * 78)
    print("TRIAGE SIGNAL — next moves (input to a decision, not a verdict)")
    print("=" * 78)
    print()
    print("Phase 0 infrastructure built:")
    print("  ✓ Clean canary suite (50 length-balanced tasks)")
    print("  ✓ v2 primitives: evidence_updater, entity_counter, distribution_reducer")
    print("  ✓ Wrapper protocol audit: recompute-bypass, side-output, redundant-encoding checks")
    print("  ✓ Mid-step corruption test: closes the atomic-with-output blind spot")
    print("  ✓ Data-flow fitness: per-slot load-bearing ratio + per-slot signatures")
    print()
    print("Phase 0 findings (read each one as a separate move):")
    print()
    # Re-run wrapper audit + report each signature
    all_sigs = []
    for pipe in [PIPELINE_NUMERIC, PIPELINE_TRANSITIVITY]:
        sigs = audit_pipeline(pipe)
        all_sigs.extend(sigs["recompute_bypass"])
        all_sigs.extend(sigs["side_output"])
        all_sigs.extend(sigs["redundant_encoding"])
    if all_sigs:
        for s in all_sigs:
            sig = s["signature"]
            print(f"  - {sig}: {s['op']} → {s['lesson']}")
    else:
        print("  (no protocol-level signatures in v1 prototype pipelines)")
    print()
    print("Open question post-Phase-0: should Branch C Phase 1 start with the v1 wrapped")
    print("pipelines or the v2 rewritten primitives? The signatures above suggest v2 will")
    print("produce more readable evolution, but evolutionary search on v2 ops is untested.")
    print("Recommended next experiment: hand-write a v2-based 3-op composition and re-run")
    print("the null-slot ablation. If v2 pipelines produce 0 'side-output' or 'recompute-")
    print("bypass' signatures under the wrapper audit, v2 is the right Phase 1 substrate.")


if __name__ == "__main__":
    main()
