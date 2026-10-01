import overlay, json, time, numpy as np
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
from prometheus.ananke.audit import ceilings as CL
from prometheus.ananke.audit.tests import _data as D
t0 = time.process_time()
lc = D.load_json("roles/Ananke/research/harvest/H-PLANT/out/lc_census.json")["rows"]
seeds = assays.world_seeds(0x48504C54, 64)
g = np.random.default_rng(3)
pick = [lc[i] for i in g.choice(len(lc), 12, replace=False)] + [x for x in lc if x["bound"] < 0.9][:8]
bad = 0
for x in pick:
    r = D.by_id()[x["cell"]]
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    a = CL.lightcone(ph, env, seeds)["bound"]; b = CL.joint(ph, env, seeds, terms=())
    ok = abs(a - x["bound"]) < 1e-12 and abs(b["lc"] - x["bound"]) < 1e-12 and abs(b["joint"] - x["bound"]) < 1e-12
    bad += not ok
    print(x["cell"][:8], x["family"], x["update_mode"], x["topology"], x["bound"], a, b["lc"], b["joint"], ok)
print("lc bad", bad, "cpu", time.process_time() - t0)
