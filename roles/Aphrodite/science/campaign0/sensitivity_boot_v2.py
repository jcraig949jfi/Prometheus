"""CORRECTED sensitivity (a): lineage-bootstrap analysis with enough resamples. TIER 2.

Disclosed defect of the first run: summarize_boot used 300 resamples, so its
smallest p-value was 1/300; Holm across 16 contrasts multiplies it by 16 to
0.053 > 0.05, so the bootstrap arm could NEVER declare significance. Its
first-run recovery (~0 for every non-null world) measures that floor, not
the assay. This file re-simulates the IDENTICAL observations (same seeds as
run_c0.py) and applies the preregistered bootstrap analysis with 4000
resamples (floor 16/4000 = 0.004). The primary analysis is untouched.
Writes ledgers/c0_rows_boot_v2.jsonl.
"""
from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import assay as A  # noqa: E402
import worlds as W  # noqa: E402
from run_c0 import LS, R, seed  # noqa: E402
import random  # noqa: E402

NB = 4000


def boot_stats(x, delta, rng):
    x = np.asarray(x)
    n = len(x)
    reps = x[rng.integers(0, n, size=(NB, n))].mean(axis=1)
    mean = float(x.mean())
    p_sup = max(float((reps <= 0).mean()), 1 / NB)
    p_inf = max(float((reps >= 0).mean()), 1 / NB)
    lo, hi = np.quantile(reps, [0.05, 0.95])
    p_eq = 0.01 if (lo > -delta and hi < delta) else 0.99
    return mean, None, p_sup, p_inf, p_eq


def job(args):
    key, L, rep = args
    obs = W.simulate(W.WORLDS[key], L, random.Random(seed("main", key, L, rep)))
    rng = np.random.default_rng(seed("bootv2", key, L, rep) % (2 ** 63))
    stats = {k: boot_stats(A.lineage_values(obs, a, b), 0.03, rng) for k, (a, b) in A.CONTRASTS.items()}
    p_adj = A.holm({k: s[2] for k, s in stats.items()})
    v = {k: A.verdict(p_adj[k] < A.ALPHA, stats[k][3], stats[k][4]) for k in stats}
    base = A.analyse(obs)  # reuse the preregistered flag logic with bootstrap verdicts swapped in
    flags = set()
    if v["D_VAULT"] == "SUPERIOR":
        flags.add("TRANSFER")
    if v["D_DEV"] == "SUPERIOR" and v["D_VAULT"] in ("EQUIVALENT", "TRIVIAL", "INFERIOR"):
        flags.add("SPECIALIZATION")
    if v["D_MEM"] == "SUPERIOR":
        flags.add("MEMORY")
    if v["D_WORK"] == "SUPERIOR":
        flags.add("WORKER")
    if base["meter_lo"] > 1.05 and v["D_COMP"] == "SUPERIOR":
        flags.add("COMPUTE")
    r = {"verdicts": v, "flags": flags, "ambiguous": v["D_DEV"] == "SUPERIOR" and v["D_VAULT"] == "INDETERMINATE",
         "modules": {m for m in W.MODULES if v[f"NEC_{m}"] == "SUPERIOR" and v[f"SUF_{m}"] == "SUPERIOR"}}
    return {"world": key, "L": L, "rep": rep, "analysis": "boot_v2", "flags": sorted(flags),
            "ambiguous": r["ambiguous"], "recovered": A.recovered(key, r)}


if __name__ == "__main__":
    jobs = [(k, L, r) for k in W.WORLDS for L in LS for r in range(R)]
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as p, \
            open(HERE / "ledgers" / "c0_rows_boot_v2.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for row in p.imap_unordered(job, jobs, chunksize=8):
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    print("done", len(jobs))
