"""PTE-C5T plan (PREREG_PTE_C5T): arm C of C4 (R4 + OPDL with the frozen LIBRARY_C4.json), GATE at the admitted GATE
cells and FLIP at the admitted FLIP cells, idx 0..7, 144 generations (4x C4-T), M32.
Order: rounds by idx; cells interleaved; GATE before FLIP within a round.
usage: python make_plan_c5t.py PLAN_C4_T.json LIBRARY_C4.json OUT.json"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c4_common as K  # noqa: E402
C = K.C

T = json.load(open(sys.argv[1])); lib = json.load(open(sys.argv[2])); out = sys.argv[3]
adm = {(j["cell_id"], j["task"]) for j in T["jobs"]}
jobs = []
for idx in range(8):
    for c in T["cells"]:
        for task in ("GATE", "FLIP"):
            if (c["cell_id"], task) not in adm:
                continue
            jobs.append({"job_id": f"{c['cell_id']}|{task}|C5T|{idx:02d}", "cell_id": c["cell_id"], "task": task,
                         "arm": "C5T", "rep": "R4", "op": "OPDL", "idx": idx, "gens": 144})
plan = {"schema": "pte_c5t.plan.v1", "selector": T["selector"], "cells": T["cells"], "jobs": jobs,
        "library": lib["modules"], "library_provenance": lib["provenance"]}
C.jdump(out, plan)
print("jobs", len(jobs))
