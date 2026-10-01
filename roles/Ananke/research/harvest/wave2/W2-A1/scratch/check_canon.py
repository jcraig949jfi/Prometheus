from common import *
import numpy as np, itertools
from prometheus.ananke import envs, search, assays
from prometheus.ananke.engine import World
from prometheus.ananke.physics import Physics
from canon import canon

def run(ph, env, G, seeds):
    ep = envs.build(ph, env, seeds)
    ws = [seeds[m - m % 2] for m in range(len(seeds))]
    w = World(ph, np.repeat(G[None], len(seeds), 0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    return w.trace.numpy().tobytes() + b"".join(w.stats[k].numpy().tobytes() for k in ("attempted","delivered","lost","collided","emitters","awake","nonnop","energy_spent")) + w.S.numpy().tobytes()

rng = np.random.default_rng(5)
seeds = assays.world_seeds(77, 8)
bases = [Physics(topology="ring", n_sites=36, radius=1, dest_mode="all", fanout=2, loss=0.1, plastic_route=1, prog_len=12),
         Physics(topology="global", n_sites=36, fanout=2, loss=0.1, lat_hop=1, update_mode="async", update_p=0.5),
         Physics(topology="smallworld", n_sites=36, rewire=200, fanout=4, loss=0.3, cap=0, collision="aloha"),
         Physics(topology="random", n_sites=36, k_random=3, fanout=2, rules=1, setrule=1)]
variants = [dict(k_random=6), dict(radius=3), dict(rewire=50), dict(fanout=8), dict(adapt_shift=5), dict(loss_per_hop=1),
            dict(lat_base=2, lat_hop=0), dict(update_period=2), dict(update_p=0.8), dict(cap=2), dict(collision="saturate"),
            dict(setrule=0), dict(dest_mode="all"), dict(plastic_route=1)]
env = envs.EnvSpec(family="RELAY", d=2, delta=4, trials=6)
n_eq = n_pred_eq = bad = 0
for ph in bases:
    G = search.random_genomes(rng, 1, ph)[0]
    # make the genome emit a lot: force a few instrs to write EMIT
    for v in variants:
        try:
            p2 = ph.replace(**v).validate()
        except AssertionError:
            continue
        pred = canon(ph.to_dict(), env.to_dict()) == canon(p2.to_dict(), env.to_dict())
        same = None
        outs = []
        for trial in range(6):
            Gt = search.random_genomes(np.random.default_rng(trial), 1, ph)[0]
            outs.append(run(ph, env, Gt, seeds) == run(p2, env, Gt, seeds))
        same = all(outs)
        n_pred_eq += pred
        if pred and not same:
            bad += 1
            print("CANON SAYS INERT BUT DIFFERS:", ph.topology, ph.dest_mode, v)
        print(f"{ph.topology:10s} {ph.dest_mode:6s} {str(v):40s} canon_equal={pred} identical={same}")
print("violations", bad)
