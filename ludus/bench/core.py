"""LUDUS bench — one world interface, one exact solver, one transfer matrix.

The bet this bench is built on:

    **Transfer is mediated by INTERFACES, not by games or genres.**

A genre label ("push your luck", "engine builder", "worker placement") groups
games by how they feel at the table. Cycle 002 showed that can group them by
their shared *easy* part: one untuned stopping rule was within 1.3% of optimal in
two very different-looking worlds, while 86% of the harder world's difficulty sat
on an axis the label does not name.

So the bench does not organise by genre. It organises by the **decision
interfaces** a world exposes. A circuit is a policy written *only* against an
interface, which makes it transplantable by construction to every world exposing
that interface. Transfer then stops being a yes/no question and becomes a
measurement: **how much of optimal value does this circuit RETAIN over there?**

One interface covers every world in the bench so far:

    initial()               -> S            starting state of a scoring episode
    draws(s)                -> [(p, draw)]  exogenous outcome (cards, dice, deck)
    options(s, draw)        -> [S]          player's choices after seeing it;
                                            an EMPTY list is death - the pot is lost
    pot(s)                  -> float        value banked if you stop here
    forced_end(s)           -> bool         no further continuation is legal

Two decision axes fall out of it, and they are measured separately because
cycle 002 proved they can carry wildly different amounts of a world's difficulty:

    SELECT axis   which option to take after the draw
    STOP axis     whether to bank after taking it

Exact value, for worlds small enough to enumerate:

    V(s)   = sum_draw p * max_{s2 in options(s,draw)} W(s2)      (no options -> 0)
    W(s2)  = pot(s2)                     if forced_end(s2)
           = max(pot(s2), V(s2))         otherwise

`V` is the value of *about to draw*; `W` is the value of *having just taken an
option and now choosing whether to bank*. Every number this bench reports about a
tractable world is exact arithmetic over that recursion, not a sample.
"""
from __future__ import annotations

import collections
import functools
import json
import math
import pathlib
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ludus" / "ledgers"
ATLAS = ROOT / "ludus" / "atlas"

sys.setrecursionlimit(100_000)


# ==========================================================================
# World interface
# ==========================================================================

class World:
    """Subclasses implement the five methods in the module docstring.

    `interfaces` declares which decision axes are live. A world whose every draw
    admits at most one option has no SELECT axis, and no select circuit will be
    scored against it -- that is a property of the world, recorded, not a gap.
    """

    name: str = "UNNAMED"
    genre: str = "unclassified"          # the human label, kept but never trusted
    surface: str = ""                    # what it looks like at the table
    interfaces: tuple = ("STOP",)
    rules_state: str = "HYPOTHESIZED"    # v1 §8 epistemic state
    exact: bool = True                   # is the state space enumerable?

    def initial(self): raise NotImplementedError
    def draws(self, s): raise NotImplementedError
    def options(self, s, draw): raise NotImplementedError
    def pot(self, s) -> float: raise NotImplementedError
    def forced_end(self, s) -> bool: raise NotImplementedError

    # -- optional descriptive hooks, used by the atlas ---------------------
    def option_features(self, s, draw, s2) -> dict:
        """Interface-level facts about an option, for circuits to read.

        Deliberately thin. A circuit that needs game-specific knowledge to work
        is not a transferable circuit, so the vocabulary here stays small on
        purpose: how much does this option bank, and how much does it consume?
        """
        return {"pot_after": self.pot(s2), "pot_gain": self.pot(s2) - self.pot(s)}


DEATH = None


# ==========================================================================
# Exact solution
# ==========================================================================

@dataclass
class Solution:
    world: str
    optimal_ev: float
    n_states: int
    V: dict = field(repr=False, default_factory=dict)
    W: dict = field(repr=False, default_factory=dict)


def solve(world: World, cap: int = 4_000_000) -> Solution:
    """Exact backward induction over the reachable state graph."""
    V: dict = {}
    W: dict = {}

    def w_val(s2):
        if s2 in W:
            return W[s2]
        if world.forced_end(s2):
            W[s2] = float(world.pot(s2))
        else:
            W[s2] = max(float(world.pot(s2)), v_val(s2))
        return W[s2]

    def v_val(s):
        if s in V:
            return V[s]
        if len(V) > cap:
            raise MemoryError(f"{world.name}: exceeded {cap} states")
        V[s] = 0.0                       # cycle guard; the graph is a DAG in practice
        total = 0.0
        for p, draw in world.draws(s):
            opts = world.options(s, draw)
            if not opts:
                continue                 # death contributes 0
            total += p * max(w_val(s2) for s2 in opts)
        V[s] = total
        return total

    ev = v_val(world.initial())
    return Solution(world.name, ev, len(V), V, W)


# ==========================================================================
# Circuits — policies written against an interface, not against a game
# ==========================================================================

CIRCUITS: dict = {}


def circuit(rid: str, axis: str, doc: str):
    """Register a reusable reasoning circuit under its ugly identifier."""
    def deco(fn):
        CIRCUITS[rid] = {"id": rid, "axis": axis, "doc": doc, "fn": fn,
                         "name": fn.__name__}
        fn.rid, fn.axis = rid, axis
        return fn
    return deco


# ---- SELECT circuits: choose among the options a draw made available -------

@circuit("r0010", "SELECT", "take the option that banks the most right now")
def select_greedy_pot(world, s, draw, opts):
    return max(opts, key=lambda s2: world.pot(s2))


@circuit("r0011", "SELECT", "take the option that consumes the least future capacity, "
                            "breaking ties toward immediate pot")
def select_min_consumption(world, s, draw, opts):
    return max(opts, key=lambda s2: (-_consumed(world, s, s2), world.pot(s2)))


@circuit("r0012", "SELECT", "one-ply lookahead: take the option with the best "
                            "expected value of ONE further draw under greedy play")
def select_one_ply(world, s, draw, opts):
    return max(opts, key=lambda s2: _one_draw_ev(world, s2))


@circuit("r0013", "SELECT", "take the first option in the world's own enumeration "
                            "order (a null circuit: it reads nothing)")
def select_null(world, s, draw, opts):
    return opts[0]


def _consumed(world, s, s2):
    """Interface-level proxy for irreversible capacity spent by an option."""
    try:
        return world.consumption(s, s2)
    except AttributeError:
        return 0.0


def _one_draw_ev(world, s2):
    if world.forced_end(s2):
        return float(world.pot(s2))
    total = 0.0
    for p, draw in world.draws(s2):
        opts = world.options(s2, draw)
        if not opts:
            continue
        total += p * max(float(world.pot(x)) for x in opts)
    return total


# ---- STOP circuits: bank, or expose the pot to another draw ---------------

@circuit("r0003", "STOP", "myopic one-step rule: stop iff P(death) * pot >= "
                          "E[immediate gain]. Cycle 002's transferring circuit.")
def stop_myopic(world, s2, select):
    if world.forced_end(s2):
        return True
    pot = float(world.pot(s2))
    p_dead, e_gain = 0.0, 0.0
    for p, draw in world.draws(s2):
        opts = world.options(s2, draw)
        if not opts:
            p_dead += p
            continue
        nxt = select(world, s2, draw, opts)
        e_gain += p * (float(world.pot(nxt)) - pot)
    return not (e_gain > p_dead * pot)


@circuit("r0004", "STOP", "never bank voluntarily; ride every episode to its "
                          "forced end or death (a floor circuit)")
def stop_never(world, s2, select):
    return world.forced_end(s2)


@circuit("r0005", "STOP", "bank at the first opportunity (a floor circuit)")
def stop_always(world, s2, select):
    return True


def stop_threshold(T: float):
    """Bank once the pot reaches T. Parameterised, so it is FITTED per world --
    the strongest possible per-world cheap baseline and therefore the right
    thing for a transferable circuit to have to beat."""
    def f(world, s2, select):
        return world.forced_end(s2) or float(world.pot(s2)) >= T
    f.rid, f.axis = f"r0006[T={T}]", "STOP"
    return f


@circuit("r0007", "STOP", "survival-rate rule: stop iff the chance of surviving "
                          "one more draw falls below a fixed 1/2")
def stop_survival_half(world, s2, select):
    if world.forced_end(s2):
        return True
    p_dead = 0.0
    for p, draw in world.draws(s2):
        if not world.options(s2, draw):
            p_dead += p
    return p_dead >= 0.5


# ==========================================================================
# Exact policy evaluation
# ==========================================================================

def evaluate(world: World, select, stop, cap: int = 4_000_000) -> float:
    """Exact expected value of the policy (select, stop). No sampling."""
    memo: dict = {}

    def w_val(s2):
        if world.forced_end(s2):
            return float(world.pot(s2))
        if stop(world, s2, select):
            return float(world.pot(s2))
        return v_val(s2)

    def v_val(s):
        if s in memo:
            return memo[s]
        if len(memo) > cap:
            raise MemoryError(f"{world.name}: policy eval exceeded {cap} states")
        memo[s] = 0.0
        total = 0.0
        for p, draw in world.draws(s):
            opts = world.options(s, draw)
            if not opts:
                continue
            total += p * w_val(select(world, s, draw, opts))
        memo[s] = total
        return total

    return v_val(world.initial())


def optimal_select(sol: Solution):
    """The exact optimal SELECT rule, read off the solved table."""
    def f(world, s, draw, opts):
        return max(opts, key=lambda s2: sol.W.get(s2, float(world.pot(s2))))
    f.rid, f.axis = "OPTIMAL", "SELECT"
    return f


def optimal_stop(sol: Solution):
    """The exact optimal STOP rule, read off the solved table.

    NOTE, and it is not a footnote: this rule is optimal *given optimal
    continuation*. Bolted onto a cheap SELECT circuit it is mismatched and can
    score slightly WORSE than a myopic stopper that at least evaluates the
    continuation it will actually receive. Cycle 002 measured exactly that
    (-0.0005 on Martian Dice). An ablation that swaps one component of a policy
    for a component optimised against a different partner is not a clean
    decomposition, and the bench reports it rather than smoothing it.
    """
    def f(world, s2, select):
        if world.forced_end(s2):
            return True
        return float(world.pot(s2)) >= sol.V.get(s2, 0.0)
    f.rid, f.axis = "OPTIMAL", "STOP"
    return f
