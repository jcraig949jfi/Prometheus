"""(1) Coverage of the held-out pair CI (assays.pair_ci = percentile bootstrap over mirror pairs, 99%) on
synthetic mirror-pair data with known truth; comparison estimators: t-interval (df P-1), BOOTT
(swap_rel.interval 'BOOTT', studentized); and the WRONG-UNIT world bootstrap (2P worlds as if independent).
Output out/coverage.json. CPU, numpy."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[5]))
import numpy as np  # noqa: E402

import w2h_stats as W  # noqa: E402

N = int(os.environ.get("W2H_N", "4000"))


def world_boot(P, Kw, p, rho, conc, n, seed):
    """wrong unit: percentile bootstrap over 2P worlds."""
    rng = np.random.default_rng(seed)
    lo_m = hi_m = 0
    for c0 in range(0, n, 100):
        m = min(100, n - c0)
        _, w = W.sim_pairs(P, Kw, p, rho, conc, m, rng)
        _, lo, hi = W.pct_ci(w)
        lo_m += int(np.sum(lo > p + 1e-12))
        hi_m += int(np.sum(hi < p - 1e-12))
    return {"lo_miss": lo_m / n, "hi_miss": hi_m / n, "miss": (lo_m + hi_m) / n}


if __name__ == "__main__":
    t0 = time.time()
    res = []
    # C1 held design: M_held 64 -> P 32, 12 scored trials/world (FLIP: 12 of 16 scored too)
    PS = [int(a) for a in sys.argv[1:]] or [8, 32, 128]
    for P in PS:
        for p in (0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 0.97):
            for rho in (1.0, 0.0):
                for conc in (None, 4.0):
                    seed = [P, int(p * 1000), int(rho * 10), 0 if conc is None else int(conc)]
                    row = {"P": P, "Kw": 12, "p": p, "rho": rho, "conc": conc}
                    row["pct"] = W.coverage(W.pct_ci, P, 12, p, rho, conc, N, seed)
                    row["t"] = W.coverage(W.t_ci, P, 12, p, rho, conc, N, seed)
                    row["boott"] = W.coverage(W.boott_ci, P, 12, p, rho, conc, N, seed)
                    row["world_boot"] = world_boot(P, 12, p, rho, conc, N, seed)
                    res.append(row)
                    print(P, p, rho, conc, {k: round(row[k]["miss"], 4) for k in ("pct", "t", "boott", "world_boot")},
                          round(time.time() - t0), flush=True)
    json.dump({"N": N, "rows": res}, open(HERE / "out" / f"coverage_P{'_'.join(map(str, PS))}.json", "w"), indent=1)
