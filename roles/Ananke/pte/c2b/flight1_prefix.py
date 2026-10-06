"""PTE-C2B Flight 1: B4X prefix replay (order s11, s26). Re-runs C2A BASE (cell, idx) under the C2B runner for
37 generations (so generation index 35 is followed by one more selection step, as in B4X) and checks that the
population after gen 36, the gen-36 champion, its competence status and the accuracy curve equal C2A's frozen
record exactly. Not production science: the gen-36 state of these searches is already published (C2A).
usage: python flight1_prefix.py OUT.json CELL_ID IDX [CELL_ID IDX ...]"""
import dataclasses
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c2b_common as B  # noqa: E402
import run_c2b as R  # noqa: E402
C = B.C
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.search import HELD_NS  # noqa: E402

out = sys.argv[1]
pairs = list(zip(sys.argv[2::2], map(int, sys.argv[3::2])))
plan = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2a", "PLAN_C2A.json")))
cells = {c["cell_id"]: c for c in plan["cells"]}
ref = R.load_c2a_reference(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2a"))
res = []
for cid, idx in pairs:
    t0 = time.time()
    c = cells[cid]
    ph = C.Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
    s = C.search_seed(c["cell_key"], idx)
    sp = dataclasses.replace(R.arm_spec("B4X"), gens=37)
    hs = assays.world_seeds(C.H_int(s, HELD_NS), C.M_HELD)
    ev = R.evolve_c2b(ph, env, s, sp, "cuda", ckpts=(35,), held=hs, role=c["role"])
    p = ref[(cid, idx)]
    r = {"cell_id": cid, "idx": idx,
         "pop35_equal": bool(np.array_equal(ev["snap35"].astype(np.int16), p["pop"])),
         "champion36_equal": bool(np.array_equal(np.asarray(ev["checkpoints"][36]["champion"]), np.asarray(p["champion"]))),
         "status36": ev["checkpoints"][36]["status"], "c2a_status": p["status"],
         "curve_acc_equal": all(a["max_acc"] == b["max_acc"] and a["best_acc"] == b["best_acc"]
                                for a, b in zip(ev["curve"][:36], p["curve"])),
         "best_fit_maxabs": max(abs(a["best_fit"] - b["best_fit"]) for a, b in zip(ev["curve"][:36], p["curve"])),
         "wall_s": round(time.time() - t0, 1)}
    r["PASS"] = r["pop35_equal"] and r["champion36_equal"] and r["curve_acc_equal"] and r["status36"] == r["c2a_status"]
    print(r, flush=True)
    res.append(r)
C.jdump(out, res)
