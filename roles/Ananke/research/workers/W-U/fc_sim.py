"""PLAN s2/s3: FC tables for all candidates (+T90 control). Usage: python fc_sim.py WORKER NWORKERS
Jobs = (P, K, model); job j runs on worker j % NWORKERS. Writes out/fc_w<WORKER>.json."""
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

PS = (8, 16, 32, 64, 128, 256)
KS = (3, 11, 12)
MODELS = ("worst", "realistic", "hetero")
GRID = s2.FC_GRID
N1, N2, CH = 20000, 60000, 2000
ALLC = iv.CANDS + iv.CONTROLS
VS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")


def truths(p):
    return [0.0] if p == 0.5 else [-0.5, 0.5]


def counts(model, p, z, P, K, n, stage, C):
    mi = MODELS.index(model)
    rng = np.random.default_rng([10 + stage, P, K, int(round(p * 1000)), int(round(z * 1000)) + 5000, mi])
    cnt = {c: {v: 0 for v in VS} for c in ALLC}
    done = 0
    while done < n:
        m = min(CH, n - done)
        a, s = s2.simulate(model, p, z, P, K, m, rng)
        vv = iv.verdicts(a, s, C)
        for c in ALLC:
            for v in VS:
                cnt[c][v] += int(np.sum(vv[c] == v))
        done += m
    return cnt


def fc_of(cnt_by_z, p, n):
    """per candidate: FC per verdict at its boundary truth (counts + n)."""
    out = {}
    for c in ALLC:
        if p == 0.5:
            r = {v: cnt_by_z[0.0][c][v] for v in VS}
        else:
            r = {"FLIP_REL": cnt_by_z[-0.5][c]["FLIP_REL"], "NO_EFFECT_REL": cnt_by_z[0.5][c]["NO_EFFECT_REL"],
                 "CHANCE_REL": max(cnt_by_z[-0.5][c]["CHANCE_REL"], cnt_by_z[0.5][c]["CHANCE_REL"])}
        out[c] = r
    return out


if __name__ == "__main__":
    W, NW = int(sys.argv[1]), int(sys.argv[2])
    jobs = [(P, K, m) for P in PS[::-1] for K in KS for m in MODELS]
    mine = jobs[W::NW]
    res = {}
    t0 = time.time()
    fn = HERE / "out" / f"fc_w{W}.json"
    print("pid", os.getpid(), "jobs", mine, flush=True)
    for P, K, m in mine:
        C = s2.boot_counts(P)
        key = f"P{P}_K{K}_{m}"
        res[key] = {}
        for p in GRID:
            cz = {z: counts(m, p, z, P, K, N1, 1, C) for z in truths(p)}
            f1 = fc_of(cz, p, N1)
            border = any(0.008 < f1[c][v] / N1 <= 0.012 for c in iv.CANDS for v in VS)
            n = N1
            if border:
                cz2 = {z: counts(m, p, z, P, K, N2, 2, C) for z in truths(p)}
                for z in cz:
                    for c in ALLC:
                        for v in VS:
                            cz[z][c][v] += cz2[z][c][v]
                n = N1 + N2
            res[key][f"{p:.2f}"] = {"n": n, "stage2": border, "k": fc_of(cz, p, n)}
            json.dump(res, open(fn, "w"))
        print(key, f"{time.time()-t0:.0f}s", flush=True)
    print("DONE", f"{time.time()-t0:.0f}s", flush=True)
