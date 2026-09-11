"""TECHNE-12: the program-space shrink target -- size order and validity predicates.

Techne qualified Hypothesis as a witness-minimiser over ASSIGNMENTS and recorded the honest
limit: at 3 inputs there are only 8 assignments, so enumeration is cheaper and exact, and the
result establishes SOUND rather than USEFUL. This module supplies the PROGRAM-space target, the
post-conditions in Proteus's own code, and the size order Proteus wants minimised.

STDLIB ONLY. Hypothesis is NOT imported here. The predicates and the order are the contract and
must work with no third-party package installed; the strategy lives in `hypothesis_strategy.py`
and imports Hypothesis lazily. Proteus's stdlib-only property is not spent on a test tool.

--------------------------------------------------------------------------------------------
THE DECLARED SIZE ORDER -- OURS, AND IT IS NOT HYPOTHESIS'S
--------------------------------------------------------------------------------------------
    size_key(expr) = (node_count, depth, canonical_string)

primary   NODE COUNT, because that is the cost the experiment actually charges: the kind's
          `enumerate_candidates` is size-ordered, and a component library's entire claimed
          effect is to make a useful expression SMALLER -- a frozen subtree costing 1 instead of
          the 3 or 5 nodes it stands for.
then      DEPTH, which breaks ties toward flatter programs. Two size-5 expressions are not
          equally simple if one is a chain and the other a balanced tree.
then      the CANONICAL STRING, purely so the order is total and replayable. It carries no
          claim about simplicity; it exists to make "the minimum" a single well-defined object.

Hypothesis shrinks toward ITS OWN notion of simplicity -- smaller integers, shorter sequences,
earlier strategy branches. THAT IS NOT THIS ORDER, and Techne should MEASURE the agreement
rather than assume it. `minimal_by_enumeration` returns the exact minimum under this order so a
shrink result can be scored against ground truth instead of against a hope.

--------------------------------------------------------------------------------------------
TWO PREDICATES, AND WHY THE ASKED-FOR ONE IS TRIVIAL HERE
--------------------------------------------------------------------------------------------
`still_a_counterexample` is the post-condition the brief asked for, and it is correct. It is also
TRIVIAL ON THIS DOMAIN, and that is a measured fact, not an opinion: the five leaves have five
distinct truth tables, so for every one of the 256 possible 3-input targets at least FOUR leaves
disagree with it. The minimal counterexample program therefore has node count 1 for EVERY target,
with no search. That is the same honest limit Techne already found for assignments, in a
different guise -- enumeration is again cheaper and exact.

`still_solves` is where a minimiser can earn its place. Minimising a program that SOLVES the task
is a real search with a non-trivial floor, and it is exactly the quantity H0's component library
is built to reduce. Both are shipped; the second is the one worth scoring.
"""
from __future__ import annotations

from proteus.eval import boolean as B
from proteus.eval.library import evaluate

SHRINK_CONTRACT = "proteus.program_shrink.v1"
INTERFACE_VERSION = B.INTERFACE_VERSION


# --------------------------------------------------------------------------- size order

def program_size(expr):
    """Node count. Leaves cost 1; this matches the kind's `size` exactly."""
    B.check(expr)
    return _size(expr)


def _size(e):
    if e[0] in (B.CONST, B.INPUT):
        return 1
    return 1 + sum(_size(a) for a in e[1:])


def program_depth(expr):
    B.check(expr)
    return _depth(expr)


def _depth(e):
    if e[0] in (B.CONST, B.INPUT):
        return 1
    return 1 + max(_depth(a) for a in e[1:])


def canonical(expr):
    """A total, replayable serialization. NOT a simplicity claim -- only a tie-break."""
    if expr[0] == B.CONST:
        return f"c{expr[1]}"
    if expr[0] == B.INPUT:
        return f"x{expr[1]}"
    return f"({expr[0]} " + " ".join(canonical(a) for a in expr[1:]) + ")"


def size_key(expr):
    """THE DECLARED ORDER. Smaller tuple is simpler."""
    return (program_size(expr), program_depth(expr), canonical(expr))


# --------------------------------------------------------------------------- predicates

def compiles(expr):
    """A program that cannot be compiled is INVALID, not a counterexample and not a solution."""
    try:
        B.compile_boolean(expr)
        return True
    except B.BooleanError:
        return False


def still_a_counterexample(candidate, target, seed=0):
    """POST-CONDITION AS ASKED. A shrunk program must still disagree with the target.

    Decided by PROTEUS'S EVALUATOR, not by the independent truth table, because the brief asks
    for the post-condition under the evaluator. Parity between the two is separately asserted.

    B1's budget contract carries through: budget exhaustion is a STATUS and not a witness, so a
    starved program is NOT a counterexample. A shrink that starves a program has not preserved
    the property, and this predicate will say so.
    """
    if not compiles(candidate):
        return False
    res = evaluate(B.compile_boolean(candidate), B.boolean_spec(target), seed=seed)
    return bool(res["has_witness"])


def still_solves(candidate, target, seed=0):
    """THE NON-TRIVIAL TARGET. A shrunk program must still pass every declared case.

    Full coverage is required, exactly as C3 demands: no-witness alone is never solved.
    """
    if not compiles(candidate):
        return False
    res = evaluate(B.compile_boolean(candidate), B.boolean_spec(target), seed=seed)
    return bool(res["all_passed"]
                and res["cases_with_expectation"] == 2 ** B.N_INPUTS)


PREDICATES = {"still_a_counterexample": still_a_counterexample, "still_solves": still_solves}


# --------------------------------------------------------------------------- ground truth

def enumerate_programs(max_size, n_inputs=B.N_INPUTS):
    """Every well-typed expression up to `max_size` nodes, size-ordered. Exact, not sampled."""
    leaves = [B.C(0), B.C(1)] + [B.I(i) for i in range(n_inputs)]
    by_size = {1: list(leaves)}
    for size in range(2, max_size + 1):
        here = []
        for a in by_size[size - 1]:
            here.append(B.Not(a))
        for i in range(1, size - 1):
            for x in by_size.get(i, ()):
                for y in by_size.get(size - 1 - i, ()):
                    here.append(B.And(x, y))
                    here.append(B.Or(x, y))
                    here.append(B.Xor(x, y))
        by_size[size] = here
    out = []
    for size in range(1, max_size + 1):
        out.extend(by_size.get(size, ()))
    return out


def minimal_by_enumeration(target, predicate="still_solves", max_size=5, seed=0):
    """The EXACT minimum under the declared order, by exhaustive enumeration.

    This is the ground truth a shrink result is scored against. It is affordable precisely
    because the domain is small -- which is also why a minimiser has to beat it to matter.
    """
    pred = PREDICATES[predicate] if isinstance(predicate, str) else predicate
    best = None
    for expr in enumerate_programs(max_size):
        if not pred(expr, target, seed=seed):
            continue
        k = size_key(expr)
        if best is None or k < best[0]:
            best = (k, expr)
    return None if best is None else {"expr": best[1], "size_key": best[0],
                                      "size": best[0][0], "depth": best[0][1],
                                      "canonical": best[0][2]}
