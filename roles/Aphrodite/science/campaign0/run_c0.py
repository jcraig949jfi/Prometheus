"""Run the Campaign 0 calibration exactly as preregistered (PREREG_C0 sections 5-7). TIER 2.

python run_c0.py [--quick]   (--quick: tiny R, timing smoke only; never a result)
Writes ledgers/c0_rows.jsonl (one row per replicate experiment and analysis),
ledgers/C0_SUMMARY.json. The verdict is computed by summarize_c0.py from rows.
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
import assay  # noqa: E402
import worlds as W  # noqa: E402

QUICK = "--quick" in sys.argv
R = 10 if QUICK else 200
LS = (16, 32, 64)
MDE_SHIFTS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.6)
L_DIR = HERE / ("ledgers_quick" if QUICK else "ledgers")


def seed(*parts) -> int:
    return int(hashlib.sha256(json.dumps(parts).encode()).hexdigest()[:15], 16)


def job(args):
    """One (world, L, replicate): simulate once, analyse under every preregistered analysis."""
    tag, key, L, rep = args
    if tag == "main":
        world = W.WORLDS[key]
    elif tag == "mis":
        world = W.misspecified(W.WORLDS[key])
    else:  # "mde"
        world = W.mde_world(float(key))
    obs = W.simulate(world, L, random.Random(seed(tag, key, L, rep)))
    analyses = {"primary": dict(), "boot": dict(method="boot"), "delta0.02": dict(delta=0.02),
                "delta0.05": dict(delta=0.05), "noholm": dict(use_holm=False), "pseudo": dict(method="pseudo")}
    if tag != "main":
        analyses = {"primary": dict()}
    rows = []
    for name, kw in analyses.items():
        r = assay.analyse(obs, rng=random.Random(seed("boot", tag, key, L, rep)), **kw)
        wk = key if tag in ("main", "mis") else "W1"
        rows.append({"tag": tag, "world": key, "L": L, "rep": rep, "analysis": name,
                     "flags": sorted(r["flags"]), "ambiguous": r["ambiguous"], "modules": sorted(r["modules"]),
                     "recovered": assay.recovered(wk, r), "verdicts": r["verdicts"],
                     "means": {k: round(v, 5) for k, v in r["means"].items()},
                     "meter_lo": round(r["meter_lo"], 4),
                     "frontier": {str(b): round(v, 5) for b, v in r["frontier"].items()}})
    return rows


def main():
    t0 = time.time()
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "."], capture_output=True, text=True,
                                cwd=HERE).stdout.strip())
    jobs = [("main", k, L, r) for k in W.WORLDS for L in LS for r in range(R)]
    jobs += [("mis", k, L, r) for k in W.WORLDS for L in LS for r in range(R)]
    jobs += [("mde", str(s), L, r) for s in MDE_SHIFTS for L in LS for r in range(R)]
    L_DIR.mkdir(exist_ok=True)
    n = 0
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as pool, \
            open(L_DIR / "c0_rows.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for rows in pool.imap_unordered(job, jobs, chunksize=4):
            for row in rows:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
                n += 1
            fh.flush()
    meta = {"head_sha": sha, "dirty_tree": dirty, "quick": QUICK, "R": R, "Ls": LS, "rows": n,
            "jobs": len(jobs), "runtime_s": round(time.time() - t0, 1),
            "cells_per_lineage": len(W.CELLS), "families_per_cell": W.N_DEV,
            "tasks_per_family_per_cell": W.N_TASKS,
            "task_evaluations_per_lineage": len(W.CELLS) * W.N_DEV * W.N_TASKS}
    (L_DIR / "C0_RUN_META.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
