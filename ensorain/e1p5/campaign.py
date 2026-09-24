"""E1.5 campaign steps (PREREG_E1P5). python -m ensorain.e1p5.campaign <calibrate|tune|confirm>"""
import collections
import json
import sys

import numpy as np

from ensorain.e1.tune import ECON
from .core import CAPS, run

OUT = "ensorain/runs/"
SET_A, SET_B = range(30000, 30040), range(30100, 30140)
TUNABLE = ("CP", "LOWRANK", "MLP", "TT_TUNED")
N_CFG, N_WORLDS = 32, 4


def calibrate():
    grid = [dict(lam=l, sweeps=s, init_scale=0.5) for l in (3, 10, 30, 100) for s in (5, 10, 20)]
    jobs = [dict(arm="TT_LATENT", cap=c, inst_seed=i, org_seed=0, econ=ECON, cfg=g, gi=gi, measure=False)
            for c in CAPS for gi, g in enumerate(grid) for i in range(300, 306)]
    rows = run(jobs, OUT + "e1p5_calibrate.jsonl")
    agg = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "OK":
            agg[(r["cap"], r["gi"])].append(r["r2_ho"])
    out = {}
    for c in CAPS:
        best = max(range(len(grid)), key=lambda gi: np.median(agg[(c, gi)]) if agg[(c, gi)] else -1e9)
        out[str(c)] = dict(cfg=grid[best], dev_median_r2_ho=float(np.median(agg[(c, best)])))
        print(c, out[str(c)])
    json.dump(out, open(OUT + "e1p5_latent_constants.json", "w"), indent=1)


def sample(arm, cap, g):
    c = dict(lam=float(np.exp(g.uniform(np.log(0.3), np.log(100)))),
             sweeps=int(g.choice([2, 5, 10, 20])), init_scale=float(g.choice([0.3, 0.5, 1.0])))
    if arm == "TT_TUNED":
        c["ranks"] = [int(x) for x in g.integers(1, 9, size=3)]
        c["order"] = [int(x) for x in g.permutation(4)]
    elif arm == "CP":
        c["R"] = int(g.integers(1, cap // 32 + 1))
    elif arm == "LOWRANK":
        c["part"] = int(g.integers(3))
        c["R"] = int(g.integers(1, cap // 128 + 1))
    elif arm == "MLP":
        c = dict(H=int(g.integers(1, (cap - 1) // 34 + 1)),
                 lr=float(np.exp(g.uniform(np.log(0.01), np.log(0.3)))),
                 lam=float(np.exp(g.uniform(np.log(1e-4), np.log(1e-1)))),
                 epochs=int(g.choice([5, 10, 20, 40])))
    return c


def tune():
    jobs, cfgs = [], {}
    for ci, cap in enumerate(CAPS):
        g = np.random.default_rng(424243 + cap)
        worlds = [3000 + 4 * ci + k for k in range(N_WORLDS)]
        for w in worlds:
            jobs.append(dict(arm="NOMEM", cap=cap, inst_seed=w, org_seed=0, econ=ECON, key=["NOMEM", cap, -1], measure=False))
        for arm in TUNABLE:
            for i in range(N_CFG):
                c = sample(arm, cap, g)
                cfgs[(arm, cap, i)] = c
                for w in worlds:
                    jobs.append(dict(arm=arm, cap=cap, inst_seed=w, org_seed=0, econ=ECON, cfg=c, key=[arm, cap, i], measure=False))
    rows = run(jobs, OUT + "e1p5_tune.jsonl")
    nom = {(r["cap"], r["inst_seed"]): r["U"] for r in rows if r["arm"] == "NOMEM"}
    eff = collections.defaultdict(list)
    for r in rows:
        if r["arm"] == "NOMEM":
            continue
        k = tuple(r["key"])
        eff[k].append((r["U"] - nom[(r["cap"], r["inst_seed"])]) / max(r["P_used"], 1) if r["status"] == "OK" else -np.inf)
    champs = {}
    for arm in TUNABLE:
        for cap in CAPS:
            ks = [k for k in eff if k[0] == arm and k[1] == cap and np.all(np.isfinite(eff[k]))]
            if not ks:
                champs[f"{arm}@{cap}"] = None
                continue
            b = max(ks, key=lambda k: np.mean(eff[k]))
            champs[f"{arm}@{cap}"] = dict(cfg=cfgs[b], train_eff=float(np.mean(eff[b])))
            print(f"{arm:9s} {cap:4d} {np.mean(eff[b]):8.3f} {cfgs[b]}")
    json.dump(champs, open(OUT + "e1p5_champions.json", "w"), indent=1)


def confirm():
    ch = json.load(open(OUT + "e1p5_champions.json"))
    lat = json.load(open(OUT + "e1p5_latent_constants.json"))
    arms = ("NOMEM", "LRU", "KNN", "CP", "LOWRANK", "MLP", "TT_TUNED", "TT_LATENT", "ORACLE")

    def cfg(a, c):
        if a in TUNABLE:
            x = ch.get(f"{a}@{c}")
            return None if x is None else x["cfg"]
        if a == "TT_LATENT":
            return lat[str(c)]["cfg"]
        return None
    jobs = []
    for set_name, insts in (("A", SET_A), ("B", SET_B)):
        for cap in CAPS:
            for a in arms:
                if a in TUNABLE and cfg(a, cap) is None:
                    continue
                for i in insts:
                    for o in (0, 1):
                        jobs.append(dict(arm=a, cap=cap, lam=0.0, inst_seed=i, org_seed=o, econ=ECON, cfg=cfg(a, cap), set=set_name))
    for cap in (192, 384):
        for a in arms:
            if a in TUNABLE and cfg(a, cap) is None:
                continue
            for i in SET_A:
                for o in (0, 1):
                    jobs.append(dict(arm=a, cap=cap, lam=1.0, inst_seed=i, org_seed=o, econ=ECON, cfg=cfg(a, cap), set="A"))
    run(jobs, OUT + "e1p5_confirm.jsonl")


if __name__ == "__main__":
    {"calibrate": calibrate, "tune": tune, "confirm": confirm}[sys.argv[1]]()
