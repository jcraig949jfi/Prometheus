"""Falsification attempt on the A0 rows whose recorded relay_flood plant acc most exceeds the exact-seed ceiling (.5).
(1) KA: re-evaluate the plant on its recorded seeds (must reproduce result.plant.acc);
(2) deterministic: negate trial k's cue alone -> actuator S0 at ro_k must be unchanged in every world, every k;
(3) fresh seeds 2 x 64 worlds: mean must be ~.5."""
from w2u_ceil import *   # noqa
from w2p_common import Clock
from prometheus.ananke import plants
from prometheus.ananke.engine import World
ck = Clock()
CELLS = ["74b13c29", "a1b0e959", "3f05312e"]
by8 = {r["cell_id"][:8]: r for r in hc.rows() if r["wave"] == "A0"}
def trace_of(ph, g, env, seeds, flip_k=None):
    M = len(seeds); ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    if flip_k is not None:
        t0 = flip_k * env.period()
        ep.schedule.sense_val[t0:t0 + env.cue_len] *= -1
    w = World(ph, np.repeat(g[None], M, axis=0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    return ep, w.trace.cpu().numpy()
out = {}
for c8 in CELLS:
    r = by8[c8]
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    p2 = ph.replace(prog_len=max(ph.prog_len, 12))
    g = plants.plant("relay_flood", p2)
    seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
    ka = hc.evaluate(p2, g, env, seeds)["acc"]
    ep, base = trace_of(p2, g, env, seeds)
    B = len(seeds); changed = []
    for k in range(env.trials):
        _, tr = trace_of(p2, g, env, seeds, flip_k=k)
        ro = ep.ro_tick[:, k]
        changed.append(int((base[ro, np.arange(B), 0] != tr[ro, np.arange(B), 0]).sum()))
    fresh = [hc.evaluate(p2, g, env, assays.world_seeds(H_int(0x57325546, int(c8, 16), i), 64))["acc"] for i in range(2)]
    out[c8] = {"recorded": r["result"]["plant"]["acc"], "ka_reeval": ka, "ka_exact": abs(ka - r["result"]["plant"]["acc"]) < 1e-12,
               "worlds_changed_per_trial": changed, "fresh_2x64": fresh}
    print(c8, out[c8], flush=True)
out["compute"] = ck.done()
save("check_a0_exceed.json", out)
print(ck.done())
