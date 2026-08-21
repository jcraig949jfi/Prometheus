"""CANON R9 acceptance suite — and the 8th instance of the competitor-relative law.

Everything asserted here was MEASURED against Lean 4.30.0 before it was written down. The
headline result is negative and is about the canon itself: the kill test canon §3 specifies for
R9 (proof-dependency-graph analysis) admits the circular trap that the same canon entry names.

All Lean sources are memoised per process, so the suite pays for each distinct check once.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.canon_r9_lemma import (  # noqa: E402
    GOAL_A, PROPOSALS, STRONG_EQUIVALENCE_BUDGET, WEAK_EQUIVALENCE_BUDGET,
    CircularLemmaEmitter, DecorativeLemmaEmitter, DeletionOnlyInventor, LemmaInventor,
    OverStrongCircularityChecker, SwappedCircularEmitter, deletion_test, is_restatement,
    naive_syntactic_restatement,
)
from prometheus_math.lean_oracle import lean_available  # noqa: E402

pytestmark = pytest.mark.skipif(not lean_available(), reason="Lean toolchain not reachable")

HONEST = PROPOSALS[("LemmaInventor", "double_succ")]
DECORATIVE = PROPOSALS[("DecorativeLemmaEmitter", "double_succ")]
CIRCULAR = PROPOSALS[("CircularLemmaEmitter", "double_succ")]
SWAPPED = PROPOSALS[("SwappedCircularEmitter", "double_succ")]


# ---- capability: the artifact the canon asks for ---------------------------------------------

def test_honest_lemma_is_accepted_with_a_load_bearing_flag():
    """The canon's artifact: the lemma, NAMED, plus the load-bearing flag. n+n = 2*n is true,
    the goal proof rewrites with it, and deleting it breaks that proof."""
    v = LemmaInventor().judge(GOAL_A)
    assert v.lemma_statement == "∀ n : Nat, n + n = 2 * n"
    assert v.lemma_true and v.goal_proved and v.load_bearing
    assert not v.restatement and v.accepted


def test_a_lemma_that_does_not_check_is_never_accepted():
    """An invented lemma that is false is not a contribution however useful it would be.
    Lean settles this, not the circuit."""
    from techne.ladder_circuits.canon_r9_lemma import LemmaProposal
    false_lemma = LemmaProposal("pm_false", "∀ n : Nat, n + n = 2 * n + 1",
                                "by intro n; omega", "by intro n; rw [pm_false]")
    v = LemmaInventor().judge(GOAL_A, false_lemma)
    assert not v.lemma_true and not v.accepted


# ---- trap 1: decorative --------------------------------------------------------------------

def test_KILL_decorative_lemma_dies_on_the_deletion_test():
    """`n * 0 = 0` is perfectly true and the goal is proved — by `omega`, which never touches
    it. The proof still checks with the lemma removed, so it is load-bearing on nothing."""
    v = DecorativeLemmaEmitter().judge(GOAL_A)
    assert v.lemma_true and v.goal_proved       # both surface signals look fine
    assert not v.load_bearing and not v.accepted


def test_deletion_test_is_what_separates_decorative_from_honest():
    """Isolate the mechanism: same test function, opposite verdicts, nothing else varying."""
    assert deletion_test(GOAL_A, HONEST)[0] is True
    assert deletion_test(GOAL_A, DECORATIVE)[0] is False


# ---- trap 2: circular, and the canon's blind spot ---------------------------------------------

def test_EIGHTH_INSTANCE_deletion_test_alone_cannot_separate_honest_from_circular():
    """**Eighth instance of the competitor-relative law, and the finding of this cycle.**

    Under the canon's stated R9 kill test — proof-dependency-graph analysis — the honest
    inventor and an emitter that hands back the goal verbatim are observationally IDENTICAL:
    lemma true, goal proved, deletion breaks the proof, accepted. The canon names the circular
    trap and then specifies a kill test that cannot see it.

    MEASURED, not argued: the two verdicts agree on every field the deletion-only checker
    populates.
    """
    honest = DeletionOnlyInventor().judge(GOAL_A, HONEST)
    circular = DeletionOnlyInventor().judge(GOAL_A, CIRCULAR)
    fields = lambda v: (v.lemma_true, v.goal_proved, v.load_bearing, v.accepted)
    assert fields(honest) == fields(circular) == (True, True, True, True)


def test_REPAIR_ONE_triviality_budget_separates_them():
    """Defence 1: ask whether `lemma ↔ goal` falls to a weak tactic. The circular lemma's
    equivalence to the goal is literally `Iff.rfl`; the honest lemma's is not provable by
    anything in the budget."""
    circular = CircularLemmaEmitter().judge(GOAL_A)
    honest = LemmaInventor().judge(GOAL_A)
    assert circular.load_bearing and circular.restatement and not circular.accepted
    assert honest.load_bearing and not honest.restatement and honest.accepted


def test_REPAIR_ZERO_naive_string_comparison_also_catches_the_plain_circular_lemma():
    """The cheap check works on the obvious case — which is exactly why it gets trusted."""
    assert naive_syntactic_restatement(CIRCULAR.lemma_statement, GOAL_A.goal)
    assert not naive_syntactic_restatement(HONEST.lemma_statement, GOAL_A.goal)


def test_KILL_swapping_the_equation_defeats_the_naive_check_but_not_the_budget():
    """Trap 2b. `2*n+1 = n+n+1` is a different string and the same claim. The free check says
    'not a restatement'; the semantic budget closes the equivalence with symm on both sides.
    A gaming system reaches for exactly this rewrite."""
    assert not naive_syntactic_restatement(SWAPPED.lemma_statement, GOAL_A.goal)
    v = SwappedCircularEmitter().judge(GOAL_A)
    assert v.load_bearing               # survives the canon's kill test too
    assert v.restatement and not v.accepted
    assert "symm" in v.checker_notes    # caught by the second budget entry specifically


# ---- trap 3: the over-strong checker ----------------------------------------------------------

def test_KILL_decision_procedure_in_the_budget_rejects_the_honest_lemma():
    """R6's phantom-failure pathology, relocated. With `omega` in the equivalence budget any
    two true linear-arithmetic statements are 'equivalent', so the checker calls the honest
    lemma a restatement. It admits no circular lemma and no real one either."""
    strict = OverStrongCircularityChecker()
    honest = strict.judge(GOAL_A)
    assert honest.restatement and not honest.accepted        # phantom rejection
    assert strict.judge(GOAL_A, CIRCULAR).accepted is False  # and no credit for the catch


def test_the_budget_is_the_only_difference_between_the_two_checkers():
    """Mechanism isolation: same lemma, same goal, budget swapped, verdict flips."""
    weak, _ = is_restatement(HONEST.lemma_statement, GOAL_A.goal, WEAK_EQUIVALENCE_BUDGET)
    strong, _ = is_restatement(HONEST.lemma_statement, GOAL_A.goal, STRONG_EQUIVALENCE_BUDGET)
    assert weak is False and strong is True


def test_acceptance_requires_all_four_properties_together():
    """Each competitor fails exactly one conjunct, and one conjunct is enough to sink it."""
    verdicts = {
        "honest": LemmaInventor().judge(GOAL_A),
        "decorative": DecorativeLemmaEmitter().judge(GOAL_A),
        "circular": CircularLemmaEmitter().judge(GOAL_A),
        "swapped": SwappedCircularEmitter().judge(GOAL_A),
    }
    assert [k for k, v in verdicts.items() if v.accepted] == ["honest"]
    assert all(v.lemma_true and v.goal_proved for v in verdicts.values())
