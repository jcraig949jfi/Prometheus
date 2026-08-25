"""STEP 1, part 3 (fast) — the EXACT single-program ceiling, at all depths, with repetition.

Same object as `product_ceiling.py`, computed the way that actually finishes.

METHOD. Two stages.

  Stage 1, per task. BFS the answer-relevant closure of task t (see `answer_slice.py` for
  why keying on the slice D is sound and why it terminates). Number its states 0..n_t-1 and
  build the transition table  delta_t[i][o] = index of the state reached by applying
  operator o to state i.  Measured: 5,029 states over 120 tasks, max 104 per task, so a
  state index fits in one byte.

  Stage 2, joint. A PROGRAM is an operator sequence. Because every operator is
  deterministic, a program induces exactly one trajectory per task, so the joint state is
  the 120-tuple of per-task state indices -- encoded here as a 120-byte string. The
  transition is 120 table lookups, no operator ever runs again. BFS from the initial joint
  state enumerates precisely the set of joint states reachable by SOME program, of ANY
  length, with ANY repetition, in ANY order, with ANY tail.

  CEILING = max over reachable joint states of the number of tasks whose selected_answer
  equals the correct answer, divided by 120.

If the frontier empties, that is the exact ceiling and STEP 1 is closed. If the cap is hit
first, the value is reported as a LOWER bound and labelled as one -- never silently.

PRE-COMMITTED (unchanged from product_ceiling.py, fixed before either ran):
    CEILING > 0.8333   -> "0.833 is the substrate's ceiling" is FALSIFIED as a number.
    CEILING == 0.8333  -> 0.8333 is exact at all depths and repetitions; O1's k<=10 /
                          no-repetition caveat is removed outright.

Read-only with respect to apollo/.
"""
from __future__ import annotations

import argparse
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


def build_task_table(task, ops):
    """-> (delta, is_correct) ; delta[i][o] = successor index, is_correct[i] = bool."""
    s0 = BlackboardState(problem_text=task["prompt"], candidates=task["candidates"])
    states = [s0]
    index = {skey(s0): 0}
    delta = []
    q = deque([0])
    while q:
        i = q.popleft()
        while len(delta) <= i:
            delta.append([None] * len(ops))
        s = states[i]
        for o, op in enumerate(ops):
            try:
                s2 = op(copy.deepcopy(s))
            except Exception:
                s2 = s
            k = skey(s2)
            j = index.get(k)
            if j is None:
                j = len(states)
                index[k] = j
                states.append(s2)
                q.append(j)
            delta[i][o] = j
    is_correct = [1 if s.selected_answer == task["correct"] else 0 for s in states]
    return delta, is_correct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=5_000_000)
    ap.add_argument("--pool", choices=["all", "clean"], default="all",
                    help="all   = every registry operator (the representational ceiling).\n"
                         "clean = transformers + GUARDED scorers only. This is Apollo's own"
                         " dispatch-mode pool: `evolve()` sets _MUT_SCORER_POOL ="
                         " GUARDED_SCORERS, and `fitness()` zeroes causal_composition_score"
                         " for any organism mixing a plain scorer with a guarded one"
                         " (routing_purity=0), because an unconditional scorer fires on"
                         " every task and racks up incidental hits. So 'clean' is the pool"
                         " under which 0.833 was actually obtained and defended.")
    ap.add_argument("--prune-decorative", action="store_true",
                    help="drop operators that write ONLY slots outside the answer-relevant "
                         "slice D. Provably cannot change any answer (answer_slice.py), so "
                         "this narrows the branching factor without narrowing the ceiling.")
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "product_ceiling_result.json"))
    args = ap.parse_args()

    tasks, bounds = build_battery()
    names = sorted(be.REGISTRY)
    if args.pool == "clean":
        names = [n for n in names
                 if be.role_of(n) == "transformer" or n in be.GUARDED_SCORERS]
    if args.prune_decorative:
        dec = [n for n in names
               if be.REGISTRY[n][0].writes and not (set(be.REGISTRY[n][0].writes) & set(_SLICE))]
        if dec:
            print("pruned as provably decorative (write nothing in D): %s" % dec)
        names = [n for n in names if n not in dec]
    print("operator pool '%s': %d operators" % (args.pool, len(names)))
    ops = [be.REGISTRY[n][0] for n in names]
    nT, nO = len(tasks), len(ops)

    known_acc = be._evaluate_acc([be.REGISTRY[n][0] for n in KNOWN_0833], tasks)
    print("POSITIVE CONTROL  known organism = %.4f (expect 0.8333) -> %s"
          % (known_acc, "MATCH" if abs(known_acc - 0.8333) < 1e-3 else "MISMATCH"))
    if abs(known_acc - 0.8333) >= 1e-3:
        return 2

    t0 = time.time()
    deltas, corrects = [], []
    for t in tasks:
        d, c = build_task_table(t, ops)
        deltas.append(d)
        corrects.append(c)
    sizes = [len(d) for d in deltas]
    print("stage 1: per-task closures built in %.1fs -- %d states total, max %d per task"
          % (time.time() - t0, sum(sizes), max(sizes)))
    if max(sizes) > 255:
        print("  a task closure exceeds 255 states; the byte encoding is invalid. Aborting.")
        return 2

    # ---- second positive control: the known organism's trajectory in the tables --------
    _missing = [n for n in KNOWN_0833 if n not in names]
    prog = [names.index(n) for n in KNOWN_0833 if n in names]
    cur = [0] * nT
    for o in prog:
        cur = [deltas[t][cur[t]][o] for t in range(nT)]
    tbl_acc = sum(corrects[t][cur[t]] for t in range(nT)) / nT
    if _missing:
        print("  note: known organism ops absent from this pool: %s" % _missing)
    print("POSITIVE CONTROL  known organism replayed THROUGH THE TABLES = %.4f -> %s"
          % (tbl_acc, "MATCH" if abs(tbl_acc - known_acc) < 1e-9 else "MISMATCH"))
    if not _missing and abs(tbl_acc - known_acc) >= 1e-9:
        print("  the transition tables do not reproduce the substrate. Aborting.")
        return 2
    print()

    # ---- stage 2: joint BFS -----------------------------------------------------------
    start = bytes([0] * nT)

    def score(b):
        return sum(corrects[t][b[t]] for t in range(nT))

    seen = {start}
    frontier = [start]
    best = score(start)
    best_key = start
    parent = {start: None}
    depth = 0
    capped = False
    t1 = time.time()

    while frontier and not capped:
        depth += 1
        nxt = []
        for b in frontier:
            for o in range(nO):
                nb = bytes(deltas[t][b[t]][o] for t in range(nT))
                if nb in seen:
                    continue
                seen.add(nb)
                parent[nb] = (b, o)
                nxt.append(nb)
                sc = score(nb)
                if sc > best:
                    best, best_key = sc, nb
                    print("  depth %2d  NEW BEST %d/%d = %.4f" % (depth, sc, nT, sc / nT))
                if len(seen) >= args.cap:
                    capped = True
                    break
            if capped:
                break
        print("  depth %2d: %d joint states, frontier %d, best %d/%d, %.0fs"
              % (depth, len(seen), len(nxt), best, nT, time.time() - t1))
        frontier = nxt

    # recover the winning program
    prog_names, cur_b = [], best_key
    while parent.get(cur_b):
        pb, o = parent[cur_b]
        prog_names.append(names[o])
        cur_b = pb
    prog_names.reverse()

    ceiling = best / nT
    print()
    print("=" * 76)
    if capped:
        print("SEARCH CAPPED at %d joint states. The figure below is a LOWER BOUND on the"
              % args.cap)
        print("all-depths ceiling, not the ceiling.")
    else:
        print("SEARCH EXHAUSTED -- the joint reachable set CLOSED. This is exact.")
    print("BEST ACHIEVABLE BY ANY PROGRAM, ANY DEPTH, ANY REPETITION = %d/%d = %.4f"
          % (best, nT, ceiling))
    print("O1's enumerated optimum (k<=10 transformers, no repeats)   = 0.8333")
    print("per-task upper bound (a different program allowed per task)= 0.8917")
    print("=" * 76)
    print()
    print("best program (%d ops): %s" % (len(prog_names), " -> ".join(prog_names) or "<empty>"))
    print()
    if ceiling > 100.0 / 120.0 + 1e-9:
        print("VERDICT: KILL FIRES. A program outside O1's bounds beats 0.833.")
    elif not capped:
        print("VERDICT: 0.8333 is EXACT. No program of any depth, with any repetition, in")
        print("any order, with any tail, exceeds what O1 found. The k<=10 / no-repetition")
        print("qualifier is removed outright.")
    else:
        print("VERDICT: INCONCLUSIVE at this cap. Nothing above 0.8333 was reached, but the")
        print("joint set did not close, so no upper bound is established.")

    Path(args.out).write_text(json.dumps({
        "capped": capped, "cap": args.cap, "joint_states": len(seen),
        "best_correct": best, "n_tasks": nT, "ceiling": ceiling,
        "best_program": prog_names, "depth_reached": depth,
        "known_organism_acc": known_acc, "table_replay_acc": tbl_acc,
        "per_task_closure_sizes": sizes,
    }, indent=1), encoding="utf-8")
    print("\nwrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
