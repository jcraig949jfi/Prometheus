"""PLAN s3: FC grid (P 32-256 x K 3/11/12 x worst/realistic/hetero x W-Q FC_GRID) and power grid for H0-H3 + T90/PCT.
Usage: python sim4.py WORKER_TAG. Workers claim jobs atomically (out/claims/<job>), so extra workers may join later.
Each job writes out/jobs/<job>.json. Data seeds for FC = W-U fc_sim.py exactly (addendum D4); power seed 41."""
import json
import os
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import intervals4 as i4  # noqa: E402
import swap_rel2 as s2  # noqa: E402  (W-Q, via intervals4 path)

PS = (32, 64, 128, 256)
KS = (3, 11, 12)
MODELS = ("worst", "realistic", "hetero")
GRID = s2.FC_GRID
N1, N2, CH = 20000, 60000, 2000
ALLC = i4.CANDS + i4.CONTROLS
VS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")
POW_P = (0.60, 0.70, 0.80, 0.90, 0.95, 0.99)
TZ = {"FLIP_REL": -1.0, "CHANCE_REL": 0.0, "NO_EFFECT_REL": 1.0}
NPOW = 2000

JOBS = ([("POW", P, K, m) for P in (64, 32) for K in (11, 3) for m in ("realistic", "worst")]
        + [("FC", P, K, m) for P in PS[::-1] for K in KS for m in MODELS])


def jname(j):
    return f"{j[0]}_P{j[1]}_K{j[2]}_{j[3]}"


def truths(p):
    return [0.0] if p == 0.5 else [-0.5, 0.5]


def counts(model, p, z, P, K, n, stage, C, C1):
    mi = MODELS.index(model)
    rng = np.random.default_rng([10 + stage, P, K, int(round(p * 1000)), int(round(z * 1000)) + 5000, mi])
    cnt = {c: {v: 0 for v in VS} for c in ALLC}
    fb = [0, 0]
    done = 0
    while done < n:
        m = min(CH, n - done)
        a, s = s2.simulate(model, p, z, P, K, m, rng)
        vv = i4.verdicts(a, s, C, C1, K)
        for c in ALLC:
            for v in VS:
                cnt[c][v] += int(np.sum(vv[c] == v))
        fb[0] += int(vv["_fb"][0].sum())
        fb[1] += int(vv["_fb"][1].sum())
        done += m
    cnt["_H1_fallback_DF_DN"] = fb
    return cnt


def fc_of(cz, p):
    out = {}
    for c in ALLC:
        if p == 0.5:
            out[c] = {v: cz[0.0][c][v] for v in VS}
        else:
            out[c] = {"FLIP_REL": cz[-0.5][c]["FLIP_REL"], "NO_EFFECT_REL": cz[0.5][c]["NO_EFFECT_REL"],
                      "CHANCE_REL": max(cz[-0.5][c]["CHANCE_REL"], cz[0.5][c]["CHANCE_REL"])}
    return out


def run_fc(P, K, m, fn):
    C, C1 = s2.boot_counts(P), s2.boot_counts(P + 1)
    res = {}
    for p in GRID:
        cz = {z: counts(m, p, z, P, K, N1, 1, C, C1) for z in truths(p)}
        f1 = fc_of(cz, p)
        border = any(0.008 < f1[c][v] / N1 <= 0.012 for c in i4.CANDS for v in VS)
        n = N1
        if border:
            for z in cz:
                c2 = counts(m, p, z, P, K, N2, 2, C, C1)
                for c in ALLC:
                    for v in VS:
                        cz[z][c][v] += c2[c][v]
                cz[z]["_H1_fallback_DF_DN"] = [x + y for x, y in zip(cz[z]["_H1_fallback_DF_DN"],
                                                                    c2["_H1_fallback_DF_DN"])]
            n = N1 + N2
        res[f"{p:.2f}"] = {"n": n, "stage2": border, "k": fc_of(cz, p),
                           "fallback": {str(z): cz[z]["_H1_fallback_DF_DN"] for z in cz}}
        json.dump(res, open(fn.with_suffix(".part"), "w"))
    return res


def run_pow(P, K, m):
    C, C1 = s2.boot_counts(P), s2.boot_counts(P + 1)
    res = {}
    for p in POW_P:
        res[f"{p:.2f}"] = {}
        for v, z in TZ.items():
            rng = np.random.default_rng([41, P, K, int(round(p * 1000)), int(round(z * 1000)) + 5000,
                                         MODELS.index(m)])
            a, s = s2.simulate(m, p, z, P, K, NPOW, rng)
            vv = i4.verdicts(a, s, C, C1, K)
            res[f"{p:.2f}"][v] = {c: float(np.mean(vv[c] == v)) for c in ALLC}
            res[f"{p:.2f}"][v]["_fb"] = [float(vv["_fb"][0].mean()), float(vv["_fb"][1].mean())]
    return res


if __name__ == "__main__":
    tag = sys.argv[1]
    (HERE / "out" / "claims").mkdir(parents=True, exist_ok=True)
    (HERE / "out" / "jobs").mkdir(parents=True, exist_ok=True)
    print("pid", os.getpid(), "tag", tag, flush=True)
    t0 = time.time()
    for j in JOBS:
        if (HERE / "out" / "STOP").exists():
            print("STOP file seen", flush=True)
            break
        try:
            fd = os.open(HERE / "out" / "claims" / jname(j), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{tag} {os.getpid()} {time.time():.0f}".encode())
            os.close(fd)
        except FileExistsError:
            continue
        t1, c1 = time.time(), time.process_time()
        fn = HERE / "out" / "jobs" / f"{jname(j)}.json"
        r = run_pow(*j[1:]) if j[0] == "POW" else run_fc(*j[1:], fn)
        json.dump({"job": jname(j), "cpu_s": time.process_time() - c1, "wall_s": time.time() - t1, "res": r},
                  open(fn, "w"))
        print(jname(j), f"{time.time()-t1:.0f}s total {time.time()-t0:.0f}s", flush=True)
    print("DONE", f"{time.time()-t0:.0f}s", flush=True)
