"""Pre-E1 arena calibration probe -- NOT a campaign experiment.

Purpose: find the difficulty band in which search works AT ALL, so that the campaign
measures the arms rather than measuring my fitness function.

DISCIPLINE: the ladder is scored with arms A_LOCAL and B_STRUCT only -- the arms the
hypothesis is NOT about.  Calibrating on a composition arm would rig the arena toward
the answer.  This file is committed so the calibration is auditable.
"""
from __future__ import annotations

import sys
import time

import numpy as np

import arena
from arena import _u8


def L(name, fn):
    return (name, fn)


LADDER = [
    L("d1  x0^x1",                 lambda x: _u8(x[0] ^ x[1])),
    L("d2  (x0^x1)+x2",            lambda x: _u8((x[0] ^ x[1]) + x[2])),
    L("d3  (x0+x1)^(x2&x3)",       lambda x: _u8((x[0] + x[1]) ^ (x[2] & x[3]))),
    L("d4  (x0*x1)+x2",            lambda x: _u8(x[0] * x[1] + x[2])),
    L("d5  ((x0^x1)+x2)<<1",       lambda x: _u8(((x[0] ^ x[1]) + x[2]) << 1)),
    L("d6  g(f(x)) 9-instr",       arena.w1_T),
    L("d7  entangled 10-instr",    arena.w2_T),
]


def probe(fn, arm, evals, seed):
    """Single-slot world carrying just this reference function."""
    arena.WORLDS["_CAL"] = dict(refs=[fn], goal=0, note="calibration")
    import arms as A
    r = A.Run(arm, "_CAL", seed, evals=evals).go()
    return len(r.summary()["heldout_slots"]) > 0, r.summary()


def main():
    evals = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    seeds = range(20260901, 20260901 + 6)
    print("difficulty ladder   evals=%d  seeds=6  arms=A_LOCAL,B_STRUCT" % evals)
    print("=" * 72)
    print("%-26s %12s %12s" % ("target", "A_LOCAL", "B_STRUCT"))
    print("-" * 72)
    for name, fn in LADDER:
        row = []
        for arm in ("A_LOCAL", "B_STRUCT"):
            t = time.time()
            hits = sum(probe(fn, arm, evals, s)[0] for s in seeds)
            row.append("%d/6 (%.0fs)" % (hits, time.time() - t))
        print("%-26s %12s %12s" % (name, row[0], row[1]))


if __name__ == "__main__":
    main()
