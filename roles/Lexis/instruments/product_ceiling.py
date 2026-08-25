"""STEP 1, part 3 — the EXACT single-program ceiling, at all depths, with repetition.

`reachable_answers.py` computes a per-task bound: it lets a different program answer each
task, so its 0.8917 is an over-estimate of what one program can do. O1's 0.833 is a
sample-based under-estimate. The true all-depths ceiling lies between them and neither
instrument can pin it.

This one can. Apollo's operators are deterministic, so a PROGRAM (an operator sequence)
induces, for each of the 120 tasks, exactly one trajectory. Track all 120 at once:

    JOINT STATE  J = (s_1, ..., s_120),  one blackboard state per task
    initial      J0 = the 120 initial states
    transition   op . J = (op(s_1), ..., op(s_120))     -- the SAME op applied to all

Then { J reachable from J0 } is exactly { the joint state induced by some program }, and

    CEILING = max over reachable J of  |{ t : J[t].selected_answer == correct(t) }|  / 120

is the exact accuracy of the best program of ANY length, with ANY repetition, in ANY order,
with ANY scorer tail. Nothing is sampled and nothing is bounded by k.

Finiteness: each component lives in that task's finite answer-relevant closure (see
`answer_slice.py`), so the joint space is finite and BFS terminates. Joint states are keyed
on the answer-relevant slice D only, which is sound by the same theorem: two joint states
agreeing on D componentwise produce the same accuracy under every continuation.

If the search is capped before the frontier empties, the number reported is a LOWER bound
on the ceiling and is labelled as such. It is never silently truncated.

PRE-COMMITTED, before the run:
    CEILING > 0.8333  ->  a deeper or repeating program beats the enumerated optimum.
                          "0.833 is the substrate's ceiling" is FALSIFIED as a number.
    CEILING == 0.8333 ->  0.833 is exact at all depths and repetitions. O1's caveat is
                          removed outright and the ceiling claim is at its strongest.

Read-only with respect to apollo/.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APOLLO = ROOT / "apollo"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(APOLLO / "src"))
sys.path.insert(0, str(APOLLO / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be                      # noqa: E402
from blackboard import BlackboardState              # noqa: E402
from o1_enumerate import build_battery, KNOWN_0833  # noqa: E402
from _answer_slice import D as _SLICE               # noqa: E402

SLOTS = [f for f in BlackboardState.__dataclass_fields__ if f in _SLICE]


def skey(s):
    parts = []
    for f in SLOTS:
        v = getattr(s, f)
        if isinstance(v, set):
            parts.append(tuple(sorted(map(repr, v))))
        elif isinstance(v, dict):
            parts.append(tuple(sorted((repr(k), repr(x)) for k, x in v.items())))
        elif isinstance(v, list):
            parts.append(tuple(map(repr, v)))
        else:
            parts.append(repr(v))
    return tuple(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=40000,
                    help="max distinct JOINT states to expand before stopping")
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "product_ceiling_result.json"))
    args = ap.parse_args()

    tasks, bounds = build_battery()
    correct = [t["correct"] for t in tasks]
    names = sorted(be.REGISTRY)
    ops = [be.REGISTRY[n][0] for n in names]

    known_acc = be._evaluate_acc([be.REGISTRY[n][0] for n in KNOWN_0833], tasks)
    print("POSITIVE CONTROL  known organism = %.4f (expect 0.8333) -> %s"
          % (known_acc, "MATCH" if abs(known_acc - 0.8333) < 1e-3 else "MISMATCH"))
    if abs(known_acc - 0.8333) >= 1e-3:
        return 2
    print("battery %d tasks, %d operators, joint BFS over ALL programs of ALL depths"
          % (len(tasks), len(ops)))
    print()

    J0 = [BlackboardState(problem_text=t["prompt"], candidates=t["candidates"]) for t in tasks]

    def score(J):
        return sum(1 for s, c in zip(J, correct) if s.selected_answer == c)

    def jkey(J):
        return tuple(skey(s) for s in J)

    seen = {jkey(J0)}
    frontier = [J0]
    best = score(J0)
    best_prog = []
    prog_of = {jkey(J0): []}
    depth = 0
    t0 = time.time()
    capped = False

    while frontier and not capped:
        depth += 1
        nxt = []
        for J in frontier:
            base_prog = prog_of[jkey(J)]
            for nm, op in zip(names, ops):
                if len(seen) >= args.cap:
                    capped = True
                    break
                J2 = []
                ok = True
                for s in J:
                    try:
                        J2.append(op(copy.deepcopy(s)))
                    except Exception:
                        J2.append(s)
                k = jkey(J2)
                if k in seen:
                    continue
                seen.add(k)
                prog_of[k] = base_prog + [nm]
                nxt.append(J2)
                sc = score(J2)
                if sc > best:
                    best = sc
                    best_prog = prog_of[k]
                    print("  depth %2d  NEW BEST %d/%d = %.4f  via %s"
                          % (depth, sc, len(tasks), sc / len(tasks), " -> ".join(best_prog)))
            if capped:
                break
        print("  depth %2d done: %d joint states total, best %d/%d, %.0fs"
              % (depth, len(seen), best, len(tasks), time.time() - t0))
        frontier = nxt

    ceiling = best / len(tasks)
    print()
    print("=" * 74)
    if capped:
        print("SEARCH CAPPED at %d joint states -- the number below is a LOWER BOUND"
              % args.cap)
        print("on the true all-depths ceiling, not the ceiling itself.")
    else:
        print("SEARCH EXHAUSTED: the joint reachable set closed. This IS the ceiling.")
    print("BEST ACHIEVABLE BY ANY PROGRAM, ANY DEPTH, ANY REPETITION = %d/%d = %.4f"
          % (best, len(tasks), ceiling))
    print("O1's enumerated optimum (k<=10, no repeats)               = 0.8333")
    print("per-task upper bound (different program per task allowed) = 0.8917")
    print("=" * 74)
    print()
    print("best program found (%d ops): %s" % (len(best_prog), " -> ".join(best_prog) or "<empty>"))
    print()
    if ceiling > 100.0 / 120.0 + 1e-9:
        print("VERDICT: KILL FIRES. A program outside O1's bounds beats 0.833.")
    elif not capped:
        print("VERDICT: 0.8333 is EXACT. No program of any depth, with any repetition, in")
        print("any order, with any tail, exceeds what O1 found. The k<=10 / no-repetition")
        print("qualifier is removed outright and the ceiling claim is at its strongest.")
    else:
        print("VERDICT: INCONCLUSIVE at this cap. Nothing above 0.8333 was found, but the")
        print("joint set did not close, so no upper bound is established. Raise --cap.")

    Path(args.out).write_text(json.dumps({
        "capped": capped, "cap": args.cap, "joint_states": len(seen),
        "best_correct": best, "n_tasks": len(tasks), "ceiling": ceiling,
        "best_program": best_prog, "depth_reached": depth,
        "known_organism_acc": known_acc,
    }, indent=1), encoding="utf-8")
    print("\nwrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
