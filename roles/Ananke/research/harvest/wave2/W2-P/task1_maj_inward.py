"""TASK 1: re-evaluate the 35 C1 MAJ evolve champions on random/smallworld under ORIGINAL vs INWARD
sensor placement. Known-answer: original placement on recorded held seeds must equal recorded held acc.
Sets: held (recorded M_held=64 seeds; orig + inward) and fresh (64 worlds, W2PP namespace; orig + inward).
Placement check: fraction of sensors at transport distance M[s,a]==d, and unreachable sensors."""
from w2p_common import *
ck = Clock()
R = [r for r in hc.rows() if r["kind"] == "evolve" and r["env"]["family"] == "MAJ"
     and r["physics"]["topology"] in ("random", "smallworld")]
assert len(R) == 35, len(R)

def placement(ph, env, seeds, inw):
    M = envs.dist_matrix(ph)
    if inw:
        with inward():
            ep = envs.build(ph, env, seeds)
    else:
        ep = envs.build(ph, env, seeds)
    s = ep.schedule.sense_idx.numpy(); a = ep.schedule.read_idx.numpy()[:, 0]
    f = np.stack([M[s[b], a[b]] for b in range(0, len(seeds), 2)])
    return {"frac_eq_d": float((f == env.d).mean()), "frac_gt_d": float(((f > env.d) & (f < 10**6)).mean()),
            "frac_unreach": float((f >= 10**6).mean()), "mean_hops_reach": float(f[f < 10**6].mean())}

out = []
for r in R:
    ph, env, g = load(r)
    rec = r["result"]["held"]
    row = {"cell": r["cell_id"], "wave": r["wave"], "topology": ph.topology, "update_mode": ph.update_mode,
           "update_period": ph.update_period, "update_p": ph.update_p, "d": env.d, "delta": env.delta,
           "rec_held_acc": rec["acc"], "rec_held_lo99": rec["lo99"], "SIGNAL_label": r["labels"]["SIGNAL"]}
    hs, fs = held_seeds(r), fresh_seeds(r)
    for name, seeds in (("held", hs), ("fresh", fs)):
        for inw in (False, True):
            if inw:
                envs._DIST_CACHE.clear()
                with inward():
                    o = hc.evaluate(ph, g, env, seeds)
            else:
                o = hc.evaluate(ph, g, env, seeds)
            row[f"{name}_{'in' if inw else 'orig'}"] = {k: o[k] for k in ("acc", "lo99", "hi99")}
            row[f"{name}_{'in' if inw else 'orig'}"]["emit"] = o["stats"].get("emitters")
    row["ka_exact"] = abs(row["held_orig"]["acc"] - rec["acc"]) < 1e-12 and abs(row["held_orig"]["lo99"] - rec["lo99"]) < 1e-12
    row["place_orig"] = placement(ph, env, fs, False)
    row["place_in"] = placement(ph, env, fs, True)
    out.append(row)
    print(r["cell_id"][:8], ph.topology[:5], ph.update_mode, "d", env.d, "dl", env.delta,
          "rec %.3f" % rec["acc"], "KA", row["ka_exact"],
          "held o/i %.3f/%.3f" % (row["held_orig"]["acc"], row["held_in"]["acc"]),
          "fresh o/i %.3f/%.3f lo %.3f/%.3f" % (row["fresh_orig"]["acc"], row["fresh_in"]["acc"],
                                                 row["fresh_orig"]["lo99"], row["fresh_in"]["lo99"]),
          "eq_d o/i %.2f/%.2f" % (row["place_orig"]["frac_eq_d"], row["place_in"]["frac_eq_d"]), flush=True)

def summ(sel):
    n = len(sel)
    return {"n": n,
            "ka_exact": sum(o["ka_exact"] for o in sel),
            "ka_exact_nontrivial": sum(o["ka_exact"] and abs(o["rec_held_acc"] - .5) > 1e-9 for o in sel),
            "signal_fresh_orig": sum(o["fresh_orig"]["lo99"] > .55 for o in sel),
            "signal_fresh_in": sum(o["fresh_in"]["lo99"] > .55 for o in sel),
            "signal_held_in": sum(o["held_in"]["lo99"] > .55 for o in sel),
            "mean_fresh_orig": float(np.mean([o["fresh_orig"]["acc"] for o in sel])),
            "mean_fresh_in": float(np.mean([o["fresh_in"]["acc"] for o in sel])),
            "mean_delta_fresh": float(np.mean([o["fresh_in"]["acc"] - o["fresh_orig"]["acc"] for o in sel])),
            "mean_delta_held": float(np.mean([o["held_in"]["acc"] - o["held_orig"]["acc"] for o in sel])),
            "max_fresh_in": float(max(o["fresh_in"]["acc"] for o in sel)),
            "max_fresh_in_lo99": float(max(o["fresh_in"]["lo99"] for o in sel)),
            "n_fresh_orig_exact_half": sum(o["fresh_orig"]["acc"] == .5 for o in sel),
            "n_fresh_in_exact_half": sum(o["fresh_in"]["acc"] == .5 for o in sel)}
S = {"all": summ(out)}
for t in ("random", "smallworld"):
    S[t] = summ([o for o in out if o["topology"] == t])
for m in ("sync", "async"):
    S[m] = summ([o for o in out if o["update_mode"] == m])
print(json.dumps(S, indent=1))
save("task1_maj_inward.json", {"summary": S, "rows": out, "compute": ck.done()})
print(ck.done())
