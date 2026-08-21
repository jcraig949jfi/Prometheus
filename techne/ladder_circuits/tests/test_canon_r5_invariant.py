"""CANON R5 acceptance suite — the conserved quantity, NAMED, and the two traps separated.

7th instance of the competitor-relative law: on a battery of ONLY classic mutilated boards,
the parity pattern-matcher is observationally identical to the real reasoner.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.canon_r5_invariant import (  # noqa: E402
    ConservedButUselessReporter, InvariantReasoner, ParityPatternMatcher, TilingProblem,
    colour_difference, full_board, mutilated_board, same_colour_removed_board,
)

DOMINOES = ("horizontal", "vertical")
MUTILATED = TilingProblem("mutilated", mutilated_board(), DOMINOES)
BALANCED = TilingProblem("opposite-colour-removed", same_colour_removed_board(), DOMINOES)
DIAGONAL = TilingProblem("diagonal-moves", mutilated_board(), ("diagonal",))


# ---- capability: the canon's named probe, with the artifact --------------------------------

def test_names_the_conserved_quantity_on_the_mutilated_board():
    c = InvariantReasoner().analyse(MUTILATED)
    assert c.verdict == "impossible"
    assert c.quantity == "colour_difference"     # NAMED, not just "impossible"
    assert c.conserved and c.decisive
    assert c.start_value == -2 and c.goal_value == 0   # both removed corners are "black"


def test_the_board_arithmetic_is_hand_checkable():
    """(0,0) and (7,7) both have r+c even, so removing them takes the difference 0 -> -2.
    (Signed the wrong way in the first draft; the board is the authority, not my arithmetic.)"""
    assert colour_difference(full_board()) == 0
    assert colour_difference(mutilated_board()) == -2
    assert colour_difference(same_colour_removed_board()) == 0


# ---- the canon kill: a near-identical problem where the invariant is INSUFFICIENT ----------

def test_KILL_near_identical_problem_where_the_obvious_invariant_says_nothing():
    """Remove two cells of OPPOSITE colour: parity is balanced, so the classic argument is
    silent. The honest circuit ABSTAINS; it does not convert 'my invariant is quiet' into
    'the tiling is possible' or 'impossible'."""
    c = InvariantReasoner().analyse(BALANCED)
    assert c.verdict == "abstain" and c.quantity is None


def test_KILL_parity_matcher_does_not_notice_the_move_set_changed():
    """Diagonal moves preserve colour, so colour_difference cannot decide anything — the
    matcher still declares impossibility because it never checked conservation under THESE
    moves."""
    reasoner, matcher = InvariantReasoner(), ParityPatternMatcher()
    assert matcher.analyse(DIAGONAL).verdict == "impossible"
    assert reasoner.analyse(DIAGONAL).verdict == "abstain"


# ---- trap 2: conserved but not decisive ----------------------------------------------------

def test_TRAP_conserved_but_not_decisive_claim_is_unsupported():
    """A genuinely conserved quantity that takes the same value on start and goal proves
    nothing. The artifact check catches it even though 'is it conserved?' passes."""
    c = ConservedButUselessReporter().analyse(MUTILATED)
    assert c.conserved is True
    assert c.decisive is False
    assert c.verdict == "impossible"
    assert c.is_supported is False        # the two-property requirement does the work


def test_honest_circuit_never_emits_an_unsupported_claim():
    r = InvariantReasoner()
    for problem in (MUTILATED, BALANCED, DIAGONAL):
        assert r.analyse(problem).is_supported


# ---- 7th instance of the competitor-relative law -------------------------------------------

def test_SEVENTH_INSTANCE_classic_only_battery_cannot_separate_matcher_from_reasoner():
    """On a battery of ONLY classic mutilated boards with domino moves, the pattern-matcher
    and the real reasoner agree on every verdict AND on the named quantity. The competitor is
    observationally equivalent on that support; the battery must vary the MOVE SET and the
    removed-cell colours."""
    classics = [TilingProblem(f"mutilated-{n}", mutilated_board(n), DOMINOES)
                for n in (4, 6, 8, 10)]
    r, m = InvariantReasoner(), ParityPatternMatcher()
    for p in classics:
        cr, cm = r.analyse(p), m.analyse(p)
        assert (cr.verdict, cr.quantity) == (cm.verdict, cm.quantity) == ("impossible",
                                                                          "colour_difference")


def test_REPAIR_only_varying_the_MOVE_SET_separates_them_not_the_removed_colours():
    """Measured, and sharper than the draft assumed: on the opposite-colour-removed board the
    matcher ALSO abstains — with parity balanced it has nothing to assert, so it looks exactly
    as careful as the real reasoner. The separating variation is the MOVE SET, where the
    matcher keeps asserting an invariant that those moves do not conserve.

    A battery that varies only the problem instance, never the operator set, cannot tell a
    conservation-checker from a shape-matcher."""
    r, m = InvariantReasoner(), ParityPatternMatcher()
    assert r.analyse(BALANCED).verdict == m.analyse(BALANCED).verdict == "abstain"
    assert r.analyse(DIAGONAL).verdict == "abstain"
    assert m.analyse(DIAGONAL).verdict == "impossible"
