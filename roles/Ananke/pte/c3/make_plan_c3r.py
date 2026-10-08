"""PTE-C3R plans. usage: python make_plan_c3r.py ADMISSION.json SELECTOR(M8|M32) STAGE(1|2) OUT.json [STATE_DIR]

Cells: the 4 admitted FLIP cells (PLAN_C2C.json), every representation admissible (rep_admission.json).
Searches: idx 0..7 per cell per arm (32 per arm).
Order (both stages): rounds by idx 0..7; within a round FLIP cells interleaved; arms in the order R4, R3, R1, R2, R5, R0
(the strongest generic arms first, so a wall censors the highest idx of every arm, starting with R0).
Stage 1: all 6 arms x 32 to gen 36. Stage 2: the same 192 trajectories continued to gen 144 (if the selector is M32,
stage 2 is limited to R4, R3, R0 -- declared before any production result).
"""
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c3r_common as R  # noqa: E402
C = R.C

ARM_ORDER = ["R4", "R3", "R1", "R2", "R5", "R0"]
adm = json.load(open(sys.argv[1])); selector = sys.argv[2]; stage = int(sys.argv[3]); out = sys.argv[4]
state_dir = sys.argv[5] if len(sys.argv) > 5 else None
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2c", "PLAN_C2C.json")))
cells = []
for c in [x for x in P["cells"] if x["role"] == "FLIP"]:
    cc = {k: c[k] for k in ("cell_id", "family", "role", "i", "physics", "env", "plant_name", "plant_genome", "cell_key")}
    cc["rep_plants"] = {}
    for rep in R.REPS:
        a = adm[f"{c['cell_id']}|{rep}"]
        assert a["admissible"], (c["cell_id"], rep)
        cc["rep_plants"][rep] = a["plant_genome"]
    cells.append(cc)
arms = ARM_ORDER if not (stage == 2 and selector == "M32") else ["R4", "R3", "R0"]
jobs = []
for idx in range(8):
    for c in cells:
        for rep in arms:
            j = {"job_id": f"{c['cell_id']}|{rep}|{idx:02d}|s{stage}", "cell_id": c["cell_id"], "rep": rep, "idx": idx,
                 "stage": stage}
            if stage == 2:
                j["state_dir"] = state_dir
            jobs.append(j)
sel = {"M": 32} if selector == "M32" else {"M": 8}
C.jdump(out, {"schema": "pte_c3r.plan.v1", "stage": stage, "selector": sel, "cells": cells, "jobs": jobs,
              "arm_order": arms, "reps": R.REPS})
print("jobs", len(jobs), "selector", sel)
