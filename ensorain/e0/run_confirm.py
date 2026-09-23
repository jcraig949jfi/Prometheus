"""Confirmatory runs M1-M4 (PREREG part 2 s5). Instances 10000-10039.
Usage: python -m ensorain.e0.run_confirm <M1|M2|M3|M4>"""
import json, sys
from .arms import run_jobs, load_tuned
from .tune import ECON

INST = range(10000, 10040)
ORGS = (0, 1)
BASE_ARMS = ["RANDOM", "NOMEM", "LRU", "HASH", "KNN", "ADDITIVE", "RF", "LOWRANK",
             "TT_FIXED", "TT_TUNED", "TT_PLANTED", "DICT_UNCAP", "ORACLE", "TT_SVD_INJECT"]


def genome(cap):
    with open(f"ensorain/runs/genome_c0_cap{cap}.json") as f:
        return json.load(f)["genome"]


def jobs_for(which):
    tuned = load_tuned()
    J = []
    def add(arm, cap, lam, cls=0, econ=ECON, g=None):
        for i in INST:
            for o in ORGS:
                J.append(dict(arm=arm, cap=cap, lam=lam, class_seed=cls, inst_seed=i, org_seed=o,
                              econ=econ, tuned=tuned, genome=g, M=which))
    if which == "M1":
        for lam in (0.0, 1.0):
            for cap in (48, 96, 168, 384, 4096):
                for a in BASE_ARMS:
                    add(a, cap, lam)
            for cap in (96, 168):
                add("TT_EVOLVED", cap, lam, g=genome(cap))
    elif which == "M2":
        for lam in (0.25, 0.5, 0.75):
            for a in ("TT_TUNED", "LRU", "HASH", "KNN", "ADDITIVE", "RF", "LOWRANK"):
                add(a, 168, lam)
    elif which == "M3":
        for cap in (96, 168):
            add("TT_TUNED", cap, 0.0, cls=1)
            add("TT_EVOLVED", cap, 0.0, cls=1, g=genome(cap))
    elif which == "M4":
        for lam in (0.0, 1.0):
            for a in BASE_ARMS:
                add(a, 168, lam, econ=dict(ECON, kappa=0.0))
    return J


if __name__ == "__main__":
    w = sys.argv[1]
    run_jobs(jobs_for(w), f"ensorain/runs/confirm_{w}.jsonl")
