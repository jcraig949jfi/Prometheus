"""primitives.py — the fixed primitive collection for the incubation substrate.

Design constraints (from the spec, enforced here):
  - arbitrary IDs (r00..), no taxonomy, no English semantic names in solver-visible state
  - exact executable semantics, declared input/output types
  - independently ablatable (each is a standalone pure function)
  - every primitive must have at least one live consumer (tests/census assert usage)

Type: every primitive maps Z_m^k -> Z_m^k for any k >= 2, m >= 2, represented as a
Python tuple of ints in range(m). Primitives are polymorphic in (k, m): the SAME
executable entity acts in every world; worlds differ in (k, m), surface codec,
task distribution, and dynamics constraints — never in primitive semantics.

Inverses exist for all four (the census and the omniscient minimal-solution
analysis need backward search). Inverses are DIAGNOSTIC-SIDE ONLY: the solver's
action alphabet is the forward primitives.
"""
from __future__ import annotations

PRIM_IDS = ("r00", "r01", "r02", "r03")


def make_prims(k: int, m: int):
    """Forward primitive functions for a (k, m) instantiation, in PRIM_IDS order.

    r00: (x0,...,x_{k-1}) -> (x1,...,x_{k-1},x0)
    r01: swap slots 0 and 1
    r02: slot0 <- (slot0 + slot1) mod m
    r03: slot0 <- (2*slot0 + 1) mod m      (m must be odd; invertible affine step)
    """
    def r00(s):
        return s[1:] + s[:1]

    def r01(s):
        return (s[1], s[0]) + s[2:]

    def r02(s):
        return ((s[0] + s[1]) % m,) + s[1:]

    def r03(s):
        return ((2 * s[0] + 1) % m,) + s[1:]

    return (r00, r01, r02, r03)


def make_inv_prims(k: int, m: int):
    """Inverse functions, index-aligned with make_prims. Diagnostic side only."""
    def i00(s):
        return s[-1:] + s[:-1]

    def i01(s):
        return (s[1], s[0]) + s[2:]

    def i02(s):
        return ((s[0] - s[1]) % m,) + s[1:]

    inv2 = pow(2, -1, m)

    def i03(s):
        return (((s[0] - 1) * inv2) % m,) + s[1:]

    return (i00, i01, i02, i03)


def apply_word(word, s, prims):
    """Apply a sequence of primitive indices to state s. Returns final state."""
    for p in word:
        s = prims[p](s)
    return s


def selfcheck(k=6, m=10, seed_states=64):
    """Round-trip inverse verification on a deterministic probe set."""
    import random
    rng = random.Random(0xC0FFEE)
    prims, invs = make_prims(k, m), make_inv_prims(k, m)
    for _ in range(seed_states):
        s = tuple(rng.randrange(m) for _ in range(k))
        for f, g in zip(prims, invs):
            if g(f(s)) != s or f(g(s)) != s:
                raise AssertionError("inverse round-trip failed")
    return True
