"""Compile a world once, then evaluate thousands of policies over the table.

The bench has to run policy evaluations in bulk: every circuit against every
world, re-run whenever either registry gains a member. Re-deriving a world's
transition structure inside each evaluation makes that quadratic in the expensive
part for no reason — Can't Stop spends almost all of its time enumerating dice
pairings, and it enumerates the same 126 rolls from the same states every single
time.

(The obvious shortcut of decorating `options` with `lru_cache` was tried first and
**measured slower** — Incan Gold went 4.1s -> 20.1s, Can't Stop 35.5s -> 59.2s.
Hashing large state tuples through a bounded cache costs more than recomputing
them. It is recorded here because the reflex to reach for `lru_cache` will recur.)

So the world is walked once into a flat table, and everything downstream —
exact solution, policy evaluation, circuits — reads only the table. Circuits
therefore never touch a game object at all, which is the property that makes them
transferable by construction: a circuit literally cannot express a game-specific
idea, because it cannot see one.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field

sys.setrecursionlimit(1_000_000)


@dataclass
class Compiled:
    name: str
    genre: str
    surface: str
    interfaces: tuple
    initial: object
    pot: dict = field(repr=False, default_factory=dict)
    forced: dict = field(repr=False, default_factory=dict)
    trans: dict = field(repr=False, default_factory=dict)   # s -> ((p, (opts...)), ...)
    cons: dict = field(repr=False, default_factory=dict)    # (s, s2) -> consumption
    n_states: int = 0

    def draws(self, s):
        return self.trans.get(s, ())


def compile_world(world, cap: int = 4_000_000) -> Compiled:
    cw = Compiled(world.name, world.genre, world.surface, world.interfaces,
                  world.initial())
    has_cons = hasattr(world, "consumption")
    stack = [world.initial()]
    seen = {world.initial()}
    while stack:
        s = stack.pop()
        cw.pot[s] = float(world.pot(s))
        cw.forced[s] = bool(world.forced_end(s))
        if cw.forced[s]:
            cw.trans[s] = ()
            continue
        rows = []
        for p, draw in world.draws(s):
            opts = tuple(world.options(s, draw))
            rows.append((p, opts))
            for s2 in opts:
                if has_cons:
                    cw.cons[(s, s2)] = float(world.consumption(s, s2))
                if s2 not in seen:
                    seen.add(s2)
                    if len(seen) > cap:
                        raise MemoryError(f"{world.name}: over {cap} states")
                    stack.append(s2)
        cw.trans[s] = tuple(rows)
    cw.n_states = len(seen)
    return cw


# ==========================================================================
# Exact solution and policy evaluation, both over the compiled table
# ==========================================================================

def solve(cw: Compiled):
    """V(s) = value of about-to-draw; W(s) = value of just-took-an-option."""
    V, W = {}, {}

    def w_val(s):
        r = W.get(s)
        if r is not None:
            return r
        W[s] = cw.pot[s] if cw.forced[s] else max(cw.pot[s], v_val(s))
        return W[s]

    def v_val(s):
        r = V.get(s)
        if r is not None:
            return r
        V[s] = 0.0
        total = 0.0
        for p, opts in cw.trans.get(s, ()):
            if not opts:
                continue
            total += p * max(w_val(x) for x in opts)
        V[s] = total
        return total

    ev = w_val(cw.initial) if False else v_val(cw.initial)
    return ev, V, W


def evaluate(cw: Compiled, select, stop) -> float:
    """Exact expected value of the policy (select, stop). No sampling."""
    memo = {}

    def w_val(s):
        if cw.forced[s]:
            return cw.pot[s]
        if stop(cw, s, select):
            return cw.pot[s]
        return v_val(s)

    def v_val(s):
        r = memo.get(s)
        if r is not None:
            return r
        memo[s] = 0.0
        total = 0.0
        for p, opts in cw.trans.get(s, ()):
            if not opts:
                continue
            total += p * w_val(select(cw, s, opts))
        memo[s] = total
        return total

    return v_val(cw.initial)
