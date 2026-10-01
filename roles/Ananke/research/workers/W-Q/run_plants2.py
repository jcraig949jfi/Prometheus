"""W-Q PLAN s4 V3: fresh engine replicate (rep 1) of W-N's plants, saving pair-level
score arrays so swap_rel2 can recompute the certificate end to end.
Usage: python run_plants2.py THREADS PLANT Q1,Q2,...   (writes out/plants_r1_<PLANT>_<tag>.npz/.json)
Imports W-N plants_rel (not edited). Physics untouched; between-tick swaps only."""
import json
import pathlib
import sys
import time

import numpy as np
import torch

TH = int(sys.argv[1])
torch.set_num_threads(TH)
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W-N"))
import plants_rel as pr  # noqa: E402
from prometheus.ananke import assays, rng  # noqa: E402

PLANT = sys.argv[2]
QS = [float(x) for x in sys.argv[3].split(",")]
KINDS = {"P1S": ["S1", "S", "S0", "S1_half", "S1_3q"], "P1SK": ["S", "Kp", "site_all"]}[PLANT]
REP = 1
M = 512
pr.nb.install()
ph = pr.physics()
env = pr.nb.spec(1)
TR = list(range(1, env.trials))
seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0x9A, REP), M)
tag = "_".join(f"{q:.2f}" for q in QS)
arrs, meta = {}, {"M": M, "rep": REP, "trials": TR, "plant": PLANT, "qs": QS, "kinds": KINDS, "cells": []}
t0 = time.time()
for q in QS:
    th = None if q == 0 else pr.th_for_q(q)
    g = pr.body(PLANT, ph, th)
    ep, n, arms, n0, s0 = pr.run_fork(ph, g, env, seeds, KINDS, TR)
    arrs[f"q{q:.2f}_normal"] = n
    for k in KINDS:
        arrs[f"q{q:.2f}_{k}"] = arms[k]
    meta["cells"].append({"q": q, "q_eff": 0 if q == 0 else pr.q_of_th(th), "t": round(time.time() - t0, 1)})
    np.savez_compressed(HERE / "out" / f"plants_r1_{PLANT}_{tag}.npz", **arrs)
    json.dump(meta, open(HERE / "out" / f"plants_r1_{PLANT}_{tag}.json", "w"), indent=1)
    print(f"{PLANT} q={q:.2f} normal={np.nanmean(n):.3f} "
          + " ".join(f"{k}={np.nanmean(arms[k]):.3f}" for k in KINDS) + f" {time.time()-t0:.0f}s", flush=True)
print("DONE", flush=True)
