"""ROBUST01 shared measurements (stage 0 controls, stage 1 reducer, stage 2b component selection).

All of them run under whatever law X.step currently is: the frozen contest XOR law, or aeth01.op_xor_fold after
fold_physics.install(). The geometry is r3_frontier's current one (F.set_geom).

INVARIANCE THEOREM (fold law, execution-only regime, mutation 0, no rain): the only coordinate- or seed-keyed path left
is the energy-field contest. So if a tile sees no tick with >= 2 valid energy-field writers on one site, its
trajectory is the same at every tile position and under every physics seed. The certifier's reference lattice holds
identical copies, so it is exactly periodic and equivalent to a single TILE x TILE torus; a contest-free torus run
therefore implies position_combine_frac in {0, 1} and seed independence. invariance_check() measures the premise and
the seed half directly; the stage 1 reducer checks the position half against the certificate.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fold_physics as FP  # noqa: E402
import r3_frontier as F  # noqa: E402

X = FP.X
IN_H = (0x12, 0x6D, 0xB4, 0xE9)   # held-out input alphabet, disjoint from F.IN = (0x0F, 0x33, 0x55, 0xAA)
SEEDS = (0xF00D, 0xBEEF, 0xCAFE)  # the search seed, then the certifier's two alternative physics seeds


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))


def table(patch, backend="gpu", alphabet=None, seed=0xF00D):
    """16-pass output table of one patch at lattice position 0 of a side-32 world (other tiles inert)."""
    old = F.IN
    try:
        if alphabet is not None:
            F.IN = tuple(alphabet)
        return F.Evaluator("XOR", side=32, backend=backend, seed=seed).run_batch(np.stack([patch]))[0]
    finally:
        F.IN = old


def rung(out16):
    return F.descriptor(out16)[1]


def n_distinct(out16):
    return int(len(set(int(v) for v in out16)))


def invariance_check(patch, alphabet=None):
    """CPU, one TILE x TILE torus (= the identical-copy lattice), 16 passes x T_EVAL ticks, under each of SEEDS.

    Returns energy_multi / template_multi: (pass, tick, site) events with >= 2 valid contenders for the energy
    field, resp. for any template field, under the first seed; seeds_identical: the three output tables agree;
    table: the output table under the first seed."""
    xp, K = X.load("cpu")
    alph = tuple(alphabet) if alphabet is not None else F.IN
    base = F.tile_world(patch)
    tables, e_multi, t_multi = [], 0, 0
    for k, sd in enumerate(SEEDS):
        out = np.zeros(16, np.uint8)
        for c in range(16):
            w = base.copy()
            w[3][F.INA] = alph[c // 4]
            w[3][F.INB] = alph[c % 4]
            s = [w[f].copy() for f in range(5)]
            for t in range(F.T_EVAL):
                if k == 0:
                    _, counts = FP.gather(np, s, F.ENERGY["write_cost"])
                    e_multi += int((counts[4] >= 2).sum())
                    t_multi += sum(int((counts[f] >= 2).sum()) for f in range(4))
                s, _ = X.step(np, K, "XOR", F.TILE, sd, t + 1, s, F.ENERGY)
            out[c] = s[3][F.OUT]
        tables.append(out)
    return {"energy_multi": e_multi, "template_multi": t_multi,
            "seeds_identical": all(np.array_equal(tables[0], t) for t in tables[1:]),
            "table": [int(v) for v in tables[0]]}


def inert_patch():
    p = np.zeros((5, 16, 16), np.uint8)
    p[0] = X.INERT
    return p


def place(cells, states, offset=(0, 0), base=None):
    p = inert_patch() if base is None else base.copy()
    for (y, x), st in zip(cells, states):
        yy, xx = y + offset[0], x + offset[1]
        if 0 <= yy < 16 and 0 <= xx < 16:
            p[:, yy, xx] = st
    return p


TRANSPLANT_OFFSETS = ((0, 0), (1, 0), (0, 1), (-1, -1), (2, 2), (-3, 3))   # R4 task 1's offsets


def transplant(cells, states, backend="gpu"):
    """R4 task 1: the component alone in an inert patch at each offset; COMBINE fraction over 256 tile positions."""
    ev = F.Evaluator("XOR", side=32, backend=backend)
    res = {}
    for off in TRANSPLANT_OFFSETS:
        outs = ev.run_batch(np.stack([place(cells, states, off)] * 256))
        res[str(off)] = float(np.mean([rung(o) == 2 for o in outs]))
    return res
