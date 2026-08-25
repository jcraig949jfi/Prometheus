"""STEP 1 — close the DEPTH and REPETITION holes in Apollo's 0.833 ceiling claim.

READ-ONLY with respect to apollo/. It imports Apollo's own modules and calls Apollo's own
operators and Apollo's own battery. It writes nothing outside roles/Lexis/.

--------------------------------------------------------------------------------------
THE ARGUMENT
--------------------------------------------------------------------------------------
O1 enumerated pipelines of at most 10 transformers with no operator repeated. So a schedule
like `A B A` is unrepresentable by construction, and on a state-mutating substrate that is
a live gap. Extending the enumeration to greater depth with repetition allowed is
combinatorially hopeless (27^k).

But we do not need to enumerate PROGRAMS. Apollo's operators are deterministic functions
BlackboardState -> BlackboardState (verified: no `random`, no clock, no uuid anywhere in
blackboard_ops*.py). Therefore, for a fixed task, the set of states reachable by ANY
sequence of operators of ANY length with ANY repetition is exactly the closure of the
initial state under the 27-operator transition relation. That closure is computable by
breadth-first search, and if it is finite the search terminates.

`_evaluate_acc` reads exactly one thing: `out.selected_answer`. So for task t define

    R(t) = { s.selected_answer : s reachable from the initial state of t }

Any program, at any depth, with any repetition, any ordering, and any scorer tail, ends in
some reachable state. Hence its answer on t lies in R(t). Therefore

    ACC_MAX  =  |{ t : correct(t) in R(t) }| / |T|

is an UPPER BOUND on the accuracy of every program the substrate can express -- and it is a
LOOSE one, because it lets a different program answer each task, while Apollo must use one
program for all 120. If ACC_MAX <= 0.833 the ceiling claim is closed outright: no deeper or
repeating program can beat it, because no program of any shape can.

--------------------------------------------------------------------------------------
PRE-COMMITTED KILL (fixed before the run, per the STEP 1 instruction)
--------------------------------------------------------------------------------------
    ACC_MAX > 0.8333  ->  "Apollo is vocabulary-bound" is FALSIFIED at this rung. Report
                          immediately. Then identify which tasks became reachable and by
                          what state, because that names the missing composition.
    ACC_MAX <= 0.8333 ->  the k<=10 / no-repetition qualifier is REMOVED. The ceiling holds
                          for all depths and all repetitions, not merely the enumerated
                          bound.

Reachability is measured per task, so the gate is shown reachable in both directions before
it is read: ACC_MAX ranges over [0, 1] by construction and 0.8333 is interior.

--------------------------------------------------------------------------------------
Repo-relative by design (feedback_paths). Run from anywhere.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # <repo>/roles/Lexis/instruments -> <repo>
APOLLO = ROOT / "apollo"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(APOLLO / "src"))
sys.path.insert(0, str(APOLLO / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be                      # noqa: E402
from blackboard import BlackboardState              # noqa: E402
from o1_enumerate import build_battery, KNOWN_0833  # noqa: E402

# Provenance slots. They are append-only logs of what ran; no operator declares a read of
# any of them, and `_evaluate_acc` never looks at them. They must be excluded from the
# state key or every state would be distinct by construction and the closure would not
# exist.
PROVENANCE = ("write_log", "op_log", "skipped_ops")

# The state key is the ANSWER-RELEVANT BACKWARD SLICE D, not every slot.
#
# Keying on every slot does not terminate, and the reason is exact: `op_fencepost` and
# `distribution_reducer` do `state.evidence.append(...)` and never clear, so applying
# either k times yields k distinct states. The substrate is not finite-state.
#
# `answer_slice.py` computes D = the least slot set containing `selected_answer` and closed
# under "if an operator writes into D, all its reads are in D", over
# declared_reads UNION ast-detected reads (over-approximated, so D can only get larger; the
# two undeclared reads of `candidates` by select_nth are absorbed this way). Its theorem:
# states agreeing on D produce the same selected_answer under every operator sequence.
# `evidence` is outside D, so the accumulation is invisible to the answer and the closure
# over D is finite. Keying on D loses no reachable answer.
from _answer_slice import D as _SLICE          # noqa: E402
SEMANTIC_SLOTS = [f for f in BlackboardState.__dataclass_fields__
                  if f in _SLICE and f not in PROVENANCE]


def verify_provenance_is_not_read():
    """Guard the one assumption the whole method rests on: no operator reads a log slot."""
    offenders = []
    for name, (op, _role) in be.REGISTRY.items():
        for r in getattr(op, "reads", []):
            if r in PROVENANCE:
                offenders.append((name, r))
    return offenders


def state_key(s):
    """Canonical, order-insensitive-where-appropriate hashable key over semantic slots."""
    parts = []
    for f in SEMANTIC_SLOTS:
        v = getattr(s, f)
        if isinstance(v, set):
            parts.append((f, tuple(sorted(map(repr, v)))))
        elif isinstance(v, dict):
            parts.append((f, tuple(sorted((repr(k), repr(x)) for k, x in v.items()))))
        elif isinstance(v, list):
            parts.append((f, tuple(map(repr, v))))
        else:
            parts.append((f, repr(v)))
    return tuple(parts)


def reachable_answers(task, ops, cap):
    """BFS the closure of the initial state under every operator.

    Returns (answers, n_states, capped, n_expansions).
    """
    s0 = BlackboardState(problem_text=task["prompt"], candidates=task["candidates"])
    seen = {state_key(s0)}
    frontier = [s0]
    answers = {s0.selected_answer}
    capped = False
    expansions = 0
    while frontier:
        nxt = []
        for s in frontier:
            for op in ops:
                if len(seen) >= cap:
                    capped = True
                    break
                try:
                    s2 = op(copy.deepcopy(s))
                except Exception:
                    continue
                expansions += 1
                k = state_key(s2)
                if k not in seen:
                    seen.add(k)
                    answers.add(s2.selected_answer)
                    nxt.append(s2)
            if capped:
                break
        if capped:
            break
        frontier = nxt
    return answers, len(seen), capped, expansions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=20000,
                    help="max distinct states per task before declaring the closure "
                         "unresolved for that task (reported, never silent)")
    ap.add_argument("--limit", type=int, default=0, help="smoke mode: first N tasks only")
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "reachable_answers_result.json"))
    args = ap.parse_args()

    offenders = verify_provenance_is_not_read()
    print("PRECONDITION  no operator declares a read of a provenance slot : %s"
          % ("OK" if not offenders else "VIOLATED %s" % offenders))
    if offenders:
        print("  -> the state key is unsound. Aborting rather than reporting a wrong bound.")
        return 2

    tasks, bounds = build_battery()
    ops = [op for _n, (op, _r) in sorted(be.REGISTRY.items())]
    print("battery: %d tasks   operators offered to BFS: %d (every registry entry, "
          "every role, unrestricted position and multiplicity)" % (len(tasks), len(ops)))

    # ---- positive control, before anything is read ----------------------------------
    known_ops = [be.REGISTRY[n][0] for n in KNOWN_0833]
    known_acc = be._evaluate_acc(known_ops, tasks)
    print("POSITIVE CONTROL  known production organism via Apollo's own _evaluate_acc: "
          "%.4f  (O1 reports 0.8333)  -> %s"
          % (known_acc, "MATCH" if abs(known_acc - 0.8333) < 0.001 else "MISMATCH"))
    if abs(known_acc - 0.8333) >= 0.001:
        print("  -> not measuring the same object O1 measured. Aborting.")
        return 2

    if args.limit:
        tasks = tasks[:args.limit]
        bounds = [(n, a, min(b, len(tasks))) for n, a, b in bounds if a < len(tasks)]

    t0 = time.time()
    rows = []
    solvable = 0
    capped_tasks = []
    for i, t in enumerate(tasks):
        answers, n_states, capped, exp = reachable_answers(t, ops, args.cap)
        hit = t["correct"] in answers
        solvable += 1 if hit else 0
        if capped:
            capped_tasks.append(i)
        rows.append({"idx": i, "correct_reachable": bool(hit), "n_states": n_states,
                     "n_answers": len(answers), "capped": bool(capped),
                     "expansions": exp, "correct": t["correct"]})
        if (i + 1) % 10 == 0 or i == len(tasks) - 1:
            print("  %3d/%d  reachable-correct so far %d  (%.1fs)"
                  % (i + 1, len(tasks), solvable, time.time() - t0))

    acc_max = solvable / len(tasks)
    print()
    print("=" * 78)
    print("ACC_MAX  (upper bound over ALL programs, ANY depth, ANY repetition,")
    print("          ANY ordering, ANY tail, one program allowed PER TASK) = %.4f  (%d/%d)"
          % (acc_max, solvable, len(tasks)))
    print("O1's measured ceiling                                            = 0.8333")
    print("=" * 78)
    if capped_tasks:
        print("!! CLOSURE UNRESOLVED on %d task(s): %s" % (len(capped_tasks), capped_tasks[:20]))
        print("   Those tasks are counted by whatever was reached before the cap, so the")
        print("   bound above is NOT yet an upper bound for them. Re-run with a larger --cap.")
    else:
        print("closure RESOLVED on every task: the BFS reached a fixpoint, so the bound is exact.")
    print()

    # per-subset profile, matching O1's table
    print("per-subset reachable-correct rate:")
    for name, a, b in bounds:
        sub = rows[a:b]
        if not sub:
            continue
        k = sum(1 for r in sub if r["correct_reachable"])
        print("   %-11s %3d/%-3d = %.3f" % (name, k, len(sub), k / len(sub)))
    print()

    if acc_max > 100.0 / 120.0 + 1e-9:
        print("VERDICT: PRE-COMMITTED KILL FIRES.")
        print("  ACC_MAX exceeds 0.8333. Some task the substrate scores wrong is nevertheless")
        print("  answerable by SOME reachable state. 'Apollo is vocabulary-bound' is not")
        print("  established at this rung. The unreached-but-reachable tasks are listed below.")
        miss = [r["idx"] for r in rows if r["correct_reachable"]]
        print("  tasks with correct answer reachable: %d" % len(miss))
    else:
        print("VERDICT: no composition at any depth or repetition exceeds 0.8333.")
        print("  The k<=10 / no-repetition qualifier is REMOVED. The ceiling is a property")
        print("  of the vocabulary, not of the enumeration bound.")

    stats = {
        "acc_max": acc_max, "n_tasks": len(tasks), "n_solvable": solvable,
        "known_organism_acc": known_acc, "cap": args.cap,
        "capped_tasks": capped_tasks,
        "max_states_any_task": max((r["n_states"] for r in rows), default=0),
        "total_expansions": sum(r["expansions"] for r in rows),
        "per_task": rows,
    }
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(stats, indent=1), encoding="utf-8")
    print("\nwrote %s" % outp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
