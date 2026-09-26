"""Dev smoke: every arm on one world per family and level (dev seeds only). Not a sweep; timing + sanity."""
import sys
import time

import numpy as np

from ensorain.wtp3.world3 import AC
from .arms import LosslessK, LosslessR, Selective, RandomMerge, Hybrid
from .families import make_world, FAMILIES, LEVELS


def arms_for(dims):
    cells = int(np.prod(dims))
    return [LosslessK(dims), LosslessR(dims), Selective("lowrank", dims, cap=max(160, cells // 4)),
            Selective("additive", dims, cap=max(160, cells // 4)), RandomMerge(dims, B=max(16, cells // 16)),
            Hybrid(dims, cap=max(160, cells // 4))]


def run(w):
    rows = []
    for arm in arms_for(w["dims"]):
        t0 = time.perf_counter()
        for A, y, s in w["train"]:
            for i in range(0, len(y), 50):
                arm.observe(A[i:i + 50], y[i:i + 50])
        acs = {k: round(AC(arm.predict(T), truth, 1.0), 3) for k, (T, truth) in w["tests"].items()}
        m = arm.meter
        rows.append((arm.name, acs, m.peak_persistent, m.bytes_read, m.ops, round(time.perf_counter() - t0, 2)))
    return rows


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 9_100_000
    for lv in LEVELS:
        for fam in FAMILIES:
            w = make_world(fam, lv, seed)
            print(f"== {lv} {fam} gen={w['gen']} r={w['rank']} cov={w['coverage']:.2f}")
            for r in run(w):
                print("  ", r)
