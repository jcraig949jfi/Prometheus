"""TECHNE-12: the program-space shrink target -- order, predicates, ground truth, strategy.

Hypothesis-dependent tests are SKIPPED when the package is absent. The order and the predicates
are stdlib-only and always run, because they are the contract; the strategy is a tool.
"""
from __future__ import annotations

import json
import os

import pytest

from proteus.eval import boolean as B
from proteus.eval import shrink as S

I, C, Not, And, Or, Xor = B.I, B.C, B.Not, B.And, B.Or, B.Xor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURE = os.path.join(ROOT, "proteus", "eval", "SHRINK_TARGET_FIXTURE.json")

XOR3 = Xor(Xor(I(0), I(1)), I(2))
AND01 = And(I(0), I(1))


# =============================================================== the declared size order

def test_size_is_node_count_matching_the_kind():
    assert S.program_size(I(0)) == 1
    assert S.program_size(Not(I(0))) == 2
    assert S.program_size(AND01) == 3
    assert S.program_size(XOR3) == 5


def test_depth_breaks_ties_toward_flatter_programs():
    chain = And(And(And(I(0), I(1)), I(1)), I(1))
    balanced = And(And(I(0), I(1)), And(I(1), I(1)))
    assert S.program_size(chain) == S.program_size(balanced) == 7
    assert S.program_depth(chain) > S.program_depth(balanced)
    assert S.size_key(balanced) < S.size_key(chain)


def test_order_is_total_and_deterministic():
    progs = S.enumerate_programs(3)
    keys = [S.size_key(e) for e in progs]
    assert len(set(keys)) == len(keys), "two distinct programs shared a size_key"
    assert keys == [S.size_key(e) for e in progs]


def test_canonical_is_a_tie_break_not_a_simplicity_claim():
    assert S.canonical(AND01) == "(and x0 x1)"
    assert S.canonical(C(0)) == "c0" and S.canonical(I(2)) == "x2"


# =============================================================== predicates

def test_still_a_counterexample_uses_the_evaluator():
    assert S.still_a_counterexample(C(0), XOR3) is True
    assert S.still_a_counterexample(XOR3, XOR3) is False


def test_still_solves_requires_full_coverage():
    assert S.still_solves(XOR3, XOR3) is True
    assert S.still_solves(C(0), XOR3) is False
    assert S.still_solves(Not(Not(AND01)), AND01) is True      # semantically inert wrapper


def test_an_uncompilable_program_is_neither():
    right = I(0)
    for _ in range(20):
        right = And(I(1), right)
    assert not S.compiles(right)
    assert S.still_a_counterexample(right, XOR3) is False
    assert S.still_solves(right, XOR3) is False


def test_budget_exhaustion_is_not_a_counterexample():
    """B1's contract carries through: a starved program has not been shown wrong."""
    from proteus.eval.library import evaluate
    # tick_budget's floor is 8 by the manifest schema, so starve a program that needs more:
    # XOR3 compiles to 11 instructions and cannot finish in 8 ops.
    starved = dict(B.compile_boolean(XOR3), tick_budget=8)
    res = evaluate(starved, B.boolean_spec(XOR3))
    assert res["status_counts"].get("budget", 0) > 0, "the program was not actually starved"
    assert res["has_witness"] is False, "a starved run produced a witness"
    assert res["all_passed"] is False, "no-witness was mistaken for solved"


# =============================================================== the measured triviality

def test_minimal_counterexample_is_size_one_for_every_target():
    """The asked-for predicate is SOUND but trivial here, and this is why.

    The five leaves have five distinct truth tables, so for any 3-input target at least four of
    them disagree. Enumeration is exact and cheap; a minimiser cannot earn its place on this.
    """
    leaf_tt = {S.canonical(e): "".join(map(str, B.truth_table(e)))
               for e in [C(0), C(1), I(0), I(1), I(2)]}
    assert len(set(leaf_tt.values())) == 5
    worst = min(sum(1 for t in leaf_tt.values() if t != format(n, "08b"))
                for n in range(256))
    assert worst == 4, "some target agreed with more than one leaf"


def test_ground_truth_minima_are_exact_and_stable():
    a = S.minimal_by_enumeration(XOR3, "still_solves", max_size=5)
    assert a["size"] == 5 and a["canonical"] == "(xor (xor x0 x1) x2)"
    b = S.minimal_by_enumeration(AND01, "still_solves", max_size=5)
    assert b["size"] == 3 and b["canonical"] == "(and x0 x1)"


# =============================================================== the strategy

def test_strategy_import_does_not_require_hypothesis():
    """Importing the module must cost nothing; only calling it needs the package."""
    from proteus.eval import hypothesis_strategy as H
    assert H.INTERFACE_VERSION == "proteus.boolean3.v0"


def test_strategy_generates_only_valid_compilable_programs():
    st = pytest.importorskip("hypothesis.strategies")           # noqa: F841
    from hypothesis import HealthCheck, given, settings
    from proteus.eval.hypothesis_strategy import programs

    @given(programs(max_leaves=6))
    @settings(max_examples=60, deadline=None,
              suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
    def inner(expr):
        B.check(expr)
        assert S.compiles(expr)
        assert S.program_size(expr) >= 1

    inner()


def test_hypothesis_shrink_is_sound_under_our_predicate():
    """SOUNDNESS is what must always hold: whatever it shrinks to still satisfies the predicate."""
    pytest.importorskip("hypothesis")
    from hypothesis import find, settings
    from proteus.eval.hypothesis_strategy import programs

    got = find(programs(max_leaves=6), lambda e: S.still_solves(e, XOR3),
               settings=settings(max_examples=1500, deadline=None))
    assert S.still_solves(got, XOR3), "the shrunk program stopped satisfying the post-condition"
    gt = S.minimal_by_enumeration(XOR3, "still_solves", max_size=5)
    assert S.program_size(got) >= gt["size"], "shrunk below the exhaustive minimum: impossible"


def test_fixture_matches_the_code():
    with open(FIXTURE, encoding="utf-8") as f:
        doc = json.load(f)
    assert doc["interface_version"] == B.INTERFACE_VERSION
    for row in doc["known_answers"]:
        target = S.minimal_by_enumeration(
            _parse(row["target"]), row["predicate"], max_size=row["enumerated_to_size"])
        assert target["canonical"] == row["ground_truth"]["canonical"]
        assert target["size"] == row["ground_truth"]["size"]


def _parse(c):
    """Tiny reader for the canonical form, so the fixture is self-describing."""
    toks = c.replace("(", " ( ").replace(")", " ) ").split()
    pos = [0]

    def rd():
        t = toks[pos[0]]
        pos[0] += 1
        if t == "(":
            op = toks[pos[0]]
            pos[0] += 1
            args = []
            while toks[pos[0]] != ")":
                args.append(rd())
            pos[0] += 1
            return (op, *args)
        if t.startswith("x"):
            return I(int(t[1:]))
        if t.startswith("c"):
            return C(int(t[1:]))
        raise ValueError(t)

    return rd()
