"""Task 1: overall acc + FLIP_CHANGE for every recorded C1 FLIP champion (82 evolve + 12 transfer).
usage: python t1_record.py <chunk> <nchunks>. M=64 (32 pairs) for rows with recorded acc > .5, else M=32 (16 pairs)."""
from w2s_common import *
chunk, nch = int(sys.argv[1]), int(sys.argv[2])
ck = Clock()
rows = sorted([r for r in hc.rows() if r["env"]["family"] == "FLIP" and r["kind"] in ("evolve", "transfer")], key=lambda r: r["cell_id"] + r["kind"])
assert len(rows) == 94
out = []
for r in rows[chunk::nch]:
    ph, env = cell(r)
    G = np.asarray(r["result"]["champion"] if r["kind"] == "evolve" else r["extra"]["genome"])
    h = r["result"]["held"]
    M = 64 if h["acc"] > 0.5 else 32
    o = flip_eval(ph, G, env, held_seeds(r, M)); o.pop("pairs")
    o.update(cell=r["cell_id"], kind=r["kind"], wave=r["wave"], held_rec=h["acc"], held_rec_lo99=h["lo99"],
             match=(abs(o["acc"] - h["acc"]) < 1e-9) if M == 64 else None, lc_bound=LC.get(r["cell_id"], {}).get("bound"),
             env={k: r["env"][k] for k in ("d", "delta", "block")})
    out.append(o)
    print(r["cell_id"][:8], r["kind"][:3], "M%d rec %.3f me %.3f %s chg %.3f [%.3f,%.3f] same %.3f" % (M, h["acc"], o["acc"], o["match"], o["chg"], o["chg_lo99"], o["chg_hi99"], o["same"]), flush=True)
save(f"t1_record_{chunk}of{nch}.json", {"rows": out, "compute": ck.done()}); print(ck.done())
