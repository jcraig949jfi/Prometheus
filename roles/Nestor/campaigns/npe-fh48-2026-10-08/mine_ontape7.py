"""Replay X-ONTAPE ONTAPE seed 44900007 (deterministic) and capture the dominant genomes during the late collapse."""
import collections, json, sys
sys.dont_write_bytecode = True
import fh, exp
cfg = dict(gate="CONST", p_const=0.15, order="ONTAPE")
r = fh.make_runner(44_900_007, cfg)
anc = 0
for i in range(r.pop_cap):
    g = r._pad(r._implant_genome()) if i == 0 else r._seed_genome()
    o = r._place(g, anc, niche=r._initial_niche(i)); o.energy = r.t["slice"] * 2; anc += 1
r._validate(force=True)
snap = {}
while r.epoch < 2000:
    r.step()
    if r.epoch in (1400, 1600, 1800, 1900, 2000):
        alive = [o for o in r.orgs if o.alive]
        cnt = collections.Counter(r._genome(o).hex() for o in alive)
        top = []
        for h, c in cnt.most_common(4):
            g = bytes.fromhex(h)
            members = [o for o in alive if r._genome(o).hex() == h]
            sc = sum(r.ontape.get(o, 0) for o in members) / len(members)
            top.append({"count": c, "u": r.cache.u(g), "ontape_ewma_mean": round(sc, 3),
                        "ham_CT_UA": sum(g[j] != fh.PLANTS["CT_UA"][j] for j in range(64)), "hex": h})
        cs = sum(r.cache.competent(r._genome(o)) for o in alive) / len(alive)
        mean_sc_comp = [r.ontape.get(o, 0) for o in alive if r.cache.u(r._genome(o)) >= 0.75]
        mean_sc_non = [r.ontape.get(o, 0) for o in alive if r.cache.u(r._genome(o)) < 0.75]
        snap[r.epoch] = {"CS": round(cs, 3), "ewma_comp": round(sum(mean_sc_comp) / max(1, len(mean_sc_comp)), 3),
                         "ewma_noncomp": round(sum(mean_sc_non) / max(1, len(mean_sc_non)), 3), "top": top}
        print(r.epoch, snap[r.epoch]["CS"], snap[r.epoch]["ewma_comp"], snap[r.epoch]["ewma_noncomp"],
              [(t["count"], t["u"], t["ontape_ewma_mean"], t["ham_CT_UA"]) for t in top], flush=True)
json.dump(snap, open("runs/X-ONTAPE/MINE_ONTAPE_44900007.json", "w"), indent=1)
