"""Injected specimens for the qualification-instrument controls (LUDUS-03).

Every fixture here is a deliberately constructed world or corruption whose
reading on an instrument is KNOWN BEFORE THE INSTRUMENT RUNS. They exist so
each instrument can show, with rows, that it can fail, that it detects known
real structure, and that it detects (or provably does not detect) injected or
trivial success. Nothing here is a bench world; nothing here enters the
transfer matrix; the names are ugly on purpose.

Three families, one per instrument:

  depth profile (GATE-W1)   LEDGER   greedy-decidable by construction
                            ORCHARD  payoff deferred to the terminal state
                            NIM345   solved by a four-line closed form
  bench verify              corrupt_pot / corrupt_prob / inject_cycle on a
                            compiled world; MartianDiceOneRay (a rule change
                            no invariant looks at)
  arena leak audits         Kuhn subclasses that leak the opponent's card
                            through a named key, an innocuous key, the
                            legal-action order, and the public state
"""
from __future__ import annotations

import copy
import functools
import math
import sys
from dataclasses import dataclass


# ==========================================================================
# Depth-profile fixtures: the cycle-001 world interface
#   initial_state / legal_actions / apply / is_terminal / result / name
#   states are frozen dataclasses with .to_move in {"A", "B"}
#   own_score(state, who) is the hook ludus.baselines.greedy_action reads
#   for worlds it was not written against
# ==========================================================================

@dataclass(frozen=True)
class PlyState:
    ply: int
    sa: int
    sb: int
    xa: int = 0
    xb: int = 0

    @property
    def to_move(self) -> str:
        return "A" if self.ply % 2 == 0 else "B"


class Ledger:
    """NEGATIVE CONTROL. Each move adds 1, 2 or 3 to the mover's own score;
    no interaction, no deferred effect. The optimal set is exactly the
    greedy set at every state, so the depth profile must read 0.000 at
    every k. A non-zero reading here is a hallucinated gap."""

    name = "CTRL_LEDGER"

    def __init__(self, plies: int = 8):
        self.plies = plies

    def initial_state(self):
        return PlyState(0, 0, 0)

    def legal_actions(self, s):
        return ["ADD1", "ADD2", "ADD3"]

    def apply(self, s, a):
        k = int(a[-1])
        if s.to_move == "A":
            return PlyState(s.ply + 1, s.sa + k, s.sb)
        return PlyState(s.ply + 1, s.sa, s.sb + k)

    def is_terminal(self, s):
        return s.ply >= self.plies

    def result(self, s):
        return s.sa - s.sb

    def own_score(self, s, who):
        return s.sa if who == "A" else s.sb


class Orchard:
    """POSITIVE CONTROL. GRAB pays +1 now; PLANT costs 1 now and pays 3 at
    the terminal state (net +2). The world's own score formula read early
    (result on a non-terminal state) cannot see the deferred payoff, so a
    depth-k search whose cutoff lands before the terminal state prefers
    GRAB while PLANT is optimal. gap(k) is the fraction of eligible states
    whose plies-to-terminal exceed k. With 12 plies gap(4) must be well
    above the 0.20 gate.

    Stated limit: PLANT-always is a constant policy, so this world is ALSO
    solved by a one-line rule. It proves the instrument detects deferred
    payoff; it does not prove the gate detects reasoning."""

    name = "CTRL_ORCHARD"

    def __init__(self, plies: int = 12, yield_: int = 3):
        self.plies, self.yield_ = plies, yield_

    def initial_state(self):
        return PlyState(0, 0, 0, 0, 0)

    def legal_actions(self, s):
        return ["GRAB", "PLANT"]

    def apply(self, s, a):
        if s.to_move == "A":
            if a == "GRAB":
                return PlyState(s.ply + 1, s.sa + 1, s.sb, s.xa, s.xb)
            return PlyState(s.ply + 1, s.sa - 1, s.sb, s.xa + 1, s.xb)
        if a == "GRAB":
            return PlyState(s.ply + 1, s.sa, s.sb + 1, s.xa, s.xb)
        return PlyState(s.ply + 1, s.sa, s.sb - 1, s.xa, s.xb + 1)

    def is_terminal(self, s):
        return s.ply >= self.plies

    def result(self, s):
        m = s.sa - s.sb
        if self.is_terminal(s):
            m += self.yield_ * (s.xa - s.xb)
        return m

    def own_score(self, s, who):
        base = s.sa if who == "A" else s.sb
        if self.is_terminal(s):
            base += self.yield_ * (s.xa if who == "A" else s.xb)
        return base


@dataclass(frozen=True)
class NimState:
    ply: int
    heaps: tuple

    @property
    def to_move(self) -> str:
        return "A" if self.ply % 2 == 0 else "B"


class Nim345:
    """CHEAT CONTROL. Normal-play Nim on heaps (3,4,5): the player who takes
    the last object wins. There is no score before the end, so the world's
    own formula read early is 0 for every non-terminal state -- the cutoff
    eval is uninformative and depth-k search is blind until it reaches a
    terminal state. GATE-W1 will read a large gap(4) and ADMIT this world.

    Bouton (1901): a four-line rule plays it perfectly (xor the heaps; if
    non-zero, reduce a heap h to h ^ x). If the gate admits a world that a
    four-line closed form solves, the gate's cheap-player class (depth
    search with the world's eval) does not contain the cheap class the
    charter's question 2 asks about, and that is recorded, not argued."""

    name = "CTRL_NIM345"

    def __init__(self, heaps=(3, 4, 5)):
        self.heaps0 = tuple(heaps)

    def initial_state(self):
        return NimState(0, self.heaps0)

    def legal_actions(self, s):
        out = []
        for i, h in enumerate(s.heaps):
            for k in range(1, h + 1):
                out.append("H%d-%d" % (i, k))
        return out

    def apply(self, s, a):
        i, k = a[1:].split("-")
        i, k = int(i), int(k)
        heaps = list(s.heaps)
        heaps[i] -= k
        return NimState(s.ply + 1, tuple(heaps))

    def is_terminal(self, s):
        return sum(s.heaps) == 0

    def result(self, s):
        if not self.is_terminal(s):
            return 0                 # no score exists before the end
        # the player who moved last (ply-1) took the last object and wins
        return 1 if (s.ply - 1) % 2 == 0 else -1

    def own_score(self, s, who):
        r = self.result(s)
        return r if who == "A" else -r


def bouton_action(s: NimState):
    """The four-line closed form. Returns a winning move on an N-position
    and None on a P-position (every move loses; all are 'optimal')."""
    x = 0
    for h in s.heaps:
        x ^= h
    if x == 0:
        return None
    for i, h in enumerate(s.heaps):
        if (h ^ x) < h:
            return "H%d-%d" % (i, h - (h ^ x))
    return None


# ==========================================================================
# Bench-verify fixtures: corruptions of a compiled world, and a rule change
# that no invariant inspects
# ==========================================================================

def corrupt_pot(cw, delta: float = 1.0):
    """Add delta to the pot of one non-initial state. A per-world invariant
    that recomputes the pot from the state must fire."""
    cw2 = copy.deepcopy(cw)
    for s in cw2.pot:
        if s != cw2.initial and not cw2.forced[s]:
            cw2.pot[s] += delta
            return cw2, s
    raise RuntimeError("no state to corrupt")


def corrupt_prob(cw, factor: float = 0.5, which: str = "largest"):
    """Scale ONE draw probability of the initial state so the distribution
    no longer normalises. The universal check must fire -- if the removed
    mass exceeds its 1e-7 tolerance. which="smallest" is kept as the first
    injection tried on 2026-09-16: on 13 dice the smallest row carries
    1/6^13 and halving it moves the sum by 3.8e-11, below the tolerance.
    That injection was INELIGIBLE, and the row that records it is the
    eligible-count lesson, not a pass."""
    cw2 = copy.deepcopy(cw)
    s = cw2.initial
    rows = list(cw2.trans[s])
    idx = max(range(len(rows)), key=lambda i: rows[i][0]) if which == "largest"         else min(range(len(rows)), key=lambda i: rows[i][0])
    p, opts = rows[idx]
    rows[idx] = (p * factor, opts)
    cw2.trans[s] = tuple(rows)
    return cw2, s, p * (1 - factor)


def inject_cycle(cw):
    """Make one successor of the initial state lead back to the initial
    state. The acyclicity check must fire."""
    cw2 = copy.deepcopy(cw)
    for s, rows in cw2.trans.items():
        for p, opts in rows:
            for s2 in opts:
                if s2 != cw2.initial and cw2.trans.get(s2):
                    (p2, opts2), rest = cw2.trans[s2][0], cw2.trans[s2][1:]
                    cw2.trans[s2] = ((p2, tuple(opts2) + (cw2.initial,)),) + tuple(rest)
                    return cw2, s2
    raise RuntimeError("no edge to redirect")


def martian_dice_one_ray():
    """MARTIAN_DICE with ONE death-ray face instead of two (the constant
    cycle 002's 86% SELECT-axis result rests on). Every per-world invariant
    in ludus/bench/verify.py recomputes pots and counts from the state; none
    inspects the draw distribution. This world must therefore read
    verified_internally=True -- the instrument's own docstring predicts it,
    and this fixture turns the prediction into a row."""
    from ludus.bench import worlds as BW

    W = {"tank": 1, "ray": 1, "human": 1, "cow": 1, "chicken": 1}
    denom = sum(W.values())

    @functools.lru_cache(maxsize=None)
    def roll_dist(n: int):
        out = []
        for t in range(n + 1):
            for r in range(n - t + 1):
                for h in range(n - t - r + 1):
                    for c in range(n - t - r - h + 1):
                        ch = n - t - r - h - c
                        coeff = math.factorial(n) // (
                            math.factorial(t) * math.factorial(r) * math.factorial(h)
                            * math.factorial(c) * math.factorial(ch))
                        out.append((coeff * (W["ray"] ** r) / (denom ** n),
                                    (t, r, h, c, ch)))
        return out

    class MartianDiceOneRay(BW.MartianDice):
        name = "MARTIAN_DICE"          # same name so PER_WORLD dispatch applies

        def draws(self, s):
            return roll_dist(self.dice_left(s))

    return MartianDiceOneRay()


# ==========================================================================
# Arena leak fixtures: Kuhn poker variants that disclose the opponent's card
# ==========================================================================

def _arena():
    """ludus/arena modules import each other as siblings."""
    import pathlib
    p = str(pathlib.Path(__file__).resolve().parents[1] / "arena")
    if p not in sys.path:
        sys.path.insert(0, p)
    import worlds as AW                       # noqa: WPS433
    return AW


def kuhn_leak_named_key():
    """observation(0) gains a key literally called opponent_card. Both the
    key-name check in arena/verify.py [7] and the differential audit are
    expected to fire."""
    AW = _arena()

    class S(AW.KuhnState):
        def observation(self, player):
            o = super().observation(player)
            o["opponent_card"] = self.cards[1 - player]
            return o

    class W(AW.KuhnPoker):
        name = "KUHN_LEAK_NAMED_KEY"

        def new_initial_state(self, rng):
            return S(self)

    return W()


def kuhn_leak_innocuous_key():
    """observation(0) gains a key called tiebreak carrying the opponent's
    card. The key-name check cannot fire (no forbidden substring); the
    differential audit must."""
    AW = _arena()

    class S(AW.KuhnState):
        def observation(self, player):
            o = super().observation(player)
            o["tiebreak"] = self.cards[1 - player]
            return o

    class W(AW.KuhnPoker):
        name = "KUHN_LEAK_INNOCUOUS_KEY"

        def new_initial_state(self, rng):
            return S(self)

    return W()


def kuhn_leak_action_order():
    """The observation is clean; the ORDER of legal actions depends on the
    opponent's card. Only a channel-by-channel differential test sees it."""
    AW = _arena()

    class S(AW.KuhnState):
        def legal_actions(self, player=None):
            la = super().legal_actions(player)
            if la and player is not None and self.cards[1 - player] == 2:
                return list(reversed(la))
            return la

    class W(AW.KuhnPoker):
        name = "KUHN_LEAK_ACTION_ORDER"

        def new_initial_state(self, rng):
            return S(self)

    return W()


def kuhn_leak_public_state():
    """public_state() carries both cards, so serialize() and state_hash()
    move with the secret while observation() stays clean."""
    AW = _arena()

    class S(AW.KuhnState):
        def public_state(self):
            o = super().public_state()
            o["dealt"] = list(self.cards)
            return o

        def observation(self, player):
            o = AW.KuhnState.public_state(self)
            o["my_card"] = self.cards[player]
            return o

    class W(AW.KuhnPoker):
        name = "KUHN_LEAK_PUBLIC_STATE"

        def new_initial_state(self, rng):
            return S(self)

    return W()
