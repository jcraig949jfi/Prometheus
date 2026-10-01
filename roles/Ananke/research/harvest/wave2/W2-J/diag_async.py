"""Diagnose TTL under async wake at X0 (decay 3): W_s/W_f sweep + LC2 reach bound. DEV worlds."""
import time
from wj_common import *
import plants_wj as pw
import lc2
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
t0 = time.process_time()
X0 = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0,
             lat_jitter=0, dup=0.0, noise=0, cap=0, collision="none", decay_shift=3, update_mode="async",
             update_p=0.8, state_dim=4, payload_width=2, channels=2, rules=1, prog_len=16).validate()
env = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)
Pd = env.period()
row = {"cell_id": "X0async", "physics": X0.to_dict(), "env": env.to_dict()}
print("lc2", lc2.bound(row, M=16, R=4)["acc_ub"])
seeds = assays.world_seeds(WJ_DEV, 16)
out = {}
for Ws in (2, 3, 5, 8):
    for Wf in (8, 9, 10):
        L = pw.ttl_lines(X0, "cnt", Ws=Ws, Wf=Wf, timer="decay")
        r = hc.evaluate(X0, pw.genome(X0, L), env, seeds)
        out[f"Ws{Ws} Wf{Wf}"] = round(r["acc"], 3)
        print(Ws, Wf, out[f"Ws{Ws} Wf{Wf}"], flush=True)
out["cpu_s"] = time.process_time() - t0
save("diag_async.json", out)
print(out["cpu_s"])
