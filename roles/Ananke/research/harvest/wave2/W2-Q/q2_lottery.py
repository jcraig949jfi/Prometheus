"""Q2: rule-mosaic lottery. setrule=0, rules>1 evolve rows, SIGNAL + near-SIGNAL (held acc>=.56, lo99>.515).
Conditions: normal, r pinned to k at ALL sites (World.r and World.r0 overwritten after init; setrule=0 so
r never changes; reset_parts 'r' would restore r0, also pinned). Covariate: actuator r0 from the run's own
(mirrored) world seeds; also W2-E a1's unmirrored recomputation for comparison. 16 pairs."""
from q_common import *
ck = Clock()
ev = [r for r in rows() if r["kind"] == "evolve" and r["physics"]["setrule"] == 0 and r["physics"]["rules"] > 1]
cells = [r for r in ev if r["labels"]["SIGNAL"]] + sorted(
    [r for r in ev if not r["labels"]["SIGNAL"] and r["result"]["held"]["acc"] >= .56 and r["result"]["held"]["lo99"] > .515],
    key=lambda r: -r["result"]["held"]["acc"])
path = OUT / "q2_lottery.json"
done = json.loads(path.read_text()) if path.exists() else {}
cap = float(sys.argv[1]) if len(sys.argv) > 1 else 330
for r in cells:
    cid = r["cell_id"][:8]
    if cid in done: continue
    if time.process_time() - ck.t0 > cap: break
    tc = time.process_time()
    ph, env = spec_of(r); g = genome_of(r); G = ph.rules
    S = seeds(H_int(NS, 0x02, int(cid, 16) & 0xFFFF), 32)
    def pin(w, sl):
        for k in range(G):
            w.r[sl[k + 1]] = k; w.r0[sl[k + 1]] = k
    holder = {}
    def post(w, sl):
        holder["r0"] = w.r0[sl[0]].clone().numpy(); pin(w, sl)
    res, w = run_batched(ph, g, env, S, [("N", None)] + [(f"pin{k}", None) for k in range(G)], post_init=post)
    aN = res["N"][0]; pN = pairs(aN)
    act = res["N"][2].schedule.read_idx[:, 0].numpy()
    r0 = holder["r0"]; ra = r0[np.arange(32), act]
    # W2-E a1-style (unmirrored seeds) recomputation of the actuator rule
    wu = World(ph, np.repeat(g[None], 32, 0), S, device="cpu", schedule=res["N"][2].schedule)
    ra_u = wu.r0.numpy()[np.arange(32), act]
    d = {"wave": r["wave"], "family": r["env"]["family"], "rules": G, "topology": ph.topology, "mode": ph.update_mode,
         "N": ph.n_sites, "signal": r["labels"]["SIGNAL"], "rec_held": round(r["result"]["held"]["acc"], 4),
         "rec_lo99": round(r["result"]["held"]["lo99"], 4), "rec_train_final": round(r["result"]["champ_train_final"], 4),
         "parent": r["parent"], "normal": ci(pN), "pairs_N": pN.tolist()}
    for k in range(G):
        p = pairs(res[f"pin{k}"][0]); d[f"pin{k}"] = ci(p); d[f"pin{k}_pairs"] = p.tolist()
        d[f"pin{k}_diff"] = ci(p - pN)
    d["acc_by_actuator_r0"] = {int(k): [round(float(aN[ra == k].mean()), 4), int((ra == k).sum())] for k in np.unique(ra)}
    d["acc_by_actuator_r0_unmirrored(a1-style)"] = {int(k): [round(float(aN[ra_u == k].mean()), 4), int((ra_u == k).sum())] for k in np.unique(ra_u)}
    d["frac_r0_mismatch_unmirrored"] = float((ra != ra_u).mean())
    fr = np.stack([(r0 == k).mean(1) for k in range(G)], 1)       # per-world rule fractions
    d["rule_frac_mean"] = fr.mean(0).round(3).tolist()
    # variance of pair acc explained by actuator rule (pairs share r0)
    rp = ra[0::2]; 
    if len(np.unique(rp)) > 1:
        mu = np.array([pN[rp == k].mean() for k in rp]); d["R2_pairs_by_actuator_r0"] = round(float(1 - ((pN - mu) ** 2).sum() / max(((pN - pN.mean()) ** 2).sum(), 1e-12)), 3)
    d["cpu_s"] = round(time.process_time() - tc, 2)
    done[cid] = d; path.write_text(json.dumps(done, indent=1))
    print(cid, d["signal"], d["rec_held"], "N", d["normal"][0], [d[f"pin{k}"][0] for k in range(G)], d["acc_by_actuator_r0"], d.get("R2_pairs_by_actuator_r0"), d["cpu_s"], flush=True)
print(len(done), "of", len(cells), ck.done())
