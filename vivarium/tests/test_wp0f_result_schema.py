"""WP-0f: a kind declares what it RETURNS, and the output is checked against it.

Before this, `Kind` declared parameter names only. An `outcome_rule.field`
naming something no executor produces was discovered at run time as an
`if_indeterminate` branch -- and an indeterminate outcome caused by a typo is
indistinguishable in the record from one caused by the science. Archaeon also
had to keep a local copy of the result fields, a second source of truth that
drifts; their WP-0e note says it defers to this the moment it exists.

Tests 0f-a (diagnostics), 0f-b (library/wrapper parity), 0f-c (bounds and
truncation), plus: `cli kinds` exposes the same contract validation uses.
"""
from __future__ import annotations

import math

import pytest

from conftest import make_spec
from test_repeat import rep
from viv import executors as _ex
from viv import kinds as _kinds
from viv.result_schema import Field as R
from viv.result_schema import (ResultSchemaError, describe,
                               reduction_supported, validate_result)

BITS = _kinds.get("evaluate_bitstring")
WALK = _kinds.get("random_walk_v0")


def good_bits():
    return {"bits": "0" * 24, "score": 0.5, "solved": False, "length": 24,
            "executor": "evaluate_bitstring",
            "reproducibility": "BIT_DETERMINISTIC"}


# --------------------------------------------------------------- 0f-a

def test_0f_a_an_unknown_output_field_is_refused_by_name():
    with pytest.raises(ResultSchemaError) as exc:
        BITS.check_result({**good_bits(), "sneaky": 1})
    assert any("sneaky" in r for r in exc.value.reasons)
    assert any("cannot be validated" in r for r in exc.value.reasons)


def test_0f_a_a_wrong_type_is_refused_naming_the_field_and_both_types():
    with pytest.raises(ResultSchemaError) as exc:
        BITS.check_result({**good_bits(), "solved": "yes"})
    assert any("solved must be a boolean, got str" in r
               for r in exc.value.reasons)


def test_0f_a_an_integer_field_refuses_a_float_and_a_bool():
    for bad in (24.5, True):
        with pytest.raises(ResultSchemaError) as exc:
            BITS.check_result({**good_bits(), "length": bad})
        assert any("length must be an integer" in r for r in exc.value.reasons)


def test_0f_a_a_missing_required_output_is_a_violation_not_an_empty_value():
    r = good_bits()
    del r["score"]
    with pytest.raises(ResultSchemaError) as exc:
        BITS.check_result(r)
    assert any("missing required output(s) ['score']" in x
               for x in exc.value.reasons)
    assert any("not an empty one" in x for x in exc.value.reasons)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_0f_a_a_non_finite_score_is_refused_with_the_reason_it_matters(bad):
    """It would compare False against every threshold, so an outcome rule keyed
    on it reads as FALSIFIED rather than as broken."""
    with pytest.raises(ResultSchemaError) as exc:
        BITS.check_result({**good_bits(), "score": bad})
    assert any("not finite" in r for r in exc.value.reasons)
    assert any("FALSIFIED rather than as broken" in r
               for r in exc.value.reasons)


def test_0f_a_an_unsupported_vector_reduction_is_refused_before_admission():
    schema = {"misclassified_ic": R("vector", element="integer",
                                    bounds=(0, 64), reductions=("count",)),
              "accuracy": R("number")}
    ok, why = reduction_supported(schema, "accuracy", "max")
    assert ok and why == ""
    ok, why = reduction_supported(schema, "misclassified_ic", "max")
    assert not ok and "supporting ['count']" in why
    ok, why = reduction_supported(schema, "misclassified_ic", "count")
    assert ok


def test_0f_a_a_field_no_kind_produces_is_refused_and_lists_what_exists():
    ok, why = reduction_supported(BITS.result_schema, "accuracy", "max")
    assert not ok
    assert "no output field 'accuracy'" in why and "'score'" in why


def test_0f_a_all_reasons_are_reported_at_once():
    """One run should not have to be repeated to find the second defect."""
    r = good_bits()
    del r["solved"]
    r["score"] = "high"
    r["extra"] = 1
    with pytest.raises(ResultSchemaError) as exc:
        BITS.check_result(r)
    assert len(exc.value.reasons) >= 3


# --------------------------------------------------------------- 0f-b

def test_0f_b_every_live_executor_satisfies_its_own_declared_schema():
    """Wrapper/library parity for the three kinds that live here: what the
    executor really returns is checked against what the kind promised."""
    noop = make_spec(kind="noop_v0")
    assert _ex.run(noop, seed=1)["executed"] is True

    bits = make_spec(kind="evaluate_bitstring")
    out = _ex.run(bits, seed=424242)
    _kinds.get("evaluate_bitstring").check_result(dict(out))
    assert out["length"] == 24

    walk = make_spec(kind="random_walk_v0",
                     repeat=rep(count=1, state="reset"))
    walk["work"] = {"kind": "random_walk_v0",
                    "payload": {"steps": 3, "step_scale": 1.0}}
    out = _ex.run(walk, seed=7, state=_ex.new_state("random_walk_v0"))
    WALK.check_result(dict(out))
    assert math.isfinite(out["position"])


def test_0f_b_the_executor_boundary_refuses_a_result_that_breaks_contract(
        monkeypatch):
    """A wrong shape must never reach an observation."""
    import viv.executors as ex

    monkeypatch.setattr(ex, "_noop_v0",
                        lambda spec: {"executed": "yes",
                                      "executor": "noop_v0",
                                      "reproducibility": "BIT_DETERMINISTIC"})
    with pytest.raises(ResultSchemaError) as exc:
        ex.run(make_spec(kind="noop_v0"), seed=1)
    assert any("executed must be a boolean" in r for r in exc.value.reasons)


def test_0f_b_the_derived_seed_is_echoed_so_parity_is_checkable():
    """A fixture comparing library and wrapper needs the seed the wrapper
    actually used, not the one the caller thinks it passed."""
    walk = make_spec(kind="random_walk_v0", repeat=rep(count=1))
    walk["work"] = {"kind": "random_walk_v0",
                    "payload": {"steps": 2, "step_scale": 0.5}}
    out = _ex.run(walk, seed=99, state=_ex.new_state("random_walk_v0"))
    assert out["seed"] == 99
    assert out["step_scale"] == 0.5


# --------------------------------------------------------------- 0f-c

VEC = {"witness": R("vector", element="integer", bounds=(0, 4),
                    reductions=("any", "count")),
       "accuracy": R("number")}


def test_0f_c_a_vector_over_its_declared_ceiling_is_refused():
    with pytest.raises(ResultSchemaError) as exc:
        validate_result("k", VEC, {"witness": [1, 2, 3, 4, 5],
                                   "accuracy": 1.0, "executor": "k",
                                   "reproducibility": "BIT_DETERMINISTIC"})
    assert any("above the declared maximum 4" in r for r in exc.value.reasons)


def test_0f_c_a_vector_AT_its_ceiling_needs_explicit_truncation_metadata():
    """A full witness list and a silently cut one must not look the same."""
    full = {"witness": [1, 2, 3, 4], "accuracy": 1.0, "executor": "k",
            "reproducibility": "BIT_DETERMINISTIC"}
    with pytest.raises(ResultSchemaError) as exc:
        validate_result("k", VEC, full)
    assert any("declared no truncation" in r for r in exc.value.reasons)

    meta = validate_result("k", VEC, full, truncation={"witness": True})
    assert meta["vectors"]["witness"]["truncated"] is True
    assert meta["vectors"]["witness"]["length"] == 4


def test_0f_c_truncation_declared_for_a_non_vector_or_unknown_field_is_refused():
    body = {"witness": [1], "accuracy": 1.0, "executor": "k",
            "reproducibility": "BIT_DETERMINISTIC"}
    with pytest.raises(ResultSchemaError) as exc:
        validate_result("k", VEC, body, truncation={"accuracy": True})
    assert any("non-vector field" in r for r in exc.value.reasons)
    with pytest.raises(ResultSchemaError) as exc:
        validate_result("k", VEC, body, truncation={"nope": True})
    assert any("unknown field" in r for r in exc.value.reasons)


def test_0f_c_a_vector_element_of_the_wrong_type_is_refused_by_index():
    with pytest.raises(ResultSchemaError) as exc:
        validate_result("k", VEC, {"witness": [1, "two"], "accuracy": 1.0,
                                   "executor": "k",
                                   "reproducibility": "BIT_DETERMINISTIC"})
    assert any("witness[1] must be an integer" in r for r in exc.value.reasons)


def test_0f_c_a_vector_must_declare_bounds_and_an_element_type():
    """An unbounded witness list is an unbounded write into the record, and it
    must be reached deliberately rather than by omission."""
    with pytest.raises(ValueError) as exc:
        R("vector", element="integer")
    assert "must declare bounds" in str(exc.value)
    with pytest.raises(ValueError):
        R("vector", bounds=(0, 4))
    assert R("vector", element="integer", bounds=(0, None)).bounds == (0, None)


# ------------------------------------------------- cli exposes the contract

def test_cli_kinds_prints_the_same_contract_validation_uses():
    lines = describe(BITS.result_schema)
    joined = "\n".join(lines)
    for name in BITS.result_schema:
        assert name in joined
    assert "executor" in joined and "reproducibility" in joined
    assert "score" in joined and "finite" in joined
    assert BITS.result_lines() == lines


def test_a_kind_whose_executor_lives_elsewhere_declares_no_result():
    """Guessing an external owner's result would be a contract Vivarium is not
    entitled to write."""
    assert _kinds.get("archaeon.probe.v0").declares_result is False
