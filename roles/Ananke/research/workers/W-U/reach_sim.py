"""PLAN s5: selection power (P64 K11, n=4000) and REACH power curves (n=1000, W-Q POW_GRID) for all
candidates. Usage: python reach_sim.py WORKER NWORKERS  -> out/reach_w<W>.json (job 0 = selection power)."""
import json
import os
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W-Q"))
sys.path.insert(0, str(HERE))
import swap_rel2 as s2  # noqa: E402
import intervals as iv  # noqa: E402

TZ = {"FLIP_REL": -1.0, "CHANCE_REL": 0.0, "NO_EFFECT_REL": 1.0}
MODELS = ("worst", "realistic")
ALLC = iv.CANDS + iv.CONTROLS


def power(model, p, P, K, n, seed, C):
    out = {c: {} for c in ALLC}
    for v, z in TZ.items():
        rng = np.random.default_rng([seed, P, K, int(round(p * 1000)), int(round(z * 1000)) + 5000, MODELS.index(model)])
        a, s = s2.simulate(model, p, z, P, K, n, rng)
        vv = iv.verdicts(a, s, C)
        for c in ALLC:
            out[c][v] = float(np.mean(vv[c] == v))
    return out


if __name__ == "__main__":
    W, NW = int(sys.argv[1]), int(sys.argv[2])
    jobs = [("SEL", 64, 11)] + [("REACH", P, K) for P in (256, 128, 64, 32, 16, 8) for K in (3, 11, 12)]
    res = {}
    t0 = time.time()
    print("pid", os.getpid(), jobs[W::NW], flush=True)
    for kind, P, K in jobs[W::NW]:
        C = s2.boot_counts(P)
        if kind == "SEL":
            res["SEL"] = {m: {f"{p:.2f}": power(m, p, P, K, 4000, 21, C) for p in (0.60, 0.65, 0.70, 0.75)}
                          for m in MODELS}
        else:
            res[f"P{P}_K{K}"] = {m: {f"{p:.2f}": power(m, p, P, K, 1000, 31, C) for p in s2.POW_GRID}
                                 for m in MODELS}
        json.dump(res, open(HERE / "out" / f"reach_w{W}.json", "w"))
        print(kind, P, K, f"{time.time()-t0:.0f}s", flush=True)
    print("DONE", flush=True)
