"""PKG-S1 ladder runner: every learner x budget on every world, scored against the EXACT Bayes predictor.

Primary metric: excess log-loss (bits/symbol) = learner log-loss - Bayes log-loss, averaged over the stream (online
prediction), with a 90% CI over seeds. Also reported: excess retention = learner bits - minimal sufficient bits at T;
query ops. Declared tolerance (PKG-S1 s6): 0.02 bits/symbol. Seeds 1..N_SEEDS (the arc3 suff dev range; no campaign).
Writes ensorain/arc3/suff/results/ladder.json. Single process, BELOW_NORMAL."""
import json
import math
import os
import sys
import time

import numpy as np
from scipy import stats

from .worlds import W0, W1, W2, W5, even_process, golden_mean, simple_nonunifilar_source, logloss
from .learners import STAT, VERB_SUM, VERB_RESTRICT, NEAREST, TABLE, LOG, WINDOW

OUT = os.path.join(os.path.dirname(__file__), "results")
TOL = 0.02


def ci(v):
    v = np.asarray(v, float)
    m, se = v.mean(), v.std(ddof=1) / math.sqrt(len(v))
    h = stats.t.ppf(0.95, len(v) - 1) * se
    return dict(mean=float(m), lo=float(m - h), hi=float(m + h))


def seq_learners():
    L = [STAT(k) for k in (0, 1, 2, 3, 4, 6, 8)]
    L += [VERB_SUM(B, k) for B in (64, 256, 1024, 4096) for k in (1, 2, 3, 4, 6)]
    L += [VERB_RESTRICT(B) for B in (256, 4096)]
    L += [NEAREST(B, 12) for B in (256, 1024, 4096)]
    return L


def run(n_seeds=16, T=4000, T_kv=20000):
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    worlds = [W0(), W1(), W2(2), W2(3), even_process(), golden_mean(), simple_nonunifilar_source()]
    res = {}
    t0 = time.time()
    for w in worlds:
        rows = {}
        for sd in range(1, n_seeds + 1):
            rng = np.random.default_rng(sd)
            x = w.sample(T, rng)
            bay = logloss(w.bayes(x), x)
            for L in seq_learners():
                P, m = L.run(x)
                rows.setdefault(L.name, []).append(dict(ex=logloss(P, x) - bay, bits=m["bits"], qops=m["query_ops"]))
        res[w.name] = {k: dict(excess=ci([r["ex"] for r in v]), bits=v[0]["bits"], query_ops=v[0]["qops"],
                               suff_bits=w.suff_bits(T)) for k, v in rows.items()}
    kv = W5()
    rows = {}
    for sd in range(1, n_seeds + 1):
        rng = np.random.default_rng(sd)
        st = kv.sample(T_kv, rng)
        y = kv.targets(st)
        bay = logloss(kv.bayes(st), y)
        seen_distinct = len(set(st["keys"][~st["isq"]]))
        for L in [TABLE(B, kv.V) for B in (64, 256, 1024)] + [WINDOW(B, kv.V) for B in (64, 256, 1024)] + [LOG(kv.V)]:
            P, m = L.run(st, np.random.default_rng(sd + 99))
            rows.setdefault(L.name, []).append(dict(ex=logloss(P, y) - bay, bits=m["bits"],
                                                    suff=kv.suff_bits(seen_distinct)))
    res[kv.name] = {k: dict(excess=ci([r["ex"] for r in v]), slots=v[0]["bits"],
                            suff_bits=float(np.mean([r["suff"] for r in v]))) for k, v in rows.items()}
    os.makedirs(OUT, exist_ok=True)
    out = dict(n_seeds=n_seeds, T=T, T_kv=T_kv, tol=TOL, wall_s=round(time.time() - t0, 1), results=res)
    with open(os.path.join(OUT, "ladder.json"), "w") as f:
        json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    o = run(int(sys.argv[1]) if len(sys.argv) > 1 else 16)
    print("wall", o["wall_s"])
