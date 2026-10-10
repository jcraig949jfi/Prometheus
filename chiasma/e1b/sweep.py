"""E1b grid: (world, seed, cap, arm) -> one JSONL row per run.

Usage: python -B -m chiasma.e1b.sweep <out_dir> <seed> [<seed> ...]
       [--worlds H:R21,H:R11,H:R12,H3] [--caps 600,1000,3000] [--caps-h3 1800,3000,9000]
       [--arms O1,...] [--pevict] [--full] [--procs 8]
Uncapped arms (O3U) run once per (world, seed). PW-H3 has its own caps: its positive
geometry P is about 3x PW-H's (dev seed 910001: 1442 vs 481 bytes at the end of F), so
PW-H's caps would leave P alone over budget.
"""
import argparse
import os
import sys
import time
from multiprocessing import Pool

from ..runner import canonical
from ..sweep import RATIOS
from ..world import WorldSpec, make_world
from .arms import E1B_ARMS, UNCAPPED
from .run import run
from .world_d import WorldSpecD, make_world_d
from .world_h3 import WorldSpecH3, make_world_h3

WORLDS = ["H:R21", "H:R11", "H:R12", "H3"]


def build(world: str, seed: int):
    if world == "D":
        return make_world_d(WorldSpecD(), seed)
    if world == "Dm":
        return make_world_d(WorldSpecD(marker=True), seed)
    if world == "H3":
        return make_world_h3(WorldSpecH3(), seed)
    fam, ratio = world.split(":")
    assert fam == "H", world
    return make_world(WorldSpec(**RATIOS[ratio]), seed)


def job(args):
    world, seed, cap, arm, full_dir, pevict = args
    t0 = time.process_time()
    r = run(build(world, seed), arm, cap, pevict=pevict)
    cpu_ms = int((time.process_time() - t0) * 1000)
    if full_dir:
        fn = "{}_{}_{}_{}{}.json".format(world.replace(":", "-"), seed, r["cap"], arm, "_pe" if pevict else "")
        with open(os.path.join(full_dir, fn), "wb") as fh:
            fh.write(canonical(r))
    return {"world": world, "seed": seed, "cap": r["cap"], "arm": arm, "pevict": pevict,
            "world_sha256": r["world_sha256"], "receipt_sha256": r["receipt_sha256"],
            "endpoints": r["endpoints"], "summary": r["summary"], "cpu_ms": cpu_ms}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("seeds", nargs="+", type=int)
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--caps", default="600,1000,3000")
    ap.add_argument("--caps-h3", default="1800,3000,9000")
    ap.add_argument("--caps-d", default="")
    ap.add_argument("--arms", default=",".join(E1B_ARMS))
    ap.add_argument("--pevict", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    full_dir = None
    if a.full:
        full_dir = os.path.join(a.out_dir, "receipts")
        os.makedirs(full_dir, exist_ok=True)
    caps_h = [int(c) for c in a.caps.split(",")]
    caps_h3 = [int(c) for c in a.caps_h3.split(",")]
    caps_d = [int(c) for c in a.caps_d.split(",")] if a.caps_d else []
    jobs = []
    for world in a.worlds.split(","):
        caps = caps_h3 if world == "H3" else caps_d if world in ("D", "Dm") else caps_h
        for seed in a.seeds:
            for arm in a.arms.split(","):
                for cap in ([None] if arm in UNCAPPED else caps):
                    jobs.append((world, seed, cap, arm, full_dir, a.pevict))
    out = os.path.join(a.out_dir, "rows.jsonl")
    with Pool(a.procs) as pool, open(out, "w", encoding="utf-8", newline="\n") as fh:
        for row in pool.imap_unordered(job, jobs):
            fh.write(canonical(row).decode() + "\n")
            fh.flush()
    print("wrote {} rows to {}".format(len(jobs), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
