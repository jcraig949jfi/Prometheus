"""Case ordering: the BETA alternative, and the fixture that explains the alpha's witness pool.

THE MECHANISM, stated once. `cegis_boolean_v1` seeds its first K constraints from the first K
cases OF THE DECLARED ORDER, then reports the first MISMATCH in that same order. The two use one
order, so the seeded prefix is exactly the region that can no longer yield a witness and every
witness must fall in the complement. At 3 bits with K=4 the complement is cases 4..7 -- the four
assignments with input 0 = 1 -- which is what phase 1 observed, for every task, regardless of the
target or the candidate seed.

The tests below demonstrate that, and demonstrate the consequence the beta has to design around:
a DIFFERENT FIXED order does not widen the pool, it relocates it.
"""
from __future__ import annotations

import pytest

from proteus.eval import boolean as B
from proteus.eval.library import evaluate

I, C, Not, And, Or, Xor = B.I, B.C, B.Not, B.And, B.Or, B.Xor

K_PACK = 4      # the alpha's seed_probe_count
EXPRS = {"xor3": Xor(Xor(I(0), I(1)), I(2)),
         "majority": Or(And(I(0), I(1)), Or(And(I(0), I(2)), And(I(1), I(2)))),
         "and01": And(I(0), I(1)), "i2": I(2), "nand01": Not(And(I(0), I(1)))}


def _reachable_witness_cases(order, k=K_PACK):
    """The mechanism in three lines: seed the first k of `order`, the rest can still mismatch."""
    return set(order[k:])


# =============================================================== ordering is well formed

@pytest.mark.parametrize("ordering", B.CASE_ORDERINGS)
def test_case_order_is_a_permutation(ordering):
    for seed in (0, 1, 940001, 2 ** 31):
        o = B.case_order(ordering, seed)
        assert sorted(o) == list(range(8)), "an ordering must be a bijection on the 8 cases"


def test_declared_ordering_is_the_identity_and_unchanged():
    assert B.case_order(B.ORDERING_DECLARED) == list(range(8))
    assert B.case_order(B.ORDERING_DECLARED, seed=12345) == list(range(8)), \
        "the declared ordering must ignore the seed; the alpha depends on it"


def test_seeded_ordering_is_deterministic_and_seed_sensitive():
    a = B.case_order(B.ORDERING_SEEDED, seed=940001)
    assert a == B.case_order(B.ORDERING_SEEDED, seed=940001)
    others = {tuple(B.case_order(B.ORDERING_SEEDED, seed=s)) for s in range(24)}
    assert len(others) > 1, "the permutation never moved across 24 seeds"


def test_unknown_ordering_fails_closed():
    with pytest.raises(B.BooleanError, match="unknown case ordering"):
        B.case_order("gray_code_v9")


def test_ordering_uses_splitmix_not_random():
    import ast
    import os
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "eval", "boolean.py")
    with open(src, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            name = (node.module or "") if isinstance(node, ast.ImportFrom) else node.names[0].name
            assert name.split(".")[0] != "random", "boolean.py imported `random`"


# =============================================================== parity under any ordering

@pytest.mark.parametrize("name", sorted(EXPRS))
@pytest.mark.parametrize("ordering,seed", [(B.ORDERING_DECLARED, 0),
                                           (B.ORDERING_SEEDED, 940001),
                                           (B.ORDERING_SEEDED, 7)])
def test_compile_evaluate_parity_holds_under_every_ordering(name, ordering, seed):
    """A permutation reorders cases; it must not change coverage or any verdict."""
    expr = EXPRS[name]
    man = B.compile_boolean(expr)
    spec = B.boolean_spec(expr, ordering=ordering, ordering_seed=seed)
    res = evaluate(man, spec)
    assert res["cases_total"] == 8 and res["cases_with_expectation"] == 8
    assert res["all_passed"], "a correct program failed under a reordering"
    assert res["witness"] is None


def test_coverage_is_identical_under_reordering():
    expr = EXPRS["xor3"]
    a = B.boolean_spec(expr)
    b = B.boolean_spec(expr, ordering=B.ORDERING_SEEDED, ordering_seed=940001)
    key = lambda s: sorted((tuple(c["inputs"][0]), tuple(c["expected"][0])) for c in s["cases"])
    assert key(a) == key(b), "reordering changed WHICH cases exist, not just their order"
    assert [c["inputs"] for c in a["cases"]] != [c["inputs"] for c in b["cases"]]


# =============================================================== first-witness ordering

def test_first_witness_is_the_first_mismatch_in_the_given_order():
    """The witness must follow the ordering, not the underlying assignment index."""
    target, wrong = EXPRS["xor3"], EXPRS["and01"]
    man = B.compile_boolean(wrong)
    tt_t, tt_w = B.truth_table(target), B.truth_table(wrong)
    mismatched = [k for k in range(8) if tt_t[k] != tt_w[k]]
    assert mismatched, "fixture is vacuous: the two functions agree everywhere"

    for ordering, seed in [(B.ORDERING_DECLARED, 0), (B.ORDERING_SEEDED, 940001),
                           (B.ORDERING_SEEDED, 3), (B.ORDERING_SEEDED, 11)]:
        order = B.case_order(ordering, seed)
        spec = B.boolean_spec(target, ordering=ordering, ordering_seed=seed)
        w = evaluate(man, spec)["witness"]
        assert w is not None
        expected_case = next(k for k in order if k in set(mismatched))
        assert w["inputs"][0] == B.assignments()[expected_case], (
            f"{ordering}/{seed}: witness was not the first mismatch in the declared order")


def test_reordering_can_move_the_witness_to_a_different_input():
    """If it could not, an alternative ordering would be pointless."""
    target, wrong = EXPRS["xor3"], EXPRS["and01"]
    man = B.compile_boolean(wrong)
    seen = set()
    for seed in range(40):
        spec = B.boolean_spec(target, ordering=B.ORDERING_SEEDED, ordering_seed=seed)
        w = evaluate(man, spec)["witness"]
        seen.add(tuple(w["inputs"][0]))
    assert len(seen) > 1, "no seed moved the witness; the ordering is inert"


# =============================================================== the alpha's collapse

def test_declared_ordering_with_k4_confines_witnesses_to_input0_equals_1():
    """THE PHASE-1 FIXTURE. Seeding the first 4 declared cases leaves exactly {100,101,110,111}."""
    order = B.case_order(B.ORDERING_DECLARED)
    reachable = _reachable_witness_cases(order, K_PACK)
    assert reachable == {4, 5, 6, 7}
    inputs = {tuple(B.assignments()[k]) for k in reachable}
    assert inputs == {(1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)}
    assert all(a[0] == 1 for a in inputs), "every reachable witness has input 0 = 1"


def test_a_fixed_alternative_ordering_relocates_the_pool_but_does_not_widen_it():
    """The result the beta must design around: |reachable| is 2^n - K under ANY fixed order."""
    for seed in (940001, 7, 99):
        order = B.case_order(B.ORDERING_SEEDED, seed)
        assert len(_reachable_witness_cases(order, K_PACK)) == 8 - K_PACK
    a = _reachable_witness_cases(B.case_order(B.ORDERING_SEEDED, 940001), K_PACK)
    b = _reachable_witness_cases(B.case_order(B.ORDERING_DECLARED), K_PACK)
    assert a != b, "the alternative ordering did not even relocate the pool"


def test_only_a_task_varying_seed_widens_the_union_across_tasks():
    """Vary the seed PER TASK and the union over 24 tasks covers more than four inputs."""
    fixed = set()
    varying = set()
    for task in range(24):
        fixed |= _reachable_witness_cases(B.case_order(B.ORDERING_SEEDED, 940001), K_PACK)
        varying |= _reachable_witness_cases(
            B.case_order(B.ORDERING_SEEDED, 940001 ^ (task * 0x9E3779B1)), K_PACK)
    assert len(fixed) == 4, "one sealed constant reproduces the alpha's four-input pool"
    assert len(varying) == 8, "a per-task seed should reach every assignment across the campaign"
