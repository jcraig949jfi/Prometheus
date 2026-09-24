"""Offline learner check (dev seeds): feed iid noisy samples of X to a
memory, report R^2 over all cells after K samples. Separates learner
failure (B2) from world/economy effects."""
import sys, json
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from .world import World
from . import memories as M


def curve(args):
    kind, cap, lam, inst, kw = args
    w = World(0, inst, lam=lam)
    if kind == "TT_OBS":
        m = M.TTMem(cap, **kw)
    elif kind == "TT_LAT":
        m = M.TTMem(cap, order=tuple(int(i) for i in np.argsort(w.perm)), **kw)
    elif kind == "LOWRANK":
        m = M.LowRank(cap, **kw)
    elif kind == "RF":
        m = M.RF(cap, **kw)
    elif kind == "ADDITIVE":
        m = M.Additive(cap, **kw)
    rng = np.random.default_rng(inst)
    out = {}
    for k in range(1, 8001):
        v = int(rng.integers(len(w.x)))
        m.observe(w.addr[v], w.x[v] + rng.normal(0, 0.1))
        if k in (250, 500, 1000, 2000, 4000, 8000):
            p = m.predict_all(w.addr)
            out[k] = float(1 - ((w.x - p) ** 2).sum() / ((w.x - w.x.mean()) ** 2).sum())
    return dict(kind=kind, cap=cap, lam=lam, inst=inst, kw=kw, r2=out)


def main():
    specs = json.loads(sys.argv[1])
    jobs = []
    for s in specs:
        for inst in range(4):
            jobs.append((s["kind"], s["cap"], s.get("lam", 0.0), inst, s.get("kw", {})))
    with ProcessPoolExecutor(24) as ex:
        res = list(ex.map(curve, jobs))
    agg = {}
    for r in res:
        key = (r["kind"], r["cap"], r["lam"], json.dumps(r["kw"]))
        agg.setdefault(key, []).append(r["r2"])
    for key, v in agg.items():
        ks = sorted(v[0], key=int)
        med = [np.median([x[k] for x in v]) for k in ks]
        print(key, " ".join(f"{k}:{m:.2f}" for k, m in zip(ks, med)))
    with open("ensorain/runs/dev_offline.jsonl", "a") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
