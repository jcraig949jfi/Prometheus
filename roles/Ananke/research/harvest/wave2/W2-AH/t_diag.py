from w2ah_common import *
from prometheus.ananke.engine import World
r = [r for r in hc.rows() if r["wave"] == "B" and r["extra"].get("transect") == "economy" and r["env"]["family"] == "RELAY"
     and r["extra"].get("rep", 0) == 0 and r["extra"]["base"] == 1 and r["levels"]["economy"] == "high"][0]
ph, env = cell(r); p12 = ph.replace(prog_len=12)
seeds = plant_seeds(r); M = 32
ws = [seeds[m - (m % 2)] for m in range(M)]
ep = envs.build(p12, env, seeds)
w = World(p12, np.repeat(genome(p12, "F1")[None], M, 0), ws, device="cpu", schedule=ep.schedule)
em = []
for t in range(env.T()):
    w.step(); em.append(w.last_emit.any(-1).numpy())
em = np.array(em)
print("emission ticks world0:", np.flatnonzero(em[:, 0]), " all worlds same?", (em == em[:, :1]).all())
pt = envs.per_trial(ep, w.trace.numpy())
print("per-trial acc:", pt.mean(0).round(2))
s0 = w.trace.numpy()[ep.ro_tick, np.arange(M)[:, None], 0]
print("S0 at readout world0:", s0[0], "y", ep.y[0])
