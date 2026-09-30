"""W-X REL5 driver. Usage: python run5.py MODE W NW   (MODE = val | fc). Points = PLAN s2 grid; point j -> worker j%NW.
val: stage-0 draw, n=2000 per truth (addendum D5). fc: stage 1 n=20000 per truth, + stage 2 n=60000 iff any H2 FC in
(0.8%, 1.2%] (D3). Writes out/<mode>_w<W>.json after every point."""
import json
import os
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import degen as dg  # noqa: E402

PS, KS, DS, PN = (32, 64), (3, 11), (0.5, 0.8, 0.95), (0.90, 0.95, 0.99)
POINTS = [(P, K, d, p) for P in PS for K in KS for d in DS for p in PN]
ZS = (-0.5, 0.5)
CH = 2000
N_VAL, N1, N2 = 2000, 20000, 60000


def key(pt):
    return f"P{pt[0]}_K{pt[1]}_d{pt[2]:.2f}_p{pt[3]:.2f}"


def draw(pt, z, stage, n, C):
    P, K, d, p = pt
    rng = dg.rng_for(stage, P, K, d, p, z)
    stat = "DF" if z < 0 else "DN"
    cnt = {c: {v: 0 for v in dg.VS} for c in dg.CANDS}
    deg = {"share_sum": 0.0, "any": 0, "ge_tail": 0, "diff_H2": 0, "diff_ZW": 0, "sample_sd0": 0}
    done = 0
    while done < n:
        m = min(CH, n - done)
        a, s = dg.simulate_degen(p, z, d, P, K, m, rng)
        vv, g, diff = dg.verdicts(a, s, C, K)
        for c in dg.CANDS:
            for v in dg.VS:
                cnt[c][v] += int(np.sum(vv[c] == v))
        gs = g[stat]
        deg["share_sum"] += float(gs.sum())
        deg["any"] += int((gs > 0).sum())
        deg["ge_tail"] += int((gs >= 0.005).sum())
        deg["diff_H2"] += int(diff["H2"].sum())
        deg["diff_ZW"] += int(diff["ZW"].sum())
        X = (s - 0.5) + (a - 0.5) / 2 if z < 0 else (s - 0.5) - (a - 0.5) / 2
        deg["sample_sd0"] += int((X.std(1, ddof=1) <= 1e-12).sum())
        done += m
    return cnt, deg


def fc_of(cz):
    return {c: {"FLIP_REL": cz[-0.5][c]["FLIP_REL"], "NO_EFFECT_REL": cz[0.5][c]["NO_EFFECT_REL"],
                "CHANCE_REL": max(cz[-0.5][c]["CHANCE_REL"], cz[0.5][c]["CHANCE_REL"])} for c in dg.CANDS}


def add(dst, src):
    for k, v in src.items():
        if isinstance(v, dict):
            add(dst[k], v)
        else:
            dst[k] += v


def run_point(pt, mode, C):
    if mode == "val":
        r = {z: draw(pt, z, 0, N_VAL, C) for z in ZS}
        return {"n": N_VAL, "stage2": False, "k": fc_of({z: r[z][0] for z in ZS}),
                "deg": {str(z): r[z][1] for z in ZS}}
    r = {z: draw(pt, z, 1, N1, C) for z in ZS}
    f1 = fc_of({z: r[z][0] for z in ZS})
    border = any(0.008 < f1["H2"][v] / N1 <= 0.012 for v in dg.VS)
    n = N1
    if border:
        for z in ZS:
            c2, d2 = draw(pt, z, 2, N2, C)
            add(r[z][0], c2)
            add(r[z][1], d2)
        n = N1 + N2
    return {"n": n, "stage2": border, "k": fc_of({z: r[z][0] for z in ZS}), "deg": {str(z): r[z][1] for z in ZS}}


if __name__ == "__main__":
    mode, W, NW = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    fn = HERE / "out" / f"{mode}_w{W}.json"
    print("pid", os.getpid(), mode, W, NW, flush=True)
    Cs = {P: dg.s2.boot_counts(P) for P in PS}
    res, t0, c0 = {}, time.time(), time.process_time()
    for j, pt in enumerate(POINTS):
        if j % NW != W:
            continue
        t1, c1 = time.time(), time.process_time()
        res[key(pt)] = run_point(pt, mode, Cs[pt[0]])
        res[key(pt)]["cpu_s"] = time.process_time() - c1
        res["_cpu_s_total"] = time.process_time() - c0
        json.dump(res, open(fn, "w"))
        print(key(pt), f"{time.time()-t1:.0f}s", flush=True)
    print("DONE", f"{time.time()-t0:.0f}s cpu {time.process_time()-c0:.0f}s", flush=True)
