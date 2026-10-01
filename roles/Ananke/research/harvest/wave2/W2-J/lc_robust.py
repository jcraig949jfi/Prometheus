"""Robust bounds for all 83 XOR evolve rows on 64 fresh worlds (32 position pairs; namespace W2JS+9):
  lc1 = H-PLANT lightcone.earliest (deterministic, optimistic for async), recomputed on THESE worlds;
  lc2 = W2-J MC bound (async wake incl. sensors, loss, fanout, dup, jitter), R=4 replicates/trial.
Per-pair f -> percentile bootstrap (2000, seed 0) 99% interval of the bound over pairs (world sampling is
the dominant uncertainty: H-PLANT's census used 64 other worlds)."""
import time
import numpy as np
from wj_common import *
import lightcone as lcm
import lc2
from prometheus.ananke import assays, envs, topology
from prometheus.ananke.physics import Physics

t0 = time.process_time()
M, R = 64, 4
seeds = assays.world_seeds(WJ_NS + 9, M)
rng = np.random.default_rng(11)
boot = np.random.default_rng(0)
out = []
for r in xor_evolve():
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy(); ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph)
    Pd = env.period(); p = ph.update_period if ph.update_mode == "sync" else 1
    modes = ["all" if (ph.dest_mode == "all" and ph.topology != "global") else "sample"]
    if modes[0] == "sample" and ph.plastic_route and ph.topology != "global":
        modes.append("all")
    f1, f2 = [], {m: [] for m in modes}
    cache = {}
    for b in range(0, M, 2):
        a1 = []
        for k in range(env.trials):
            t0k = k * Pd
            ro = int(ep.ro_tick[b, k])
            ok = True
            for s in sidx[b][:2]:
                key = (int(s), t0k % p)
                if key not in cache:
                    cache[key] = lcm.earliest(ph, int(s), t0k % p, env.cue_len) - (t0k % p)
                ok &= bool(cache[key][ridx[b]] + t0k <= ro)
            a1.append(ok)
        f1.append(np.mean(a1))
        for m in modes:
            a2 = []
            for k in range(env.trials):
                for _ in range(R):
                    i1, i2 = lc2.reach_trial(ph, env, sidx[b][:2], int(ridx[b]), k * Pd, rng, nbr, dist, m)
                    a2.append(i1 and i2)
            f2[m].append(np.mean(a2))
    f1 = np.array(f1)
    f2opt = np.max(np.stack([np.array(v) for v in f2.values()]), 0)

    def ci(x):
        bs = x[boot.integers(0, len(x), size=(2000, len(x)))].mean(1)
        return float(np.quantile(bs, 0.005)), float(np.quantile(bs, 0.995))
    l1, h1 = ci(f1); l2, h2 = ci(f2opt)
    rec = {"cell": r["cell_id"], "lc1": 0.5 + f1.mean() / 2, "lc1_ci99": [0.5 + l1 / 2, 0.5 + h1 / 2],
           "lc2": 0.5 + f2opt.mean() / 2, "lc2_ci99": [0.5 + l2 / 2, 0.5 + h2 / 2],
           "lc2_modes": {m: 0.5 + float(np.mean(v)) / 2 for m, v in f2.items()}}
    out.append(rec)
    print(r["cell_id"][:8], "lc1 %.3f [%.3f,%.3f]  lc2 %.3f [%.3f,%.3f]" % (rec["lc1"], *rec["lc1_ci99"], rec["lc2"], *rec["lc2_ci99"]), flush=True)
save("lc_robust.json", {"rows": out, "M": M, "R": R, "ns": WJ_NS + 9, "cpu_s": time.process_time() - t0})
print("cpu_s", time.process_time() - t0)
