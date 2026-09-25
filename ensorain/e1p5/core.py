"""E1.5 compression headroom assay (PREREG_E1P5). Reuses E1 unchanged;
adds only post-life measurement: effective ranks, self-compression (no
retraining, truth never consulted), replay scoring.
"""
import itertools
import json
import os
import time

import numpy as np

from ensorain.e0.tt import tt_svd, n_params_for_ranks
from ensorain.e1 import mem as M
from ensorain.e1.arms import make, run_jobs as _unused  # noqa: F401  (env pinning side effect)
from ensorain.e1.life import live
from ensorain.e1.world import World1, NV, D

CAPS = (128, 160, 192, 224, 256, 320, 384, 512)
BUDGETS = (384, 320, 256, 224, 192, 160, 128)
COMPRESS_ARMS = ("TT_TUNED", "TT_LATENT", "LOWRANK")
WORKSPACE_FLOATS = NV ** D  # declared transient workspace for self-compression


def tt_own_dense(tt):
    t = tt.cores[0]
    for c in tt.cores[1:]:
        t = np.tensordot(t, c, axes=([-1], [0]))
    return t.reshape([NV] * D)  # axes in the TT's own order


def effective_ranks(tt, tol=1e-2):
    t = tt_own_dense(tt)
    out = []
    for k in range(1, D):
        s = np.linalg.svd(t.reshape(NV ** k, -1), compute_uv=False)
        out.append(int((s > tol * s[0]).sum()) if s[0] > 0 else 0)
    return out


def compress_tt(mem, b):
    """Round the learned TT to <= b floats by TT-SVD of its OWN dense tensor,
    choosing the rank triple (each <= trained rank) with least error to itself."""
    dense = tt_own_dense(mem.tt)
    best = None
    for r in itertools.product(*[range(1, x + 1) for x in mem.ranks]):
        if n_params_for_ranks(r, [NV] * D) > b:
            continue
        cores, _ = tt_svd(dense, max_rank=list(r))
        rec = cores[0]
        for c in cores[1:]:
            rec = np.tensordot(rec, c, axes=([-1], [0]))
        err = float(((rec.reshape(dense.shape) - dense) ** 2).sum())
        if best is None or err < best[0]:
            best = (err, r, cores)
    if best is None:
        return None
    _, r, cores = best
    out = M.TTAls(b, order=mem.order, ranks=tuple(c.shape[2] for c in cores[:-1]))
    for k, c in enumerate(cores):
        out.tt.cores[k] = c.copy()
    return out


def compress_lowrank(mem, b):
    k = b // 128
    if k < 1 or k >= mem.R:
        return None
    U, s, Vt = np.linalg.svd(mem.Ur @ mem.Vc.T, full_matrices=False)
    out = M.LowRank(max(b, 128 * k), part=mem.part, R=k)
    out.Ur = U[:, :k] * np.sqrt(s[:k])
    out.Vc = Vt[:k].T * np.sqrt(s[:k])
    return out


def replay(world, mem, events, tau=0.15):
    """Answer every lock of the stream with `mem`; reward without energy dynamics."""
    ok = {"L1": 0, "L2": 0, "L3s": 0, "L3h": 0}
    n = dict(ok)
    for ev in events:
        if ev[0] == "obs":
            continue
        if ev[0] == "L3":
            a, w, truth, ho = ev[1], ev[2], ev[3], ev[4]
            key = "L3h" if ho else "L3s"
            fa = np.repeat(np.asarray(a)[None, :], NV, 0)
            fa[:, world.ax["D"]] = np.arange(NV)
            ans = float(sum(wi * mem.predict(x) for wi, x in zip(w, fa)))
            sd = world.sd["L3"]
        else:
            key, truth, sd = ev[0], ev[3], world.sd[ev[0]]
            ans = mem.predict(ev[1])
        n[key] += 1
        ok[key] += int(abs(ans - truth) < tau * sd)
    return dict(reward=10.0 * sum(ok.values()), **{f"n_{k}": v for k, v in n.items()},
                **{f"ok_{k}": v for k, v in ok.items()})


def r2_ho(world, mem):
    p = mem.predict_many(world.addr)
    xf, ho = world.x.reshape(-1), world.heldout_cell
    y = xf[ho]
    return float(1 - ((y - p[ho]) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def run_one(job):
    t0 = time.time()
    w = World1(0, job["inst_seed"], lam=job.get("lam", 0.0))
    ev = w.events()
    try:
        m = make(job["arm"], job["cap"], w, job["org_seed"], job.get("cfg"))
    except ValueError as ex:
        return dict({k: v for k, v in job.items() if k != "cfg"}, cfg=job.get("cfg"), status="NA", reason=str(ex))
    r = live(w, m, ev, job.get("econ"))
    r.update({k: v for k, v in job.items() if k != "cfg"})
    r["cfg"] = job.get("cfg")
    if job.get("measure", True) and job.get("lam", 0.0) == 0.0:
        base = replay(w, M.NoMem(0), ev)
        r["replay_nomem"] = base["reward"]
        rp = replay(w, m, ev)
        r["replay_trained"] = rp["reward"]
        r["replay_trained_L2"] = rp["ok_L2"] / max(rp["n_L2"], 1)
        if job["arm"] in ("TT_TUNED", "TT_LATENT"):
            r["ranks_trained"] = list(m.ranks)
            r["ranks_effective"] = effective_ranks(m.tt)
        if job["arm"] in COMPRESS_ARMS:
            curve = []
            for b in BUDGETS:
                if b >= r["P_used"]:
                    continue
                cm = compress_tt(m, b) if job["arm"] != "LOWRANK" else compress_lowrank(m, b)
                if cm is None:
                    continue
                rc = replay(w, cm, ev)
                curve.append(dict(b=b, size=int(M.audit(cm, 10 ** 6)), r2_ho=r2_ho(w, cm),
                                  replay=rc["reward"], L2=rc["ok_L2"] / max(rc["n_L2"], 1),
                                  ranks=list(getattr(cm, "ranks", [getattr(cm, "R", 0)]))))
            r["compress_curve"] = curve
            r["workspace_floats"] = WORKSPACE_FLOATS
    r["scratch_samples"] = (job.get("econ") or {}).get("scratch", 128)
    r["status"] = "OK"
    r["secs"] = round(time.time() - t0, 2)
    return r


def run(jobs, out_path, workers=None):
    from concurrent.futures import ProcessPoolExecutor
    workers = workers or int(os.environ.get("ENSORAIN_WORKERS", "18"))
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex, open(out_path, "a") as f:
        for r in ex.map(run_one, jobs, chunksize=1):
            f.write(json.dumps(r, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o)) + "\n")
            f.flush()
            rows.append(r)
    return rows
