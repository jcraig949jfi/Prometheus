"""TASK 1b (positive control for the placement question): the hand-written relay_flood plant
(campaign.plant_viability semantics: prog_len=max(L,12)) on the same 35 MAJ graph evolve cells,
ORIGINAL vs INWARD placement. KA: original placement on the recorded plant seeds (H(seed,0x9147), 32)
must equal the recorded result.plant.acc. Fresh: 64 worlds, W2PP namespace."""
from w2p_common import *
from prometheus.ananke import plants
ck = Clock()
R = [r for r in hc.rows() if r["kind"] == "evolve" and r["env"]["family"] == "MAJ"
     and r["physics"]["topology"] in ("random", "smallworld")]
out = []
for r in R:
    ph, env, _ = load(r)
    p2 = ph.replace(prog_len=max(ph.prog_len, 12))
    g = plants.plant("relay_flood", p2)
    sets = {"rec": assays.world_seeds(H_int(r["search_seed"], 0x9147), 32), "fresh": fresh_seeds(r)}
    row = {"cell": r["cell_id"], "topology": ph.topology, "update_mode": ph.update_mode, "d": env.d,
           "delta": env.delta, "rec_plant_acc": r["result"]["plant"]["acc"]}
    for nm, seeds in sets.items():
        o = hc.evaluate(p2, g, env, seeds)
        with inward():
            oi = hc.evaluate(p2, g, env, seeds)
        row[nm + "_orig"] = {k: o[k] for k in ("acc", "lo99", "hi99")}
        row[nm + "_in"] = {k: oi[k] for k in ("acc", "lo99", "hi99")}
    row["ka_exact"] = abs(row["rec_orig"]["acc"] - row["rec_plant_acc"]) < 1e-12
    out.append(row)
    print(r["cell_id"][:8], ph.topology[:5], ph.update_mode, "d", env.d, "dl", env.delta, "KA", row["ka_exact"],
          "rec o/i %.3f/%.3f" % (row["rec_orig"]["acc"], row["rec_in"]["acc"]),
          "fresh o/i %.3f/%.3f lo %.3f/%.3f" % (row["fresh_orig"]["acc"], row["fresh_in"]["acc"],
                                                 row["fresh_orig"]["lo99"], row["fresh_in"]["lo99"]), flush=True)
def summ(sel):
    return {"n": len(sel), "ka_exact": sum(o["ka_exact"] for o in sel),
            "mean_fresh_orig": float(np.mean([o["fresh_orig"]["acc"] for o in sel])),
            "mean_fresh_in": float(np.mean([o["fresh_in"]["acc"] for o in sel])),
            "mean_delta_fresh": float(np.mean([o["fresh_in"]["acc"] - o["fresh_orig"]["acc"] for o in sel])),
            "lo99_gt_.55_orig": sum(o["fresh_orig"]["lo99"] > .55 for o in sel),
            "lo99_gt_.55_in": sum(o["fresh_in"]["lo99"] > .55 for o in sel)}
S = {"all": summ(out)}
for t in ("random", "smallworld"):
    S[t] = summ([o for o in out if o["topology"] == t])
for m in ("sync", "async"):
    S[m] = summ([o for o in out if o["update_mode"] == m])
print(json.dumps(S, indent=1))
save("task1b_plant_inward.json", {"summary": S, "rows": out, "compute": ck.done()})
print(ck.done())
