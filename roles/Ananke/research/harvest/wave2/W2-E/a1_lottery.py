"""A1: 0187372b held .750 vs champ_train_final .529. Per-world lottery?"""
from w2e_common import *
from prometheus.ananke.search import HELD_NS, FINAL_NS
ck = Clock()
out = {}
for cid in ["0187372b", "8d1c8213"]:
    r = row(cid, "evolve"); ph, env = spec_of(r); g = genome_of(r)
    ss = r["search_seed"]
    res = {}
    for name, base, M in [("held", H_int(ss, HELD_NS), 64), ("final", H_int(ss, FINAL_NS), 16),
                          ("fresh", H_int(NS, 0xA1, ss & 0xFFFF), 256)]:
        acc, tr, ep, w = run(ph, g, env, seeds(base, M))
        p = pairs(acc)
        # initial rule of the actuator site per world (r at INIT; recomputed)
        a = ep.schedule.read_idx[:, 0].numpy()
        res[name] = {"M": M, "ci": ci(p), "pair_hist": np.histogram(p, bins=[0, .3, .45, .55, .7, .85, .95, 1.01])[0].tolist(),
                     "frac_pairs_ge_.95": float((p >= .95).mean()), "frac_pairs_le_.55": float((p <= .55).mean())}
        if name == "fresh":
            # rule index at actuator at t=0 from engine init: rerun 0 ticks
            w0 = World(ph, np.repeat(g[None], M, 0), [s for s in seeds(base, M)], device="cpu", schedule=ep.schedule)
            r0 = w0.r.numpy()[np.arange(M), a]
            res[name]["acc_by_r0"] = {int(k): float(acc[r0 == k].mean()) for k in np.unique(r0)}
            res[name]["n_by_r0"] = {int(k): int((r0 == k).sum()) for k in np.unique(r0)}
    out[cid] = {"recorded_held": r["result"]["held"]["acc"], "recorded_train_final": r["result"]["champ_train_final"],
                "physics_rules": ph.rules, "setrule": ph.setrule, "res": res}
    print(cid, json.dumps(out[cid]))
out["clock"] = ck.done(); save("a1_lottery.json", out); print(out["clock"])
