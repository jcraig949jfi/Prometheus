import overlay, json, time, numpy as np
from prometheus.ananke import assays, envs, topology
from prometheus.ananke.physics import Physics
from prometheus.ananke.audit import ceilings as CL
from prometheus.ananke.audit.tests import _data as D
t0 = time.process_time()
lc2 = D.load_json("roles/Ananke/research/harvest/wave2/W2-J/out/lc2.json")["rows"]
print(len(lc2), lc2[0])
seeds = assays.world_seeds(0x57324A53 + 7, 32)
for o in lc2[:3]:
    r = D.by_id()[o["cell"]]; ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    t = time.process_time(); m = CL.mc(ph, env, seeds, reps=4, rng_seed=0)
    print(o["cell"][:8], ph.update_mode, ph.topology, o["f_opt"], m["f_opt"], o["acc_ub"], m["bound"], {k: v["f_both"] for k, v in o["modes"].items()}, {k: v["f_all"] for k, v in m["modes"].items()}, round(time.process_time()-t, 1))
# deterministic limit
xs = [r for r in D.rows() if r["env"]["family"] == "XOR" and r["kind"] == "evolve" and r["physics"]["topology"] != "global"]
n = bad = 0
g = np.random.default_rng(1)
for r in xs[::max(1, len(xs)//6)][:6]:
    ph = Physics.from_dict(r["physics"]).replace(loss=0.0, dup=0.0, dest_mode="all", update_mode="sync", lat_jitter=0)
    env = envs.EnvSpec(**r["env"]); s8 = assays.world_seeds(0x57324A53 + 7, 8)
    lcp = CL.lightcone(ph, env, s8, per_trial=True)
    ep = envs.build(ph, env, s8); sidx = ep.schedule.sense_idx.numpy(); ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph)
    for wi, b in enumerate(range(0, 8, 2)):
        for k in range(env.trials):
            i = CL.mc_trial(ph, env, [int(x) for x in sidx[b][:2]], int(ridx[b]), k * env.period(), g, nbr, dist, "all")
            n += 1; bad += bool(i.all()) != bool(lcp["per_trial_ok"][wi, k].all())
print("det-limit", n, bad, round(time.process_time()-t0, 1))
