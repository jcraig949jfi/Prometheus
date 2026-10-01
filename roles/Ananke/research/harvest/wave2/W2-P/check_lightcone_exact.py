"""Deterministic engine check of the light-cone ceiling on the rows whose recorded held acc exceeds
the analytic ceiling (task2 'violators'). Every random draw is a pure function of (ws, stream, t, n, j),
so editing the cue of ONE trial k changes nothing but the cue. If the light cone is right, the actuator
S0 at trial k's readout tick must be bit-identical with trial k's cue negated (in every world) for every
trial the analytic model calls out-of-reach. Also: fresh-seed accuracy (4 x 64 worlds) of the champion,
which must be ~.5 if the excess is stale-information noise around a .5 expectation."""
from w2p_common import *
from prometheus.ananke.engine import World

CELLS = ["8a47a64b", "c90a8d57", "3ee88ab6", "cf195eaf"]
ck = Clock()


def trace_of(ph, g, env, seeds, flip_k=None):
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    if flip_k is not None:
        t0 = flip_k * env.period()
        ep.schedule.sense_val[t0:t0 + env.cue_len] *= -1
    w = World(ph, np.repeat(g[None], M, axis=0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    return ep, w.trace.cpu().numpy()


out = {}
by8 = {r["cell_id"][:8]: r for r in hc.rows()}
for c8 in CELLS:
    r = by8[c8]
    ph, env, g = load(r)
    seeds = held_seeds(r)
    ep, base = trace_of(ph, g, env, seeds)
    B = len(seeds)
    changed = []
    for k in range(env.trials):
        _, tr = trace_of(ph, g, env, seeds, flip_k=k)
        ro = ep.ro_tick[:, k]
        s_base = base[ro, np.arange(B), 0]
        s_flip = tr[ro, np.arange(B), 0]
        changed.append(int((s_base != s_flip).sum()))
    fresh = []
    for i in range(4):
        fs = assays.world_seeds(H_int(NS, 0xF5E5, int(c8, 16), i), 64)
        fresh.append(hc.evaluate(ph, g, env, fs)["acc"])
    out[c8] = {"worlds_with_S0_at_ro_k_changed_by_cue_k": changed, "fresh_acc_4x64": fresh,
               "fresh_mean": float(np.mean(fresh)), "rec_held": r["result"]["held"]["acc"]}
    print(c8, out[c8], flush=True)
out["compute"] = ck.done()
save("check_lightcone_exact.json", out)
print(ck.done())
