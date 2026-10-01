"""PLAN s5 post-hoc readout-noise modes D2 (flip, arm-shared), D3 (flip, arm-independent),
D4 (abstain, arm-independent) on the noiseless P1S engine readouts; + hook equivalence check."""
import json, sys, time
from collections import Counter
import numpy as np, torch
torch.set_num_threads(2)
import plants_rel as pr, swap_rel as sr
from prometheus.ananke import assays, rng, lens

# ---- equivalence: in-engine between-tick readout negation == post-hoc flip
pr.nb.install()
ph = pr.physics(); env = pr.nb.spec(1)
seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0x5312), 64)
g = pr.body("P1S", ph)
ep = pr.envs.build(ph, env, seeds)
gen = np.random.default_rng(99)
mask = gen.random(ep.y.shape) < 0.3
Pd = env.period()
def noise_hooks():
    h = {}
    for k in range(env.trials):
        t = int(ep.ro_tick[0, k]) - 1
        def f(w, k=k):
            b = torch.as_tensor(np.nonzero(mask[:, k])[0])
            if len(b):
                w.S[b, w.read_idx[b, 0], 0] *= -1
        h.setdefault(t, []).append(f)
    return h
eq = {}
base = lens.run(ph, g, env, seeds, hooks=noise_hooks())
clean = lens.run(ph, g, env, seeds)
s0c = clean.trace[ep.ro_tick, np.arange(64)[:, None], ep.ro_slot].astype(np.int64)
ph_n, _ = pr.readout_noise(s0c, ep.y, ep.scored, 0.3, gen, "flip", mask=mask)
eq["normal"] = bool(np.array_equal(np.nan_to_num(ph_n, nan=9), np.nan_to_num(np.where(ep.scored, base.per_trial, np.nan), nan=9)))
h = noise_hooks(); h.setdefault(4 * Pd - 1, []).append(lambda w: pr.make_fn("S1", 64)(w, torch.arange(64)))
sw = lens.run(ph, g, env, seeds, hooks=h)
swc = lens.run(ph, g, env, seeds, hooks={4 * Pd - 1: lambda w: pr.make_fn("S1", 64)(w, torch.arange(64))})
s0s = swc.trace[ep.ro_tick, np.arange(64)[:, None], ep.ro_slot].astype(np.int64)
ph_s, _ = pr.readout_noise(s0s, ep.y, ep.scored, 0.3, gen, "flip", mask=mask)
eq["S1_trial4"] = bool(np.array_equal(ph_s[:, 4], sw.per_trial[:, 4].astype(float)))
print("equivalence", eq, flush=True)

# ---- post-hoc grid
z = np.load("out/p1s_noiseless_r0.npz")
n0, y, scored = z["n0"], z["y"], z["scored"]
KINDS = ["S1", "S", "S0", "S1_half", "S1_3q"]
TRUTH = {"S1": "FLIP_REL", "S": "FLIP_REL", "S0": "NO_EFFECT_REL", "S1_half": "CHANCE_REL", "S1_3q": "INDETERMINATE"}
QS = (0.10, 0.20, 0.30, 0.35, 0.40, 0.45)
R = int(sys.argv[1]) if len(sys.argv) > 1 else 100
res = {"equivalence": eq, "R": R, "cells": []}
t0 = time.time()
for mode in ("D2", "D3", "D4"):
    for q in QS:
        tall = {k: Counter() for k in KINDS}
        abst = {k: Counter() for k in KINDS}
        elig = {k: 0 for k in KINDS}
        g_ = np.random.default_rng([7, int(q * 100), ord(mode[1])])
        for r in range(R):
            kind = "abstain" if mode == "D4" else "flip"
            qq = 2 * q if mode == "D4" else q
            nrm, m = pr.readout_noise(n0, y, scored, qq, g_, kind)
            for k in KINDS:
                sa = z[f"s0_{k}"]
                s, _ = pr.readout_noise(sa, y, scored, qq, g_, kind, mask=m if mode == "D2" else None)
                v = sr.swap_verdict_rel(nrm, s)
                tall[k][v["verdict"]] += 1
                elig[k] += v["eligible"]
                if r < 20:
                    abst[k][sr.absolute_verdict(nrm, s)] += 1
        for k in KINDS:
            t = TRUTH[k]
            e = elig[k]
            correct = tall[k][t]
            wrong_def = sum(c for vv, c in tall[k].items() if vv in ("FLIP_REL", "CHANCE_REL", "NO_EFFECT_REL") and vv != t)
            if t == "INDETERMINATE":
                ok = wrong_def <= 0.05 * R
            else:
                ok = (e == 0) or (correct >= 0.9 * e and wrong_def <= 0.02 * R)
            cell = {"mode": mode, "q": q, "p": 1 - q, "arm": k, "truth": t, "eligible": e, "tally": dict(tall[k]),
                    "abs_tally20": dict(abst[k]), "pass": bool(ok)}
            res["cells"].append(cell)
            print(mode, q, k, t, "elig", e, dict(tall[k]), "abs", dict(abst[k]), "PASS" if ok else "FAIL",
                  f"{time.time()-t0:.0f}s", flush=True)
json.dump(res, open("out/plants_posthoc.json", "w"), indent=1)
print("pass", sum(c["pass"] for c in res["cells"]), "/", len(res["cells"]))
