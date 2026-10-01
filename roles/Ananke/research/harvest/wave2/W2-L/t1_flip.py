"""Task 1: P-FLIP on the 58 light-cone-uncapped FLIP evolve rows (row physics/env, row held seeds, 32 pairs).
usage: python t1_flip.py <chunk> <nchunks> [variant]"""
from w2l_common import *
import hp_variants as hv
chunk, nch = int(sys.argv[1]), int(sys.argv[2])
variant = sys.argv[3] if len(sys.argv) > 3 else "base"
only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
ck = Clock()
rows = [r for r in hc.rows() if r["kind"] == "evolve" and r["env"]["family"] == "FLIP" and LC[r["cell_id"]]["bound"] >= 0.60]
assert len(rows) == 58, len(rows)
rows.sort(key=lambda r: r["cell_id"])
if only:
    rows = [r for r in rows if r["cell_id"] in only]
else:
    rows = rows[chunk::nch]
M = int(os.environ.get("W2L_M", "64"))
out = []
for r in rows:
    ph, env = cell(r)
    need_L = hv.NEED_L[variant]
    exact = ph.state_dim >= 2 and ph.prog_len >= need_L
    p2 = ph if exact else ph.replace(state_dim=max(2, ph.state_dim), prog_len=max(need_L, ph.prog_len)).validate()
    g = hv.plant(variant, p2)
    res = hc.evaluate(p2, g, env, held_seeds(r, M))
    h = r["result"]["held"]
    o = {"cell": r["cell_id"], "wave": r["wave"], "variant": variant, "exact_space": exact,
         "override": {} if exact else {"state_dim": [ph.state_dim, p2.state_dim], "prog_len": [ph.prog_len, p2.prog_len]},
         "acc": res["acc"], "lo99": res["lo99"], "hi99": res["hi99"], "M": M, "stats": res["stats"],
         "held_rec": h["acc"], "held_rec_lo99": h["lo99"], "lc_bound": LC[r["cell_id"]]["bound"],
         "relay_rec": r["result"]["plant"]["acc"],
         "phys": {k: r["physics"][k] for k in ("topology", "n_sites", "radius", "dest_mode", "fanout", "loss", "lat_base", "lat_hop",
                                                 "lat_jitter", "dup", "noise", "cap", "collision", "decay_shift", "update_mode",
                                                 "update_period", "update_p", "state_dim", "prog_len", "payload_width", "rules",
                                                 "e_income", "c_emit", "c_op", "c_mem", "mut_site")},
         "env": {k: r["env"][k] for k in ("d", "delta", "block")}}
    out.append(o)
    print(o["cell"], variant, "exact" if exact else "OVR", "acc %.3f [%.3f,%.3f]" % (o["acc"], o["lo99"], o["hi99"]), o["phys"]["update_mode"], o["phys"]["topology"],
          "dec", o["phys"]["decay_shift"], "cap", o["phys"]["cap"], o["phys"]["collision"], "loss", o["phys"]["loss"], flush=True)
tag = "_".join(only)[:40] if only else f"{chunk}of{nch}"
save(f"t1_{variant}_M{M}_{tag}.json", {"rows": out, "compute": ck.done()})
print(ck.done())
