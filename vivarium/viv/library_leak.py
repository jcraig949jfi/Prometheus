"""Does a component library contain the answers to the tasks it will be used on?

WHY THIS EXISTS, and it is not a hypothetical. Techne found on 2026-09-11 that
a library extracted from all 17 solved H1 programs contained three abstractions
that were each a COMPLETE held-out phase-2 solution. Handed to a search, those
targets are found as SIZE-1 LEAVES. The run would have measured the leak and
reported it as the library effect, and it would have looked like a large one.

Checking my own hand-built demo library immediately afterwards: `and x0 x1` is
a complete solution to task `and01` in the same task set, and the other two
components are the remaining subterms of `maj3`, also in the set. So the
"library solved maj3" result in tools/h1_h0_alpha_demo.py was contamination,
not a library effect. I had labelled the library an instrument control and
called its help "arithmetic" -- which flagged the wrong thing and missed the
leak entirely.

ARITY IS NOT THE PROBLEM. A zero-arity component is a legitimate leaf and an
arity-2 abstraction drawn from the test set would be exactly as contaminated.
The defect is the CORPUS: a library derived from, or containing, anything that
solves a held-out task.

WHAT THIS CANNOT DO. It compares SEMANTICS over the declared assignment set, so
it catches a component that computes a target's function however it is spelled.
It does NOT catch a library that merely makes a target much easier without
solving it -- that is a matter of degree, it is the effect the experiment is
trying to measure, and a checker that tried to rule on it would be ruling on
the hypothesis. `SUBTERM_OF_SOLUTION` is reported for exactly that reason: it
is a WARNING with a threshold nobody has agreed, not a verdict.

IT WORKS FROM THE TASKS, NOT FROM THE SOLUTIONS, and that is the difference
that matters. Techne's own first leak test compared s-expression strings
against SOLVED programs, which made it blind to two things: the same function
spelled differently, and any held-out target that was never solved -- 9 of
Archaeon's 12, since solutions are all such a test knows. Taking the task
truth tables directly sees all of them, solved or not. Their weaker test
happened to return the same answer on that corpus, and agreement between a
weak test and a strong one is a fact about the inputs rather than evidence of
coverage.

RUN IT ON AN EMPTY LIBRARY TOO. Techne's point, and it is right: a null leak
field reads as either "not checked" or "nothing to check" and a reader cannot
tell which, while CLEAN over zero components is a measurement. `check([], ...)`
is defined and returns CLEAN with `n_components: 0`.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent.parent

SOLVES_A_TASK = "SOLVES_A_TASK"
COMPOSES_TO_A_TASK = "COMPOSES_TO_A_TASK"
SUBTERM_OF_SOLUTION = "SUBTERM_OF_SOLUTION"
CLEAN = "CLEAN"

#: Classes that mean the library already contains its answers. The third does
#: not: it is a warning whose threshold nobody has agreed.
DISQUALIFYING = (SOLVES_A_TASK, COMPOSES_TO_A_TASK)


def _proteus():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from proteus.eval import boolean as _b                   # noqa: PLC0415
    return _b


def _tt(expr, _b) -> str:
    return "".join(str(v) for v in _b.truth_table(expr))


def _subterms(expr):
    yield expr
    if expr[0] not in ("const", "input"):
        for a in expr[1:]:
            yield from _subterms(a)


def check(components: List[dict], task_truth_tables: Dict[str, str], *,
          known_solutions: Optional[Dict[str, list]] = None) -> dict:
    """Report every way this library already contains its own answers.

    `components`  [{name, expr}] with expr as nested JSON lists.
    `task_truth_tables`  {task_id: "01010101"} -- the tasks it will be used on.
    `known_solutions`  {task_id: expr-as-JSON}, optional; enables the weaker
                       subterm warning.
    """
    _b = _proteus()
    from . import cegis_boolean as _cb                       # noqa: PLC0415

    findings, worst = [], CLEAN
    sub_index = {}
    for task, sol in (known_solutions or {}).items():
        for st in _subterms(_cb._from_json(sol, None)):      # noqa: SLF001
            if st[0] not in ("const", "input"):
                sub_index.setdefault(_tt(st, _b), []).append(task)

    comps = []
    for c in components:
        comps.append((c["name"], _cb._from_json(c["expr"], None)))  # noqa: SLF001

    for c, (_name, expr) in zip(components, comps):
        _b.check(expr)
        tt = _tt(expr, _b)
        solves = sorted(t for t, v in task_truth_tables.items() if v == tt)
        if solves:
            worst = SOLVES_A_TASK
            findings.append({
                "component": c["name"], "class": SOLVES_A_TASK,
                "truth_table": tt, "tasks": solves,
                "why": "this component IS the answer. A search handed it finds "
                       "those tasks as a size-1 leaf, and the run measures the "
                       "leak rather than the library."})
            continue
        near = sorted(set(sub_index.get(tt, ())))
        if near:
            if worst == CLEAN:
                worst = SUBTERM_OF_SOLUTION
            findings.append({
                "component": c["name"], "class": SUBTERM_OF_SOLUTION,
                "truth_table": tt, "tasks": near,
                "why": "a subterm of a known solution to those tasks. NOT a "
                       "verdict: making a target easier is the effect under "
                       "test, and the threshold is nobody's to set here."})

    # ONE STEP FROM THE LIBRARY. A target reachable by a single operator over
    # library components is not "easier" -- it is the answer in two pieces, and
    # SOLVES_A_TASK cannot see it because no single component computes it.
    #
    # DEPTH 1 AND NO FURTHER, and the cutoff is principled rather than
    # convenient: at depth 1 the library has supplied everything but one
    # operator, which is the answer key split. At depth k for growing k the
    # question becomes "how much easier", which IS the effect under test, and
    # there is no non-arbitrary line past the first step.
    #
    # AT LEAST ONE OPERAND MUST BE A LIBRARY COMPONENT. Without that rule this
    # flags any task solvable in one operator over raw inputs -- `and01` is
    # `and(x0, x1)` whatever library is present -- and the check would report
    # contamination as a fact about the task set rather than about the library.
    # Tasks already reported as solved outright add nothing when they also
    # compose: the finding is the same leak twice, and a report where the new
    # information is buried under restatements is one nobody reads to the end.
    already = {t for f in findings if f["class"] == SOLVES_A_TASK
               for t in f["tasks"]}
    leaves = list(comps) + [("input%d" % i, _b.I(i)) for i in range(_b.N_INPUTS)]
    leaves += [("const0", _b.C(0)), ("const1", _b.C(1))]
    lib_names = {n for n, _ in comps}
    seen_pairs = set()
    for op in ("and", "or", "xor"):
        for na, a in leaves:
            for nb, b in leaves:
                if na not in lib_names and nb not in lib_names:
                    continue
                key = (op, tuple(sorted((na, nb))))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                t = _tt((op, a, b), _b)
                tasks = sorted(k for k, v in task_truth_tables.items()
                               if v == t and k not in already)
                if not tasks:
                    continue
                worst = SOLVES_A_TASK if worst == SOLVES_A_TASK \
                    else COMPOSES_TO_A_TASK
                findings.append({
                    "component": "%s(%s, %s)" % (op, na, nb),
                    "class": COMPOSES_TO_A_TASK, "truth_table": t,
                    "tasks": tasks,
                    "why": "one operator over library components reaches those "
                           "tasks. Not 'easier' -- the answer in two pieces."})
    for nc, c_expr in comps:
        t = _tt(("not", c_expr), _b)
        tasks = sorted(k for k, v in task_truth_tables.items()
                       if v == t and k not in already)
        if tasks:
            worst = SOLVES_A_TASK if worst == SOLVES_A_TASK \
                else COMPOSES_TO_A_TASK
            findings.append({
                "component": "not(%s)" % nc, "class": COMPOSES_TO_A_TASK,
                "truth_table": t, "tasks": tasks,
                "why": "one operator over a library component reaches those "
                       "tasks."})

    return {
        "verdict": worst,
        "usable_as_a_library_effect": worst not in DISQUALIFYING,
        "n_components": len(components),
        "n_tasks": len(task_truth_tables),
        "findings": findings,
        "note": "arity is irrelevant: a zero-arity component is a legitimate "
                "leaf and an arity-2 abstraction from the test set is equally "
                "contaminated. The defect is the corpus.",
    }
