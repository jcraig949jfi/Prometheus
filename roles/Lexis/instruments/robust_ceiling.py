"""The ceiling under PERMUTATION-ROBUST correctness, over the UNRESTRICTED operator pool.

This exists to remove the one judgment call the external review flagged as load-bearing.

THE PROBLEM THE REVIEWER IDENTIFIED. My exact 0.8333 holds over Apollo's "clean" pool
(guarded scorers only). The unrestricted pool reaches 0.8917, and I excluded the operator
responsible on the grounds that Apollo itself excludes it. That defence is real -- the
restriction predates the experiment and is mechanically enforced -- but it is still the
move that rescues a result going my way, and it deserves not to be load-bearing.

THE REVIEWER'S FIX, ADOPTED VERBATIM:

    "Instead of saying 'this operator is excluded because Apollo's registry says so', ask
     for the best unrestricted program subject to permutation robustness... If unrestricted
     closure under that objective still caps at 100/120, the controversial operator-pool
     boundary becomes much less important."

METHOD. A task counts as solved only if the program answers it correctly under **all 24**
permutations of its 4 candidates -- not the two-permutation canary, which the same review
correctly called an inadequate characterisation of invariance (2 points of a 24-element
orbit; reverse and rotate generate D_4, and D_4 is not S_4).

For each task, build the 24 permuted variants as 24 coordinates of a joint state and run
the joint BFS over them under the **unrestricted** 27-operator pool. A reachable joint
state with all 24 coordinates correct witnesses a program that answers that task robustly.
Because each task gets its own search, this is a PER-TASK upper bound -- it allows a
different program per task, which the real system cannot do. So it OVER-counts, and if even
this over-count fails to exceed 100/120, no single unrestricted program can either.

WHAT THE READING WILL BE, fixed before the run:

  robust bound <= 100/120  ->  the operator-pool restriction stops mattering. Restoring the
                               excluded operator buys nothing that survives the invariance
                               required of an answerer, and 0.8333 stands without the
                               contested narrowing.
  robust bound  > 100/120  ->  there is unrestricted headroom that is NOT guessing, the
                               restriction IS load-bearing, and the honest headline is the
                               unrestricted number with its qualifier.

Note what this test does and does not establish, per the same review: failing permutation
invariance demonstrates unacceptable order sensitivity; passing it demonstrates
permutation-equivariance, NOT semantic reasoning. "Choose the shortest string" passes.
The bound is therefore an upper bound on robust answering, not evidence of reasoning.

Read-only with respect to apollo/.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from collections import deque
from itertools import permutations
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


def apply_op(op, s):
    try:
        return op(copy.deepcopy(s))
    except Exception:
        return s


def table(prompt, cands, correct, ops):
    """Per-variant transition table over the answer-relevant slice."""
    s0 = BlackboardState(problem_text=prompt, candidates=list(cands))
    states, index, delta, q = [s0], {skey(s0): 0}, [], deque([0])
    while q:
        i = q.popleft()
        while len(delta) <= i:
            delta.append([None] * len(ops))
        for o, op in enumerate(ops):
            s2 = apply_op(op, states[i])
            k = skey(s2)
            j = index.get(k)
            if j is None:
                j = len(states)
                index[k] = j
                states.append(s2)
                q.append(j)
            delta[i][o] = j
    ok = [1 if s.selected_answer == correct else 0 for s in states]
    return delta, ok


def robust_solvable(task, ops, cap):
    """Is there ONE program answering this task correctly under all 24 permutations?"""
    perms = list(permutations(range(len(task["candidates"]))))
    variants = []
    for p in perms:
        cands = [task["candidates"][i] for i in p]
        variants.append(table(task["prompt"], cands, task["correct"], ops))
    nV, nO = len(variants), len(ops)
    if max(len(v[0]) for v in variants) > 255:
        return None, 0, False            # byte encoding invalid; report as unresolved
    start = bytes([0] * nV)

    def allok(b):
        return all(variants[v][1][b[v]] for v in range(nV))

    if allok(start):
        return True, 1, True
    seen, frontier = {start}, [start]
    while frontier:
        nxt = []
        for b in frontier:
            for o in range(nO):
                nb = bytes(variants[v][0][b[v]][o] for v in range(nV))
                if nb in seen:
                    continue
                seen.add(nb)
                if allok(nb):
                    return True, len(seen), True
                nxt.append(nb)
                if len(seen) >= cap:
                    return False, len(seen), False   # unresolved, not a negative
        frontier = nxt
    return False, len(seen), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=400000)
    ap.add_argument("--pool", choices=["all", "clean"], default="all")
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "robust_ceiling_result.json"))
    args = ap.parse_args()

    tasks, bounds = build_battery()
    names = sorted(be.REGISTRY)
    if args.pool == "clean":
        names = [n for n in names
                 if be.role_of(n) == "transformer" or n in be.GUARDED_SCORERS]
    ops = [be.REGISTRY[n][0] for n in names]

    known = be._evaluate_acc([be.REGISTRY[n][0] for n in KNOWN_0833], tasks)
    print("POSITIVE CONTROL  known organism = %.4f (expect 0.8333) -> %s"
          % (known, "MATCH" if abs(known - 0.8333) < 1e-3 else "MISMATCH"))
    if abs(known - 0.8333) >= 1e-3:
        return 2
    print("pool '%s': %d operators. Objective: correct under ALL 24 candidate permutations."
          % (args.pool, len(ops)))
    print("Per-task search, so a DIFFERENT program is allowed per task -- this OVER-counts.")
    print()

    t0 = time.time()
    solved, unresolved, rows = [], [], []
    for i, t in enumerate(tasks):
        ok, nstates, resolved = robust_solvable(t, ops, args.cap)
        if not resolved:
            unresolved.append(i)
        elif ok:
            solved.append(i)
        rows.append({"task": i, "category": t.get("category"), "robust": bool(ok),
                     "resolved": bool(resolved), "joint_states": nstates})
        if (i + 1) % 20 == 0 or i == len(tasks) - 1:
            print("  %3d/%d  robustly solvable so far %d  unresolved %d  (%.0fs)"
                  % (i + 1, len(tasks), len(solved), len(unresolved), time.time() - t0))

    n = len(tasks)
    bound = len(solved) / n
    print()
    print("=" * 76)
    print("PERMUTATION-ROBUST PER-TASK UPPER BOUND, pool '%s' = %d/%d = %.4f"
          % (args.pool, len(solved), n, bound))
    print("exact clean-pool ceiling under ordinary correctness    = 100/120 = 0.8333")
    print("unrestricted-pool ceiling under ordinary correctness   = 107/120 = 0.8917")
    print("=" * 76)
    if unresolved:
        print("!! UNRESOLVED on %d task(s) at cap %d: %s" % (len(unresolved), args.cap,
                                                             unresolved[:12]))
        print("   Those are counted as NOT robustly solvable, which biases the bound DOWN.")
        print("   Raise --cap before treating the number as tight.")
    print()
    for name, a, b in bounds:
        sub = [r for r in rows[a:b]]
        k = sum(1 for r in sub if r["robust"])
        print("   %-11s %3d/%-3d = %.3f" % (name, k, len(sub), k / max(1, len(sub))))
    print()
    if args.pool != "all":
        print("READING: not applicable. The pre-committed reading is defined for --pool all;")
        print("this run is the MATCHED CLEAN-POOL COMPARATOR, whose only job is to say what")
        print("the same objective yields without the contested operator restored.")
    elif bound <= 100.0 / 120.0 + 1e-9:
        print("READING: the operator-pool restriction STOPS MATTERING. Even with every")
        print("operator restored and a different program allowed per task, nothing beyond")
        print("100/120 survives the invariance required of an answerer. 0.8333 stands")
        print("WITHOUT the contested narrowing.")
    else:
        print("READING: there is unrestricted headroom that is NOT guessing. The pool")
        print("restriction IS load-bearing and the honest headline is the unrestricted")
        print("number with its qualifier attached.")

    Path(args.out).write_text(json.dumps(
        {"pool": args.pool, "n_tasks": n, "robust_solvable": solved,
         "unresolved": unresolved, "bound": bound, "cap": args.cap,
         "known_organism_acc": known, "rows": rows}, indent=1), encoding="utf-8")
    print("\nwrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
