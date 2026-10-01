"""Task 1 addendum: balanced accuracy B=(same+chg)/2 (pair CI) and answer-source decomposition."""
from w2s_common import *
ck = Clock(); out = []
jobs = [("6f82f9c7d51bcef1", "P-FLIP"), ("996716ac46f73a43", "P-FLIP"), ("64d33b89811637f7", "P-FLIP"),
        ("6f82f9c7d51bcef1", "RELAY_LATCH"), ("996716ac46f73a43", "RELAY_LATCH"), ("64d33b89811637f7", "RELAY_LATCH"),
        ("6f82f9c7d51bcef1", "relay_flood")]
jobs += [(c, "champion") for c in ("964053bb4c9065fd", "221042948e32063c", "34f84c6b", "f30f89b0", "996716ac46f73a43")]
jobs += [(c, "transfer") for c in ("f728b1d2", "1ec4e938")]
allr = hc.rows()
for cid, prog in jobs:
    kind = "transfer" if prog == "transfer" else "evolve"
    r = [x for x in allr if x["cell_id"].startswith(cid) and x["kind"] == kind and x["env"]["family"] == "FLIP"][0]
    ph, env = cell(r)
    if prog == "P-FLIP": p, g = ph, hp_plants.p_flip(ph)
    elif prog == "RELAY_LATCH":
        p = ph if ph.prog_len >= 14 else ph.replace(prog_len=14).validate(); g = relay_latch(p)
    elif prog == "relay_flood":
        p = ph if ph.prog_len >= 12 else ph.replace(prog_len=12).validate(); g = plants.plant("relay_flood", p)
    else:
        p, g = ph, np.asarray(r["result"]["champion"] if kind == "evolve" else r["extra"]["genome"])
    o = flip_eval(p, g, env, held_seeds(r, 64)); o.pop("pairs")
    o.update(cell=r["cell_id"], program=prog, kind=kind, exact=(p is ph)); out.append(o)
    print(r["cell_id"][:8], prog, "acc %.3f [%.3f] same %.3f chg %.3f [%.3f] bal %.3f [%.3f,%.3f]" % (o["acc"], o["lo99"], o["same"], o["chg"], o["chg_lo99"], o["bal"], o["bal_lo99"], o["bal_hi99"]),
          {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in o["src"].items()}, flush=True)
save("t1_balanced.json", {"rows": out, "compute": ck.done()}); print(ck.done())
