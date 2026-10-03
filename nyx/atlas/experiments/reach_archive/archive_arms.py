"""Archive arms for the reach harness: separate RETENTION, RARELY-VISITED SELECTION and NEW-CELL ACCEPTANCE.

Design: nyx/atlas/experiments/reach_archive/DESIGN_G1_ARCHIVE_ARMS.md (operator directive 2026-10-03 item 6; the
attack roles/Nyx/ATTACK_reachability_go_explore_2026-10-03.md B1). A DESIGN AND REFERENCE IMPLEMENTATION ONLY:
nothing here has been run against the reach world as science. The unit tests run it on toy landscapes.

The three archive arms form a LADDER, each one factor away from its neighbour, so that every contrast isolates
exactly one ingredient of the bundled "Go-Explore-like" arm (S4 in Atlas G1):

    chain  (existing reach.py 'neutral')  no archive; accept child iff f(child) >= f(parent)
    X1  ARCHIVE + GREEDY + PARENT-GE      archive kept; parent = the elite of the best-scoring cell;
                                          child admitted iff f(child) >= f(parent)        -> X1 vs chain = RETENTION
    X2  ARCHIVE + COUNT  + PARENT-GE      as X1, parent drawn by count weight 1/sqrt(1 + times chosen)
                                                                                          -> X2 vs X1 = SELECTION
    X3  ARCHIVE + COUNT  + NEW-CELL       as X2, child also admitted when it lands in an EMPTY cell, whatever
                                          its score (the Go-Explore / MAP-Elites acceptance) -> X3 vs X2 = ACCEPTANCE

In every archive arm an admitted child replaces its cell's elite iff f(child) >= f(elite) (or the cell is empty).

The program is the state; "returning" to an archived program is copying it (attack B2), so no arm here tests
Go-Explore's own mechanism (avoiding re-traversal of an MDP trajectory). The arms test the three bundled effects
that an archive search adds to a mutation chain.

Interfaces (kept free of the reach world so this file can be reviewed and tested without numba):
    propose(parent, i)  -> child        the harness's single-point mutation, deterministic in (lineage, i)
    evaluate(prog)      -> (fitness, cell_key)   cell_key = a hashable behaviour descriptor
"""
from __future__ import annotations

import math
from typing import Callable, Dict, Hashable, List, Tuple

ARMS = ("X1_archive_greedy_ge", "X2_archive_count_ge", "X3_archive_count_newcell")


class Archive:
    def __init__(self):
        self.elite: Dict[Hashable, object] = {}
        self.fit: Dict[Hashable, int] = {}
        self.chosen: Dict[Hashable, int] = {}

    def offer(self, cell, prog, f) -> bool:
        if cell not in self.elite or f >= self.fit[cell]:
            new = cell not in self.elite
            self.elite[cell], self.fit[cell] = prog, f
            if new:
                self.chosen[cell] = 0
            return True
        return False


def run_lineage(arm: str, start, evaluate: Callable, propose: Callable, budget: int, target_fit: int, rng_u: Callable[[int], float]) -> Tuple[int, dict]:
    """One lineage. rng_u(i) is a deterministic uniform in [0, 1) for step i (the harness's counter hash).
    Returns (evaluations until a program with fitness >= target_fit was evaluated, or -1; diagnostics)."""
    assert arm in ARMS
    A = Archive()
    f0, c0 = evaluate(start)
    A.offer(c0, start, f0)
    if f0 >= target_fit:
        return 0, {"cells": 1}
    selections_per_cell_new = 0
    for i in range(budget):
        cells: List[Hashable] = list(A.elite)
        if arm == "X1_archive_greedy_ge":
            best = max(A.fit[c] for c in cells)
            top = sorted([c for c in cells if A.fit[c] == best], key=repr)
            cell = top[int(rng_u(i) * len(top))]
        else:
            w = [1.0 / math.sqrt(1 + A.chosen[c]) for c in cells]
            r, acc, cell = rng_u(i) * sum(w), 0.0, cells[-1]
            for c, wc in zip(cells, w):
                acc += wc
                if r < acc:
                    cell = c
                    break
        A.chosen[cell] += 1
        parent, fp = A.elite[cell], A.fit[cell]
        child = propose(parent, i)
        fc, cc = evaluate(child)
        if fc >= target_fit:
            return i + 1, {"cells": len(A.elite)}
        admit = fc >= fp or (arm == "X3_archive_count_newcell" and cc not in A.elite)
        if admit:
            selections_per_cell_new += int(cc not in A.elite)
            A.offer(cc, child, fc)
    return -1, {"cells": len(A.elite), "new_cells_admitted": selections_per_cell_new}


def run_chain(start, evaluate, propose, budget, target_fit) -> int:
    """The existing reach.py 'neutral' regime, restated with the same interfaces (reference only)."""
    parent = start
    fp, _ = evaluate(parent)
    if fp >= target_fit:
        return 0
    for i in range(budget):
        child = propose(parent, i)
        fc, _ = evaluate(child)
        if fc >= target_fit:
            return i + 1
        if fc >= fp:
            parent, fp = child, fc
    return -1
