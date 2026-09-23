"""E1 confirmatory runs (PREREG_E1 part 2 s4). python -m ensorain.e1.run_confirm <C1|C2|C3|C4>"""
import json
import sys

from .arms import run_jobs
from .tune import ECON

INST = range(20000, 20040)
ORGS = (0, 1)
CAPS = (96, 128, 192, 384)
C1_ARMS = ("NOMEM", "LRU", "KNN", "CP", "LOWRANK", "MLP", "TT_OBS", "TT_TUNED", "TT_LATENT", "TT_INJECT", "ORACLE")
LEARNING = ("LRU", "KNN", "CP", "LOWRANK", "MLP", "TT_OBS", "TT_TUNED", "TT_LATENT")


def champions():
    with open("ensorain/runs/e1_champions.json") as f:
        return json.load(f)


def cfg_for(arm, cap, ch):
    if arm in ("CP", "LOWRANK", "MLP", "TT_OBS", "TT_TUNED"):
        c = ch.get(f"{arm}@{cap}")
        return None if c is None else c["cfg"]
    if arm == "TT_LATENT":
        c = ch.get(f"TT_TUNED@{cap}")
        return None if c is None else {k: c["cfg"][k] for k in ("lam", "sweeps", "init_scale")}
    return None


def jobs_for(which):
    ch = champions()
    J = []

    def add(arm, cap, lam=0.0, econ=ECON, **kw):
        if arm in ("CP", "LOWRANK", "MLP", "TT_OBS", "TT_TUNED", "TT_LATENT") and cfg_for(arm, cap, ch) is None:
            return
        for i in INST:
            for o in ORGS:
                J.append(dict(arm=arm, cap=cap, lam=lam, inst_seed=i, org_seed=o, econ=econ,
                              cfg=cfg_for(arm, cap, ch), C=which, **kw))

    if which == "C1":
        for lam in (0.0, 1.0):
            for cap in CAPS:
                for a in C1_ARMS:
                    add(a, cap, lam)
    elif which == "C2":
        for a in LEARNING:
            add(a, 192, 0.0, transplant=True)
    elif which == "C3":
        J.append(dict(arm="SMUGGLER", cap=192, lam=0.0, inst_seed=20000, org_seed=0, econ=ECON,
                      cfg=cfg_for("TT_TUNED", 192, ch), C=which))
    elif which == "C4":
        for mult in (0.0, 4.0):
            e = dict(ECON, kappa=ECON["kappa"] * mult)
            for cap in (128, 192):
                for a in ("NOMEM", "LRU", "KNN", "CP", "LOWRANK", "MLP", "TT_OBS", "TT_TUNED"):
                    add(a, cap, 0.0, econ=e, kappa_mult=mult)
    return J


if __name__ == "__main__":
    w = sys.argv[1]
    run_jobs(jobs_for(w), f"ensorain/runs/e1_confirm_{w}.jsonl")
