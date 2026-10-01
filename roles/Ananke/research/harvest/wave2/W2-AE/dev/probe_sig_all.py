"""All 166 recorded SIGNAL evolve cells: exact-wake bound on the held set reproduces W2-T and is never exceeded."""
import overlay, json, time
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
from prometheus.ananke.search import HELD_NS
from prometheus.ananke.audit import ceilings as CL
from prometheus.ananke.audit.tests import _data as D
t0 = time.process_time()
sig = D.load_json("roles/Ananke/research/harvest/wave2/W2-T/out/lcwake_sig_b0of1.json")["rows"]
mism = viol = 0; nontriv = []
for o in sig:
    r = D.by_id()[o["cell"]]; ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    hs = assays.world_seeds(H_int(r["search_seed"], HELD_NS), r["search"]["M_held"])
    e = CL.lightcone(ph, env, hs, wake="exact")["bound"]
    mism += abs(e - o["held_exact"]["bound"]) > 1e-12
    viol += r["result"]["held"]["acc"] > e + 1e-12
    if e < o["held_opt"]["bound"] - 1e-9:
        nontriv.append((o["cell"][:8], o["family"], r["result"]["held"]["acc"], e, o["held_opt"]["bound"]))
out = {"cells": len(sig), "mismatch_vs_W2T": mism, "signal_violations": viol, "exact_tighter_than_opt": len(nontriv),
       "tightest": sorted(nontriv, key=lambda x: x[3] - x[2])[:8], "cpu_s": round(time.process_time() - t0, 1)}
print(json.dumps(out))
(overlay.HERE / "dev/out_sig_all.json").write_text(json.dumps(out, indent=1))
