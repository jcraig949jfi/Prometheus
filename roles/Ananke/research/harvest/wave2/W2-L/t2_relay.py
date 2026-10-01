"""Task 2: relay_flood at every selected MAJ row (held lo99 > .52 or SIGNAL) and FLIP row (held lo99 > .52; none exist),
row physics/env (prog_len raised to 12 where smaller, labelled), row held seeds (32 pairs). Zero-comm delta when acc >= .55."""
from w2l_common import *
ck = Clock()
sel = [r for r in hc.rows() if r["kind"] in ("evolve", "transfer") and r["env"]["family"] in ("FLIP", "MAJ")
       and ((r["result"].get("held") or {}).get("lo99", 0) > 0.52 or (r["env"]["family"] == "MAJ" and r["labels"].get("SIGNAL")))]
print(len(sel), "rows")
out = []
for r in sel:
    ph, env = cell(r)
    p2 = ph if ph.prog_len >= 12 else ph.replace(prog_len=12).validate()
    g = plants.plant("relay_flood", p2)
    s = held_seeds(r)
    a = hc.evaluate(p2, g, env, s)
    o = {"cell": r["cell_id"], "family": env.family, "kind": r["kind"], "wave": r["wave"],
         "prog_len_override": None if p2 is ph else [ph.prog_len, 12],
         "relay_acc": a["acc"], "relay_lo99": a["lo99"], "relay_hi99": a["hi99"],
         "rec_acc": r["result"]["held"]["acc"], "rec_lo99": r["result"]["held"]["lo99"], "rec_hi99": r["result"]["held"]["hi99"],
         "rec_cd_lo99": r["result"]["held"]["comm_delta_lo99"], "rec_SIGNAL": r["labels"]["SIGNAL"],
         "rec_relay_pv32": r["result"]["plant"]["acc"],
         "phys": {k: r["physics"][k] for k in ("topology", "update_mode", "dest_mode", "radius", "loss", "cap", "collision", "decay_shift")},
         "env": {k: r["env"][k] for k in ("d", "delta")}}
    if a["acc"] >= 0.55:
        z = hc.evaluate(p2, g, env, s, ctrl=Controls(zero_comm=True))
        dm, dlo, dhi = assays.pair_ci(np.array(a["pairs"]) - np.array(z["pairs"]))
        o.update({"relay_zero_comm": z["acc"], "relay_cd_lo99": float(dlo)})
    o["relay_SIGNAL"] = a["lo99"] > 0.55
    o["matches"] = a["acc"] >= o["rec_acc"] - (o["rec_hi99"] - o["rec_lo99"]) / 2
    o["exceeds"] = a["acc"] >= o["rec_acc"]
    out.append(o)
    print(o["cell"], o["family"], "rec %.3f lo %.3f SIG %s | relay %.3f [%.3f,%.3f] %s" % (o["rec_acc"], o["rec_lo99"], o["rec_SIGNAL"], a["acc"], a["lo99"], a["hi99"],
          "MATCH" if o["matches"] else ""), flush=True)
save("t2_relay_maj.json", {"rows": out, "compute": ck.done()})
print(ck.done())
