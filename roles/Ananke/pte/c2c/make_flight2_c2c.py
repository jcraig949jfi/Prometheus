"""Flight 2 plan: C2C four arms at FLIP-0004 idx 8 (a stone qualified for idx 8 by the frozen rule; idx 8 is never a
production index) and the C2BX code path at RELAY-0010 idx 0 limited to 145 generations (the already-published C2B
prefix; no generation beyond 144 is computed). usage: python make_flight2_c2c.py PLAN_C2C.json OUT.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import c2c_common as X
C = X.C
from prometheus.ananke import envs
P = json.load(open(sys.argv[1]))
cells = {c["cell_id"]: c for c in P["cells"]}
f = cells["FLIP-0004-125dfbff"]
ph = C.Physics.from_dict(f["physics"]).validate(); env = envs.EnvSpec(**f["env"])
g, att = X.graded_stone(ph, env, np.asarray(f["plant_genome"]), f["cell_key"], 8, device="cuda")
f["stones"]["8"] = {"genome": g.tolist(), "attempt": att[-1], "n_attempts": len(att)}
print("stone idx8", len(att), att[-1]["B"])
jobs = [{"job_id": f"FLIP-0004-125dfbff|{a}|08", "cell_id": f["cell_id"], "campaign": "C2C", "arm": a, "idx": 8}
        for a in ("OP0_BASE", "OPB_BASE", "OP0_STEP", "OPB_STEP")]
jobs.append({"job_id": "RELAY-0010-e89a8022|C2BX|00|g145", "cell_id": "RELAY-0010-e89a8022", "campaign": "C2BX",
             "arm": "B16X", "idx": 0, "gens": 145})
C.jdump(sys.argv[2], {"flight": True, "cells": [f, cells["RELAY-0010-e89a8022"]], "jobs": jobs})
