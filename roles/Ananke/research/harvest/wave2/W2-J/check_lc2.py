"""Consistency check: with loss 0, dup 0, dest all, sync wake, LC2's per-trial reach must EQUAL
H-PLANT lightcone.earliest's per-trial reach on the same worlds (both deterministic then).
Also a must-fail: LC2 on a row with lat inflated so nothing arrives -> f=0."""
import numpy as np
from wj_common import *
import lightcone as lcm
import lc2
from prometheus.ananke import assays, envs, topology
from prometheus.ananke.physics import Physics

rows = [r for r in xor_evolve() if r["physics"]["topology"] not in ("global",)]
rng = np.random.default_rng(1)
n_cmp = n_bad = 0
checked = []
for r in rows[:: max(1, len(rows) // 14)]:
    ph = Physics.from_dict(r["physics"]).replace(loss=0.0, dup=0.0, dest_mode="all", update_mode="sync")
    env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(WJ_NS + 7, 8)
    ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy(); ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph)
    Pd = env.period(); p = ph.update_period
    for b in range(0, 8, 2):
        for k in range(env.trials):
            t0 = k * Pd
            ro = int(ep.ro_tick[b, k])
            ok1 = True
            for s in sidx[b][:2]:
                e = lcm.earliest(ph, int(s), t0 % p, env.cue_len) - (t0 % p)
                ok1 &= bool(e[ridx[b]] + t0 <= ro)
            i1, i2 = lc2.reach_trial(ph, env, sidx[b][:2], int(ridx[b]), t0, rng, nbr, dist, "all")
            n_cmp += 1
            n_bad += (ok1 != (i1 and i2))
    checked.append(r["cell_id"][:8])
print("compared", n_cmp, "mismatches", n_bad, "rows", checked)
# must-fail: huge latency
r = rows[0]
rr = dict(r); rr["physics"] = dict(r["physics"], lat_base=40, lat_jitter=0)
b = lc2.bound(rr, M=4, R=1)
print("must-fail lat=40 f_opt", b["f_opt"])
save("check_lc2.json", {"compared": n_cmp, "mismatches": n_bad, "rows": checked, "mf_lat40_f": b["f_opt"]})
