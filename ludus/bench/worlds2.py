"""Batch 2 — worlds that isolate one measured property at a time.

Two hypotheses are live after cycle 003 and neither can be settled by adding
more games that happen to exist:

  w0001  GATING. Martian Dice is the only gated world in the bench (0.4272
         against ~0.0000 elsewhere) and it is also the only world where the
         minimise-consumption circuit r0011 collapses. One world is a
         coincidence, not a mechanism.
  r0003  TOTAL-LOSS PRECONDITION. The myopic stopping rule is at or near 1.0000
         in all four worlds, and every one of those worlds destroys the WHOLE pot
         on death. It has never met a world where loss is partial.

Both are confounded with everything else about Martian Dice and everything else
about push-your-luck. Charter v2 §34 says what to do: *generate worlds where the
candidate is essential, worlds where it is irrelevant, and worlds containing its
usual proxy without it.*

So this module supplies two things.

FOUNDRY — a synthetic family, parameterised so that **exactly one property moves
at a time**. Gate on/off with everything else identical. Ruin vs decay with
everything else identical. These are not games and are never reported as games;
they are the controls that let a property be attributed rather than merely
observed. Charter v1 §37's warning applies and is respected: a synthetic pass is
instrument calibration, not an architectural result.

REAL-DERIVED WORLDS — Lucky Numbers and Coloretto, because a control family that
only ever talks to itself proves nothing about games. Both are structurally
unlike everything already in the bench: Lucky Numbers has a live SELECT axis and
NO death at all, and Coloretto's loss is partial rather than total, which is the
precondition r0003 has never been tested against.

RULE PROVENANCE: the two real worlds are reconstructed from memory, HYPOTHESIZED,
and belong in `RULES_AUDIT.md`. The Foundry worlds have no provenance question
because they are not claims about anything published.
"""
from __future__ import annotations

import functools
import itertools

from ludus.bench.core import World


# ==========================================================================
# FOUNDRY — the synthetic control family
# ==========================================================================

#: Option archetypes: (pot gain, capacity cost, is_prerequisite)
#: `PREREQ` is the whole point of the gate axis: it costs capacity and pays
#: nothing, exactly like claiming rays in Martian Dice.
OPT_RICH = (2, 1, False)
OPT_CHEAP = (1, 0, False)
OPT_PREREQ = (0, 1, True)
#: DECOY: the best option by immediate pot and one of the worst by long-run value,
#: because it eats capacity. Its only job is to make a greedy selector and an
#: optimal selector DISAGREE without invoking the gate. That separation is what
#: the partner-dependence factorial needs: it lets the SELECT structure change
#: while the STOP structure (pot dynamics, death probability, horizon) stays
#: bit-for-bit identical.
OPT_DECOY = (3, 3, False)
ARCHETYPES = (OPT_RICH, OPT_CHEAP, OPT_PREREQ, OPT_DECOY)


class Foundry(World):
    """A synthetic accumulate-or-bank world with independently movable properties.

    State = (capacity_left, pot, prereq_claimed, draws_left).

    Axes, each variable with everything else held fixed:
      gate        terminal pot is 0 unless a prerequisite was ever claimed
      decay       fraction of pot retained on death (0.0 = ruin, as in every
                  world the bench has measured so far)
      arity       how many options a live draw offers (the SELECT axis width)
      capacity    how much irreversible capacity there is to spend
      horizon     how many draws the episode lasts
      p_bust      probability a draw offers nothing at all
    """

    rules_state = "SYNTHETIC"          # no provenance question; not a real game
    exact = True

    def __init__(self, gate=False, decay=0.0, arity=3, capacity=4, horizon=6,
                 p_bust=0.25, decoy=False):
        self.gate, self.decay = gate, float(decay)
        self.arity, self.capacity, self.horizon = arity, capacity, horizon
        self.p_bust = float(p_bust)
        self.decoy = bool(decoy)
        self.name = (f"FOUNDRY[gate={int(gate)},decay={decay:g},k={arity},"
                     f"cap={capacity},h={horizon}"
                     + (",decoy=1]" if decoy else "]"))
        self.genre = "synthetic control"
        self.surface = "no theme at all, deliberately"
        self.interfaces = ("STOP", "SELECT") if arity > 1 else ("STOP",)
        self.admission_question = (
            "isolates gate/decay from every other property so w0001 and r0003's "
            "total-loss precondition can be ATTRIBUTED, not merely observed")

    def initial(self):
        return (self.capacity, 0, 0, self.horizon)

    def pot(self, s) -> float:
        cap, pot, prereq, left = s
        if self.gate and not prereq:
            return 0.0
        return float(pot)

    def forced_end(self, s) -> bool:
        return s[3] <= 0

    def _pool(self):
        """Which archetypes exist in this world.

        RICH, CHEAP and PREREQ are ALWAYS present, exactly as in the construction
        frozen in `ludus/fossils/FOSSIL_r0003_2026-08-27.json`. Making PREREQ
        conditional on `gate` would have been tidier and would have silently
        changed every FOUNDRY number already recorded in that fossil, so the
        decoy is purely ADDITIVE: `decoy=False` reproduces the frozen worlds
        bit-for-bit.
        """
        pool = [0, 1, 2]
        if self.decoy:
            pool.append(3)
        return tuple(pool)

    def _offers(self, arity):
        """Every subset of the world's archetype pool of the given size."""
        pool = self._pool()
        return list(itertools.combinations(pool, min(arity, len(pool))))

    def draws(self, s):
        offers = self._offers(self.arity)
        live = (1.0 - self.p_bust) / len(offers)
        return [(self.p_bust, None)] + [(live, o) for o in offers]

    def options(self, s, draw):
        if draw is None:
            return []                                  # death
        cap, pot, prereq, left = s
        out = []
        for i in draw:
            gain, cost, is_pre = ARCHETYPES[i]
            if cost > cap:
                continue                               # unaffordable
            out.append((cap - cost, pot + gain, prereq or int(is_pre), left - 1))
        if not out:
            # capacity exhausted: the episode continues but nothing can be taken.
            out.append((cap, pot, prereq, left - 1))
        return out

    def consumption(self, s, s2) -> float:
        return (s[0] - s2[0]) / self.capacity if self.capacity else 0.0

    def death_value(self, s) -> float:
        """Retained value on death. The bench's solver treats death as 0, so a
        decay world is expressed by folding the retained fraction into the pot
        of a survivor branch instead — see `DecayFoundry`."""
        return self.decay * self.pot(s)


class DecayFoundry(Foundry):
    """Partial loss instead of ruin.

    The core interface has exactly one death semantics: an empty option list
    forfeits everything. Rather than widen the interface for one family -- which
    would be a patch, and would silently change the meaning of every world
    already measured -- decay is expressed WITHIN the existing interface: the
    death branch is replaced by a survivor branch that keeps `decay * pot` and
    ends the episode immediately.

    That is a faithful encoding of partial loss, and it is worth being explicit
    that it is an encoding. If r0003's behaviour differs here, the honest first
    question is whether the difference is about partial loss or about this
    encoding of it, and the FOUNDRY[decay=0] control answers exactly that: it is
    the same construction with the retained fraction set to zero, so it must
    reproduce the ruin world's numbers. If it does not, the encoding is the
    finding.
    """

    def __init__(self, decay=0.5, **kw):
        kw["decay"] = decay
        super().__init__(**kw)
        self.name = self.name.replace("FOUNDRY[", "FOUNDRY-DECAY[")

    def options(self, s, draw):
        if draw is None:
            cap, pot, prereq, left = s
            kept = int(self.decay * pot)
            return [(cap, kept, prereq, 0)]            # survives, banked, ended
        return super().options(s, draw)


# ==========================================================================
# LUCKY NUMBERS — a live SELECT axis with NO death anywhere
# ==========================================================================

#: 2x2 board, tiles 1..6, drawn WITHOUT replacement.
#: Two earlier sizings were measured and rejected, and the reason is worth
#: keeping because both looked obviously fine on paper:
#:   3x3 + without replacement -> the state must carry the set of tiles seen,
#:     multiplying the grid space by 2^9 (>2.4GB, still climbing).
#:   3x3 + WITH replacement    -> WORSE, not better: repeated values may sit
#:     in different rows and columns, so the grid alphabet stops being a
#:     permutation and the space explodes (>2.1GB).
#: The board shrinks; the property the world was admitted for -- a live
#: SELECT axis with no death anywhere -- is untouched.
LN_N = 2
LN_TILES = tuple(range(1, 7))


class LuckyNumbers(World):
    """Solitaire Lucky Numbers on a 3x3 grid with tiles 1..9.

    Rows and columns must both increase. A drawn tile may be placed on any legal
    empty cell, or discarded. Score is the number of tiles placed.

    Why it earns admission: **there is no death in this world at all.** Every
    circuit in the STOP registry was measured where continuing risks losing
    everything; here continuing risks nothing and the only cost is a wasted tile.
    It is also a pure SELECT world -- and SELECT circuits currently have ZERO
    untouched test worlds, which is the single largest hole in the ledger.
    """

    name = "LUCKY_NUMBERS"
    genre = "constrained placement"
    surface = "a small grid, numbered tiles, rows and columns that must ascend"
    interfaces = ("SELECT",)
    rules_state = "HYPOTHESIZED"
    exact = True
    admission_question = ("gives SELECT circuits their first untouched test world, "
                          "and the first world in the bench with NO death at all")

    #: SCOPE CUT, stated rather than hidden: tiles are drawn WITH replacement and
    #: the episode lasts a fixed number of draws. The real game draws without
    #: replacement, which would require the state to carry the set of tiles seen
    #: so far -- multiplying the grid space by 2^9 and pushing the world past
    #: exact solvability (measured: >2.4GB and still climbing before this cut).
    #: The property this world was ADMITTED for -- a live SELECT axis with no
    #: death anywhere -- is untouched by the change, and that is the test the cut
    #: has to pass: it may simplify anything except the reason the world is here.
    def initial(self):
        return ((0,) * (LN_N * LN_N), ())

    def _legal_cells(self, grid, v):
        out = []
        for i in range(LN_N):
            for j in range(LN_N):
                if grid[i * LN_N + j]:
                    continue
                ok = True
                for jj in range(LN_N):
                    x = grid[i * LN_N + jj]
                    if x and ((jj < j and x >= v) or (jj > j and x <= v)):
                        ok = False
                for ii in range(LN_N):
                    x = grid[ii * LN_N + j]
                    if x and ((ii < i and x >= v) or (ii > i and x <= v)):
                        ok = False
                if ok:
                    out.append(i * LN_N + j)
        return out

    def pot(self, s) -> float:
        return float(sum(1 for x in s[0] if x))

    def forced_end(self, s) -> bool:
        grid, drawn = s
        return len(drawn) >= len(LN_TILES) or all(grid)

    def draws(self, s):
        grid, drawn = s
        rem = [x for x in LN_TILES if x not in drawn]
        if not rem:
            return []
        p = 1.0 / len(rem)
        return [(p, x) for x in rem]

    def options(self, s, draw):
        grid, drawn = s
        nd = tuple(sorted(drawn + (draw,)))
        out = [(grid, nd)]                             # discard is always legal
        for c in self._legal_cells(grid, draw):
            g = list(grid)
            g[c] = draw
            out.append((tuple(g), nd))
        return out

    def consumption(self, s, s2) -> float:
        """A placed tile permanently spends a cell."""
        return (sum(1 for x in s2[0] if x) - sum(1 for x in s[0] if x)) / (LN_N * LN_N)


# ==========================================================================
# COLORETTO — loss is partial, not total
# ==========================================================================

CO_COLORS = 4
CO_PER_COLOR = 5
CO_ROWS = 2
CO_ROW_CAP = 3


class Coloretto(World):
    """Solitaire Coloretto core.

    Draw a card and add it to one of the open rows, or take a row and end the
    round. Scoring is the real game's: your three best colours score
    triangularly, every other colour scores triangularly NEGATIVE.

    Why it earns admission: **loss here is partial, not total.** Every world the
    bench has measured destroys the entire pot on death, and r0003 -- the one
    circuit with a passed prospective prediction -- has never been tested where
    that is untrue. Here the pot can DECLINE without ever being wiped out, which
    is the precondition r0003's registered scope explicitly says is untested.
    """

    name = "COLORETTO"
    genre = "set collection with negative scoring"
    surface = "chameleons, colour cards, and rows you may claim"
    interfaces = ("STOP", "SELECT")
    rules_state = "HYPOTHESIZED"
    exact = True
    admission_question = ("first world where loss is PARTIAL rather than total - "
                          "the precondition r0003's scope says is untested")

    def initial(self):
        return ((0,) * CO_COLORS, (0,) * (CO_ROWS * CO_COLORS))

    @staticmethod
    def _tri(n):
        return n * (n + 1) // 2

    def pot(self, s) -> float:
        held = sorted(s[0], reverse=True)
        return float(sum(self._tri(x) for x in held[:3])
                     - sum(self._tri(x) for x in held[3:]))

    def forced_end(self, s) -> bool:
        held, rows = s
        return sum(held) + sum(rows) >= CO_PER_COLOR * CO_COLORS or sum(held) >= 8

    def draws(self, s):
        held, rows = s
        rem = [CO_PER_COLOR - held[c] - sum(rows[r * CO_COLORS + c]
                                            for r in range(CO_ROWS))
               for c in range(CO_COLORS)]
        tot = sum(max(0, x) for x in rem)
        if tot <= 0:
            return []
        return [(max(0, rem[c]) / tot, c) for c in range(CO_COLORS)
                if rem[c] > 0]

    def options(self, s, draw):
        held, rows = s
        out = []
        for r in range(CO_ROWS):                        # add the card to a row
            if sum(rows[r * CO_COLORS:(r + 1) * CO_COLORS]) >= CO_ROW_CAP:
                continue
            nr = list(rows)
            nr[r * CO_COLORS + draw] += 1
            out.append((held, tuple(nr)))
        for r in range(CO_ROWS):                        # or claim a row
            if sum(rows[r * CO_COLORS:(r + 1) * CO_COLORS]) == 0:
                continue
            nh = list(held)
            nr = list(rows)
            for c in range(CO_COLORS):
                nh[c] += rows[r * CO_COLORS + c]
                nr[r * CO_COLORS + c] = 0
            out.append((tuple(nh), tuple(nr)))
        if not out:
            out.append((held, rows))
        return out

    def consumption(self, s, s2) -> float:
        return max(0.0, (sum(s2[0]) - sum(s[0])) / 8.0)


# ==========================================================================
# The generated batch
# ==========================================================================

def foundry_batch():
    """One property moves at a time. That is the whole design."""
    out = []
    for gate in (False, True):                          # the w0001 axis
        for k in (2, 3):                                # SELECT width
            for cap in (2, 4):                          # capacity pressure
                out.append(Foundry(gate=gate, arity=k, capacity=cap))
    for gate in (False, True):                          # the ruin/decay axis
        for d in (0.25, 0.5, 0.75):
            out.append(DecayFoundry(decay=d, gate=gate, arity=3, capacity=4))
    # ENCODING CHECK. DecayFoundry expresses partial loss by replacing the death
    # branch with a survivor branch that keeps `decay * pot`. At decay=0 that
    # construction must reproduce the plain ruin world EXACTLY. If it does not,
    # every decay result is measuring the encoding rather than partial loss.
    out.append(DecayFoundry(decay=0.0, gate=False, arity=3, capacity=4))
    return out


BATCH2 = foundry_batch() + [LuckyNumbers(), Coloretto()]
