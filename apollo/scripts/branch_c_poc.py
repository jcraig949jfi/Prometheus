"""branch_c_poc.py — Branch C light POC.

Reproduces the 2026-05-24 blackboard_prototype.py finding (+5pp over
Apollo's gen-3551 elite) using the production-grade @blackboard_op
decorator and wrapped Frame H primitives. Sanity check that the
production interface preserves the prototype's lift before committing
to the larger Phase 0 / Phase 1 build.

Usage:
    python branch_c_poc.py [n_per_category=5]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src"))

from blackboard import BlackboardState, run_pipeline, compile_check
from blackboard_ops import (
    parse_numbers, parse_names_and_relations, parse_question_target,
    op_transitive_closure, op_numeric_argmax,
    score_by_max_entity, score_by_max_value,
)


# ── Seed pipelines (hand-written) ─────────────────────────────────────


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


def pipeline_dispatch(state: BlackboardState) -> BlackboardState:
    """Meta-pipeline: parse relations first, run transitivity if present, else numeric.

    This is the analog of the prototype's composition_dispatch — except
    each step is now a typed BlackboardOp with declared reads/writes.
    """
    probe = parse_names_and_relations(BlackboardState(
        problem_text=state.problem_text, candidates=state.candidates))
    if probe.relations:
        return run_pipeline(PIPELINE_TRANSITIVITY, state)
    return run_pipeline(PIPELINE_NUMERIC, state)


# ── Baselines (for comparison) ────────────────────────────────────────


def baseline_first(state: BlackboardState) -> BlackboardState:
    state.selected_answer = state.candidates[0] if state.candidates else ""
    return state


def baseline_longest(state: BlackboardState) -> BlackboardState:
    if not state.candidates:
        state.selected_answer = ""
        return state
    state.selected_answer = max(state.candidates, key=len)
    return state


# ── Evaluation ────────────────────────────────────────────────────────


def evaluate(fn, tasks, label):
    n_correct = 0
    by_cat = {}
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            out = fn(s)
            ok = (out.selected_answer == t["correct"])
        except Exception:
            ok = False
        cat = t.get("category", "?")
        by_cat.setdefault(cat, []).append(int(ok))
        n_correct += int(ok)
    n = len(tasks)
    return {
        "label": label,
        "acc": n_correct / max(n, 1),
        "n_correct": n_correct,
        "n_tasks": n,
        "by_cat": by_cat,
    }


def main():
    from trap_generator import generate_trap_battery
    n_per = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    tasks = generate_trap_battery(n_per_category=n_per, seed=42)
    print(f"Loaded {len(tasks)} trap-battery tasks ({n_per} per category)")
    print()

    # Static compile-check sanity
    for name, pipe in [("PIPELINE_NUMERIC", PIPELINE_NUMERIC),
                       ("PIPELINE_TRANSITIVITY", PIPELINE_TRANSITIVITY)]:
        ok, errors = compile_check(pipe)
        print(f"compile_check {name}: ok={ok} errors={errors}")
    print()

    runners = [
        ("B1 first candidate", baseline_first),
        ("B2 longest candidate", baseline_longest),
        ("C1 numeric pipeline (4 ops)", lambda s: run_pipeline(PIPELINE_NUMERIC, s)),
        ("C2 transitivity pipeline (3 ops)", lambda s: run_pipeline(PIPELINE_TRANSITIVITY, s)),
        ("C3 dispatch (probe + branch)", pipeline_dispatch),
    ]

    print(f"{'composition':45s} {'accuracy':>10s}  {'n':>9s}")
    print("-" * 75)
    results = []
    for label, fn in runners:
        r = evaluate(fn, tasks, label)
        results.append(r)
        print(f"{label:45s} {r['acc']:>10.3f}  {r['n_correct']:>3d}/{r['n_tasks']:<3d}")

    # Per-category breakdown for the dispatch composition
    print()
    print("Per-category breakdown for dispatch composition:")
    for cat, hits in sorted(results[-1]["by_cat"].items()):
        if any(hits) or len(hits) >= 5:
            print(f"  {cat:42s} {sum(hits)}/{len(hits)}")

    # Reproduce the prototype's lift comparison
    apollo_elite = 0.36
    best_baseline = max(r["acc"] for r in results[:2])
    best_pipeline = max(r["acc"] for r in results[2:])
    print()
    print("=" * 75)
    print(f"Best dumb baseline:                {best_baseline:.3f}")
    print(f"Best blackboard pipeline:          {best_pipeline:.3f}")
    print(f"Apollo evolved elite (reference):  {apollo_elite:.3f}")
    print(f"Pipeline lift over Apollo elite:   {best_pipeline - apollo_elite:+.3f}")
    print(f"Pipeline lift over longest hack:   {best_pipeline - best_baseline:+.3f}")
    print()
    if best_pipeline > apollo_elite + 0.05:
        print("PRODUCTION-INTERFACE REPRO: confirmed (+5pp over Apollo elite).")
        print("Phase 0 light POC passes. The @blackboard_op decorator preserves")
        print("the prototype's compositional lift. Branch C Phase 1 build is")
        print("the next commitment.")
    else:
        print("PRODUCTION-INTERFACE REPRO: NOT confirmed.")
        print("Investigate before continuing — wrapping may have introduced regression.")


if __name__ == "__main__":
    main()
