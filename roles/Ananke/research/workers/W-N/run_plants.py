"""PLAN s5 known-answer validation on plants (engine RAND noise D1; post-hoc D2-D4)."""
import json, sys, time
import numpy as np, torch
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 8
torch.set_num_threads(TH)
import plants_rel as pr, swap_rel as sr
from prometheus.ananke import assays, rng, lens
pr.nb.install()
ph = pr.physics(); env = pr.nb.spec(1)
TR = list(range(1, env.trials))
M = 512
QS = (0.0, 0.10, 0.20, 0.30, 0.35, 0.40, 0.45)
TRUTH = {("P1S", "S1"): "FLIP_REL", ("P1S", "S"): "FLIP_REL", ("P1S", "S0"): "NO_EFFECT_REL",
         ("P1S", "S1_half"): "CHANCE_REL", ("P1S", "S1_3q"): "INDETERMINATE",
         ("P1SK", "S"): "CHANCE_REL", ("P1SK", "Kp"): "CHANCE_REL", ("P1SK", "site_all"): "FLIP_REL"}
KINDS = {"P1S": ["S1", "S", "S0", "S1_half", "S1_3q"], "P1SK": ["S", "Kp", "site_all"]}
rep = int(sys.argv[2]) if len(sys.argv) > 2 else 0
seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0x9A, rep), M)
out = {"M": M, "trials": TR, "rep": rep, "cells": []}
raw = {}
t0 = time.time()
PLANTS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["P1S", "P1SK"]
for plant in PLANTS:
    for q in QS:
        th = None if q == 0 else pr.th_for_q(q)
        g = pr.body(plant, ph, th)
        ep, n, arms, n0, s0 = pr.run_fork(ph, g, env, seeds, KINDS[plant], TR)
        if q == 0 and plant == "P1S":
            raw = {"n0": n0, "s0": s0, "y": ep.y, "scored": ep.scored}
        for k in KINDS[plant]:
            v = sr.swap_verdict_rel(n, arms[k])
            truth = TRUTH[(plant, k)]
            exp = truth if v["eligible"] else "NOT_ELIGIBLE"
            cell = {"plant": plant, "q": q, "q_eff": 0 if q == 0 else pr.q_of_th(th), "arm": k, "truth": truth,
                    "expected": exp, "verdict": v["verdict"], "ungated": v["verdict_ungated"],
                    "pass": v["verdict"] == exp, "absolute": sr.absolute_verdict(n, arms[k]),
                    **{kk: v[kk] for kk in ("normal", "swap", "DF", "DN", "z", "p_min", "flip_rate", "P", "K")}}
            out["cells"].append(cell)
            print(f"{plant:4s} q={q:.2f} {k:8s} n={v['normal'][0]:.3f}[{v['normal'][1]:.3f}] s={v['swap'][0]:.3f} "
                  f"truth={truth:13s} got={v['verdict']:13s} abs={cell['absolute']:9s} {'PASS' if cell['pass'] else 'FAIL'} "
                  f"f={v['flip_rate']['f']} {time.time()-t0:.0f}s", flush=True)
json.dump(out, open(f"out/plants_engine_r{rep}_{'_'.join(PLANTS)}.json", "w"), indent=1)
if raw:
  np.savez_compressed(f"out/p1s_noiseless_r{rep}.npz", n0=raw["n0"], y=raw["y"], scored=raw["scored"],
                    **{f"s0_{k}": v for k, v in raw["s0"].items()})
print("pass", sum(c["pass"] for c in out["cells"]), "/", len(out["cells"]))
