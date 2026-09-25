"""Equal-budget random-search tuning (PREREG_E1 part 2 s3), training seeds only.
python -m ensorain.e1.tune"""
import collections
import json
import numpy as np

from .arms import run_jobs

CAPS = (96, 128, 192, 384)
ARMS = ("CP", "LOWRANK", "MLP", "TT_OBS", "TT_TUNED")
ECON = dict(energy0=400.0, metabolism=0.5, reward=10.0, tau=0.15, kappa=5e-6, budget=3e7, scratch=128)
N_CFG, N_WORLDS = 24, 4


def sample(arm, cap, g):
    c = dict(lam=float(np.exp(g.uniform(np.log(0.3), np.log(100)))),
             sweeps=int(g.choice([2, 5, 10, 20])),
             init_scale=float(g.choice([0.3, 0.5, 1.0])))
    if arm in ("TT_OBS", "TT_TUNED"):
        c["ranks"] = [int(x) for x in g.integers(1, 7, size=3)]
        if arm == "TT_TUNED":
            c["order"] = [int(x) for x in g.permutation(4)]
    elif arm == "CP":
        c["R"] = int(g.integers(1, cap // 32 + 1))
    elif arm == "LOWRANK":
        c["part"] = int(g.integers(3))
        c["R"] = int(g.integers(1, max(cap // 128, 1) + 1))
    elif arm == "MLP":
        c = dict(H=int(g.integers(1, (cap - 1) // 34 + 1)),
                 lr=float(np.exp(g.uniform(np.log(0.01), np.log(0.3)))),
                 lam=float(np.exp(g.uniform(np.log(1e-4), np.log(1e-1)))),
                 epochs=int(g.choice([5, 10, 20, 40])))
    return c


def main():
    jobs = []
    cfgs = {}
    for ci_cap, cap in enumerate(CAPS):
        g = np.random.default_rng(31337 + cap)
        worlds = [1000 + 4 * ci_cap + k for k in range(N_WORLDS)]
        for w in worlds:
            jobs.append(dict(arm="NOMEM", cap=cap, inst_seed=w, org_seed=0, econ=ECON, key=("NOMEM", cap, -1)))
        for arm in ARMS:
            for i in range(N_CFG):
                c = sample(arm, cap, g)
                cfgs[(arm, cap, i)] = c
                for w in worlds:
                    jobs.append(dict(arm=arm, cap=cap, inst_seed=w, org_seed=0, econ=ECON, cfg=c, key=(arm, cap, i)))
    rows = run_jobs(jobs, "ensorain/runs/e1_tune.jsonl")
    nomem = {(r["cap"], r["inst_seed"]): r["U"] for r in rows if r["arm"] == "NOMEM"}
    eff = collections.defaultdict(list)
    for r in rows:
        if r["arm"] == "NOMEM":
            continue
        k = tuple(r["key"])
        if r["status"] != "OK":
            eff[k].append(float("-inf"))
            continue
        eff[k].append((r["U"] - nomem[(r["cap"], r["inst_seed"])]) / max(r["P_used"], 1))
    champs = {}
    for arm in ARMS:
        for cap in CAPS:
            ks = [k for k in eff if k[0] == arm and k[1] == cap and np.all(np.isfinite(eff[k]))]
            if not ks:
                champs[f"{arm}@{cap}"] = None
                print(arm, cap, "NA")
                continue
            best = max(ks, key=lambda k: np.mean(eff[k]))
            champs[f"{arm}@{cap}"] = dict(cfg=cfgs[best], train_eff=float(np.mean(eff[best])))
            print(f"{arm:9s} {cap:4d} EFF {np.mean(eff[best]):8.3f} {cfgs[best]}")
    with open("ensorain/runs/e1_champions.json", "w") as f:
        json.dump(champs, f, indent=1)


if __name__ == "__main__":
    main()
