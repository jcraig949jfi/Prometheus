"""Run a grid of (world ratio, seed, cap, arm) and write one JSONL row per run.

Usage: python -B -m chiasma.sweep <out_dir> <seed> [<seed> ...] [--caps 1000,3000,10000]
       [--ratios R21,R12,R11] [--arms O1,O2,...] [--full] [--procs 8]

Rows carry the endpoints, summary and receipt sha256; --full also writes every
receipt (with checkpoints) to <out_dir>/receipts/. CEIL ignores the cap and runs
once per (ratio, seed).
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

from .organisms import ARMS
from .runner import canonical, run
from .world import WorldSpec, make_world

RATIOS = {"R21": dict(n_ydep=16, n_decoy=8), "R11": dict(n_ydep=12, n_decoy=12),
          "R12": dict(n_ydep=8, n_decoy=16)}


def job(args):
    ratio, seed, cap, arm, full_dir = args
    t0 = time.process_time()
    w = make_world(WorldSpec(**RATIOS[ratio]), seed)
    r = run(w, arm, cap)
    cpu_ms = int((time.process_time() - t0) * 1000)
    if full_dir:
        fn = "{}_{}_{}_{}.json".format(ratio, seed, cap if cap is not None else "NONE", arm)
        with open(os.path.join(full_dir, fn), "wb") as fh:
            fh.write(canonical(r))
    return {"ratio": ratio, "seed": seed, "cap": r["cap"], "arm": arm,
            "world_sha256": r["world_sha256"], "receipt_sha256": r["receipt_sha256"],
            "endpoints": r["endpoints"], "summary": r["summary"], "cpu_ms": cpu_ms}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("seeds", nargs="+", type=int)
    ap.add_argument("--caps", default="1000,3000,10000")
    ap.add_argument("--ratios", default="R21,R11,R12")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    full_dir = None
    if a.full:
        full_dir = os.path.join(a.out_dir, "receipts")
        os.makedirs(full_dir, exist_ok=True)
    caps = [int(c) for c in a.caps.split(",")]
    jobs = []
    for ratio in a.ratios.split(","):
        for seed in a.seeds:
            for arm in a.arms.split(","):
                for cap in ([None] if arm == "CEIL" else caps):
                    jobs.append((ratio, seed, cap, arm, full_dir))
    out = os.path.join(a.out_dir, "rows.jsonl")
    with Pool(a.procs) as pool, open(out, "w", encoding="utf-8", newline="\n") as fh:
        for row in pool.imap_unordered(job, jobs):
            fh.write(canonical(row).decode() + "\n")
            fh.flush()
    print("wrote {} rows to {}".format(len(jobs), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
