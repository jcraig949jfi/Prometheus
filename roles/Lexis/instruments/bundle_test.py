"""Interface complementarity: does a COMPUTE primitive plus a READOUT primitive beat both?

The external review of 2026-08-25 refused to let "readout bottleneck" stand as an
interpretation of `NEW = 1 and dE = 0`, and proposed the measurement that would settle it:

    "test minimal bundles as well as primitives. Parser alone; readout alone;
     parser+readout. If each alone gives zero and the pair gives positive dS, you have
     directly demonstrated an interface complementarity rather than merely inferred one.
     The strongest version would be almost embarrassingly clean:
        new parser       NEW=1  dS=0
        new router       NEW=1  dS=0
        parser + router  NEW=1  dS>0"

It also named the three nested explanations the singleton result cannot separate:

    A. dead computation  - the value is simply wrong or irrelevant
    B. correct computation, incompatible representation
    C. correct computation, missing routing

A positive pair discriminates: if the value were wrong (A), adding a reader cannot make it
right. So `pair > 0` with `each = 0` is direct evidence for B/C over A.

WHAT IS MEASURED. For each bundle, over the baseline clean pool C:
  dE      tasks whose correct answer enters the closure
  dS      rise in the exact single-program ceiling (joint BFS, exhausted or reported capped)
  dROBUST rise in the permutation-robust per-task bound (correct under ALL 24 orderings)

The robust column is included because the same review established that ordinary correctness
credits positional fallback. A bundle that only moves `dS` and not `dROBUST` has bought a
guess, not an answer.

PRE-COMMITTED, before the run:
  each alone 0 and pair > 0  -> interface complementarity DEMONSTRATED; "readout
                                bottleneck" stops being interpretation.
  pair also 0                -> explanation A survives; my diagnosis was wrong and the
                                candidates are simply not useful.
  either alone > 0           -> the singleton result was pool-dependent, not a bottleneck.

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
from o1_enumerate import build_battery              # noqa: E402
from _answer_slice import D as _SLICE               # noqa: E402
from candidate_primitives import CANDIDATES         # noqa: E402

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


def joint_ceiling(deltas, oks, n_ops, cap):
    nT = len(deltas)
    start = bytes([0] * nT)
    seen, frontier = {start}, [start]
    best = sum(oks[t][0] for t in range(nT))
    while frontier:
        nxt = []
        for b in frontier:
            for o in range(n_ops):
                nb = bytes(deltas[t][b[t]][o] for t in range(nT))
                if nb in seen:
                    continue
                seen.add(nb)
                nxt.append(nb)
                sc = sum(oks[t][nb[t]] for t in range(nT))
                if sc > best:
                    best = sc
                if len(seen) >= cap:
                    return best, False, len(seen)
        frontier = nxt
    return best, True, len(seen)


def robust_solvable(task, ops, cap):
    variants = [table(task["prompt"],
                      [task["candidates"][i] for i in p],
                      task["correct"], ops)
                for p in permutations(range(len(task["candidates"])))]
    nV, nO = len(variants), len(ops)
    if max(len(v[0]) for v in variants) > 255:
        return None
    start = bytes([0] * nV)

    def allok(b):
        return all(variants[v][1][b[v]] for v in range(nV))
    if allok(start):
        return True
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
                    return True
                nxt.append(nb)
                if len(seen) >= cap:
                    return None
        frontier = nxt
    return False


def evaluate(label, extra_ops, base_ops, tasks, cap, rcap):
    ops = base_ops + list(extra_ops)
    tabs = [table(t["prompt"], t["candidates"], t["correct"], ops) for t in tasks]
    reach = [bool(any(o[1])) for o in tabs]
    ceil, exh, nj = joint_ceiling([o[0] for o in tabs], [o[1] for o in tabs], len(ops), cap)
    rob, unres = [], []
    for i, t in enumerate(tasks):
        r = robust_solvable(t, ops, rcap)
        if r is None:
            unres.append(i)
        elif r:
            rob.append(i)
    return {"label": label, "n_ops": len(ops), "reach": reach,
            "reach_n": sum(reach), "ceiling": ceil, "exhausted": exh, "joint": nj,
            "robust": rob, "robust_n": len(rob), "robust_unresolved": unres}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=2_000_000)
    ap.add_argument("--rcap", type=int, default=300000)
    ap.add_argument("--compute", default="lexis_op_subtract")
    ap.add_argument("--readout", default="lexis_score_by_value_match__g")
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "bundle_test_result.json"))
    args = ap.parse_args()

    tasks, bounds = build_battery()
    base_names = [n for n in sorted(be.REGISTRY)
                  if (be.role_of(n) == "transformer" or n in be.GUARDED_SCORERS)
                  and set(be.REGISTRY[n][0].writes) & set(_SLICE)]
    base_ops = [be.REGISTRY[n][0] for n in base_names]
    C = CANDIDATES[args.compute]
    R = CANDIDATES[args.readout]

    print("BASELINE C: %d operators (Apollo clean-routing pool)" % len(base_ops))
    print("compute primitive : %s" % args.compute)
    print("readout primitive : %s" % args.readout)
    print()

    arms = [("baseline C", ()), ("C + compute", (C,)),
            ("C + readout", (R,)), ("C + compute + readout", (C, R))]
    out, t0 = {}, time.time()
    for label, extra in arms:
        r = evaluate(label, extra, base_ops, tasks, args.cap, args.rcap)
        out[label] = {k: v for k, v in r.items() if k != "reach"}
        out[label]["reach_tasks"] = [i for i, b in enumerate(r["reach"]) if b]
        print("  %-24s ops=%-3d  reachable=%3d  ceiling=%3d/%d %-11s  robust=%3d %s (%.0fs)"
              % (label, r["n_ops"], r["reach_n"], r["ceiling"], len(tasks),
                 "(exhausted)" if r["exhausted"] else "(CAPPED)", r["robust_n"],
                 ("unres %d" % len(r["robust_unresolved"])) if r["robust_unresolved"] else "",
                 time.time() - t0))

    b = out["baseline C"]
    print()
    print("=" * 76)
    print("DELTAS against baseline C")
    print("=" * 76)
    print("  %-24s %8s %8s %9s" % ("arm", "dE", "dS", "dROBUST"))
    for label, _ in arms[1:]:
        a = out[label]
        a["dE"] = a["reach_n"] - b["reach_n"]
        a["dS"] = a["ceiling"] - b["ceiling"]
        a["dROBUST"] = a["robust_n"] - b["robust_n"]
        print("  %-24s %+8d %+8d %+9d" % (label, a["dE"], a["dS"], a["dROBUST"]))
    print()

    c_alone = out["C + compute"]
    r_alone = out["C + readout"]
    pair = out["C + compute + readout"]
    singles_zero = (c_alone["dS"] == 0 and r_alone["dS"] == 0)
    pair_pos = pair["dS"] > 0
    if singles_zero and pair_pos:
        print("READING: INTERFACE COMPLEMENTARITY DEMONSTRATED.")
        print("  Each primitive alone moves nothing; together they move the exact ceiling")
        print("  by %+d. A wrong value cannot be rescued by adding a reader, so explanation" % pair["dS"])
        print("  A (dead computation) is ruled out. The deficit was READOUT, and this is")
        print("  now a measurement rather than an interpretation.")
        if pair["dROBUST"] > 0:
            print("  And the gain survives all 24 permutations (+%d), so it is not a"
                  % pair["dROBUST"])
            print("  positional fallback.")
        else:
            print("  BUT dROBUST = 0: the ceiling gain does NOT survive permutation. The")
            print("  pair bought a guess, not an answer. Report it as such.")
    elif not pair_pos:
        print("READING: the pair moves nothing either. Explanation A survives -- the")
        print("  computed values are not useful, and the readout-bottleneck diagnosis was")
        print("  wrong. Report the diagnosis as withdrawn.")
    else:
        print("READING: at least one primitive moves the ceiling ALONE, so the singleton")
        print("  result was pool-dependent rather than a bottleneck. Re-examine.")

    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\nwrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
