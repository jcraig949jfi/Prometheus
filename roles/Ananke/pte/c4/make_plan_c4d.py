"""PTE-C4 s8 diagnostic plan (PREREG_PTE_C4 s7): arm D = R4 + OPDL with the DESIGNED two-module library D-LIB (the
GATE plant's CONTEXT and CUE halves, built by build_dlib.py), GATE at every admitted cell, idx 0..7, 36 generations.
Each job carries its OWN cell's two halves as a per-job library (run_c4 job["library"]); seeds are the C4 GATE seeds,
so arm D shares the gen-0 population and training worlds with arms A/B/C of the target stage.
usage: python make_plan_c4d.py PLAN_C4_T.json DLIB.json OUT.json"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c4_common as K  # noqa: E402
C = K.C

T = json.load(open(sys.argv[1])); dl = json.load(open(sys.argv[2])); out = sys.argv[3]
assert all(c["pass"] for c in dl["checks"]), "D-LIB known-answer checks must pass"
gate_cells = sorted({j["cell_id"] for j in T["jobs"] if j["task"] == "GATE"})
by_cell = {}
for m in dl["modules"]:
    by_cell.setdefault(m["cell_id"], []).append({"id": len(by_cell.get(m["cell_id"], [])) + 1, "name": m["name"],
                                                 "lines": m["lines"], "source_lines": m["source_lines"]})
jobs = []
for idx in range(8):
    for cid in gate_cells:
        lib = by_cell[cid]
        assert [m["name"] for m in lib] == ["GATE_CONTEXT_HALF", "GATE_CUE_HALF"]
        jobs.append({"job_id": f"{cid}|GATE|D|{idx:02d}", "cell_id": cid, "task": "GATE", "arm": "D", "rep": "R4",
                     "op": "OPDL", "idx": idx, "gens": 36, "library": lib})
plan = {"schema": "pte_c4.plan.D.v1", "selector": T["selector"], "cells": T["cells"], "jobs": jobs, "library": [],
        "dlib_source": os.path.basename(sys.argv[2])}
C.jdump(out, plan)
print("jobs", len(jobs))
