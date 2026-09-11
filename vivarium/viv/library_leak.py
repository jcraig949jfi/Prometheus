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
the hypothesis. `subterm_of_solution` is reported for exactly that reason: it
is a WARNING with a threshold nobody has agreed, not a verdict.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent.parent

SOLVES_A_TASK = "SOLVES_A_TASK"
SUBTERM_OF_SOLUTION = "SUBTERM_OF_SOLUTION"
CLEAN = "CLEAN"


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

    for c in components:
        expr = _cb._from_json(c["expr"], None)               # noqa: SLF001
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

    return {
        "verdict": worst,
        "usable_as_a_library_effect": worst == CLEAN,
        "n_components": len(components),
        "n_tasks": len(task_truth_tables),
        "findings": findings,
        "note": "arity is irrelevant: a zero-arity component is a legitimate "
                "leaf and an arity-2 abstraction from the test set is equally "
                "contaminated. The defect is the corpus.",
    }
