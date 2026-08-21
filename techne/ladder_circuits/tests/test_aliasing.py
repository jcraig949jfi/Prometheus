"""Evaluator aliasing — the instrument, and its retrofit to canon R6, R9 and R10.

Claim v11 was measured at R10 as a dial that could not reach the honest operating point.
External review supplied the provable form, and this suite is the check that the provable form
actually covers the earlier sightings rather than merely sounding like it does.

For each rung: state the finest projection the evaluator family can see, FIND the aliasing pair,
then sweep the family and confirm every member errs. Theorem and measurement.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.aliasing import (  # noqa: E402
    all_aliasing_witnesses, family_cannot_be_correct, find_aliasing_witness,
    verify_family_incapacity,
)


# ---- the instrument itself --------------------------------------------------------------------

def test_witness_found_when_projection_collapses_a_distinction():
    """Minimal case: π keeps only parity, truth depends on magnitude."""
    w = find_aliasing_witness([1, 3], projection=lambda n: n % 2, truth=lambda n: n > 2)
    assert w is not None and w.projection_value == 1
    assert (w.left_truth, w.right_truth) == (False, True)


def test_no_witness_when_the_projection_is_sufficient():
    """A None result is evidence of adequacy ON THIS BATTERY, never a proof of adequacy —
    which is why the docstring says so and this test only checks the mechanics."""
    assert find_aliasing_witness([1, 2, 3], projection=lambda n: n, truth=lambda n: n > 2) is None
    assert family_cannot_be_correct([1, 2, 3], lambda n: n, lambda n: n > 2) is False


def test_theorem_and_measurement_agree_on_the_toy():
    """Every member of a family restricted to parity must err on the witness pair."""
    w = find_aliasing_witness([1, 3], lambda n: n % 2, lambda n: n > 2)
    # the family: "answer True iff parity == p", for p in {0, 1}, plus the two constants
    family = ["parity0", "parity1", "always_true", "always_false"]

    def evaluate(theta, n):
        return {"parity0": n % 2 == 0, "parity1": n % 2 == 1,
                "always_true": True, "always_false": False}[theta]

    result = verify_family_incapacity(family, evaluate, w)
    assert result["all_members_err"] and result["all_members_aliased"]


# ---- retrofit: canon R6, search horizon --------------------------------------------------------

def test_R6_horizon_aliases_a_late_failure_against_a_true_conjecture():
    """Finest projection for the family {BoundedSearcher(h) : h <= H} is the conjecture's
    behaviour on n = 0..H — every member sees a coarsening of it.

    Witness: a conjecture that first fails at H+2 is indistinguishable from a true one on that
    view, and their truths differ. So no horizon in the family is correct on both. This is why
    Euler's n²+n+41 at n=40 defeats any searcher whose horizon was fixed in advance.
    """
    from techne.ladder_circuits.canon_r6_falsification import (
        BoundedSearcher, late_failure_conjecture, true_conjecture_sum,
    )
    H = 10
    instances = [late_failure_conjecture(H + 2), true_conjecture_sum()]
    projection = lambda c: tuple(c[1](n) for n in range(H + 1))
    truth = lambda c: not c[2]                     # "should be claimed false"

    w = find_aliasing_witness(instances, projection, truth,
                              note=f"behaviour on n <= {H}, the finest view in the family")
    assert w is not None and w.projection_value == (True,) * (H + 1)

    result = verify_family_incapacity(
        family=list(range(H + 1)),
        evaluate=lambda h, c: BoundedSearcher(horizon=h).judge(c).claimed_false,
        witness=w,
    )
    assert result["all_members_err"] and result["all_members_aliased"]


def test_R6_the_witness_dissolves_once_the_horizon_can_exceed_the_boundary():
    """The theorem is about a FAMILY, not about search being hopeless: widen the finest view
    past the failure point and the aliasing disappears."""
    from techne.ladder_circuits.canon_r6_falsification import (
        late_failure_conjecture, true_conjecture_sum,
    )
    instances = [late_failure_conjecture(12), true_conjecture_sum()]
    wide = lambda c: tuple(c[1](n) for n in range(20))
    assert find_aliasing_witness(instances, wide, lambda c: not c[2]) is None


# ---- retrofit: canon R10, world features -------------------------------------------------------

def test_R10_world_features_alias_two_techniques_on_one_world_pair():
    """The cycle-017 result, restated as an impossibility rather than a sweep. The finest view
    available to FeatureSensitiveTransfer at ANY k is the triple of world features of the
    (source, target) pair — so two techniques sharing a pair are aliased, and their transfer
    verdicts differ."""
    from techne.ladder_circuits.canon_r10_analogy import (
        BATTERY, FEATURES, FeatureSensitiveTransfer, ground_truth,
    )
    projection = lambda tw: tuple(f(tw[0].home) == f(tw[1]) for _label, f in FEATURES)
    truth = lambda tw: ground_truth(*tw)

    w = find_aliasing_witness(list(BATTERY), projection, truth,
                              note="all three world features, the k=3 view")
    assert w is not None
    assert w.left[1] is w.right[1]                 # same target world
    assert w.left[0].home is w.right[0].home       # same source world
    assert w.left[0].name != w.right[0].name       # different techniques

    result = verify_family_incapacity(
        family=list(range(4)),
        evaluate=lambda k, tw: FeatureSensitiveTransfer(k).transfer(*tw).verdict == "TRANSFERS",
        witness=w,
    )
    assert result["all_members_err"] and result["all_members_aliased"]


def test_R10_the_battery_is_riddled_with_aliased_pairs_not_merely_one():
    """Reporting: how badly the projection collapses the battery. One witness suffices for the
    proof; the count says how much of the battery the family is blind to."""
    from techne.ladder_circuits.canon_r10_analogy import BATTERY, FEATURES, ground_truth
    projection = lambda tw: tuple(f(tw[0].home) == f(tw[1]) for _label, f in FEATURES)
    pairs = all_aliasing_witnesses(list(BATTERY), projection, lambda tw: ground_truth(*tw))
    assert len(pairs) >= 5


# ---- retrofit: canon R9, the deletion test ------------------------------------------------------

def test_R9_deletion_test_aliases_the_honest_lemma_against_the_circular_one():
    """Aliasing is NOT a fact about dials. The deletion-only checker has no parameter at all,
    and is still killed by the same argument: its finest observable is
    (lemma_true, goal_proved, load_bearing), the honest and circular proposals agree on all
    three, and only one of them is a genuine contribution.

    This is cycle 016's finding, re-derived from the general instrument instead of by hand.
    """
    from prometheus_math.lean_oracle import lean_available
    if not lean_available():
        pytest.skip("Lean toolchain not reachable")

    from techne.ladder_circuits.canon_r9_lemma import (
        GOAL_A, PROPOSALS, DeletionOnlyInventor, LemmaInventor,
    )
    honest = PROPOSALS[("LemmaInventor", "double_succ")]
    circular = PROPOSALS[("CircularLemmaEmitter", "double_succ")]
    checker = DeletionOnlyInventor()

    def projection(prop):
        v = checker.judge(GOAL_A, prop)
        return (v.lemma_true, v.goal_proved, v.load_bearing)

    def truth(prop):
        return LemmaInventor().judge(GOAL_A, prop).accepted   # the full four-way check

    w = find_aliasing_witness([honest, circular], projection, truth,
                              note="the deletion-only view: (true, proved, load_bearing)")
    assert w is not None and w.projection_value == (True, True, True)
    assert (w.left_truth, w.right_truth) == (True, False)

    result = verify_family_incapacity(
        family=["deletion_only"],
        evaluate=lambda _t, prop: checker.judge(GOAL_A, prop).accepted,
        witness=w,
    )
    assert result["all_members_err"] and result["all_members_aliased"]


def test_R9_adding_the_circularity_check_removes_the_aliasing():
    """And the repair is visible in the same instrument: extend what the evaluator can see, and
    the witness stops existing. That is what a genuine repair looks like, as against a retune."""
    from prometheus_math.lean_oracle import lean_available
    if not lean_available():
        pytest.skip("Lean toolchain not reachable")

    from techne.ladder_circuits.canon_r9_lemma import GOAL_A, PROPOSALS, LemmaInventor
    honest = PROPOSALS[("LemmaInventor", "double_succ")]
    circular = PROPOSALS[("CircularLemmaEmitter", "double_succ")]
    full = LemmaInventor()

    def projection(prop):
        v = full.judge(GOAL_A, prop)
        return (v.lemma_true, v.goal_proved, v.load_bearing, v.restatement)

    assert find_aliasing_witness([honest, circular], projection,
                                 lambda p: full.judge(GOAL_A, p).accepted) is None


# ---- cycle 019: synthesis, and the factorization precondition ---------------------------------

def test_FIBER_SEARCH_synthesises_a_witness_instead_of_finding_one():
    """Round-7 review: the instrument was a diagnostic because it searched a battery I had
    already built. Fiber search makes it an attack — fix the world pair (one fiber of π) and
    mutate only the technique parameter until the truth flips.

    Seeded at a = 3 over F_7 (a nonsquare, so the technique transfers), the search walks a and
    finds a = 2, where 3² = 2 mod 7 makes it break. Nothing about the worlds changed.
    """
    from techne.ladder_circuits.aliasing import fiber_search
    from techne.ladder_circuits.canon_r10_analogy import (
        W_F7, ground_truth, nonsquare_technique,
    )
    seed = (nonsquare_technique(3), W_F7)
    mutate = lambda tw: ((nonsquare_technique(a), tw[1]) for a in range(2, 40))
    projection = lambda tw: (tw[0].home.name, tw[1].name)       # complete world knowledge
    w = fiber_search(seed, mutate, projection, lambda tw: ground_truth(*tw))
    assert w is not None
    assert w.left[0].name == "nonsquare_3" and w.right[0].name == "nonsquare_2"
    assert (w.left_truth, w.right_truth) == (True, False)
    assert "fiber search" in w.note


def test_fiber_search_discards_candidates_that_leave_the_fiber():
    """A mutation that changes the world is useless here: the evaluator CAN see it, so the pair
    proves nothing about the family. Mutating q only, the search finds nothing."""
    from techne.ladder_circuits.aliasing import fiber_search
    from techne.ladder_circuits.canon_r10_analogy import (
        W_F3, W_F5, W_F7, ground_truth, nonsquare_technique,
    )
    seed = (nonsquare_technique(3), W_F7)
    mutate = lambda tw: ((tw[0], w) for w in (W_F3, W_F5, W_F7))
    projection = lambda tw: (tw[0].home.name, tw[1].name)
    assert fiber_search(seed, mutate, projection, lambda tw: ground_truth(*tw)) is None


def test_FACTORIZATION_PRECONDITION_holds_for_the_R6_horizon_family():
    """The precondition the cycle-018 write-up assumed without checking: every member's view
    must factor through π. A horizon-5 searcher's view is determined by the horizon-10 view, so
    a witness under the finer projection binds the coarser member."""
    from techne.ladder_circuits.aliasing import verify_factorization
    from techne.ladder_circuits.canon_r6_falsification import (
        euler_prime_conjecture, late_failure_conjecture, true_conjecture_square,
        true_conjecture_sum,
    )
    conjs = [euler_prime_conjecture(), true_conjecture_sum(), true_conjecture_square(),
             late_failure_conjecture(7), late_failure_conjecture(12)]
    fine = lambda c: tuple(c[1](n) for n in range(11))
    coarse = lambda c: tuple(c[1](n) for n in range(6))
    assert verify_factorization(conjs, coarse, fine)
    assert not verify_factorization(conjs, fine, coarse)      # and not the other way round


def test_INCOMPARABLE_OBSERVATIONS_break_the_finest_projection_argument():
    """The failure mode the precondition exists to catch. Two members observing incomparable
    features have no common projection short of the full input, so no single witness binds both
    and incapacity must be argued per observation class."""
    from techne.ladder_circuits.aliasing import verify_factorization
    instances = [(0, 0), (0, 1), (1, 0), (1, 1)]
    first, second = lambda p: p[0], lambda p: p[1]
    assert not verify_factorization(instances, first, second)
    assert not verify_factorization(instances, second, first)
