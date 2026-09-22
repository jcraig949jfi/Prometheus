"""H1 beta sizing: the enumerated Boolean universe table and the n-input compiler extension.

What is asserted, in the order the base role asks for it:
  - the ALPHA IS UNTOUCHED: 3-input compile output is byte-identical to a golden hash taken
    before the compiler learned about `n_inputs`;
  - the minimal-size DP agrees with brute-force EXPRESSION enumeration (an independent route);
  - POSITIVE controls (known minima land where they must), a NEGATIVE control (4-input parity is
    absent below its minimum), and a CHEAT control (an injected component is seen as a size-1 solution
    and lifts every cumulative count, so the measurement channel can see a solution appear);
  - the witness-pool arithmetic on the real `case_order`, at both ends (K = 0 and K = 2^n);
  - verification cost measured == predicted, and 4-input compile/evaluate parity exhaustive over
    all 16 assignments for every expression of node count <= 4;
  - the committed table reproduces from source.
"""
from __future__ import annotations

import json
import os

import pytest

from proteus.eval import boolean as B
from proteus.eval import boolean_universe as U
from proteus.foundry.identity import canonical_json, sha256_hex
from proteus.tests.test_h1_boolean import EXPRESSIONS

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(os.path.dirname(HERE), "eval", "BOOLEAN_UNIVERSE_TABLE.json")

#: sha256 of the canonical JSON of {name: compile_boolean(expr)} over EXPRESSIONS, computed at
#: ccb26df01 BEFORE proteus/eval/boolean.py learned `n_inputs`. If this moves, the alpha moved.
GOLDEN_ALPHA = "f150767a2cdf939f494bcb340ba40b596f195521c1c7d5f1ac8fe28f157e9a71"


def _enumerate_expressions(n, max_size):
    """The kind's enumeration, re-derived here as the INDEPENDENT route (expressions, not
    minimal sets): every well-formed expression of each node count."""
    leaves = [B.I(i, n) for i in range(n)] + [B.C(0), B.C(1)]
    by = {1: leaves}
    for s in range(2, max_size + 1):
        here = [("not", a) for a in by[s - 1]]
        for i in range(1, s - 1):
            for op in ("and", "or", "xor"):
                for x in by[i]:
                    for y in by[s - 1 - i]:
                        here.append((op, x, y))
        by[s] = here
    return by


# ============================================================== the alpha is untouched

def test_alpha_compile_output_is_byte_identical_to_the_golden_hash():
    blob = canonical_json({k: B.compile_boolean(v) for k, v in sorted(EXPRESSIONS.items())})
    assert sha256_hex(blob) == GOLDEN_ALPHA


def test_explicit_n_inputs_3_equals_the_default():
    for e in EXPRESSIONS.values():
        assert B.compile_boolean(e, 3) == B.compile_boolean(e)
        assert B.truth_table(e, 3) == B.truth_table(e)


def test_alpha_still_rejects_a_fourth_input_by_default():
    with pytest.raises(B.BooleanError):
        B.I(3)
    with pytest.raises(B.BooleanError):
        B.check(("input", 3))
    with pytest.raises(B.BooleanError):
        B.compile_boolean(("input", 3))


# ============================================================== DP vs brute force

@pytest.mark.parametrize("n,max_size", [(3, 7), (4, 6)])
def test_minimal_size_dp_agrees_with_brute_force_expression_enumeration(n, max_size):
    by = _enumerate_expressions(n, max_size)
    seen = set()
    M, _ = U.minimal_size_sets(n, max_size)
    cum = 0
    for s in range(1, max_size + 1):
        for e in by[s]:
            seen.add(U.table_int(e, n))
        cum += len(M[s])
        assert len(seen) == cum, (n, s, len(seen), cum)
    # and the minimal sets are what they say: disjoint, and each table's first size is its size
    all_tables = [t for s in M for t in M[s]]
    assert len(all_tables) == len(set(all_tables))


def test_expression_counts_match_the_enumerator():
    by = _enumerate_expressions(4, 6)
    rows = U.expression_counts(4, 6)
    assert [r["expressions"] for r in rows] == [len(by[s]) for s in range(1, 7)]


# ============================================================== controls

def test_positive_controls_known_minima():
    I, Not, Xor = B.I, B.Not, B.Xor
    M, _ = U.minimal_size_sets(4, 8)
    where = {t: s for s in M for t in M[s]}
    assert where[U.table_int(I(0, 4), 4)] == 1
    assert where[U.table_int(Not(I(0, 4)), 4)] == 2
    assert where[U.table_int(Xor(I(0, 4), I(1, 4)), 4)] == 3
    xor4 = Xor(Xor(Xor(I(0, 4), I(1, 4)), I(2, 4)), I(3, 4))
    assert where[U.table_int(xor4, 4)] == 7


def test_negative_control_four_input_parity_is_absent_below_size_7():
    I, Xor = B.I, B.Xor
    xor4 = U.table_int(Xor(Xor(Xor(I(0, 4), I(1, 4)), I(2, 4)), I(3, 4)), 4)
    _, seen6 = U.minimal_size_sets(4, 6)
    assert xor4 not in seen6
    _, seen7 = U.minimal_size_sets(4, 7)
    assert xor4 in seen7


def test_cheat_control_injected_component_is_seen_as_a_size_1_solution():
    I, Xor = B.I, B.Xor
    xor4 = U.table_int(Xor(Xor(Xor(I(0, 4), I(1, 4)), I(2, 4)), I(3, 4)), 4)
    base = U.solvable_fraction_table(4, 7)
    cheat = U.solvable_fraction_table(4, 7, components=(xor4,))
    assert cheat["components_injected"] == 1
    # the injected table moves from minimal size 7 to minimal size 1 -- the channel sees it
    M_base, _ = U.minimal_size_sets(4, 7)
    M_cheat, _ = U.minimal_size_sets(4, 7, components=(xor4,))
    assert xor4 in M_base[7] and xor4 not in M_base[1]
    assert xor4 in M_cheat[1] and xor4 not in M_cheat[7]
    assert cheat["rows"][0]["first_reached"] == base["rows"][0]["first_reached"] + 1
    # a new leaf composes further, so the cumulative count at EVERY size rises (recorded, not
    # asserted as "exactly one": at size 7 the injected leaf brings 1071 first-reached tables
    # against 415 without it -- a component is a multiplier, not a single extra solution)
    for b, c in zip(base["rows"], cheat["rows"]):
        assert c["cumulative"] > b["cumulative"]
    # a table already a leaf changes nothing: the channel does not invent signal
    x0 = U.table_int(I(0, 4), 4)
    same = U.solvable_fraction_table(4, 7, components=(x0,))
    assert [r["cumulative"] for r in same["rows"]] == [r["cumulative"] for r in base["rows"]]


# ============================================================== witness pool

@pytest.mark.parametrize("n", [3, 4])
def test_witness_pool_constant_seed_is_the_complement_of_the_prefix(n):
    m = 2 ** n
    for K in range(0, m + 1):
        p = U.witness_pool_constant(n, K)
        assert p["union_distinct_inputs"] == m - K
        assert p["pool_per_task"] == [m - K]
    assert U.witness_pool_constant(n, 0)["union_distinct_inputs"] == m       # K = 0: everything
    assert U.witness_pool_constant(n, m)["union_distinct_inputs"] == 0       # K = 2^n: nothing


def test_witness_pool_per_task_seeds_reach_every_input_while_each_task_still_sees_2n_minus_K():
    for n, K in ((3, 4), (4, 4), (4, 8)):
        m = 2 ** n
        p = U.witness_pool(n, K, list(range(24)))
        assert p["union_distinct_inputs"] == m
        assert p["pool_per_task"] == [m - K]
        assert sum(p["reach_count_per_input"]) == 24 * (m - K)
    # n = 3, K = 8 is the alpha's collapse: nothing can be a witness, per task or not
    p = U.witness_pool(3, 8, list(range(24)))
    assert p["union_distinct_inputs"] == 0


def test_coverage_curve_is_monotone_and_reports_the_first_full_task_count():
    c = U.coverage_curve(4, 8, list(range(64)))
    assert c["curve"] == sorted(c["curve"])
    assert c["curve"][-1] == 16
    assert c["tasks_to_full_coverage"] is not None
    assert c["curve"][c["tasks_to_full_coverage"] - 1] == 16
    assert c["curve"][c["tasks_to_full_coverage"] - 2] < 16


def test_witness_pool_rejects_K_out_of_range():
    with pytest.raises(ValueError):
        U.witness_pool(4, 17, [0])


# ============================================================== verification cost + 4-input parity

@pytest.mark.parametrize("n", [3, 4])
def test_verification_cost_measured_equals_predicted(n):
    I, Not, Xor = B.I, B.Not, B.Xor
    xs = [I(i, n) for i in range(n)]
    for e in (xs[0], Not(xs[0]), Xor(xs[0], xs[1]), Xor(Xor(xs[0], xs[1]), xs[n - 1])):
        r = U.verification_cost(e, n)
        assert r["ops_per_case_measured"] == [r["ops_per_case_predicted"]]
        assert r["ops_total_measured"] == r["ops_total_predicted"]
        assert r["cases"] == 2 ** n
        assert r["all_passed"]


def test_four_input_compile_evaluate_parity_exhaustive_over_all_16_assignments_to_size_4():
    from proteus.eval.library import evaluate
    by = _enumerate_expressions(4, 4)
    n_checked = 0
    for s in by:
        for e in by[s]:
            man = B.compile_boolean(e, 4)
            for w in man["genome"][::4]:
                assert w in B.DECLARED_OPCODES
            res = evaluate(man, B.boolean_spec(e, 4))
            assert res["cases_total"] == 16
            assert res["all_passed"], e
            n_checked += 1
    assert n_checked == 456


def test_four_inputs_use_one_more_temporary_and_too_many_inputs_fail_closed():
    I, Xor = B.I, B.Xor
    man = B.compile_boolean(Xor(I(0, 4), I(3, 4)), 4)
    # prologue: LDC r14, then IN r0..r3; the first temporary is r4
    assert man["genome"][:4] == [B.OP_LDC, B.R_ONE, 1, 0]
    assert man["genome"][4 + 3 * 4:4 + 4 * 4] == [B.OP_IN, 3, B.R_CHANNEL, 0]
    assert man["genome"][-8:-4] == [B.OP_OUT, 4, B.R_CHANNEL, 0]
    with pytest.raises(B.BooleanError):
        B.compile_boolean(I(0, 14), 14)


# ============================================================== the committed table

def test_committed_table_reproduces_from_source():
    with open(TABLE, encoding="utf-8") as f:
        doc = json.load(f)
    for n in (3, 4):
        d = doc["per_n"][str(n)]
        sat = U.solvable_fraction_table(n, d["solvable_by_size"]["max_size"])
        assert sat["rows"] == d["solvable_by_size"]["rows"]
        assert sat["saturated_at"] == d["solvable_by_size"]["saturated_at"]
        for a in d["asked"]:
            assert a["solvable"] == sat["rows"][a["max_expr_size"] - 1]["cumulative"]
    # the headline numbers, stated so a reader of this file sees them without opening the JSON
    n4 = doc["per_n"]["4"]["solvable_by_size"]["rows"]
    assert [r["cumulative"] for r in n4[:7]] == [6, 10, 28, 70, 154, 478, 893]
    assert doc["per_n"]["4"]["solvable_by_size"]["saturated_at"] == 17
    assert doc["per_n"]["3"]["solvable_by_size"]["saturated_at"] == 10
