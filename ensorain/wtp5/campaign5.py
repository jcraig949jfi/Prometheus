"""WTP-05 campaign runner (PREREG_WTP05 s7): finish-in-place with durable checkpoints.

    python -m ensorain.wtp5.campaign5 <stage> --plan <plan.json> [--workers 3] [--max-wall-h H]

plan.json = {"budget": evals per run, "log_every": n, "cells": [[world_spec, arm], ...], "seeds": [...]}.
Each run checkpoints every log interval to ensorain/runs/wtp05/<stage>/ckpt/ (not tracked; regenerable);
a restart resumes every unfinished run from its checkpoint. Finished-run summaries are appended to
ensorain/runs/wtp05/<stage>/summaries_<k>of<n>.jsonl (tracked). --shard k/n splits the job list across
independent runner processes (e.g. one worker now, more when the CPU frees); resume reads every shard's file."""
import argparse
import json
import multiprocessing as mp
import os
import shutil
import sys
import time

import numpy as np
import psutil

from .search import Run, summary

ROOT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp05")


def _enc(x):
    if isinstance(x, np.ndarray):
        return np.round(x, 4).tolist()
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, (np.bool_,)):
        return bool(x)
    raise TypeError(type(x))


def _job(a):
    spec, arm, seed, budget, log_every, ckdir, max_wall = a[:7]
    from_ck, flat = (a[7:] + (None, False))[:2]        # 7-tuples from runners started before DEEP support
    os.nice(10) if os.nice(0) < 10 else None
    name = f"{spec}__{arm}__{seed}.pkl"
    path = os.path.join(ckdir, name)
    if not os.path.exists(path) and from_ck and os.path.exists(os.path.join(from_ck, name)):
        shutil.copy2(os.path.join(from_ck, name), path)        # continue from the earlier stage (finish in place)
    if os.path.exists(path):
        r = Run.load(path)
        r.path, r.log_every = path, log_every
    else:
        r = Run(spec, arm, seed, budget, ckdir, log_every=log_every)
    if budget > r.budget:
        r.budget, r.done = budget, False
    r.flat_stop = flat
    r.run(max_wall=max_wall)
    return summary(r)


def run(stage, plan, workers=3, max_wall_h=None, shard=(0, 1), from_stage=None, flat=False):
    d = os.path.join(ROOT, stage)
    ck = os.path.join(d, "ckpt")
    os.makedirs(ck, exist_ok=True)
    out = os.path.join(d, f"summaries_{shard[0]}of{shard[1]}.jsonl")
    done = set()
    for fn in os.listdir(d):
        if fn.startswith("summaries") and fn.endswith(".jsonl"):
            for line in open(os.path.join(d, fn)):
                r = json.loads(line)
                if r.get("done"):
                    done.add((r["spec"], r["arm"], r["seed"]))
    alljobs = [(spec, arm, int(s)) for spec, arm in plan["cells"] for s in plan["seeds"]]
    from_ck = os.path.join(ROOT, from_stage, "ckpt") if from_stage else None
    jobs = [(spec, arm, s, plan["budget"], plan.get("log_every", 2000), ck, None, from_ck, flat)
            for i, (spec, arm, s) in enumerate(alljobs) if i % shard[1] == shard[0] and (spec, arm, s) not in done]
    print(f"{stage}: {len(jobs)} runs, budget {plan['budget']} evals, {workers} workers", flush=True)
    t0 = time.time()
    deadline = t0 + max_wall_h * 3600 if max_wall_h else None
    with mp.get_context("spawn").Pool(workers, maxtasksperchild=4) as pool, open(out, "a") as fh:
        it, pending, n = iter(jobs), [], 0
        while True:
            while len(pending) < workers and psutil.virtual_memory().available / 2 ** 30 >= 3.0:
                if deadline and time.time() > deadline:
                    break
                j = next(it, None)
                if j is None:
                    break
                if deadline:
                    j = j[:6] + (max(60, deadline - time.time()),) + j[7:]
                pending.append(pool.apply_async(_job, (j,)))
            if not pending:
                break
            r = pending.pop(0).get()
            fh.write(json.dumps(r, default=_enc) + "\n")
            fh.flush()
            n += 1
            print(f"  {n}/{len(jobs)} {r['spec']} {r['arm']} s{r['seed']} rung {r['best_rung']} fit {r['best_fit']} "
                  f"evals {r['evals']} {time.time() - t0:.0f}s", flush=True)
    print(f"{stage}: finished {n} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-wall-h", type=float)
    ap.add_argument("--shard", default="0/1", help="k/n: run jobs with index %% n == k (separate summaries file)")
    ap.add_argument("--from-stage", help="continue each run from this stage's checkpoint (DEEP: screen)")
    ap.add_argument("--flat-stop", action="store_true", help="PREREG s7.3 flat-frontier stop (DEEP, EXTENDED)")
    a = ap.parse_args()
    k, n = map(int, a.shard.split("/"))
    run(a.stage, json.load(open(a.plan)), a.workers, a.max_wall_h, (k, n), a.from_stage, a.flat_stop)
    sys.exit(0)
