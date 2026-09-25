"""Dev-only recipe selection for structured substrates (PREREG_WTP03 s2): one grid, the same for
every substrate, scored on planted worlds (dev seeds 9,300,000+). Output: runs/wtp03/recipes.json."""
import itertools
import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .collider import experience, holdout, test_sets, train, score, STRUCT, _addr
from .controls import planted
from .world3 import mem_cap

GRID = [("sgd", 0.02, 1), ("sgd", 0.1, 1), ("sgd", 0.1, 3), ("sgd", 0.3, 3), ("nlms", 0.1, 1), ("nlms", 0.5, 1), ("nlms", 0.5, 3)]
WORLDS = [("lowrank", (10, 10, 10), 2, 0.25), ("cp", (10, 10, 10), 2, 0.1), ("tt", (6, 6, 6, 6), 2, 0.1),
          ("spectral", (12, 12, 12), 3, 0.03), ("pairwise", (10, 10, 10), 2, 0.25), ("sum", (8, 8, 8), 2, 0.1)]
OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp03")


def job(a):
    wi, seed, kind = a
    gen, dims, rank, band = WORLDS[wi]
    g = planted(gen, dims, rank, band)
    st, _ = experience(g, seed)
    cap = mem_cap(g, st["x"].size)
    tests = test_sets(st, np.random.default_rng(seed + 17))
    stR, blk, _ = holdout(st, np.random.default_rng(seed + 29))
    out = {}
    for rc in GRID:
        m, _ = train(kind, st, cap, seed + 101, rc)
        if m is None:
            return wi, seed, kind, None
        a1 = score(m, st, tests)["interp"]
        a2 = None
        if stR is not None:
            mR, _ = train(kind, stR, cap, seed + 101, rc)
            a2 = score(mR, stR, dict(interp=np.zeros(0, int), novel=np.zeros(0, int), recomb=blk))["recomb"]
        out[str(rc)] = [a1, a2]
    return wi, seed, kind, out


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [(wi, s, k) for wi in range(len(WORLDS)) for s in (9_300_001, 9_300_002) for k in STRUCT]
    with ProcessPoolExecutor(int(os.environ.get("ENSORAIN_WORKERS", 20))) as ex:
        res = list(ex.map(job, jobs))
    table = {}
    for k in STRUCT:
        per = {str(rc): [] for rc in GRID}
        for wi, s, kk, out in res:
            if kk != k or out is None:
                continue
            for rc, v in out.items():
                vals = [a for a in v if a is not None]
                per[rc].append(float(np.mean(vals)) if vals else np.nan)
        med = {rc: float(np.nanmedian(v)) if v else np.nan for rc, v in per.items()}
        best = max(med, key=lambda r: -1e9 if not np.isfinite(med[r]) else med[r])
        table[k] = dict(median_by_recipe=med, chosen=best)
        print(k, "chosen", best, {r: round(v, 3) for r, v in med.items()})
    json.dump(dict(grid=[list(r) for r in GRID], worlds=WORLDS, seeds=[9_300_001, 9_300_002], table=table, raw=res),
              open(os.path.join(OUT, "recipes.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
