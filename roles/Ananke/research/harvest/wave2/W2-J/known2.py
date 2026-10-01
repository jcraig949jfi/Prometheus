"""Known answers for v2 plants (genome-representable constants) at X0-like lossless physics. 16 DEV worlds."""
import time
from wj_common import *
import plants_wj as pw
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
t0 = time.process_time()
X0 = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0,
             lat_jitter=0, dup=0.0, noise=0, cap=0, collision="none", decay_shift=0, update_mode="sync",
             update_period=1, state_dim=4, payload_width=2, channels=2, rules=1, prog_len=32).validate()
env = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)
Pd, dl = env.period(), env.delta
seeds = assays.world_seeds(WJ_DEV, 16)
res = {}
cases = []
for p, k in ((1, 0), (2, 1), (1, 6)):
    for emit in ("once", "persist"):
        cases.append(("clk2", dict(update_period=p, decay_shift=k), dict(p=p, comp=k, emit=emit)))
cases.append(("clk1", dict(update_period=2, decay_shift=1), dict(p=2, comp=1, ev="payN")))
for um, k in (("sync", 0), ("async", 0), ("async", 3), ("async", 6), ("async", 1)):
    for emit in ("once", "persist"):
        cases.append(("ttl2", dict(update_mode=um, update_p=0.8, decay_shift=k), dict(emit=emit)))
for fam, phk, o in cases:
    ph = X0.replace(**phk)
    if fam == "clk2":
        L = pw.clk2_lines(Pd, dl, o["p"], o["comp"], emit=o["emit"], lat_min=1)
    elif fam == "clk1":
        L = pw.clk_lines(Pd, o["p"], o["comp"], o["ev"])
    else:
        L = pw.ttl2_lines(ph, Ws=Pd - 1, Wf=dl + 1, We=3, emit=o["emit"])
    r = hc.evaluate(ph, pw.genome(ph, L), env, seeds)
    key = f"{fam} {phk} {o} len={len(L)}"
    res[key] = round(r["acc"], 3)
    print(key, res[key], flush=True)
res["cpu_s"] = time.process_time() - t0
save("known2.json", res)
print(res["cpu_s"])
