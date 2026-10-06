"""C2BX Flight 1: prefix replay. Re-run C2B B4X (cell, idx) under the C2BX runner for 145 generations (so that
generation index 143 is followed by a selection step, as in the 576-gen continuation) and check that the population
after gen 144 and the checkpoint statuses at 36/72/108/144 equal C2B's frozen record.
usage: python flight1_c2bx.py OUT.json CELL IDX [CELL IDX ...]"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import run_c2c as R
X = R.X; C = R.C
from prometheus.ananke import assays, envs
from prometheus.ananke.search import HELD_NS, SearchSpec
plan = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2a", "PLAN_C2A.json")))
cells = {c["cell_id"]: c for c in plan["cells"]}
ref = R.load_c2b_b4x(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2b"))
res = []
for cid, idx in zip(sys.argv[2::2], map(int, sys.argv[3::2])):
    t0 = time.time(); c = cells[cid]
    ph = C.Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
    s = C.search_seed(c["cell_key"], idx); sp = SearchSpec(**dict(R.BASE_SPEC, gens=145))
    hs = assays.world_seeds(C.H_int(s, HELD_NS), C.M_HELD)
    ev = R.evolve(ph, env, s, sp, "cuda", X.B.mutate_tagged, ckpts=(35, 71, 107, 143), snaps=(143,), held=hs, role=c["role"])
    r = ref[(cid, idx)]
    out = {"cell_id": cid, "idx": idx, "pop143_equal": bool(np.array_equal(ev["snap"][143].astype(np.int16), r["pop"])),
           "statuses": {g: ev["checkpoints"][g]["status"] for g in (36, 72, 108, 144)}, "c2b": r["checkpoint_status"],
           "wall_s": round(time.time() - t0, 1)}
    out["PASS"] = out["pop143_equal"] and all(out["statuses"][g] == r["checkpoint_status"][str(g)] for g in (36, 72, 108, 144))
    print(out, flush=True); res.append(out)
C.jdump(sys.argv[1], res)
