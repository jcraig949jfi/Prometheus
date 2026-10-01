"""W2-20 step 5 (post-hoc, NOT decisive; the decision uses analysis.py's primary CI only).

    python -B supplement.py -> supplement.json
S1 bootstrap Monte-Carlo sensitivity: the primary percentile CI recomputed with 10 other bootstrap seeds (4,000 each).
S2 primary WLS restricted to L_pre >= 30 and >= 35 (genome bootstrap 4,000).
S3 scheme check: NEW (S_late) vs OLD RAND, rate ~ L_pre + NEW (does the scheme shift RAND at fixed length?).
S4 both-pre pair class: pooled rates EVO_SD, OLD RAND, NEW, RAND; difference EVO_SD - RAND with genome bootstrap CI.
S5 EVO_SD vs NEW only, primary model.
"""
import json
import pathlib
import random

import numpy as np

import analysis as A

HERE = pathlib.Path(__file__).resolve().parent
D = A.D
for r in D:
    r["NEW"] = int(r.get("source") == "W2-20 S_late")
SD = [r for r in A.G["EVO_SD"] if r["n_null0"]]
RAND = [r for r in A.G["RAND"] if r["n_null0"]]
NEW = [r for r in RAND if r["NEW"]]
OLD = [r for r in RAND if not r["NEW"]]
out = {}


def boot_c(rs, seed, nb=4000, lab="EVO"):
    X = np.array([[1.0, r["L_pre"], float(r[lab])] for r in rs])
    y = np.array([r["n_strict"] / r["n_null0"] for r in rs]); w = np.array([r["n_null0"] for r in rs], float)
    beta, _ = A.wls(X, y, w)
    rng = random.Random(seed)
    gs = {}
    for i, r in enumerate(rs):
        gs.setdefault(r[lab], []).append(i)
    bc = []
    for _ in range(nb):
        idx = [rng.choice(g) for g in gs.values() for _ in g]
        bc.append(A.wls(X[idx], y[idx], w[idx])[0][2])
    return {"n": [len(gs.get(1, [])), len(gs.get(0, []))], "c": float(beta[2]),
            "ci": [float(np.percentile(bc, 2.5)), float(np.percentile(bc, 97.5))]}


out["S1"] = [boot_c(SD + RAND, s)["ci"] for s in range(1, 11)]
ups = [c[1] for c in out["S1"]]
out["S1_upper_summary"] = {"min": min(ups), "max": max(ups), "mean": float(np.mean(ups)), "n_below_0.007": sum(u < 0.007 for u in ups)}
for t in (30, 35):
    out["S2_Lpre_ge_%d" % t] = boot_c([r for r in SD + RAND if r["L_pre"] >= t], 20261013)
out["S3_NEW_vs_OLD"] = boot_c(NEW + OLD, 20261013, lab="NEW")
out["S5_SD_vs_NEWonly"] = boot_c(SD + NEW, 20261013)


def bp(r):
    pre = set(r["pre_set"])
    n0 = [x for x in r["pairs"] if x[3] == 0 and x[0] in pre and x[1] in pre]
    return len(n0), sum(1 for x in n0 if x[2])


def pool(rs):
    n = sum(bp(r)[0] for r in rs); k = sum(bp(r)[1] for r in rs)
    return [k, n, k / n if n else None]


out["S4_both_pre"] = {"EVO_SD": pool(SD), "OLD_RAND": pool(OLD), "NEW": pool(NEW), "RAND": pool(RAND)}
rng = random.Random(5)
diffs = []
for _ in range(4000):
    a = [rng.choice(SD) for _ in SD]; b = [rng.choice(RAND) for _ in RAND]
    pa, pb = pool(a), pool(b)
    if pa[1] and pb[1]:
        diffs.append(pa[2] - pb[2])
d0 = pool(SD)[2] - pool(RAND)[2]
out["S4_diff_SD_minus_RAND"] = {"diff": d0, "boot95": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]}
json.dump(out, open(HERE / "supplement.json", "w"), indent=1)
for k, v in out.items():
    print(k, v)
