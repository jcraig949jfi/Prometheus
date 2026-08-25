"""STEP 1, part 2 — split Apollo's unreached 16.7% into dE and dS.

Consumes `roles/Lexis/notes/reachable_answers_result.json` produced by
`reachable_answers.py`, plus a fresh per-task run of the known 0.833 organism.

THE DISTINCTION THIS MEASURES (gate G5's two ledgers, applied to the ceiling itself):

  A task the production organism gets WRONG is in exactly one of two classes.

  dE-BOUND (vocabulary expansion needed)
      The correct answer is not in R(t) -- it is not reachable by ANY sequence of the 27
      operators, at any depth, with any repetition. No arrangement of the existing
      vocabulary can ever answer it. Only a NEW operator can. This is the class the
      "Apollo is vocabulary-bound" claim asserts the 16.7% belongs to.

  dS-BOUND (searchability / routing only)
      The correct answer IS in R(t). Some reachable state carries it. The substrate can
      express the answer; the single production program simply does not route to it on
      this task. A macro, a better guard, or a better search could reach it -- no new
      vocabulary required.

These are different products and they must not share a column. If the unreached tasks are
dE-bound, growing the operator menu is the only move and the slice's premise stands. If
they are dS-bound, the ceiling is a routing failure wearing an expressivity costume, and
"Apollo is vocabulary-bound" is the wrong diagnosis.

Read-only with respect to apollo/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APOLLO = ROOT / "apollo"
sys.path.insert(0, str(APOLLO / "src"))
sys.path.insert(0, str(APOLLO / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be                      # noqa: E402
from blackboard import BlackboardState, run_pipeline  # noqa: E402
from o1_enumerate import build_battery, KNOWN_0833  # noqa: E402

RESULT = HERE.parent / "notes" / "reachable_answers_result.json"


def per_task_correct(pipeline_names, tasks):
    ops = [be.REGISTRY[n][0] for n in pipeline_names]
    out = []
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            f = run_pipeline(ops, s)
            out.append((f.selected_answer == t["correct"], f.selected_answer))
        except Exception as e:
            out.append((False, "<exception:%s>" % type(e).__name__))
    return out


def main():
    if not RESULT.exists():
        print("missing %s -- run reachable_answers.py first" % RESULT)
        return 2
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    reach = {r["idx"]: r for r in data["per_task"]}
    if data["capped_tasks"]:
        print("REFUSING TO REPORT: closure unresolved on %d task(s) %s."
              % (len(data["capped_tasks"]), data["capped_tasks"][:10]))
        print("An unresolved closure cannot support an unreachability claim -- absence of")
        print("the answer in a TRUNCATED search is not absence from the closure.")
        return 2

    tasks, bounds = build_battery()
    assert len(tasks) == data["n_tasks"], "battery changed since the closure was computed"

    got = per_task_correct(KNOWN_0833, tasks)
    acc = sum(1 for ok, _ in got if ok) / len(tasks)
    print("POSITIVE CONTROL  known organism accuracy = %.4f (expect 0.8333) -> %s"
          % (acc, "MATCH" if abs(acc - 0.8333) < 0.001 else "MISMATCH"))
    if abs(acc - 0.8333) >= 0.001:
        return 2
    print()

    dE, dS, solved = [], [], []
    for i, (ok, ans) in enumerate(got):
        if ok:
            solved.append(i)
        elif reach[i]["correct_reachable"]:
            dS.append(i)
        else:
            dE.append(i)

    n = len(tasks)
    print("=" * 76)
    print("DECOMPOSITION OF THE 120-TASK BATTERY under the production 0.833 organism")
    print("=" * 76)
    print("  solved by the organism                       %3d / %d  = %.4f" % (len(solved), n, len(solved) / n))
    print("  UNREACHED, correct answer NOT in closure     %3d / %d  = %.4f   <- dE-bound"
          % (len(dE), n, len(dE) / n))
    print("  UNREACHED, correct answer IS in closure      %3d / %d  = %.4f   <- dS-bound"
          % (len(dS), n, len(dS) / n))
    print()
    unreached = len(dE) + len(dS)
    if unreached:
        print("  of the unreached %.1f%% of the battery:" % (100.0 * unreached / n))
        print("     %5.1f%% is genuinely beyond the vocabulary  (dE)" % (100.0 * len(dE) / unreached))
        print("     %5.1f%% is expressible but not routed to    (dS)" % (100.0 * len(dS) / unreached))
    print()

    print("per-subset split (solved / dS-bound / dE-bound):")
    for name, a, b in bounds:
        s_ = sum(1 for i in solved if a <= i < b)
        ds_ = sum(1 for i in dS if a <= i < b)
        de_ = sum(1 for i in dE if a <= i < b)
        print("   %-11s  solved %3d   dS %3d   dE %3d   (n=%d)" % (name, s_, ds_, de_, b - a))
    print()

    print("dS-bound task indices (expressible, unrouted): %s" % dS)
    print("dE-bound task indices (outside the closure)  : %s" % dE)
    print()
    print("READING")
    if not dE:
        print("  Every task the organism fails has its correct answer inside the operator")
        print("  closure. NOTHING in the battery is beyond the vocabulary. The 16.7% is")
        print("  entirely a ROUTING failure. 'Apollo is vocabulary-bound' is FALSIFIED as a")
        print("  description of this battery: dE = 0, dS = 16.7%.")
    elif not dS:
        print("  Every task the organism fails is outside the operator closure. The 16.7%")
        print("  is entirely dE. No arrangement, macro, or search improvement can touch it.")
        print("  'Apollo is vocabulary-bound' is CONFIRMED, and now at all depths and")
        print("  repetitions rather than only k<=10 without repeats.")
    else:
        print("  The ceiling is MIXED. %.1f%% of the battery needs new vocabulary (dE) and"
              % (100.0 * len(dE) / n))
        print("  %.1f%% is already expressible and merely unrouted (dS). Only the dE part"
              % (100.0 * len(dS) / n))
        print("  supports the vocabulary-bound claim. The dS part is Apollo's own slice and")
        print("  its headroom is real but bounded at %.4f." % ((len(solved) + len(dS)) / n))

    out = HERE.parent / "notes" / "ceiling_diagnosis_result.json"
    out.write_text(json.dumps({
        "n_tasks": n, "organism_acc": acc,
        "solved": solved, "dS_bound": dS, "dE_bound": dE,
        "dE_fraction_of_battery": len(dE) / n,
        "dS_fraction_of_battery": len(dS) / n,
        "single_program_ceiling_if_routing_were_perfect": (len(solved) + len(dS)) / n,
    }, indent=1), encoding="utf-8")
    print("\nwrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
