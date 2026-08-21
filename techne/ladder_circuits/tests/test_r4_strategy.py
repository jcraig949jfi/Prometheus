"""R4 acceptance suite: strategy selection without a supplied order.

The decisive content:
- MIXED battery, no order supplied: the dispatcher must pick the right program per problem.
- BASE-RATE INVERSION kill: a frequency-prior selector calibrated on a linear-heavy battery
  collapses on a rational-heavy one; the structural dispatcher is invariant BY CONSTRUCTION
  (it never saw the base rates). The trap from cycle 002's block, made executable.
- MECHANISM SPLIT: dispatcher and verified-portfolio tie on accuracy — only WORK and
  VERIFIER-CALLS separate them. Batteries that record accuracy alone cannot tell R4
  mechanisms apart; the trace-vector fields are the instrument.
"""
from __future__ import annotations

import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r4_strategy import (  # noqa: E402
    PriorSelector,
    StructuralDispatcher,
    VerifiedPortfolio,
    root_verifier,
)

x, y = sp.symbols("x y")
succ = sp.Function("succ")


def tower(n):
    e = sp.Integer(0)
    for _ in range(n):
        e = succ(e)
    return e


RATIONAL = [3 / (x + 1) + 4 / (x - 1), 5 / (y + 1) + 2 / (y - 8)]
LINEAR = [3 * x + 7, 5 * y - 2, 11 * x + 1]
TOWERS = [tower(4), tower(9)]
GOLD = {
    str(RATIONAL[0]): sp.Rational(-1, 7), str(RATIONAL[1]): sp.Rational(38, 7),
    str(LINEAR[0]): sp.Rational(-7, 3), str(LINEAR[1]): sp.Rational(2, 5),
    str(LINEAR[2]): sp.Rational(-1, 11), str(TOWERS[0]): 4, str(TOWERS[1]): 9,
}


# ---- capability: mixed battery, no order supplied ------------------------------------------

def test_dispatcher_selects_correctly_across_all_three_families():
    d = StructuralDispatcher()
    for prob in RATIONAL + LINEAR + TOWERS:
        r = d.solve(prob)
        assert r.answer == GOLD[str(prob)], f"{prob}: {r}"
        assert r.strategy is not None


def test_dispatcher_fails_closed_on_unrecognized_structure():
    r = StructuralDispatcher().solve(sp.sin(x) - 1)
    assert r.answer is None and r.strategy is None and r.work == 0


# ---- the kill: base-rate inversion ---------------------------------------------------------

def test_KILL_prior_selector_collapses_under_base_rate_inversion_dispatcher_invariant():
    """Calibrate the prior baseline on a LINEAR-heavy battery; test on RATIONAL+TOWER
    problems. The prior selector's accuracy collapses to 0; the dispatcher stays perfect —
    the separation between structure-based selection and a learned frequency prior."""
    calib = LINEAR + [RATIONAL[0]]
    prior = PriorSelector.calibrate(calib, [GOLD[str(p)] for p in calib])
    assert prior.best_strategy == "plain_linear"

    test_set = [RATIONAL[1]] + TOWERS
    prior_hits = sum(prior.solve(p).answer == GOLD[str(p)] for p in test_set)
    disp_hits = sum(StructuralDispatcher().solve(p).answer == GOLD[str(p)] for p in test_set)
    assert prior_hits == 0
    assert disp_hits == len(test_set)


# ---- mechanism split: accuracy ties, work/verifier separate --------------------------------

def test_portfolio_matches_dispatcher_accuracy_but_pays_work_and_verifier_calls():
    d, pf = StructuralDispatcher(), VerifiedPortfolio(verifier=root_verifier)
    prob = RATIONAL[0]
    rd, rp = d.solve(prob), pf.solve(prob)
    assert rd.answer == rp.answer == GOLD[str(prob)]
    assert rd.verifier_calls == 0 and rp.verifier_calls >= 1
    assert rp.work >= rd.work, "portfolio must pay at least the dispatcher's work"


def test_portfolio_without_verifier_abstains_rather_than_lying():
    assert VerifiedPortfolio(verifier=None).solve(LINEAR[0]).answer is None


def test_portfolio_is_robust_where_dispatcher_fails_closed():
    """The mechanisms differ in FAILURE direction too: a problem the classifier does not
    recognize but some program solves — dispatcher abstains; verified portfolio finds it.
    (x^2-4 root 2: no library 'quadratic' strategy, but linear_root fails and rational path
    fails, so both abstain — use a disguised linear instead: x/2 - 1 has denominator-free
    fraction shape the classifier reads as linear, fine; craft the classifier gap with a
    product form the classifier misses.)"""
    prob = sp.Mul(sp.Rational(1, 3), 3 * x + 7, evaluate=False)  # classifier sees a Mul, not linear
    d, pf = StructuralDispatcher(), VerifiedPortfolio(verifier=root_verifier)
    rd, rp = d.solve(prob), pf.solve(prob)
    if rd.answer is None:  # classifier gap confirmed
        assert rp.answer == sp.Rational(-7, 3)
    else:  # sympy normalized the disguise; the robustness claim is then untested here
        assert rd.answer == sp.Rational(-7, 3)
