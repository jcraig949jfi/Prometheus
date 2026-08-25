"""G5 — the redundancy gate, made decidable, with the dS/dE ledger kept separate.

CONTROLS.md section 3 specifies the predicate:

    NEW(p, C, T) = 1[ not exists g in G(C) : for all x in T, p(x) = g(x) ]

"is this primitive already representable by a composition of the existing vocabulary over
the claimed domain?" On Apollo it is not merely decidable in principle -- the reachability
closure computed for STEP 1 makes it computable exactly, because the closure IS G(C)
evaluated behaviourally on T.

THREE SEPARATE QUESTIONS, THREE SEPARATE COLUMNS. They have been conflated under the word
"reachability" throughout this study and they will not share a column again.

  NEW   (representability)  Does p ever produce a blackboard state that no composition over
                            C can produce? Computed by: build the closure under C; apply p
                            to every state in it; if every result is already in the closure,
                            p is REPRESENTABLE -- NEW = 0 -- and p is a search macro at best.

  dE    (expressible-function gain)  How many tasks have their correct answer inside the
                            closure of C+p but outside the closure of C? This is new
                            EXPRESSIVE power: previously impossible, now possible.

  dS    (searchability gain)  How much does the exact single-program ceiling rise? A
                            primitive can have dE > 0 and dS = 0 (the answer becomes
                            reachable but no single program picks it up alongside the rest),
                            and it can have dE = 0 and dS > 0 (pure macro).

A primitive that is admitted on dS alone is a search macro. The Prometheus thesis needs
dE > 0. Both are reported; neither is allowed to stand in for the other.

BASELINE C: Apollo's clean-routing pool -- transformers plus GUARDED scorers, minus the two
operators proven in `answer_slice.py` to write only outside the answer-relevant slice. This
is the pool under which 0.8333 was obtained and defended, and its exact ceiling is
100/120 = 0.8333 with the joint closure EXHAUSTED (`product_ceiling_clean.json`).

CONFOUND DIRECTION, stated before any number is read. Adding an operator can only enlarge
a closure, so dE >= 0 and NEW is monotone. The risk runs the other way: a primitive can
raise the ceiling by GUESSING rather than by reasoning, exactly as `score_by_max_value` was
shown to do in STEP 1 section 4. So every ceiling gain is additionally checked against a
positional null -- if the newly-solved tasks concentrate on one candidate index, the gain is
guessing and is reported as such, not as capability.

Read-only with respect to apollo/.
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import sys
import time
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


def apply_op(op, s):
    try:
        return op(copy.deepcopy(s))
    except Exception:
        return s


def closure(task, ops):
    """-> (states, index, delta, is_correct) over the answer-relevant slice."""
    s0 = BlackboardState(problem_text=task["prompt"], candidates=task["candidates"])
    states, index = [s0], {skey(s0): 0}
    delta, q = [], deque([0])
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
    ic = [1 if s.selected_answer == task["correct"] else 0 for s in states]
    return states, index, delta, ic


def joint_ceiling(deltas, corrects, n_ops, cap):
    """Exact ceiling over all programs. -> (best, exhausted, n_joint)."""
    nT = len(deltas)
    start = bytes([0] * nT)
    seen, frontier = {start}, [start]
    best = sum(corrects[t][0] for t in range(nT))
    exhausted = True
    while frontier:
        nxt = []
        for b in frontier:
            for o in range(n_ops):
                nb = bytes(deltas[t][b[t]][o] for t in range(nT))
                if nb in seen:
                    continue
                seen.add(nb)
                nxt.append(nb)
                sc = sum(corrects[t][nb[t]] for t in range(nT))
                if sc > best:
                    best = sc
                if len(seen) >= cap:
                    return best, False, len(seen)
        frontier = nxt
    return best, exhausted, len(seen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=4_000_000)
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "g5_redundancy_result.json"))
    args = ap.parse_args()

    tasks, bounds = build_battery()
    nT = len(tasks)

    base_names = [n for n in sorted(be.REGISTRY)
                  if be.role_of(n) == "transformer" or n in be.GUARDED_SCORERS]
    base_names = [n for n in base_names
                  if set(be.REGISTRY[n][0].writes) & set(_SLICE)]
    base_ops = [be.REGISTRY[n][0] for n in base_names]
    print("BASELINE VOCABULARY C: %d operators (Apollo clean-routing pool, "
          "decorative ops pruned)" % len(base_ops))

    t0 = time.time()
    base = [closure(t, base_ops) for t in tasks]
    base_deltas = [b[2] for b in base]
    base_corrects = [b[3] for b in base]
    base_reach = [bool(any(b[3])) for b in base]
    base_ceiling, base_exh, base_nj = joint_ceiling(
        base_deltas, base_corrects, len(base_ops), args.cap)
    print("  per-task closures: %d states total (%.1fs)" % (sum(len(b[0]) for b in base),
                                                            time.time() - t0))
    print("  tasks with correct answer inside the closure of C : %d/%d" % (sum(base_reach), nT))
    print("  EXACT ceiling of C: %d/%d = %.4f   (%s, %d joint states)"
          % (base_ceiling, nT, base_ceiling / nT,
             "closure EXHAUSTED" if base_exh else "CAPPED - lower bound only", base_nj))
    if not base_exh:
        print("  refusing to report deltas against a capped baseline.")
        return 2
    print()

    results = {}
    for cname, cop in CANDIDATES.items():
        print("=" * 74)
        print("CANDIDATE  %s" % cname)
        print("=" * 74)

        # ---- NEW(p, C, T): does p ever leave the closure of C? -------------------
        escapes, escape_tasks = 0, []
        for i, t in enumerate(tasks):
            states, index, _d, _c = base[i]
            left = False
            for s in states:
                if skey(apply_op(cop, s)) not in index:
                    left = True
                    break
            if left:
                escapes += 1
                escape_tasks.append(i)
        is_new = escapes > 0
        print("  NEW(p,C,T) : %s" % ("1  -- p produces states no composition over C reaches"
                                     if is_new else
                                     "0  -- REPRESENTABLE; every p-image is already in the "
                                     "closure of C. Search macro at best."))
        print("     tasks where p escapes the closure: %d/%d" % (escapes, nT))

        # ---- dE and dS ------------------------------------------------------------
        ops2 = base_ops + [cop]
        c2 = [closure(t, ops2) for t in tasks]
        reach2 = [bool(any(x[3])) for x in c2]
        dE_tasks = [i for i in range(nT) if reach2[i] and not base_reach[i]]
        ceil2, exh2, nj2 = joint_ceiling([x[2] for x in c2], [x[3] for x in c2],
                                         len(ops2), args.cap)

        dE = len(dE_tasks)
        dS_raw = ceil2 - base_ceiling
        print("     closure of C+p: %s, %d joint states" %
              ("EXHAUSTED" if exh2 else "CAPPED (ceiling is a LOWER bound)", nj2))
        print()
        print("  dE  expressible-function gain : %+d tasks  (%+.4f of battery)"
              % (dE, dE / nT))
        print("      newly-expressible tasks   : %s" % (dE_tasks or "none"))
        print("  ceiling of C+p                : %d/%d = %.4f  (was %.4f)"
              % (ceil2, nT, ceil2 / nT, base_ceiling / nT))
        print("  dS  searchability gain        : %+d tasks  (%+.4f of battery)"
              % (dS_raw, dS_raw / nT))
        if dE and dS_raw:
            print("      -> the ceiling rise is BACKED by new expressibility, not macro-ing")
        elif dS_raw and not dE:
            print("      -> PURE SEARCH MACRO: ceiling rose with no new expressible function")
        elif dE and not dS_raw:
            print("      -> expressible but UNROUTED: no single program picks it up alongside"
                  " the rest. dE is real, dS is zero.")

        # ---- positional null on the ceiling gain ---------------------------------
        null_note = None
        if dS_raw > 0:
            idx = [tasks[i]["candidates"].index(tasks[i]["correct"])
                   for i in dE_tasks if tasks[i]["correct"] in tasks[i]["candidates"]]
            cnt = collections.Counter(idx)
            top = cnt.most_common(1)[0] if cnt else (None, 0)
            print()
            print("  POSITIONAL NULL on the gained tasks: answer-index distribution %s"
                  % dict(sorted(cnt.items())))
            if idx and top[1] == len(idx) and len(idx) >= 3:
                null_note = ("ALL %d gained tasks have the correct answer at index %s -- "
                             "this is the guessing signature, not capability" % (top[1], top[0]))
                print("  !! %s" % null_note)
            else:
                null_note = "gained-task answer positions are not concentrated on one index"
                print("  -> %s" % null_note)

        results[cname] = {
            "NEW": int(is_new), "escape_tasks": escape_tasks,
            "dE_tasks": dE_tasks, "dE": dE, "dE_frac": dE / nT,
            "ceiling_with_p": ceil2 / nT, "ceiling_baseline": base_ceiling / nT,
            "dS": dS_raw, "dS_frac": dS_raw / nT,
            "closure_exhausted": exh2, "positional_null": null_note,
        }
        print()

    # ---- ledger --------------------------------------------------------------------
    print("=" * 74)
    print("G5 LEDGER -- two columns, never merged")
    print("=" * 74)
    print("  %-34s %5s %8s %8s" % ("primitive", "NEW", "dE", "dS"))
    for k, v in results.items():
        print("  %-34s %5d %+8.4f %+8.4f" % (k[:34], v["NEW"], v["dE_frac"], v["dS_frac"]))
    print()
    admit = [k for k, v in results.items() if v["NEW"] and v["dE"] > 0]
    print("  vocabulary expansions (NEW=1 and dE>0): %s" % (admit or "none"))
    print("  search macros (NEW=0 or dE=0)         : %s"
          % ([k for k in results if k not in admit] or "none"))

    Path(args.out).write_text(json.dumps({
        "baseline_ops": base_names, "baseline_ceiling": base_ceiling / nT,
        "baseline_exhausted": base_exh, "n_tasks": nT, "candidates": results,
    }, indent=1), encoding="utf-8")
    print("\nwrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
