"""Known answers for the W2-J plants at X0-like physics (lossless torus, dest all) before any C1 row:
CLK at period 1 and 2 (decay 0/1/6) and TTL (decay 3/6; dec under sync and async). 16 worlds each."""
import sys, time
from wj_common import *
import plants_wj as pw
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
t0 = time.process_time()
X0 = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0,
             lat_jitter=0, dup=0.0, noise=0, cap=0, collision="none", decay_shift=0, update_mode="sync",
             update_period=1, state_dim=4, payload_width=2, channels=2, rules=1, prog_len=24).validate()
env = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)
Pd = env.period()
seeds = assays.world_seeds(WJ_DEV, 16)
res = {}
cases = []
for p in (1, 2):
    for k, comp in ((0, 0), (1, 1), (6, 6)):
        for ev in ("cnt", "pay", "payN"):
            cases.append(("clk", dict(update_period=p, decay_shift=k), dict(p=p, comp=comp, ev=ev)))
for k in (3, 6):
    for um in ("sync", "async"):
        cases.append(("ttl", dict(decay_shift=k, update_mode=um, update_p=0.8), dict(ev="cnt", timer="decay")))
for um, pp in (("sync", 1), ("sync", 2), ("async", 1)):
    cases.append(("ttl", dict(update_mode=um, update_period=pp, update_p=0.8), dict(ev="cnt", timer="dec")))
for fam, phk, o in cases:
    ph = X0.replace(**phk)
    if fam == "clk":
        L = pw.clk_lines(Pd, o["p"], o["comp"], o["ev"])
    else:
        L = pw.ttl_lines(ph, o["ev"], Ws=Pd // 2, Wf=env.delta + 1, timer=o["timer"])
    ph2 = ph.replace(prog_len=max(len(L), 1))
    g = pw.genome(ph2, L)
    r = hc.evaluate(ph2, g, env, seeds)
    key = f"{fam} {phk} {o} len={len(L)}"
    res[key] = round(r["acc"], 3)
    print(key, res[key], flush=True)
res["cpu_s"] = time.process_time() - t0
save("known.json", res)
print(res["cpu_s"])
