"""LUDUS synthetic worlds — contamination-free by construction.

Three tiny two-player worlds, each with an EXACT solver. They exist so that the
attainable range of the measurement can be computed before any transfer claim is
made (`feedback_gate_must_be_shown_reachable`): the ground truth at every rung of
the ladder is produced by minimax over the full reachable state space, not by a
model and not by a heuristic.

Design constraints, all deliberate:

  * **Novel by construction.** No published game is reskinned here. That removes
    C001-C005 (rulebook / strategy-guide / title / component / edition leakage)
    from cycle 001 entirely rather than controlling for it. The cost is that
    these worlds are small; the benefit is that a ceiling reading is not
    confounded by memorised play.
  * **Perfect information, deterministic.** X (exogenous processes) is empty.
    Stochastic worlds come later; a ceiling measured against a noisy oracle is
    not a ceiling.
  * **Genuine interaction.** W1's ore stock, W2's shared edge set and W3's
    single prize queue each make one player's move change the other's option
    set. A world that decomposes into two independent single-agent problems
    measures planning, not strategy, and would have been the wrong instrument.
  * **Exactly solvable.** Every rung's answer is computed, so R2/R3 scoring
    involves no judge model.

Each world exposes the same interface so the ladder runner is world-agnostic:

    rules_text()            -> str    the complete laws of the world
    initial_state()         -> State
    legal_actions(s)        -> list[str]
    apply(s, a)             -> State
    is_terminal(s)          -> bool
    result(s)               -> int     final margin, positive = player A ahead
    render_state(s)         -> str     the state as the model sees it
    parse_state(txt)        -> State   inverse of render_state, for rung R1
"""
from __future__ import annotations

import functools
import re
from dataclasses import dataclass
from typing import Iterable


# --------------------------------------------------------------------------
# W1 — LOOM.  Resource conversion under a shared, depleting stock.
#   Strategic realms present: resource economy (conversion chain, opportunity
#   cost), temporal (fixed 6-move horizon), interaction (stock denial).
# --------------------------------------------------------------------------

LOOM_MOVES = 6
LOOM_STOCK = 12
LOOM_TRACK = 5


@dataclass(frozen=True)
class LoomState:
    ply: int          # 0..2*LOOM_MOVES-1 ; even plies are A's
    stock: int
    a: tuple          # (pos, dross, thread)
    b: tuple

    @property
    def to_move(self) -> str:
        return "A" if self.ply % 2 == 0 else "B"


class Loom:
    """LOOM, parameterised so the horizon can be swept.

    The sweep exists because "a one-ply heuristic already plays this perfectly"
    has two rival causes — the world has no strategic content, or the world is
    simply too short for lookahead to pay. Those are distinguished by varying
    the horizon and nothing else.
    """

    def __init__(self, moves: int = LOOM_MOVES, stock: int = LOOM_STOCK,
                 track: int = LOOM_TRACK):
        self.moves, self.stock0, self.track = moves, stock, track
        self.name = ("LOOM" if (moves, stock, track)
                     == (LOOM_MOVES, LOOM_STOCK, LOOM_TRACK)
                     else f"LOOM(m={moves},s={stock},t={track})")

    def rules_text(self) -> str:
        LOOM_MOVES, LOOM_STOCK, LOOM_TRACK = self.moves, self.stock0, self.track
        return f"""LOOM — complete rules.

Two players, A and B. A moves first. Players alternate. Each player takes
exactly {LOOM_MOVES} moves, then the game ends.

Each player privately owns three quantities, all starting at 0:
  RUNG   an integer from 0 to {LOOM_TRACK}
  DROSS  a non-negative integer
  THREAD a non-negative integer

There is one shared quantity, the STOCK, starting at {LOOM_STOCK}.

On your move you must choose exactly one of these four actions:

  DRAW    Requires STOCK >= 2. Removes 2 from the STOCK and adds 2 to your
          DROSS. (The STOCK is shared: what you take, the other player
          cannot take.)
  SPIN    Requires your DROSS >= 3. Removes 3 from your DROSS and adds 2 to
          your THREAD.
  CLIMB   Requires your THREAD >= 1 and your RUNG < {LOOM_TRACK}. Removes 1
          from your THREAD and adds 1 to your RUNG.
  WAIT    Always legal. Nothing changes. It still consumes one of your
          {LOOM_MOVES} moves.

Nothing is ever returned to the STOCK. DROSS spent on SPIN is destroyed.
THREAD spent on CLIMB is destroyed. RUNG never decreases.

When both players have taken all {LOOM_MOVES} moves, each player scores:

  SCORE = 5 * RUNG + THREAD

The MARGIN is A's SCORE minus B's SCORE. A is trying to make the MARGIN as
large as possible; B is trying to make it as small as possible (B may make it
negative)."""

    def initial_state(self) -> LoomState:
        return LoomState(ply=0, stock=self.stock0, a=(0, 0, 0), b=(0, 0, 0))

    def legal_actions(self, s: LoomState) -> list[str]:
        if self.is_terminal(s):
            return []
        me = s.a if s.to_move == "A" else s.b
        pos, dross, thread = me
        acts = ["WAIT"]
        if s.stock >= 2:
            acts.append("DRAW")
        if dross >= 3:
            acts.append("SPIN")
        if thread >= 1 and pos < self.track:
            acts.append("CLIMB")
        return sorted(acts)

    def apply(self, s: LoomState, a: str) -> LoomState:
        if a not in self.legal_actions(s):
            raise ValueError(f"illegal action {a!r} in {s}")
        pos, dross, thread = s.a if s.to_move == "A" else s.b
        stock = s.stock
        if a == "DRAW":
            stock -= 2
            dross += 2
        elif a == "SPIN":
            dross -= 3
            thread += 2
        elif a == "CLIMB":
            thread -= 1
            pos += 1
        me = (pos, dross, thread)
        if s.to_move == "A":
            return LoomState(s.ply + 1, stock, me, s.b)
        return LoomState(s.ply + 1, stock, s.a, me)

    def is_terminal(self, s: LoomState) -> bool:
        return s.ply >= 2 * self.moves

    def result(self, s: LoomState) -> int:
        sa = 5 * s.a[0] + s.a[2]
        sb = 5 * s.b[0] + s.b[2]
        return sa - sb

    def render_state(self, s: LoomState) -> str:
        return (f"STOCK={s.stock}\n"
                f"A: RUNG={s.a[0]} DROSS={s.a[1]} THREAD={s.a[2]} "
                f"MOVES_LEFT={self.moves - (s.ply + 1) // 2}\n"
                f"B: RUNG={s.b[0]} DROSS={s.b[1]} THREAD={s.b[2]} "
                f"MOVES_LEFT={self.moves - s.ply // 2}\n"
                f"TO_MOVE={s.to_move}")

    def state_signature(self, s: LoomState) -> str:
        """Canonical form used to score rung R1 (transition prediction)."""
        return (f"STOCK={s.stock};A={s.a[0]},{s.a[1]},{s.a[2]};"
                f"B={s.b[0]},{s.b[1]},{s.b[2]};TO_MOVE={s.to_move}")


# --------------------------------------------------------------------------
# W2 — WEIR.  Budgeted edge acquisition on a shared graph.
#   Strategic realms present: spatial control (connectivity, denial), resource
#   economy (a hard budget), interaction (every edge taken is an edge denied).
# --------------------------------------------------------------------------

WEIR_EDGES = [
    ("P", "Q", 2), ("P", "R", 3), ("Q", "S", 2), ("R", "S", 1),
    ("Q", "T", 4), ("S", "U", 3), ("T", "U", 2), ("R", "T", 3),
    ("S", "T", 1),
]
WEIR_BUDGET = 8
WEIR_A_ENDS = ("P", "U")
WEIR_B_ENDS = ("Q", "R")


@dataclass(frozen=True)
class WeirState:
    ply: int
    owner: tuple      # per-edge: 0 unclaimed, 1 A, 2 B
    ba: int
    bb: int
    yields: int = 0   # consecutive YIELDs; 2 ends the game

    @property
    def to_move(self) -> str:
        return "A" if self.ply % 2 == 0 else "B"


class Weir:
    name = "WEIR"

    def rules_text(self) -> str:
        lines = "\n".join(f"  {i}: {u}-{v}  cost {c}"
                          for i, (u, v, c) in enumerate(WEIR_EDGES))
        return f"""WEIR — complete rules.

Two players, A and B. A moves first. Players alternate moves.

There are six sites: P, Q, R, S, T, U.
There are nine links. Each link joins two sites and has a cost:

{lines}

Each player starts with a PURSE of {WEIR_BUDGET}.

On your move you must choose exactly one of:

  TAKE n   Requires link n to be unclaimed and its cost to be less than or
           equal to your current PURSE. You claim link n and subtract its
           cost from your PURSE. A claimed link belongs to you permanently;
           the other player can never claim it.
  YIELD    Always legal. You claim nothing.

The game ends immediately once two YIELDs are chosen in a row (one by each
player), or once no unclaimed link is affordable to either player. The
position states how many consecutive YIELDs have just been chosen; a TAKE
resets that count to 0.

At the end, each player scores:

  SCORE = 10 if that player owns a chain of their own links connecting their
          two goal sites, otherwise 0
        + that player's remaining PURSE

A's goal sites are {WEIR_A_ENDS[0]} and {WEIR_A_ENDS[1]}.
B's goal sites are {WEIR_B_ENDS[0]} and {WEIR_B_ENDS[1]}.
A chain may pass through any number of intermediate sites, but every link in
it must be owned by that player.

The MARGIN is A's SCORE minus B's SCORE. A maximises the MARGIN; B minimises
it."""

    def initial_state(self) -> WeirState:
        return WeirState(0, tuple([0] * len(WEIR_EDGES)), WEIR_BUDGET, WEIR_BUDGET)

    def _purse(self, s: WeirState) -> int:
        return s.ba if s.to_move == "A" else s.bb

    def _affordable(self, s: WeirState, purse: int) -> list[int]:
        return [i for i, (_, _, c) in enumerate(WEIR_EDGES)
                if s.owner[i] == 0 and c <= purse]

    def legal_actions(self, s: WeirState) -> list[str]:
        if self.is_terminal(s):
            return []
        acts = [f"TAKE {i}" for i in self._affordable(s, self._purse(s))]
        return acts + ["YIELD"]

    def apply(self, s: WeirState, a: str) -> WeirState:
        if a not in self.legal_actions(s):
            raise ValueError(f"illegal action {a!r}")
        if a == "YIELD":
            return WeirState(s.ply + 1, s.owner, s.ba, s.bb, s.yields + 1)
        i = int(a.split()[1])
        owner = list(s.owner)
        owner[i] = 1 if s.to_move == "A" else 2
        cost = WEIR_EDGES[i][2]
        ba, bb = (s.ba - cost, s.bb) if s.to_move == "A" else (s.ba, s.bb - cost)
        return WeirState(s.ply + 1, tuple(owner), ba, bb, 0)

    def is_terminal(self, s: WeirState) -> bool:
        # Two YIELDs in a row end it. This is a real decision, not bookkeeping:
        # a player who is ahead can close the game while links remain.
        if s.yields >= 2:
            return True
        # No affordable unclaimed link for EITHER player -> nothing can change.
        none_a = not [i for i, (_, _, c) in enumerate(WEIR_EDGES)
                      if s.owner[i] == 0 and c <= s.ba]
        none_b = not [i for i, (_, _, c) in enumerate(WEIR_EDGES)
                      if s.owner[i] == 0 and c <= s.bb]
        if none_a and none_b:
            return True
        return s.ply >= 2 * len(WEIR_EDGES) + 2

    def _connected(self, owner: tuple, mark: int, ends: tuple) -> bool:
        adj: dict[str, list[str]] = {}
        for i, (u, v, _) in enumerate(WEIR_EDGES):
            if owner[i] == mark:
                adj.setdefault(u, []).append(v)
                adj.setdefault(v, []).append(u)
        src, dst = ends
        seen, stack = {src}, [src]
        while stack:
            n = stack.pop()
            if n == dst:
                return True
            for m in adj.get(n, []):
                if m not in seen:
                    seen.add(m)
                    stack.append(m)
        return False

    def result(self, s: WeirState) -> int:
        sa = (10 if self._connected(s.owner, 1, WEIR_A_ENDS) else 0) + s.ba
        sb = (10 if self._connected(s.owner, 2, WEIR_B_ENDS) else 0) + s.bb
        return sa - sb

    def render_state(self, s: WeirState) -> str:
        who = {0: "unclaimed", 1: "A", 2: "B"}
        links = "\n".join(
            f"  {i}: {u}-{v} cost {c} -> {who[s.owner[i]]}"
            for i, (u, v, c) in enumerate(WEIR_EDGES))
        return (f"LINKS:\n{links}\nA_PURSE={s.ba}\nB_PURSE={s.bb}\n"
                f"CONSECUTIVE_YIELDS={s.yields}\nTO_MOVE={s.to_move}")

    def state_signature(self, s: WeirState) -> str:
        return (f"OWNER={''.join(str(x) for x in s.owner)};"
                f"A_PURSE={s.ba};B_PURSE={s.bb};YIELDS={s.yields};"
                f"TO_MOVE={s.to_move}")


# --------------------------------------------------------------------------
# W3 — TITHE.  A descending-price queue with a shared, irreversible order.
#   Strategic realms present: temporal (tempo, timing windows), auction,
#   action economy, interaction (one queue, two claimants).
# --------------------------------------------------------------------------

TITHE_PRIZES = (3, 1, 4, 1, 5)
TITHE_START_PRICE = 4
TITHE_PURSE = 7


@dataclass(frozen=True)
class TitheState:
    ply: int
    idx: int          # which prize is on offer
    price: int
    ta: int           # A's taken total
    tb: int
    pa: int           # A's purse
    pb: int

    @property
    def to_move(self) -> str:
        return "A" if self.ply % 2 == 0 else "B"


class Tithe:
    name = "TITHE"

    def rules_text(self) -> str:
        return f"""TITHE — complete rules.

Two players, A and B. A moves first. Players alternate moves.

There is a queue of {len(TITHE_PRIZES)} offerings with these worths, offered
strictly in this order and never reordered:

  {', '.join(str(v) for v in TITHE_PRIZES)}

Each player starts with a PURSE of {TITHE_PURSE}.
Exactly one offering is on offer at a time. Its PRICE starts at
{TITHE_START_PRICE} each time a new offering comes up.

On your move you must choose exactly one of:

  CLAIM    Requires PRICE <= your PURSE. You subtract PRICE from your PURSE
           and add the offering's WORTH to your TAKINGS. The next offering in
           the queue comes on offer at PRICE {TITHE_START_PRICE}.
  DECLINE  Always legal.
             - If the PRICE is greater than 1, the PRICE drops by 1 and the
               same offering stays on offer.
             - If the PRICE is already 1, the offering is discarded, nobody
               takes it, and the next offering in the queue comes on offer at
               PRICE {TITHE_START_PRICE}.

The game ends when the queue is exhausted.

At the end, each player scores:

  SCORE = 2 * TAKINGS + PURSE

The MARGIN is A's SCORE minus B's SCORE. A maximises the MARGIN; B minimises
it."""

    def initial_state(self) -> TitheState:
        return TitheState(0, 0, TITHE_START_PRICE, 0, 0, TITHE_PURSE, TITHE_PURSE)

    def legal_actions(self, s: TitheState) -> list[str]:
        if self.is_terminal(s):
            return []
        purse = s.pa if s.to_move == "A" else s.pb
        acts = ["DECLINE"]
        if s.price <= purse:
            acts.append("CLAIM")
        return sorted(acts)

    def apply(self, s: TitheState, a: str) -> TitheState:
        if a not in self.legal_actions(s):
            raise ValueError(f"illegal action {a!r}")
        worth = TITHE_PRIZES[s.idx]
        if a == "CLAIM":
            if s.to_move == "A":
                pa, ta, pb, tb = s.pa - s.price, s.ta + worth, s.pb, s.tb
            else:
                pa, ta, pb, tb = s.pa, s.ta, s.pb - s.price, s.tb + worth
            return TitheState(s.ply + 1, s.idx + 1, TITHE_START_PRICE,
                              ta, tb, pa, pb)
        if s.price == 1:  # DECLINE at the floor discards the offering
            return TitheState(s.ply + 1, s.idx + 1, TITHE_START_PRICE,
                              s.ta, s.tb, s.pa, s.pb)
        return TitheState(s.ply + 1, s.idx, s.price - 1,
                          s.ta, s.tb, s.pa, s.pb)

    def is_terminal(self, s: TitheState) -> bool:
        return s.idx >= len(TITHE_PRIZES)

    def result(self, s: TitheState) -> int:
        return (2 * s.ta + s.pa) - (2 * s.tb + s.pb)

    def render_state(self, s: TitheState) -> str:
        rem = ", ".join(str(v) for v in TITHE_PRIZES[s.idx + 1:]) or "(none)"
        return (f"ON_OFFER_WORTH={TITHE_PRIZES[s.idx]}\nPRICE={s.price}\n"
                f"STILL_TO_COME={rem}\n"
                f"A: TAKINGS={s.ta} PURSE={s.pa}\n"
                f"B: TAKINGS={s.tb} PURSE={s.pb}\nTO_MOVE={s.to_move}")

    def state_signature(self, s: TitheState) -> str:
        return (f"IDX={s.idx};PRICE={s.price};"
                f"A={s.ta},{s.pa};B={s.tb},{s.pb};TO_MOVE={s.to_move}")


WORLDS = {"LOOM": Loom(), "WEIR": Weir(), "TITHE": Tithe()}


# --------------------------------------------------------------------------
# Exact solver.  Every rung's ground truth comes from here.
# --------------------------------------------------------------------------

def solve(world, s) -> int:
    """Exact minimax margin under optimal play from s. A maximises."""
    memo: dict = {}

    def rec(st):
        if world.is_terminal(st):
            return world.result(st)
        key = st
        if key in memo:
            return memo[key]
        vals = [rec(world.apply(st, a)) for a in world.legal_actions(st)]
        v = max(vals) if st.to_move == "A" else min(vals)
        memo[key] = v
        return v

    return rec(s)


def optimal_actions(world, s) -> list[str]:
    """Every action attaining the game value. Ties all count as correct."""
    acts = world.legal_actions(s)
    vals = {a: solve(world, world.apply(s, a)) for a in acts}
    best = max(vals.values()) if s.to_move == "A" else min(vals.values())
    return sorted(a for a, v in vals.items() if v == best)


def reachable_states(world, max_states: int = 200_000) -> list:
    """Breadth-first enumeration of the reachable non-terminal state set."""
    seen, out, frontier = {world.initial_state()}, [], [world.initial_state()]
    while frontier and len(seen) < max_states:
        nxt = []
        for st in frontier:
            if world.is_terminal(st):
                continue
            out.append(st)
            for a in world.legal_actions(st):
                t = world.apply(st, a)
                if t not in seen:
                    seen.add(t)
                    nxt.append(t)
        frontier = nxt
    return out
