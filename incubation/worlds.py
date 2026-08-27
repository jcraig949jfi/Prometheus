"""worlds.py — the three procedural problem families (v2 triple).

All worlds share the SAME primitive entities (incubation/primitives.py), instantiated at
world-specific (k, m). Worlds differ in:
  - surface representation (codec)      wA: int-tuples; wB: strings, two letters per slot
                                        (base-26); wC: int-tuples
  - dimensions (k) and modulus (m)      (m odd everywhere: r03 is an affine step)
  - task generator (independent code paths, disjoint seed streams)
  - dynamics constraint (wC forbids entering states with slot1 < m//5 — a BAND trap; a
    move into a forbidden state FAILS at runtime: no state change, execution still costs)

The intended reusable composition (diagnostic side; the solver must DISCOVER it):

    M = (r01, r02, r01)   i.e. indices (1, 2, 1)
    effect: slot1 <- (slot1 + slot0) mod m       (a conjugation identity, valid for all k, m;
                                                  not available as any single primitive)

Task (solver-visible) = {"start": <surface>, "target": <surface>}. NOTHING ELSE.
Witness words, strata, world identity are omniscient diagnostics returned separately.

DESIGN LINEAGE (each step forced by a census, results/census_v*.json):
  v0 REJECTED: r03 = slot0+1 commuted with r02; monoid growth ~2.8^d; 85% of witnesses
     non-minimal; M forced in only 31% of survivors.
  v1 REJECTED: affine r03 + explicit family filters fixed forcing but acceptance was
     0.9-2.8% — diagnosis: with small m, short words touch only 2-4 slots, so the
     effective space is m^2..m^3 and value-collision shortcuts collapse witnesses.
  v2: large prime moduli (997/673/809). Collisions scale ~1/m: acceptance 0.27-0.54.
     wC's point trap (slot1==0) became vanishingly rare at large m, so the trap is a
     BAND (slot1 < m//5), giving a ~0.37 macro runtime-failure rate; guards over the
     executable probe language need threshold atoms (comp < c), not just equality.

FAMILY DEFINITION (omniscient-side rejection filters at generation; never solver-visible):
  generic witness path:  every step changes the state AND its effect differs from every
                         other primitive's effect at that state (no degenerate arithmetic)
  embed tasks:  minimal solution length == |witness| AND every minimal solution contains
                M contiguously
  null tasks:   minimal solution length == |witness| AND no minimal solution contains M

Generator hygiene (necessary but not sufficient — the filter is the gate):
  - no two adjacent r01 (r01·r01 = identity)
  - no run of r00 longer than 2 (r00^k = identity)
  - across the X·M·Y junctions too (X may not end r01; Y may not start r01)
"""
from __future__ import annotations

import random

from primitives import make_prims, make_inv_prims
import diagnostics as dx

M_WORD = (1, 2, 1)          # indices into PRIM_IDS — diagnostic-side constant


class World:
    def __init__(self, wid, k, m, encode, decode, constrained=False):
        self.wid = wid                       # diagnostic label only
        self.k, self.m = k, m
        self.prims = make_prims(k, m)
        self.invs = make_inv_prims(k, m)
        self.encode, self.decode = encode, decode
        self.constrained = constrained
        self.trap_lo = m // 5                # wC band trap boundary (unused elsewhere)
        self.gen_stats = {"embed_tries": 0, "embed_ok": 0,
                          "null_tries": 0, "null_ok": 0}

    # dynamics -------------------------------------------------------------
    def valid(self, s):
        return (not self.constrained) or s[1] >= self.trap_lo

    def step(self, p, s):
        """Apply primitive index p. Returns new state or None on runtime failure."""
        t = self.prims[p](s)
        return t if self.valid(t) else None

    def run_word(self, word, s):
        """Run a word under world dynamics. Returns (final_state_or_None, execs_used)."""
        n = 0
        for p in word:
            n += 1
            s = self.step(p, s)
            if s is None:
                return None, n
        return s, n

    # generation -----------------------------------------------------------
    def _rand_state(self, rng):
        while True:
            s = tuple(rng.randrange(self.m) for _ in range(self.k))
            if self.valid(s):
                return s

    def _word_ok(self, w):
        run00 = 0
        for i, p in enumerate(w):
            run00 = run00 + 1 if p == 0 else 0
            if run00 > 2:
                return False
            if i and p == 1 and w[i - 1] == 1:
                return False
        return True

    def _rand_word(self, rng, length, avoid_m=False):
        for _ in range(2000):
            w = tuple(rng.randrange(4) for _ in range(length))
            if not self._word_ok(w):
                continue
            if avoid_m and dx.contains_word(w, M_WORD):
                continue
            return w
        raise RuntimeError("word sampling exhausted")

    def _generic_path(self, s, w):
        """Generic witness path: every step effective, locally distinguishable, valid."""
        for p in w:
            ns = self.prims[p](s)
            if ns == s or not self.valid(ns):
                return False
            for q in range(4):
                if q != p and self.prims[q](s) == ns:
                    return False
            s = ns
        return True

    def _family_filter(self, s, t, w, embed_m):
        """Omniscient-side family definition. See module docstring."""
        L = dx.min_dist(self, s, t)
        if L != len(w):
            return False
        sols = dx.solutions_at(self, s, t, L)
        if not sols:
            return False
        n_m = sum(1 for x in sols if dx.contains_word(x, M_WORD))
        return n_m == len(sols) if embed_m else n_m == 0

    def gen_task(self, rng, embed_m, xy_lens=(2, 3)):
        """One task. embed_m: witness is X·M·Y; else an M-free witness of matched length.

        Returns (solver_visible_task, omniscient_record).
        """
        key = "embed" if embed_m else "null"
        for _ in range(20000):
            self.gen_stats[f"{key}_tries"] += 1
            lx, ly = rng.choice(xy_lens), rng.choice(xy_lens)
            if embed_m:
                x = self._rand_word(rng, lx)
                y = self._rand_word(rng, ly)
                w = x + M_WORD + y
                if not self._word_ok(w):
                    continue
            else:
                w = self._rand_word(rng, lx + 3 + ly, avoid_m=True)
            s = self._rand_state(rng)
            if not self._generic_path(s, w):
                continue
            t, _ = self.run_word(w, s)
            if t is None or t == s:
                continue
            if not self._family_filter(s, t, w, embed_m):
                continue
            self.gen_stats[f"{key}_ok"] += 1
            task = {"start": self.encode(s), "target": self.encode(t)}
            omni = {"wid": self.wid, "witness": w, "embed_m": embed_m,
                    "s": s, "t": t}
            return task, omni
        raise RuntimeError("task sampling exhausted")


# surface codecs -----------------------------------------------------------
def _ident(s):
    return tuple(s)


def _to_pairs(s):
    """Two letters per slot, base 26 (requires m <= 676)."""
    return "".join(chr(97 + v // 26) + chr(97 + v % 26) for v in s)


def _from_pairs(x):
    return tuple((ord(x[i]) - 97) * 26 + (ord(x[i + 1]) - 97)
                 for i in range(0, len(x), 2))


def make_worlds():
    wa = World("wA", k=6, m=997, encode=_ident, decode=_ident)
    wb = World("wB", k=7, m=673, encode=_to_pairs, decode=_from_pairs)
    wc = World("wC", k=8, m=809, encode=_ident, decode=_ident, constrained=True)
    return {"wA": wa, "wB": wb, "wC": wc}
