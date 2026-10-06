"""PTE-C2B Flight 2 plan: RELAY-0019 and FLIP-0000, seed index 8 (C2A BASE ran idx 8; C2B production uses 0..7,
so no flight search is a production search). BRK starts for idx 8 are qualified exactly as in production.
usage: python make_flight2.py PLAN_C2B.json OUT.json"""
import json, os, sys
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import c2b_common as B
C = B.C
from prometheus.ananke import envs
P = json.load(open(sys.argv[1]))
cells = [c for c in P["cells"] if c["cell_id"] in ("RELAY-0019-eabcdf91", "FLIP-0000-adbab9bf")]
jobs = []
for c in cells:
    ph = C.Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
    plant = np.asarray(c["plant_genome"], dtype=np.int64)
    for k in (1, 2):
        g, att = B.broken_start(ph, env, c["role"], plant, k, c["cell_key"], 8)
        c["brk"][f"BRK{k}"]["8"] = {"genome": g.tolist(), "edits": att[-1]["edits"], "attempts": att, "n_attempts": len(att)}
        print(c["cell_id"], k, [a["status"] for a in att])
    for arm in ("BRK1", "B4X", "STEP", "BRK2"):
        jobs.append({"job_id": f"{c['cell_id']}|{arm}|08", "cell_id": c["cell_id"], "arm": arm, "idx": 8})
C.jdump(sys.argv[2], {"schema": "pte_c2b.plan.v1", "flight": True, "cells": cells, "jobs": jobs})
print(len(jobs))
