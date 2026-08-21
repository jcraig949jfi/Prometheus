"""R7 acceptance suite: abandon-and-replan vs repair-locally vs thrash.

Includes the 5th instance of the recurring cheaper-mechanism law: on an easy battery (the
first alternative always works) the thrasher is INDISTINGUISHABLE from a genuine reviser.
The battery must contain problems where several plans fail before one succeeds.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r7_plan_revision import (  # noqa: E402
    LocalRepairer, PlanReviser, ThrashingSwitcher, distinct_plans_tried, wasted_retries,
)

#: Four plans; which solves a problem depends on the problem's tag.
PLANS = {
    "algebraic": lambda p: "solved-algebraically" if p.startswith("alg") else None,
    "geometric": lambda p: "solved-geometrically" if p.startswith("geo") else None,
    "numeric": lambda p: "solved-numerically" if p.startswith("num") else None,
    "combinatorial": lambda p: "solved-combinatorially" if p.startswith("com") else None,
}
ORDER = ["algebraic", "geometric", "numeric", "combinatorial"]


# ---- capability -------------------------------------------------------------------------

def test_reviser_solves_when_the_first_plan_is_wrong_in_principle():
    """The R7 probe: the obvious plan (algebraic, tried first) cannot work; the reviser
    abandons and reaches the plan that can."""
    out, log = PlanReviser(PLANS, ORDER).solve("combinatorics-problem-1")
    assert out is None or True  # tag below drives the real case
    out, log = PlanReviser(PLANS, ORDER).solve("com-1")
    assert out == "solved-combinatorially"
    assert distinct_plans_tried(log) == 4        # it worked through the alternatives
    assert wasted_retries(log) == 0              # and never retried a known failure


def test_reviser_terminates_and_reports_failure_when_no_plan_applies():
    out, log = PlanReviser(PLANS, ORDER).solve("xyz-unsolvable")
    assert out is None
    assert len(log) == len(ORDER)                # each plan tried exactly once


# ---- the R6/R7 separation, enforced -------------------------------------------------------

def test_KILL_local_repairer_never_escapes_a_plan_that_is_wrong_in_principle():
    """R6 behaviour, exactly as the canon predicts: it repairs the same doomed plan until
    patience runs out and never reaches the plan that works."""
    out, log = LocalRepairer(PLANS, first_plan="algebraic", patience=8).solve("com-1")
    assert out is None
    assert distinct_plans_tried(log) == 1
    assert len(log) == 8                          # all effort spent inside one strategy


def test_local_repairer_is_fine_when_the_first_plan_is_right():
    """The separation is about WHICH problems, not about the repairer being useless."""
    out, _log = LocalRepairer(PLANS, first_plan="algebraic").solve("alg-7")
    assert out == "solved-algebraically"


# ---- the trap: thrashing ------------------------------------------------------------------

def test_KILL_thrasher_burns_its_budget_revisiting_known_failures():
    """Measured, not assumed: the memoryless stride-2 policy cycles algebraic->numeric->
    algebraic... It DOES switch (so a naive 'did it abandon the plan?' battery passes it),
    yet it never reaches the plan that works and spends 10 of 12 attempts re-running
    strategies it already saw fail. The reviser solves in 4 with zero waste.

    (First draft of this test ASSUMED the thrasher would succeed-but-waste. It fails
    outright — a reminder that a trap circuit's pathology should be measured before it is
    described.)"""
    t_out, t_log = ThrashingSwitcher(PLANS, ORDER, budget=12).solve("com-1")
    r_out, r_log = PlanReviser(PLANS, ORDER).solve("com-1")
    assert r_out == "solved-combinatorially" and wasted_retries(r_log) == 0 and len(r_log) == 4
    assert t_out is None
    assert wasted_retries(t_log) == 10
    assert distinct_plans_tried(t_log) == 2      # it switched, and still lost


def test_on_an_unsolvable_problem_the_reviser_TERMINATES_and_the_thrasher_spins():
    """Termination is the structural property retained failure-knowledge buys: the exhausted
    set grows monotonically, so the reviser stops after one pass; the memoryless policy
    spends its whole budget."""
    _r_out, r_log = PlanReviser(PLANS, ORDER).solve("zzz-none")
    _t_out, t_log = ThrashingSwitcher(PLANS, ORDER, budget=12).solve("zzz-none")
    assert len(r_log) == len(ORDER) and wasted_retries(r_log) == 0
    assert len(t_log) == 12 and wasted_retries(t_log) > 0


def test_thrasher_can_fail_to_terminate_within_budget_on_an_adversarial_order():
    """Stride-2 revisiting on an even-length plan list never reaches the odd-index plans:
    the thrasher exhausts its budget while the answer sits one index away."""
    out, log = ThrashingSwitcher(PLANS, ORDER, budget=12).solve("geo-3")
    assert out is None                            # geometric is at index 1, never visited
    assert wasted_retries(log) >= 6
    assert PlanReviser(PLANS, ORDER).solve("geo-3")[0] == "solved-geometrically"


# ---- the cheaper-mechanism slice (5th instance of the recurring law) -----------------------

def test_EASY_BATTERY_cannot_distinguish_thrasher_from_reviser():
    """On problems where the FIRST alternative works, the two are observationally identical:
    same answer, same number of attempts, zero wasted retries. A battery built only from
    such problems certifies thrashing as plan revision — the recurring cheaper-mechanism law,
    fifth instance. Batteries must include multi-failure problems."""
    for easy in ("alg-1", "alg-2"):
        t_out, t_log = ThrashingSwitcher(PLANS, ORDER).solve(easy)
        r_out, r_log = PlanReviser(PLANS, ORDER).solve(easy)
        assert t_out == r_out
        assert len(t_log) == len(r_log) == 1
        assert wasted_retries(t_log) == wasted_retries(r_log) == 0
