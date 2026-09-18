"""Run S1-S4 exactly as preregistered; one row per run/trial-cell to ledgers/.

python run_swarm.py [--quick]   (--quick: tiny counts, timing smoke only; never a result)
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sims  # noqa: E402

QUICK = "--quick" in sys.argv
L = HERE / ("ledgers_quick" if QUICK else "ledgers")
R = (lambda full, quick: quick if QUICK else full)

S1_D, S1_TAU = (2, 4, 8), (0.25, 0.5, 0.75, 1.0)
S1_V = tuple(round(0.05 * i, 2) for i in range(21))
S2A_P = (0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4)
S2A_Q = (0.0, 0.005, 0.01, 0.02, 0.05, 0.1)
S2A_T, S2A_K = (1.0, 0.8), (1, 10, 100, 5000)
S2B_H, S2B_K = (0.0, 0.001, 0.01, 0.05), tuple(2 ** i for i in range(11))
S3_G = (0.1, 0.25, 0.5)
S3_A = tuple(round(0.02 * i, 2) for i in range(31))
S4_P, S4_N, S4_RHO = (0.4, 0.45, 0.55, 0.6, 0.7), (1, 3, 9, 27, 81), (0.0, 0.2, 0.5)
MU = 0.005


def _seed(*parts) -> int:
    """Deterministic per-cell seed (Python's hash() is salted per process)."""
    return int(hashlib.sha256(json.dumps(parts).encode()).hexdigest()[:15], 16)


def s1_cell(args):
    d, tau, v = args
    rng = random.Random(_seed("S1", d, tau, v))
    sizes = [sims.s1_run(2000, d, tau, v, rng) for _ in range(R(400, 20))]
    return {"toy": "S1", "d": d, "tau": tau, "v": v, "N": 2000, "sizes": sizes}


def s2a_cell(args):
    p, q, t, k = args
    rng = random.Random(_seed("S2a", p, q, t, k))
    res = [sims.s2a_trial(p, q, t, k, rng) for _ in range(R(4000, 200))]
    return {"toy": "S2a", "p": p, "q": q, "t": t, "k": k, "n": len(res),
            "accepted_correct": res.count(1), "accepted_wrong": res.count(0), "none": res.count(-1)}


def s2b_cell(args):
    h, k = args
    rng = random.Random(_seed("S2b", h, k))
    n = R(4000, 200)
    return {"toy": "S2b", "p": 0.1, "h": h, "k": k, "n": n,
            "correct": sum(sims.s2b_trial(0.1, h, k, rng) for _ in range(n))}


def s3_cell(args):
    g, a = args
    rng = random.Random(_seed("S3a", g, a))
    return {"toy": "S3a", "g": g, "a": a, "M": 200, "T": 300, "mu": MU,
            "final_fractions": [sims.s3_run(200, g, a, MU, 300, rng) for _ in range(R(100, 10))]}


def s3p_cell(c):
    rng = random.Random(_seed("S3p", c))
    return {"toy": "S3p", "c": c, "M": 200, "mu": MU, "pre": 200, "post": 300,
            "runs": [sims.s3_persistence_run(200, MU, 200, 300, c, rng) for _ in range(R(100, 10))]}


def s4_cell(args):
    kind, p, n, rho = args
    rng = random.Random(_seed("S4", kind, p, n, rho))
    trials = R(20000, 500)
    if kind == "majority":
        c = sum(sims.s4_majority_trial(n, p, rho, rng) for _ in range(trials))
    else:
        c = sum(sims.s4_herding_trial(n, p, rng) for _ in range(trials))
    return {"toy": "S4", "kind": kind, "p": p, "n": n, "rho": rho, "trials": trials, "correct": c}


def write(name, rows):
    L.mkdir(exist_ok=True)
    with open(L / f"{name}.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")


def main():
    t0 = time.time()
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "."], capture_output=True, text=True,
                                cwd=HERE).stdout.strip())
    meta = {"quick": QUICK, "head_sha": sha, "dirty_tree": dirty, "runtime_s": {}}
    jobs = {
        "s1": (s1_cell, [(d, t, v) for d in S1_D for t in S1_TAU for v in S1_V]),
        "s2a": (s2a_cell, [(p, q, t, k) for p in S2A_P for q in S2A_Q for t in S2A_T for k in S2A_K]),
        "s2b": (s2b_cell, [(h, k) for h in S2B_H for k in S2B_K]),
        "s3a": (s3_cell, [(g, a) for g in S3_G for a in S3_A]),
        "s3p": (s3p_cell, [0.0, 0.02, 0.1]),
        "s4": (s4_cell, [("majority", p, n, r) for p in S4_P for n in S4_N for r in S4_RHO]
               + [("herding", p, n, 0.0) for p in (0.55, 0.6, 0.7) for n in S4_N]),
    }
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as pool:
        for name, (fn, args) in jobs.items():
            t = time.time()
            write(name, pool.map(fn, args, chunksize=1))
            meta["runtime_s"][name] = round(time.time() - t, 1)
            print(name, meta["runtime_s"][name], "s", flush=True)
    meta["total_s"] = round(time.time() - t0, 1)
    (L / "RUN_META.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
