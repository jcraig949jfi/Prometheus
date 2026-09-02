"""Bench worlds. Every one implements the single interface in `core.World`.

Four of charter v2 §17's five nominated stochastic-stopping worlds are here
(Piraten Kapern is not yet built). They are deliberately unlike each other at the
surface — a depleting card deck, thirteen dice with a satisfiability constraint,
an expedition deck with paired hazards, and a dice-race on eleven columns of
different lengths — while all four expose the same STOP interface. That is the
setup charter §22 calls the critical cell: different surface, candidate-same
mechanism.

RULE PROVENANCE. Every rule here is reconstructed from memory; no rulebook was
consulted. All four worlds carry `rules_state = "HYPOTHESIZED"`. Charter v2 §4
makes the operator the instrument for this: fabricated rules, impossible moves
and missing mechanics are cheap for a human who knows the game to spot.
`ludus/bench/RULES_AUDIT.md` is the sheet. Rules audit blocks the PROMOTION of a
verdict, not the running of the bench.

SOLITAIRE SCOPE. All four are single-player, isolating the stopping computation
from opponent interaction. For Incan Gold that is a severe cut and it is stated
as such: the whole character of the real game is that other players leaving
changes your split.
"""
from __future__ import annotations

import collections
import functools
import itertools
import math

from ludus.bench.core import World


# ==========================================================================
# FLIP 7 — a depleting deck where the danger is what you already hold
# ==========================================================================

F7_COUNTS = {0: 1, **{r: r for r in range(1, 13)}}
F7_TOTAL = sum(F7_COUNTS.values())


class Flip7(World):
    name = "FLIP7"
    genre = "push-your-luck / set collection"
    surface = "cards, numbers, a deck that depletes as you draw"
    interfaces = ("STOP",)
    exact = True

    BONUS, BONUS_AT = 15, 7

    def initial(self):
        return frozenset()

    def pot(self, s) -> float:
        return float(sum(s) + (self.BONUS if len(s) >= self.BONUS_AT else 0))

    def forced_end(self, s) -> bool:
        return len(s) >= self.BONUS_AT or len(s) == len(F7_COUNTS)

    def draws(self, s):
        n = F7_TOTAL - len(s)
        if n <= 0:
            return []
        out = []
        for r, c in F7_COUNTS.items():
            rem = c - 1 if r in s else c
            if rem:
                out.append((rem / n, r))
        return out

    def options(self, s, draw):
        if draw in s:
            return []                        # a duplicate busts the round
        return [s | {draw}]


# ==========================================================================
# INCAN GOLD — an expedition deck where the danger is a repeated hazard
# ==========================================================================

IG_TREASURES = (1, 2, 3, 4, 5, 5, 7, 7, 9, 11, 11, 13, 14, 15, 17)
IG_TOTAL = sum(IG_TREASURES)
IG_HAZARD_TYPES = 5
IG_HAZARD_COPIES = 3


class IncanGold(World):
    """State = (remaining treasure multiset, bitmask of hazard types seen once).

    The pot is implied: everything drawn is everything not remaining. Remaining
    hazards of a type are implied too, since a second copy ends the round, so a
    type is drawn zero or one times before the episode is over.
    """

    name = "INCAN_GOLD"
    genre = "push-your-luck / press-your-luck"
    surface = "an expedition deck, temples, gems, and paired hazards"
    interfaces = ("STOP",)
    exact = True

    def initial(self):
        return (IG_TREASURES, 0)

    def pot(self, s) -> float:
        return float(IG_TOTAL - sum(s[0]))

    def forced_end(self, s) -> bool:
        rem, mask = s
        haz = sum(IG_HAZARD_COPIES - ((mask >> t) & 1) for t in range(IG_HAZARD_TYPES))
        return len(rem) + haz == 0

    def draws(self, s):
        rem, mask = s
        counts = collections.Counter(rem)
        haz = {t: IG_HAZARD_COPIES - ((mask >> t) & 1) for t in range(IG_HAZARD_TYPES)}
        n = len(rem) + sum(haz.values())
        if n == 0:
            return []
        out = [(c / n, ("T", v)) for v, c in counts.items()]
        out += [(k / n, ("H", t)) for t, k in haz.items() if k]
        return out

    def options(self, s, draw):
        rem, mask = s
        kind, x = draw
        if kind == "T":
            lst = list(rem)
            lst.remove(x)
            return [(tuple(lst), mask)]
        if (mask >> x) & 1:
            return []                        # second hazard of a type: round lost
        return [(rem, mask | (1 << x))]


# ==========================================================================
# MARTIAN DICE — a SELECT axis under a satisfiability constraint
# ==========================================================================

MD_DICE = 13
MD_W = {"tank": 1, "ray": 2, "human": 1, "cow": 1, "chicken": 1}
MD_DENOM = sum(MD_W.values())
MD_IDX = {"ray": 1, "human": 2, "cow": 3, "chicken": 4}
MD_SET_BONUS = 3


@functools.lru_cache(maxsize=None)
def md_roll_dist(n: int):
    out = []
    for t in range(n + 1):
        for r in range(n - t + 1):
            for h in range(n - t - r + 1):
                for c in range(n - t - r - h + 1):
                    ch = n - t - r - h - c
                    coeff = math.factorial(n) // (
                        math.factorial(t) * math.factorial(r) * math.factorial(h)
                        * math.factorial(c) * math.factorial(ch))
                    w = MD_W["ray"] ** r
                    out.append((coeff * w / (MD_DENOM ** n), (t, r, h, c, ch)))
    return out


class MartianDice(World):
    """State = (tanks, rays, humans, cows, chickens) set aside.

    The "which symbols have already been claimed" mask is redundant with the
    counts: a symbol can only be claimed if it was rolled, so a claimed symbol
    always has count >= 1. That collapse is what makes the world exactly
    solvable in a few thousand states.
    """

    name = "MARTIAN_DICE"
    genre = "push-your-luck / dice"
    surface = "thirteen dice, flying saucers, tanks, and abducted livestock"
    interfaces = ("STOP", "SELECT")
    exact = True

    def initial(self):
        return (0, 0, 0, 0, 0)

    def dice_left(self, s) -> int:
        return MD_DICE - sum(s)

    def pot(self, s) -> float:
        tanks, rays, h, c, ch = s
        if rays < tanks:
            return 0.0                       # the death rays must beat the tanks
        base = h + c + ch
        if h and c and ch:
            base += MD_SET_BONUS
        return float(base)

    def forced_end(self, s) -> bool:
        return self.dice_left(s) == 0

    def draws(self, s):
        return md_roll_dist(self.dice_left(s))

    def options(self, s, draw):
        t, r, h, c, ch = draw
        base = (s[0] + t, s[1], s[2], s[3], s[4])
        out = []
        for sym, got in (("ray", r), ("human", h), ("cow", c), ("chicken", ch)):
            if got == 0 or base[MD_IDX[sym]] > 0:
                continue                     # never rolled, or already claimed
            nxt = list(base)
            nxt[MD_IDX[sym]] += got
            out.append(tuple(nxt))
        return out

    def consumption(self, s, s2) -> float:
        """Claiming a symbol permanently spends one of four claim slots AND the
        dice that showed it. Expressed at the interface as fraction of the dice
        pool consumed, so a select circuit can read it without knowing the game."""
        return (sum(s2) - sum(s)) / MD_DICE


# ==========================================================================
# CAN'T STOP — a SELECT axis that is spatial and racing, not set-collection
# ==========================================================================

CS_HEIGHTS = {2: 3, 3: 5, 4: 7, 5: 9, 6: 11, 7: 13, 8: 11, 9: 9, 10: 7, 11: 5, 12: 3}
CS_RUNNERS = 3


@functools.lru_cache(maxsize=None)
def cs_roll_dist():
    """The 126 distinct sorted 4d6 rolls with their probabilities."""
    cnt = collections.Counter(tuple(sorted(r)) for r in itertools.product(range(1, 7), repeat=4))
    tot = sum(cnt.values())
    return [(c / tot, roll) for roll, c in sorted(cnt.items())]


CS_PAIRINGS = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))


class CantStop(World):
    """Solitaire single turn. State = sorted tuple of (column, steps advanced).

    POT IS A MODELLING CHOICE, flagged as such: progress is valued as the sum of
    fraction-of-column-completed. Counting raw steps would systematically
    undervalue the short outer columns (three steps claims column 2, thirteen
    claims column 7), which would bias every stopping circuit toward the middle
    of the board for a reason that is an artefact of the metric rather than of
    the game.
    """

    name = "CANT_STOP"
    genre = "push-your-luck / dice race"
    surface = "four dice, eleven columns of unequal length, three white runners"
    interfaces = ("STOP", "SELECT")
    exact = True

    def initial(self):
        return ()

    def pot(self, s) -> float:
        return float(sum(steps / CS_HEIGHTS[col] for col, steps in s))

    def forced_end(self, s) -> bool:
        return len(s) == CS_RUNNERS and all(st >= CS_HEIGHTS[c] for c, st in s)

    def draws(self, s):
        return cs_roll_dist()

    @staticmethod
    def _advance(state, col):
        d = dict(state)
        if col in d:
            if d[col] >= CS_HEIGHTS[col]:
                return None                  # column already topped out
            d[col] += 1
        else:
            if len(d) >= CS_RUNNERS:
                return None                  # no free runner
            d[col] = 1
        return tuple(sorted(d.items()))

    def options(self, s, draw):
        out = set()
        for (i, j), (k, m) in CS_PAIRINGS:
            a, b = draw[i] + draw[j], draw[k] + draw[m]
            both = False
            for first, second in ((a, b), (b, a)):
                mid = self._advance(s, first)
                if mid is None:
                    continue
                end = self._advance(mid, second)
                if end is not None:
                    out.add(end)
                    both = True
            if both:
                continue                     # the rules force using both sums
            for only in (a, b):
                one = self._advance(s, only)
                if one is not None:
                    out.add(one)
        return sorted(out)

    def consumption(self, s, s2) -> float:
        """A newly opened column spends one of three runners permanently."""
        return (len(s2) - len(s)) / CS_RUNNERS


BATCH1 = [Flip7(), IncanGold(), MartianDice(), CantStop()]


def _all():
    """Batch 2 is imported lazily so a failure there cannot take batch 1 down."""
    worlds = list(BATCH1)
    try:
        from ludus.bench.worlds2 import BATCH2
        worlds += list(BATCH2)
    except Exception as exc:                            # noqa: BLE001
        print(f"[worlds] batch 2 unavailable: {type(exc).__name__}: {exc}")
    return worlds


ALL_WORLDS = _all()
WORLD_BY_NAME = {w.name: w for w in ALL_WORLDS}
