"""Pre-freeze: run_fork must be bit-identical (readouts) to run_arms and to lens.run."""
import time, json, numpy as np, torch
torch.set_num_threads(2)
import plants_rel as pr
from prometheus.ananke import assays, rng, lens
pr.nb.install()
ph = pr.physics(); env = pr.nb.spec(1)
seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0x5311), 32)
TR = [1, 4, 7, 11]
ok = {}
for name, q in (("P1S", 0.3), ("P1SK", 0.3), ("P1SK", None)):
    g = pr.body(name, ph, None if q is None else pr.th_for_q(q))
    kinds = ["S", "S1", "S0", "S1_half", "Kp"]
    arms = [pr.Arm("normal")] + sum([pr.single(k, TR) for k in kinds], [])
    t = time.time(); ep, pt, s0 = pr.run_arms(ph, g, env, seeds, arms); ta = time.time() - t
    t = time.time(); ep2, n2, pf, n0, sf = pr.run_fork(ph, g, env, seeds, kinds, TR); tf = time.time() - t
    good = np.array_equal(np.nan_to_num(pt["normal"], nan=9), np.nan_to_num(n2, nan=9))
    for k in kinds:
        good &= np.array_equal(np.nan_to_num(pr.merge(pt, k, TR), nan=9), np.nan_to_num(pf[k], nan=9))
        good &= np.array_equal(pr.merge_s0(s0, k, TR)[:, TR], sf[k][:, TR])
    # lens.run reference for S at trial 4
    ref = lens.run(ph, g, env, seeds, hooks={4 * env.period() - 1: lambda w: lens.swap(w, ["S"])})
    good &= np.array_equal(np.nan_to_num(ref.per_trial[:, 4]), np.nan_to_num(pf["S"][:, 4]))
    ok[f"{name}_{q}"] = bool(good)
    print(name, q, "identical", bool(good), f"arms {ta:.1f}s fork {tf:.1f}s",
          "normal", round(float(np.nanmean(n2)), 3), {k: round(float(np.nanmean(pf[k])), 3) for k in kinds}, flush=True)
json.dump(ok, open("out/selfcheck_fork.json", "w"))
