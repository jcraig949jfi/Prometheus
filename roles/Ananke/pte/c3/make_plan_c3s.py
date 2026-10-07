"""PTE-C3S plan: the 28 qualified C2C graded stones (PLAN_C2C.json; FLIP-0000 idx 2/4/5/7 stay unavailable) x arms
S8 / S32 / W8 / W32 = 112 jobs. Order: rounds by idx 0..7, FLIP cells interleaved, arms S8, S32, W8, W32.
Asserts: monitor worlds are disjoint from every held / train (M<=32, 36 gens) / final world of every C2C seed of these
cells, and from the C2C stone-qualification worlds.
usage: python make_plan_c3s.py OUT.json"""
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c3_common as K  # noqa: E402
C = K.C; X = K.X
from prometheus.ananke import assays  # noqa: E402
from prometheus.ananke.search import FINAL_NS, HELD_NS, TRAIN_NS  # noqa: E402

ARMS = ["S8", "S32", "W8", "W32"]
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2c", "PLAN_C2C.json")))
cells = [c for c in P["cells"] if c["role"] == "FLIP"]
jobs = []
for idx in range(8):
    for c in cells:
        if str(idx) not in c["stones"]:
            continue
        for a in ARMS:
            jobs.append({"job_id": f"{c['cell_id']}|{a}|{idx:02d}", "cell_id": c["cell_id"], "arm": a, "idx": idx})
mon, other = set(), set()
for c in cells:
    mon.update(K.monitor_seeds(c["cell_key"]))
    other.update(X.stone_qual_seeds(c["cell_key"]))
    for idx in range(8):
        s = X.search_seed(c["cell_key"], idx)
        other.update(assays.world_seeds(C.H_int(s, HELD_NS), C.M_HELD))
        other.update(assays.world_seeds(C.H_int(s, FINAL_NS), 16))
        for gen in range(36):
            other.update(assays.world_seeds(C.H_int(s, TRAIN_NS, gen), 32))
disj = {"monitor_n": len(mon), "other_n": len(other), "monitor_x_other": len(mon & other)}
print("disjointness", disj)
assert disj["monitor_x_other"] == 0
C.jdump(sys.argv[1], {"schema": "pte_c3s.plan.v1", "source_plan": "roles/Ananke/pte/c2c/PLAN_C2C.json",
                      "cells": cells, "jobs": jobs, "arms": ARMS, "disjointness": disj})
print("jobs", len(jobs))
