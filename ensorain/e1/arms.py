"""E1 arm factory + parallel runner (PREREG_E1 s3)."""
import json
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import mem as M
from .life import live
from .world import World1

NON_TT = ("LRU", "KNN", "CP", "LOWRANK", "MLP")
TUNABLE = ("CP", "LOWRANK", "MLP", "TT_OBS", "TT_TUNED")


def make(arm, cap, world, seed, cfg=None):
    cfg = dict(cfg or {})
    if arm == "NOMEM":
        return M.NoMem(cap)
    if arm == "LRU":
        return M.LRU(cap)
    if arm == "KNN":
        return M.KNN(cap)
    if arm == "ORACLE":
        return M.Oracle(cap, world.x)
    if arm == "CP":
        return M.CP(cap, seed=seed, **cfg)
    if arm == "LOWRANK":
        return M.LowRank(cap, seed=seed, **cfg)
    if arm == "MLP":
        return M.MLP(cap, seed=seed, **cfg)
    if arm in ("TT_OBS", "TT_TUNED", "SMUGGLER"):
        order = tuple(cfg.pop("order", range(4))) if arm != "TT_OBS" else tuple(range(4))
        cfg.pop("order", None)
        prof = cfg.pop("ranks", None)
        ranks = M.fit_ranks(prof, cap) if prof else None
        cls = M.Smuggler if arm == "SMUGGLER" else M.TTAls
        return cls(cap, order=order, ranks=ranks, seed=seed, **cfg)
    if arm == "TT_LATENT":  # positive control: latent order, true ranks, TT_TUNED constants
        cfg.pop("order", None)
        cfg.pop("ranks", None)
        order = tuple(int(i) for i in np.argsort(world.perm))
        return M.TTAls(cap, order=order, ranks=M.fit_ranks((3, 3, 3), cap), seed=seed, **cfg)
    if arm == "TT_INJECT":  # PREREG s3: no learning
        m = M.inject_tt(world, cap, seed)
        m.sweeps = 0
        return m
    raise KeyError(arm)


def run_one(job):
    t0 = time.time()
    w = World1(job.get("class_seed", 0), job["inst_seed"], lam=job.get("lam", 0.0))
    ev = w.events()
    try:
        m = make(job["arm"], job["cap"], w, job["org_seed"], job.get("cfg"))
    except ValueError as ex:
        return dict(job, status="NA", reason=str(ex))
    try:
        r = live(w, m, ev, job.get("econ"))
    except M.AuditError as ex:
        return dict(job, status="AUDIT_REFUSED", reason=str(ex))
    if job.get("transplant"):
        w2 = World1(job.get("class_seed", 0), job["inst_seed"], relabel_seed=job["inst_seed"] + 7_000_000)
        ev2 = w2.events(seed_offset=1)
        fresh = make(job["arm"], job["cap"], w2, job["org_seed"] + 1000, job.get("cfg"))
        stop = job.get("transplant_events", 400)
        rc = live(w2, m, ev2, job.get("econ"), stop_at=stop)
        rf = live(w2, fresh, ev2, job.get("econ"), stop_at=stop)
        for pre, rr in (("tc_", rc), ("tf_", rf)):
            for k in ("ok_L1", "ok_L2", "n_L1", "n_L2", "reward", "r2_ho"):
                r[pre + k] = rr[k]
    r.update({k: v for k, v in job.items() if k != "cfg"})
    r["cfg"] = job.get("cfg")
    r["status"] = "OK"
    r["secs"] = round(time.time() - t0, 2)
    return r


def run_jobs(jobs, out_path, workers=None):
    workers = workers or int(os.environ.get("ENSORAIN_WORKERS", "16"))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex, open(out_path, "a") as f:
        for r in ex.map(run_one, jobs, chunksize=1):
            f.write(json.dumps(r, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o)) + "\n")
            f.flush()
            rows.append(r)
    return rows
