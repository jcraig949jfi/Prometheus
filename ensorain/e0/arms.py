"""Arm factory and a parallel runner that writes JSONL rows (PREREG_E0 s3)."""
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import memories as M
from .life import live
from .world import World, D

ARMS = ("RANDOM", "NOMEM", "LRU", "HASH", "KNN", "ADDITIVE", "RF", "LOWRANK",
        "TT_FIXED", "TT_TUNED", "TT_EVOLVED", "TT_PLANTED", "DICT_UNCAP", "ORACLE", "TT_SVD_INJECT")

TT_FIXED_CONST = dict(lr=0.3, init_scale=0.8, buf_frac=0.0, replay=0)  # dev round 2 best joint-NLMS constants
TT_TUNED_CONST = None  # frozen in PREREG part 2 (dev-seed grid); set by load_tuned()


def load_tuned(path=None):
    path = path or os.path.join(os.path.dirname(__file__), "tt_tuned.json")
    with open(path) as f:
        return json.load(f)


def make(arm, cap, world, seed, genome=None, tuned=None):
    """Returns (memory, audit_cap, econ_overrides)."""
    if arm == "RANDOM":
        return M.NoMem(0), 0, dict(epsilon=1.0)
    if arm == "NOMEM":
        return M.NoMem(0), 0, {}
    if arm == "LRU":
        return M.LRU(cap), cap, {}
    if arm == "HASH":
        return M.Hash(cap), cap, {}
    if arm == "KNN":
        return M.KNN(cap), cap, {}
    if arm == "ADDITIVE":
        return M.Additive(cap), cap, {}
    if arm == "RF":
        return M.RF(cap, seed=seed), cap, {}
    if arm == "LOWRANK":
        return M.LowRank(cap, seed=seed), cap, {}
    if arm == "TT_FIXED":
        return M.TTMem(cap, seed=seed, **TT_FIXED_CONST), cap, {}
    if arm == "TT_TUNED":
        t = dict(tuned or load_tuned())
        eps = t.pop("epsilon", None)
        return M.TTMem(cap, seed=seed, **t), cap, ({} if eps is None else dict(epsilon=eps))
    if arm == "TT_PLANTED":  # positive control: latent order, true ranks (if they fit)
        # PREREG part 2 A3: TT_TUNED learning constants, no buffer, so true ranks fit
        order = tuple(int(i) for i in np.argsort(world.perm))
        t = dict(tuned or load_tuned())
        eps = t.pop("epsilon", None)
        t.pop("order", None)
        t.update(buf_frac=0.0, replay=0)
        return M.TTMem(cap, order=order, seed=seed, **t), cap, ({} if eps is None else dict(epsilon=eps))
    if arm == "TT_EVOLVED":
        g = dict(genome)
        eps = g.pop("epsilon", None)
        return M.TTMem(cap, seed=seed, **g), cap, ({} if eps is None else dict(epsilon=eps))
    if arm == "DICT_UNCAP":
        return M.DictUncap(cap), cap, {}
    if arm == "ORACLE":
        return M.Oracle(cap, world.x), cap, {}
    if arm == "TT_SVD_INJECT":  # cheat control 2: true field compressed into a legal TT
        return inject_tt(world, cap, seed), cap, {}
    raise KeyError(arm)


def inject_tt(world, cap, seed):
    """TT-SVD of the TRUE field in the latent order, truncated to fit the cap."""
    from .tt import tt_svd
    order = tuple(int(i) for i in np.argsort(world.perm))
    mem = M.TTMem(cap, order=order, seed=seed)
    cores, ranks = tt_svd(np.transpose(world.dense_obs(), order), max_rank=list(mem.ranks))
    for k, c in enumerate(cores):
        mem.tt.cores[k][...] = 0.0
        a, n, b = c.shape
        mem.tt.cores[k][:a, :, :b] = c
    return mem


def run_one(job):
    t0 = time.time()
    w = World(job["class_seed"], job["inst_seed"], lam=job.get("lam", 0.0))
    try:
        mem, acap, eo = make(job["arm"], job["cap"], w, job["org_seed"], job.get("genome"), job.get("tuned"))
    except ValueError as ex:
        return dict(job, status="NA", reason=str(ex))
    econ = dict(job.get("econ") or {}, **eo)
    r = live(w, mem, acap, seed=job["org_seed"] * 7919 + job["inst_seed"], econ=econ)
    r.update(job)
    r["status"] = "OK"
    r["secs"] = round(time.time() - t0, 3)
    return r


def run_jobs(jobs, out_path, workers=24):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex, open(out_path, "a") as f:
        for r in ex.map(run_one, jobs, chunksize=1):
            f.write(json.dumps(r, default=float) + "\n")
            f.flush()
            rows.append(r)
    return rows
