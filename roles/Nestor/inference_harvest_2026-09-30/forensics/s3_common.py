"""s3 (pairwise epistasis) shared code. Reuses fsetup.py (runner + screens) and core_map.py (knockout RNG, trace).

Exact-decision fast screens. run_de.competent and run_fair.fair_assay return booleans at a >= 0.5 threshold over
k seeds, and every p11.assay call is a pure function of its seed tuple. The fast versions below make the SAME calls
with the SAME seeds, and stop only when the boolean can no longer change:
  * within a seed, the second side is skipped once the first side passes (ok = ok or pass);
  * stage 2 / fair stop once hits >= k/2 (pass certain) or misses > k/2 (fail certain);
  * STATE_FREE = R1 and R2, so R2 is skipped when R1 fails.
s3_equiv.py checks the fast screens against fsetup.competent / fsetup.state_free on real mutants.

`suffix` != "" gives the re-assay with a new seed tag: competent tag ("X-DD-ESTABLISH", sha16, stage) becomes
("X-DD-ESTABLISH" + suffix, sha16, stage); the fair tag "SFL"+hex becomes "SFL"+hex+suffix.
"""
from __future__ import annotations

import hashlib
import math
import random

import fsetup as F

W = F.world
K1, K2 = F.run_dd.K1, F.run_dd.K2
SEED = 20260930          # core_map.SEED (single-knockout value RNG)


def _p11(r, g, st, side, seed):
    n = r.L
    tl = W._pow2(2 * n)
    ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
    cp = lambda s: (None if s[0] is None else list(s[0]), s[1], s[2])   # fresh copies, as fair_assay builds them
    return W.p11.assay(W.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=cp(st), st_b=cp(st), budget=r.t["slice"],
                       ops_mask=r._ops_mask(), cmr=r.copy_mut, victim_side=1 - side, seed=seed)["pass"]


def _seq(k, hit):
    """>= 0.5 decision over seeds 0..k-1 with exact early stopping."""
    need = math.ceil(k / 2)
    h = m = 0
    for i in range(k):
        if hit(i):
            h += 1
        else:
            m += 1
        if h >= need:
            return True
        if m > k - need:
            return False
    return h >= need


def competent(cell, g, dense=True, suffix=""):
    r = F.runner(cell, dense)
    g = bytes(g)
    tag = ("X-DD-ESTABLISH" + suffix, hashlib.sha256(g).hexdigest()[:16])
    fresh = (None, 0, 0)

    def hit(stage):
        return lambda i: any(_p11(r, g, fresh, s, ("X-DONOR-DISCOVERY", tag + (stage,), i, s)) for s in (0, 1))
    h1 = hit(1)
    if not any(h1(i) for i in range(K1)):
        return False
    return _seq(K2, hit(2))


def state_free(cell, g, dense=True, suffix=""):
    r = F.runner(cell, dense)
    g = bytes(g)
    tag = "SFL" + g.hex() + suffix
    for e in ("R1", "R2"):
        st0 = F.run_fair.ENTRY[e]

        def hit(i, e=e, st0=st0):
            return any(_p11(r, g, st0, s, ("X-A3-FAIR", tag, e, i, s)) for s in (0, 1))
        if not _seq(20, hit):
            return False
    return True


def function(cell, g, dense, sf, suffix=""):
    """The pre-registered function: COMPETENT (and STATE_FREE for state-free genomes)."""
    if not competent(cell, g, dense, suffix):
        return False
    return state_free(cell, g, dense, suffix) if sf else True


def single_vals(g, p):
    """core_map.knockout's replacement values for position p (same RNG)."""
    rng = random.Random(int(hashlib.sha256(bytes(g) + bytes([p])).hexdigest()[:16], 16) ^ SEED)
    return rng.sample([v for v in range(256) if v != g[p]], 3)


def pair_vals(g, i, j):
    """3 joint draws for pair (i, j): distinct values != original at each position; own RNG stream."""
    rng = random.Random(int(hashlib.sha256(b"S3PAIR" + bytes(g) + bytes([i, j])).hexdigest()[:16], 16))
    vi = rng.sample([v for v in range(256) if v != g[i]], 3)
    vj = rng.sample([v for v in range(256) if v != g[j]], 3)
    return list(zip(vi, vj))


def lethal_call(fn, mutants):
    """Function lost in >= 2 of 3 draws; the third draw is only run when the first two disagree (exact)."""
    lost = kept = 0
    for m in mutants:
        if fn(m):
            kept += 1
        else:
            lost += 1
        if lost >= 2:
            return True
        if kept >= 2:
            return False
    return lost >= 2


def null_lethal(pi, pj):
    q = 1 - (1 - pi) * (1 - pj)
    return 3 * q * q * (1 - q) + q ** 3


def pair_mutants(g, i, j):
    out = []
    for vi, vj in pair_vals(g, i, j):
        m = bytearray(g)
        m[i], m[j] = vi, vj
        out.append(bytes(m))
    return out
