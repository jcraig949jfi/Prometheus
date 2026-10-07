"""PTE-C4 plans.
  python make_plan_c4.py L ADMISSION.json SELECTOR(M8|M32) REP OUT.json
      Library stage: the ONE-STAGE tasks RELAY1H and HOLD at the 4 FLIP cells, idx 0..7, rep REP, operator OPD,
      36 generations (64 searches). Order: rounds by idx, cells interleaved, tasks RELAY1H, HOLD.
  python make_plan_c4.py T ADMISSION.json SELECTOR REP LIBRARY.json OUT.json
      Target stage: the TWO-STAGE tasks GATE and FLIP at every admitted (cell, task), idx 0..7, arms
        A = (R5, OP0)   capacity + persistent register, no duplication, no library
        B = (REP, OPD)  duplication-and-divergence
        C = (REP, OPDL) duplication + frozen one-stage library insertion
      36 generations. Order: rounds by idx; cells interleaved; tasks GATE, FLIP; arms C, B, A.
"""
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c4_common as K  # noqa: E402
C = K.C

mode = sys.argv[1]
adm = json.load(open(sys.argv[2])); selector = sys.argv[3]; rep = sys.argv[4]
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2c", "PLAN_C2C.json")))
cells = [{k: c[k] for k in ("cell_id", "physics", "env", "cell_key", "plant_genome")} for c in P["cells"] if c["role"] == "FLIP"]
sel = {"M": 32} if selector == "M32" else {"M": 8}
jobs = []
if mode == "L":
    out = sys.argv[5]
    for idx in range(8):
        for c in cells:
            for task in ("RELAY1H", "HOLD"):
                if not adm[f"{c['cell_id']}|{task}"]["admitted"]:
                    continue
                jobs.append({"job_id": f"{c['cell_id']}|{task}|{rep}|OPD|{idx:02d}", "cell_id": c["cell_id"],
                             "task": task, "rep": rep, "op": "OPD", "idx": idx, "gens": 36})
    plan = {"schema": "pte_c4.plan.L.v1", "selector": sel, "cells": cells, "jobs": jobs, "library": []}
else:
    lib = json.load(open(sys.argv[5])); out = sys.argv[6]
    arms = [("C", rep, "OPDL"), ("B", rep, "OPD"), ("A", "R5", "OP0")]
    for idx in range(8):
        for c in cells:
            for task in ("GATE", "FLIP"):
                if not adm[f"{c['cell_id']}|{task}"]["admitted"]:
                    continue
                for arm, r, op in arms:
                    jobs.append({"job_id": f"{c['cell_id']}|{task}|{arm}|{idx:02d}", "cell_id": c["cell_id"],
                                 "task": task, "arm": arm, "rep": r, "op": op, "idx": idx, "gens": 36})
    plan = {"schema": "pte_c4.plan.T.v1", "selector": sel, "cells": cells, "jobs": jobs, "library": lib["modules"],
            "library_provenance": lib["provenance"]}
C.jdump(out, plan)
print("jobs", len(jobs))
