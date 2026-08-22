"""ADVERSARIAL RE-CERTIFICATION — the twelve, against domain-sourced anti-cases. (Cycle 038.)

One invariant per instrument, each following from what the instrument ADVERTISES rather than from
which inputs I guessed would be hard. A property search then hunts the domain for a violation.

The measure this cycle is after: **which instruments passed my hand-written anti-case and fail a
generated one?** That gap is how easy my fixtures were.
"""
from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple

from prometheus_math.adversarial_fixtures import InvariantSpec, Violation, search_for_violation

__all__ = ["build_invariants", "hunt_all"]


def _blocks(labels) -> tuple:
    out: dict = {}
    for i, lab in enumerate(labels):
        out.setdefault(lab, []).append(i)
    return tuple(frozenset(v) for v in out.values())


def build_invariants() -> List[InvariantSpec]:
    from hypothesis import strategies as st

    from prometheus_math.battery import member_resolution, reads_its_parameters
    from prometheus_math.calibration import brier_score, murphy_decomposition
    from prometheus_math.partition import (
        PartitionError, chain_direction, conditional_entropy, is_refinement_chain,
        refinement_multiplicity, refines,
    )
    from techne.ladder_circuits.aliasing import find_aliasing_witness
    from techne.ladder_circuits.preprocessing_audit import python_ast_key
    from techne.ladder_circuits.stage_taxonomy import (
        COARSENING, INCOMPARABLE, PRESERVING, REFINEMENT, partition_motion,
    )

    labels = lambda d, lo=2, hi=8: d.draw(
        st.lists(st.integers(0, 3), min_size=d.draw(st.integers(lo, hi)),
                 max_size=hi).filter(lambda x: len(x) >= 2))

    specs: List[InvariantSpec] = []

    # 1. member_resolution: 0 <= H <= log2(n), and H == 0 EXACTLY when the column is constant.
    def _res_ok(col):
        h = member_resolution({"m": col})["m"]
        if not (-1e-12 <= h <= math.log2(len(col)) + 1e-12):
            return False
        return (h <= 1e-12) == (len(set(col)) == 1)

    specs.append(InvariantSpec(
        "battery.member_resolution",
        "0 <= H <= log2(n) and H==0 iff constant",
        _res_ok,
        lambda d: d.draw(st.lists(st.integers(0, 3), min_size=1, max_size=12))))

    # 2. refinement_multiplicity: >= 1, and == 1 EXACTLY when no truth cell holds two proj cells.
    def _mult_ok(pair):
        lab_p, lab_t = pair
        n = len(lab_p)
        p, t = _blocks(lab_p), _blocks(lab_t)
        try:
            m = refinement_multiplicity(p, t, n)
        except PartitionError:
            return not refines(p, t, n)      # refusal is correct EXACTLY when it does not refine
        worst = max(sum(1 for d in p if d <= c) for c in t)
        return refines(p, t, n) and m >= 1 and m == worst

    specs.append(InvariantSpec(
        "partition.refinement_multiplicity",
        "refuses a non-refining projection; else >= 1 and equals max cells-inside-a-cell",
        _mult_ok,
        lambda d: (lambda L: (L, d.draw(st.lists(st.integers(0, 2), min_size=len(L),
                                                 max_size=len(L)))))(labels(d))))

    # 3. deficit: >= 0, and == 0 EXACTLY when the projection refines the truth.
    def _deficit_ok(pair):
        lab_t, lab_p = pair
        n = len(lab_t)
        t, p = _blocks(lab_t), _blocks(lab_p)
        dfc = conditional_entropy(t, p, n)
        return dfc >= -1e-12 and ((dfc <= 1e-9) == refines(p, t, n))

    specs.append(InvariantSpec(
        "partition.deficit",
        "deficit >= 0 and deficit==0 iff projection refines truth",
        _deficit_ok,
        lambda d: (lambda L: (L, d.draw(st.lists(st.integers(0, 2), min_size=len(L),
                                                 max_size=len(L)))))(labels(d))))

    # 4. chain_direction: DESTROYING exactly when the chain refines forward.
    def _dir_ok(triple):
        la, lb, lc = triple
        n = len(la)
        chain = [_blocks(la), _blocks(lb), _blocks(lc)]
        v = chain_direction(chain, n)
        fwd = is_refinement_chain(chain, n)
        rev = is_refinement_chain(list(reversed(chain)), n)
        expected = "DESTROYING" if fwd else ("ACCUMULATING" if rev else "NEITHER")
        return v == expected

    specs.append(InvariantSpec(
        "partition.chain_direction",
        "verdict matches is_refinement_chain forward/reversed",
        _dir_ok,
        lambda d: (lambda L: (L,
                              d.draw(st.lists(st.integers(0, 2), min_size=len(L), max_size=len(L))),
                              d.draw(st.lists(st.integers(0, 2), min_size=len(L), max_size=len(L))))
                   )(labels(d))))

    # 5. partition_motion: agrees with the two refines() calls, exhaustively.
    def _motion_ok(pair):
        la, lb = pair
        n = len(la)
        a, b = _blocks(la), _blocks(lb)
        v = partition_motion(a, b, n)
        ba, ab = refines(b, a, n), refines(a, b, n)
        expected = (PRESERVING if (ba and ab) else
                    COARSENING if ab else
                    REFINEMENT if ba else INCOMPARABLE)
        return v == expected

    specs.append(InvariantSpec(
        "stage_taxonomy.partition_motion",
        "motion agrees with refines() in both directions",
        _motion_ok,
        lambda d: (lambda L: (L, d.draw(st.lists(st.integers(0, 2), min_size=len(L),
                                                 max_size=len(L)))))(labels(d))))

    # 6. brier_score: in [0,1], and 0 EXACTLY when every forecast matches its outcome.
    def _brier_ok(pair):
        ps, ys = pair
        b = brier_score(ps, ys)
        # TOL must travel through the squaring: brier is a MEAN OF SQUARES, so an error of e
        # contributes e^2. Comparing a score threshold against an error threshold of the same
        # magnitude is a units error, and the generator found it (counterexample [1e-09] vs [0]).
        tol = 1e-9
        return (-1e-12 <= b <= 1 + 1e-12) and ((b <= tol * tol) == all(
            abs(p - y) <= tol for p, y in zip(ps, ys)))

    specs.append(InvariantSpec(
        "calibration.brier_score",
        "0 <= brier <= 1 and brier==0 iff every forecast is exact",
        _brier_ok,
        lambda d: (lambda k: (d.draw(st.lists(st.floats(0, 1, allow_nan=False),
                                              min_size=k, max_size=k)),
                              d.draw(st.lists(st.integers(0, 1), min_size=k, max_size=k))))
                   (d.draw(st.integers(1, 10)))))

    # 7. murphy_decomposition: the identity, exactly.
    def _murphy_ok(pair):
        ps, ys = pair
        m = murphy_decomposition(ps, ys)
        return abs(m.identity_residual) < 1e-9 and m.reliability >= -1e-12 and \
            m.resolution >= -1e-12

    specs.append(InvariantSpec(
        "calibration.murphy_decomposition",
        "BS == REL - RES + UNC and components non-negative",
        _murphy_ok,
        lambda d: (lambda k: (d.draw(st.lists(st.floats(0, 1, allow_nan=False),
                                              min_size=k, max_size=k)),
                              d.draw(st.lists(st.integers(0, 1), min_size=k, max_size=k))))
                   (d.draw(st.integers(1, 10)))))

    # 8. find_aliasing_witness: a returned witness must genuinely alias; None must mean none exists.
    def _alias_ok(pair):
        vals, mod = pair
        if len(vals) < 2:
            return True                       # out of domain: handled by the contract, not here
        pi = lambda v: v % mod
        truth = lambda v: v > 2
        w = find_aliasing_witness(vals, pi, truth)
        if w is not None:
            return pi(w.left) == pi(w.right) and truth(w.left) != truth(w.right)
        return not any(pi(a) == pi(b) and truth(a) != truth(b)
                       for i, a in enumerate(vals) for b in vals[i + 1:])

    specs.append(InvariantSpec(
        "aliasing.find_aliasing_witness",
        "returned witness truly aliases; None means no aliased pair exists",
        _alias_ok,
        lambda d: (d.draw(st.lists(st.integers(0, 12), min_size=2, max_size=10)),
                   d.draw(st.integers(2, 5)))))

    # 9. python_ast_key: equal keys iff the parsed trees are equal.
    def _ast_ok(pair):
        import ast
        a, b = pair
        same_key = python_ast_key(a) == python_ast_key(b)
        same_tree = ast.dump(ast.parse(a.strip(), mode="eval")) == \
            ast.dump(ast.parse(b.strip(), mode="eval"))
        return same_key == same_tree

    exprs = st.sampled_from(["x+y", "y+x", "(x)+y", "x  +  y", "2*x", "x*2", "x**2", "x*x",
                             "x-x", "0", "16", "0x10", "a+b", "x*(y+1)", "x*y+x"])
    specs.append(InvariantSpec(
        "preprocessing_audit.python_ast_key",
        "key equality iff parsed-tree equality",
        _ast_ok,
        lambda d: (d.draw(exprs), d.draw(exprs))))

    # 10. reads_its_parameters: never claims independence for a function that DOES read them.
    def _reads_ok(_ignored):
        def uses(n):
            return n > 0

        def ignores(n):
            return True
        return reads_its_parameters(uses) is True and reads_its_parameters(ignores) is False

    specs.append(InvariantSpec(
        "battery.reads_its_parameters",
        "never reports independence for a parameter-reading function",
        _reads_ok,
        lambda d: d.draw(st.integers())))

    return specs


def hunt_all(max_examples: int = 300) -> List[Tuple[str, Optional[Violation]]]:
    return [(s.instrument, search_for_violation(s, max_examples)) for s in build_invariants()]
