"""Pre-freeze fixture smoke: do the plants build, is normal acc ~ 1-q, speed."""
import time, json
import numpy as np, torch
torch.set_num_threads(2)
import plants_rel as pr
from prometheus.ananke import assays, rng
pr.nb.install()
ph = pr.physics()
env = pr.nb.spec(1)
seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0x5310), 64)
TR = list(range(1, env.trials))
for name, q in (("P1S", None), ("P1S", 0.3), ("P1SK", None), ("P1SK", 0.3)):
    th = None if q is None else pr.th_for_q(q)
    g = pr.body(name, ph, th)
    arms = [pr.Arm("normal")] + pr.single("S", TR) + pr.single("S1", TR) + pr.single("S0", TR)
    t = time.time()
    ep, pt, s0 = pr.run_arms(ph, g, env, seeds, arms)
    el = time.time() - t
    n = pt["normal"]
    res = {"normal": float(np.nanmean(n))}
    for k in ("S", "S1", "S0"):
        res[k] = float(np.nanmean(pr.merge(pt, k, TR)))
    print(name, q, {k: round(v, 3) for k, v in res.items()}, f"{el:.1f}s", flush=True)
