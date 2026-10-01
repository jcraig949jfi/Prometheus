"""Task 1 controls: P-FLIP (positives) at the 3 PLANT-SOLVED rows; RELAY_LATCH + relay_flood (negatives)."""
from w2s_common import *
ck = Clock(); out = []
for cid in ("6f82f9c7d51bcef1", "996716ac46f73a43", "64d33b89811637f7"):
    r = hc.row(cid); ph, env = cell(r); seeds = held_seeds(r)
    progs = [("P-FLIP", ph, hp_plants.p_flip(ph))]
    p12 = ph if ph.prog_len >= 14 else ph.replace(prog_len=14).validate()
    progs.append(("RELAY_LATCH", p12, relay_latch(p12)))
    if cid.startswith("6f82"):
        p12b = ph if ph.prog_len >= 12 else ph.replace(prog_len=12).validate()
        progs.append(("relay_flood", p12b, plants.plant("relay_flood", p12b)))
    for name, p, g in progs:
        o = flip_eval(p, g, env, seeds); o.pop("pairs")
        o.update(cell=cid, program=name, exact=(p is ph)); out.append(o)
        print(cid[:8], name, "acc %.3f [%.3f,%.3f] chg %.3f [%.3f,%.3f] same %.3f" % (o["acc"], o["lo99"], o["hi99"], o["chg"], o["chg_lo99"], o["chg_hi99"], o["same"]), o["tab"], flush=True)
save("t1_controls.json", {"rows": out, "compute": ck.done()}); print(ck.done())
