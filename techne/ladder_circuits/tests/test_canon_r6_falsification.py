"""CANON R6 acceptance suite — and the 6th instance of the competitor-relative law.

The canon's own instruction is the battery design: MIX true and false conjectures and score
the phantom-failure rate. This suite shows why that instruction is load-bearing — on an
all-false battery the eager falsifier is indistinguishable from the honest searcher.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.canon_r6_falsification import (  # noqa: E402
    BoundedSearcher, CredulousAsserter, EagerFalsifier, euler_prime_conjecture,
    late_failure_conjecture, score, true_conjecture_square, true_conjecture_sum,
    verdict_only_score,
)

MIXED = [euler_prime_conjecture(), true_conjecture_sum(), true_conjecture_square(),
         late_failure_conjecture(12)]
TRUTHS = {name: truth for name, _pred, truth in MIXED}


def run(circuit, conjectures=MIXED):
    return [circuit.judge(c) for c in conjectures]


# ---- capability: the canon's named probe ----------------------------------------------------

def test_finds_the_euler_boundary_at_exactly_n_equals_40():
    """n²+n+41 is prime for n = 0..39 and composite at 40 — a 40-term misleading streak.
    The artifact must carry the BOUNDARY, not merely the verdict."""
    s = BoundedSearcher(horizon=100)
    f = s.judge(euler_prime_conjecture())
    assert f.claimed_false and f.counterexample == 40


def test_honest_searcher_abstains_beyond_its_horizon_rather_than_guessing():
    """The boundary placed past the horizon: a bounded instrument must report no-counterexample
    (an honest limit), never a falsity claim it cannot witness."""
    s = BoundedSearcher(horizon=10)
    f = s.judge(late_failure_conjecture(12))
    assert f.claimed_false is False and f.counterexample is None
    assert f.is_supported          # a no-claim is trivially supported


def test_every_falsity_claim_carries_a_witness():
    s = BoundedSearcher(horizon=100)
    run(s)
    assert all(f.is_supported for f in s.ledger)
    assert score(s.ledger, TRUTHS)["unwitnessed"] == 0


# ---- the kill: phantom failures ---------------------------------------------------------------

def test_KILL_eager_falsifier_under_the_two_scorings():
    """MEASURED, and sharper than expected. Under VERDICT-ONLY scoring the eager falsifier
    looks perfect on recall (it says 'false' to everything) and is exposed only by its 100%
    phantom rate. Under WITNESS-REQUIRED scoring its recall COLLAPSES TO ZERO, because it
    never produces the counterexample its claims assert. Two independent defences."""
    e = EagerFalsifier(patience=3)
    run(e)
    naive = verdict_only_score(e.ledger, TRUTHS)
    strict = score(e.ledger, TRUTHS)
    assert naive["recall"] == 1.0 and naive["phantom_rate"] == 1.0
    assert strict["recall"] == 0.0             # the witness requirement alone destroys it
    assert strict["unwitnessed"] == 4


def test_credulous_asserter_is_the_opposite_failure():
    c = CredulousAsserter()
    run(c)
    sc = score(c.ledger, TRUTHS)
    assert sc["phantom_rate"] == 0.0 and sc["recall"] == 0.0


def test_honest_searcher_dominates_on_the_pair_of_scores():
    """Neither score alone separates the three circuits; the PAIR does. (Recall alone crowns
    the eager falsifier; phantom-rate alone crowns the credulous asserter.)"""
    s, e, c = BoundedSearcher(horizon=100), EagerFalsifier(), CredulousAsserter()
    for circ in (s, e, c):
        run(circ)
    ss, se, sc_ = (verdict_only_score(x.ledger, TRUTHS) for x in (s, e, c))
    assert ss["recall"] == 1.0 and ss["phantom_rate"] == 0.0
    assert se["recall"] >= ss["recall"] and se["phantom_rate"] > ss["phantom_rate"]
    assert sc_["phantom_rate"] <= ss["phantom_rate"] and sc_["recall"] < ss["recall"]


# ---- 6th instance of the competitor-relative law ---------------------------------------------

def test_SIXTH_INSTANCE_verdict_only_scoring_on_an_all_false_battery_cannot_separate_them():
    """Sixth instance of the competitor-relative law — and it is about the SCORING, not only
    the battery composition. Under verdict-only scoring, on a battery with no true
    conjectures, the eager falsifier and the honest searcher are observationally IDENTICAL:
    recall 1.0, phantom rate vacuously 0.0. Two independent repairs exist, and the tests
    below show either one suffices."""
    all_false = [euler_prime_conjecture(), late_failure_conjecture(5),
                 late_failure_conjecture(9)]
    truths = {n: t for n, _p, t in all_false}
    s, e = BoundedSearcher(horizon=100), EagerFalsifier(patience=20)
    run(s, all_false)
    run(e, all_false)
    assert verdict_only_score(s.ledger, truths) == verdict_only_score(e.ledger, truths)


def test_REPAIR_ONE_witness_requirement_separates_them_even_on_an_all_false_battery():
    """Defence 1 (the artifact requirement): demand the counterexample. No true conjectures
    needed at all."""
    all_false = [euler_prime_conjecture(), late_failure_conjecture(5)]
    truths = {n: t for n, _p, t in all_false}
    s, e = BoundedSearcher(horizon=100), EagerFalsifier(patience=2)
    run(s, all_false)
    run(e, all_false)
    assert score(s.ledger, truths)["recall"] == 1.0
    assert score(e.ledger, truths)["recall"] == 0.0


def test_adding_ONE_true_conjecture_restores_the_separation():
    """The minimal repair to that battery: one true conjecture, and the two diverge."""
    battery = [euler_prime_conjecture(), late_failure_conjecture(5), true_conjecture_sum()]
    truths = {n: t for n, _p, t in battery}
    s, e = BoundedSearcher(horizon=100), EagerFalsifier(patience=20)
    run(s, battery)
    run(e, battery)
    assert score(s.ledger, truths) != score(e.ledger, truths)
    assert score(e.ledger, truths)["phantom_rate"] == 1.0
