"""Soundness+power of canon(): chatty genomes (relay_flood plant and random genomes whose
instr 0 forces EMIT and whose instr 1 writes RVAL/RPORT from inbox) so that routing,
loss, collisions and wake all matter."""
from common import *
import numpy as np
from prometheus.ananke import envs, search, assays, plants
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
from canon import canon

def run(ph, env, G, seeds):
    ep = envs.build(ph, env, seeds)
    ws = [seeds[m - m % 2] for m in range(len(seeds))]
    w = World(ph, np.repeat(G[None], len(seeds), 0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    return (w.trace.numpy().tobytes() + w.S.numpy().tobytes()
            + b"".join(w.stats[k].numpy().tobytes() for k in ("attempted","delivered","lost","collided","emitters","awake","nonnop")))

def chatty(ph, seed):
    rm = plants.regmap(ph)
    G = search.random_genomes(np.random.default_rng(seed), 1, ph)[0]
    G[:, 0] = (6, rm["EMIT"], 0, 0, 1)                 # EMIT := 1
    G[:, 1] = (2, rm["PAY0"], rm["SENSE"], rm["IN0_0"], 0)
    G[:, 2] = (3, rm["RVAL"], rm["IN0_0"], rm["SENSE"], 0)
    G[:, 3] = (1, rm["RPORT"], rm["CNT0"], 0, 0)
    G[:, -1] = (2, rm["S0"], rm["S0"], rm["IN0_0"], 0)
    return G

seeds = assays.world_seeds(77, 6)
bases = [Physics(topology="ring", n_sites=36, radius=1, dest_mode="all", fanout=2, loss=0.1, plastic_route=1, prog_len=12, cap=2, collision="none"),
         Physics(topology="global", n_sites=36, fanout=2, loss=0.1, lat_hop=1, update_mode="async", update_p=0.5, prog_len=12),
         Physics(topology="smallworld", n_sites=36, rewire=200, fanout=4, loss=0.3, cap=0, collision="aloha", prog_len=12, plastic_route=1),
         Physics(topology="random", n_sites=36, k_random=3, fanout=2, rules=1, setrule=1, prog_len=12, plastic_route=1, adapt_shift=2),
         Physics(topology="torus", n_sites=36, radius=2, fanout=2, dest_mode="sample", loss=0.3, prog_len=12, plastic_route=1)]
variants = [dict(k_random=6), dict(radius=3), dict(radius=1), dict(rewire=50), dict(fanout=8), dict(adapt_shift=5), dict(loss_per_hop=1),
            dict(lat_base=2, lat_hop=0), dict(lat_hop=1), dict(update_period=2), dict(update_p=0.8), dict(cap=1), dict(collision="saturate"),
            dict(setrule=0), dict(dest_mode="all"), dict(dest_mode="sample"), dict(plastic_route=0), dict(topo_seed=5)]
env = envs.EnvSpec(family="RELAY", d=2, delta=4, trials=4)
viol = power_miss = 0
for ph in bases:
    for v in variants:
        try:
            p2 = ph.replace(**v).validate()
        except AssertionError:
            continue
        if p2 == ph: continue
        pred = canon(ph.to_dict(), env.to_dict()) == canon(p2.to_dict(), env.to_dict())
        same = all(run(ph, env, G, seeds) == run(p2, env, G, seeds)
                   for G in [plants.plant("relay_flood", ph), chatty(ph, 1), chatty(ph, 2)])
        tag = "" if pred == same else ("  <-- VIOLATION (canon says inert, run differs)" if pred else "  (canon conservative)")
        viol += pred and not same; power_miss += (not pred) and same
        print(f"{ph.topology:10s} {ph.dest_mode:6s} {str(v):32s} canon_eq={pred!s:5s} identical={same!s:5s}{tag}", flush=True)
print("violations", viol, "conservative", power_miss)
