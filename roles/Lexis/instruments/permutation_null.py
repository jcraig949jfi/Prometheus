"""The metamorphic null that separates capability from guessing.

WHY POSITION-COUNTING IS NOT ENOUGH. `g5_redundancy.py` flags a gain when every
newly-solved task has its correct answer at candidate index 0, because that is the
signature STEP 1 section 4 caught: `score_by_max_value` falling through to its documented
`candidates[0]` default. But the flag is a heuristic. A genuinely capable operator can also
happen to gain tasks whose answers sit at index 0 -- the canary's answer positions are
near-uniform (13/11/14/12), so which residual tasks a real capability picks up is not under
its control.

THE DECISIVE TEST IS METAMORPHIC, not positional. Permute each task's candidate list. The
problem text, the correct answer string, and the answer set are unchanged -- only the order
of the options moves. Then:

    a CONTENT-driven answer is invariant under the permutation
    a POSITION-driven answer is destroyed by it

So: recompute the per-task closure under a permutation that moves the correct answer OFF
index 0, and ask whether the correct answer is still inside it. Survives -> capability.
Vanishes -> guessing, and the dE credit is withdrawn.

Two permutations are run, both deterministic and seedless (no Math.random equivalent, no
hidden state): REVERSE, and ROTATE-BY-ONE. A result is only credited if it survives both.

CONFOUND DIRECTION, before the numbers: permuting can only remove a positional advantage,
never manufacture one, so this test can only LOWER a dE claim. That is the direction we want
a null to push.

Read-only with respect to apollo/.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import deque
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


def reach_correct(prompt, cands, correct, ops):
    """Is `correct` emitted by any state reachable from (prompt, cands)?"""
    s0 = BlackboardState(problem_text=prompt, candidates=list(cands))
    seen, frontier = {skey(s0)}, deque([s0])
    if s0.selected_answer == correct:
        return True
    while frontier:
        s = frontier.popleft()
        for op in ops:
            try:
                s2 = op(copy.deepcopy(s))
            except Exception:
                continue
            k = skey(s2)
            if k in seen:
                continue
            seen.add(k)
            if s2.selected_answer == correct:
                return True
            frontier.append(s2)
    return False


PERMS = {
    "identity": lambda c: list(c),
    "reverse": lambda c: list(reversed(c)),
    "rotate1": lambda c: list(c[1:]) + list(c[:1]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="", help="comma-separated task indices; "
                                                "default = the dE tasks in the G5 result")
    ap.add_argument("--g5", default=str(HERE.parent / "notes" / "g5_redundancy_result.json"))
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "permutation_null_result.json"))
    args = ap.parse_args()

    tasks, _bounds = build_battery()
    base_names = [n for n in sorted(be.REGISTRY)
                  if (be.role_of(n) == "transformer" or n in be.GUARDED_SCORERS)
                  and set(be.REGISTRY[n][0].writes) & set(_SLICE)]
    base_ops = [be.REGISTRY[n][0] for n in base_names]

    if args.tasks:
        targets = {"<manual>": [int(x) for x in args.tasks.split(",")]}
    else:
        g5 = json.loads(Path(args.g5).read_text(encoding="utf-8"))
        targets = {k: v["dE_tasks"] for k, v in g5["candidates"].items() if v["dE_tasks"]}

    out = {}
    for cname, idxs in targets.items():
        cop = CANDIDATES[cname] if cname in CANDIDATES else None
        ops = base_ops + ([cop] if cop else [])
        print("=" * 74)
        print("CANDIDATE %s -- metamorphic null over its %d claimed dE tasks"
              % (cname, len(idxs)))
        print("=" * 74)
        rows = []
        for i in idxs:
            t = tasks[i]
            res = {}
            for pname, perm in PERMS.items():
                cands = perm(t["candidates"])
                res[pname] = reach_correct(t["prompt"], cands, t["correct"], ops)
            pos0 = t["candidates"].index(t["correct"]) if t["correct"] in t["candidates"] else -1
            survives = res["reverse"] and res["rotate1"]
            rows.append({"task": i, "category": t["category"], "orig_index": pos0,
                         **res, "survives": survives})
            print("  task %3d [%-18s] answer idx %d   identity=%-5s reverse=%-5s "
                  "rotate1=%-5s  -> %s"
                  % (i, t["category"], pos0, res["identity"], res["reverse"],
                     res["rotate1"], "SURVIVES" if survives else "WITHDRAWN"))
        n_ok = sum(1 for r in rows if r["survives"])
        print()
        print("  dE claimed: %d   dE surviving the permutation null: %d" % (len(idxs), n_ok))
        if n_ok == len(idxs):
            print("  -> the gain is CONTENT-driven. The positional flag was a false alarm.")
        elif n_ok == 0:
            print("  -> the gain is entirely POSITIONAL. dE credit withdrawn in full.")
        else:
            print("  -> MIXED. Only the %d surviving tasks may be credited as dE." % n_ok)
        out[cname] = {"claimed": len(idxs), "surviving": n_ok, "rows": rows}
        print()

    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
