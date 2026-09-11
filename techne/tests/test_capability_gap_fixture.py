"""Controls for the capability-gap fixture's CORRECTNESS criterion (TECHNE-45).

Preregistered in roles/Techne/journal/2026-09-11.md before any of this ran. The
four controls, in the base role's words:

    positive   the instrument detects real success (a correct solve is CORRECT /
               CERTIFIED at the recorded error)
    cheat      the instrument detects a confidently wrong answer (a value 1.5x the
               truth with status "optimal" is SILENTLY_WRONG; a value outside its
               own certificate is SILENTLY_WRONG)
    negative   the OLD status-only rule and the NEW rule disagree on the cheat row,
               which is the whole content of the repair
    bound      the certificate never inverts (ub >= lb), and the closed forms are
               checked against literature values before they are used as truth

The solver-backed tests run C_5, Petersen and one small random graph only; the
scale rows live in the fixture's own run, not here.
"""
from __future__ import annotations

import numpy as np
import pytest

from techne.scripts import capability_gap_fixture as gf

cp = pytest.importorskip("cvxpy")
HAVE = set(cp.installed_solvers())
SOLVERS = [s for s in gf.FREE_SOLVERS if s in HAVE]
if not SOLVERS:
    pytest.skip("no free SDP solver installed", allow_module_level=True)


# ---------------------------------------------------------------- bound: closed forms

def test_closed_forms_match_literature_values():
    # Lovasz 1979: theta(C_5) = sqrt(5); theta(Petersen = K(5,2)) = 4; theta(K(m,k)) = C(m-1,k-1)
    assert abs(gf._odd_cycle_theta(5) - 5 ** 0.5) < 1e-12
    assert gf._kneser_theta(5, 2) == 4.0
    assert gf._kneser_theta(9, 3) == 28.0
    # Paley(5) is C_5 itself: sqrt(5) both ways
    assert abs(gf._paley_theta(5) - gf._odd_cycle_theta(5)) < 1e-12
    A = gf._paley(5)
    assert np.array_equal(A, gf._cycle(5)) or A.sum() == gf._cycle(5).sum()


def test_kneser_and_paley_have_the_right_degree():
    # K(5,2) is the Petersen graph: 10 vertices, 3-regular.
    P = gf._kneser(5, 2)
    assert P.shape == (10, 10) and set(P.sum(axis=1)) == {3.0}
    # Paley(13): 13 vertices, (p-1)/2 = 6-regular, and every parameter in the fixture is
    # a prime = 1 mod 4 (the constructor refuses otherwise).
    Q = gf._paley(13)
    assert Q.shape == (13, 13) and set(Q.sum(axis=1)) == {6.0}
    with pytest.raises(ValueError):
        gf._paley(7)
    with pytest.raises(ValueError):
        gf._odd_cycle_theta(6)


# ---------------------------------------------------------------- cheat + negative

def test_cheat_closed_form_value_is_silently_wrong_and_old_rule_passes_it():
    truth = 5 ** 0.5
    klass, rel = gf._classify("optimal", 1.5 * truth, truth)
    assert klass == "SILENTLY_WRONG" and rel == pytest.approx(0.5)
    # the negative control: the pre-TECHNE-45 rule reads only the status
    assert gf._old_criterion_failed("optimal") is False


@pytest.mark.parametrize("rule", [gf._classify_certified, gf._classify_certified_prereg])
def test_cheat_value_outside_its_own_certificate_is_silently_wrong(rule):
    cert = {"lb": 2.0, "ub": 2.1, "width_rel": 0.1 / 2.1}
    assert rule("optimal", 3.0, cert) == "SILENTLY_WRONG"
    assert rule("optimal", 1.0, cert) == "SILENTLY_WRONG"
    assert gf._old_criterion_failed("optimal") is False


@pytest.mark.parametrize("rule", [gf._classify_certified, gf._classify_certified_prereg])
def test_instrument_branches_are_never_passes(rule):
    loose = {"lb": 1.0, "ub": 2.0, "width_rel": 0.5}
    assert rule("optimal", 1.5, loose) == "INDETERMINATE"
    assert rule("optimal", 1.5, None) == "UNCERTIFIED"
    assert rule("optimal", None, None) == "OPTIMAL_BUT_NO_VALUE"
    assert rule("infeasible", 1.5, loose) == "DECLARED_FAILURE"
    for k in ("INDETERMINATE", "UNCERTIFIED", "OPTIMAL_BUT_NO_VALUE"):
        assert k in gf.INSTRUMENT_CLASSES
    tight = {"lb": 1.5 - 1e-9, "ub": 1.5 + 1e-9, "width_rel": 2e-9 / 1.5}
    assert rule("optimal", 1.5, tight) == "CERTIFIED"


def test_amended_rule_holds_certificate_rows_to_the_same_bar_as_closed_forms():
    # The SCS row that fired the control: 1.05e-5 above ub. Prereg said SILENTLY_WRONG at a
    # 1e-6 tolerance; a closed form would say CORRECT at the 1e-2 bar; the amended rule agrees
    # with the closed form. Both are kept on the row.
    cert = {"lb": 5.999890434916551, "ub": 6.0000000079720825, "width_rel": 1.826e-05}
    v = 6.000063182939986
    assert gf._classify_certified_prereg("optimal", v, cert) == "SILENTLY_WRONG"
    assert gf._classify_certified("optimal", v, cert) == "CERTIFIED"
    assert gf._classify("optimal", v, 6.0)[0] == "CORRECT"
    f = gf._certificate_error_fields(v, cert)
    assert f["reported_value_outside_certificate_rel"] == pytest.approx(1.05e-5, rel=0.05)
    # and the amended rule still fails a value 1.5x the bracket
    assert gf._classify_certified("optimal", 9.0, cert) == "SILENTLY_WRONG"
    # a value within the bar of the bracket but the bracket itself too loose: INDETERMINATE
    assert gf._classify_certified("optimal", 1.5, {"lb": 1.0, "ub": 2.0}) == "INDETERMINATE"


# ---------------------------------------------------------------- positive + bound (solver)

@pytest.mark.parametrize("solver", SOLVERS)
def test_positive_c5_is_correct_and_certified(solver):
    p = gf._theta_problem(gf._cycle(5))
    v, status = p.solve(solver)
    klass, rel = gf._classify(status, float(v), gf.AUTHORITY_THETA_C5)
    assert klass == "CORRECT", (status, v, rel)
    cert = p.certificate()
    assert cert is not None
    assert cert["ub"] >= cert["lb"]
    assert cert["lb"] - 1e-6 <= gf.AUTHORITY_THETA_C5 <= cert["ub"] + 1e-6
    assert gf._classify_certified(status, float(v), cert) == "CERTIFIED", cert


@pytest.mark.parametrize("solver", SOLVERS)
def test_positive_petersen_certificate_brackets_four(solver):
    p = gf._theta_problem(gf._kneser(5, 2))
    v, status = p.solve(solver)
    klass, _rel = gf._classify(status, float(v), 4.0)
    assert klass == "CORRECT"
    cert = p.certificate()
    assert cert["lb"] - 1e-6 <= 4.0 <= cert["ub"] + 1e-6
    assert cert["width_rel"] <= gf.SILENTLY_WRONG_REL


@pytest.mark.parametrize("solver", SOLVERS)
def test_random_graph_is_certified_without_a_closed_form(solver):
    p = gf._theta_problem(gf._random_graph(14, 0.3, seed=1))
    v, status = p.solve(solver)
    cert = p.certificate()
    assert cert is not None and cert["ub"] >= cert["lb"]
    assert gf._classify_certified(status, float(v), cert) == "CERTIFIED", (v, cert)


def test_certificate_is_none_before_solve_not_a_fabricated_bracket():
    p = gf._theta_problem(gf._cycle(5))
    assert p.certificate() is None


def test_lower_bound_is_feasible_by_construction_even_from_garbage():
    # Hand the projection an X that violates every constraint; the lb it returns must
    # still be the value of a FEASIBLE matrix, i.e. at most theta(C_5) = sqrt(5).
    p = gf._theta_problem(gf._cycle(5))
    p.solve(SOLVERS[0])
    garbage = np.ones((5, 5)) * 3.0 - 2.0 * np.eye(5)
    p.X.value = garbage
    cert = p.certificate()
    assert cert is not None
    assert cert["lb"] <= gf.AUTHORITY_THETA_C5 + 1e-9


def test_reclassification_receipt_counts_disagreements_and_drift():
    cases = [
        {"case": "A_x", "solver": "S", "status": "optimal", "class": "SILENTLY_WRONG",
         "failed": True, "old_criterion_failed": False, "expected": 1.0, "value": 1.5,
         "certificate": {"lb": 0.9, "ub": 1.1, "width_rel": 0.2 / 1.1},
         "certificate_brackets_truth": True},
        {"case": "B_y", "solver": "S", "status": "optimal", "class": "CERTIFIED",
         "failed": False, "old_criterion_failed": False, "value": 2.0,
         "certificate": {"lb": 1.99, "ub": 2.01, "width_rel": 0.02 / 2.01}},
        {"case": "C_z", "solver": "S", "status": "optimal", "class": "CORRECT", "failed": False},
    ]
    prev = {"cases": [{"case": "B_y", "solver": "S", "value": 2.02, "status": "optimal",
                       "failed": False}]}
    r = gf._ab_reclassification(cases, prev)
    assert r["eligible_rows"] == 2                      # C_z is not an A/B row
    assert r["n_disagree"] == 1
    assert r["rows_where_old_and_new_criteria_DISAGREE"][0]["case"] == "A_x"
    assert r["certificate_validation_on_closed_forms"]["n_bracket_truth"] == 1
    d = r["value_drift_vs_previous_committed_result"]
    assert d["n_compared"] == 1 and d["max_rel_change"] == pytest.approx(0.02 / 2.02)
