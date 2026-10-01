"""W2-44 t6: who destroys the donor's half at its non-first-mover side? W2-24 q1_trace.analyse (last-writer authorship)
on the N17e panel for the founder, AC, CNR_s22 root, the chained-LDIR founder analogue F+59:ED,60:B0, CRW_78 root,
and the CRW_1 core / root, at both sides. Reports keep, conv and the top loss sites.
python -B t6_hijack.py -> t6_hijack.json"""
import json, time
from common44 import *  # noqa
from q1_trace import analyse  # noqa
t0 = time.process_time()


def mk(base, muts):
    g = bytearray(base)
    for p, v in muts.items():
        g[p] = v
    return bytes(g)


D = {"F": F, "AC": mk(F, {44: 0xAC}), "F+43:81": mk(F, {43: 0x81}), "F+59:ED,60:B0": mk(F, {59: 0xED, 60: 0xB0}),
     "CNR22": GEN["CNR_s22_first"], "CRW78": GEN["CRW_78_first"],
     "CRW1core": mk(rot_of(F, 46), {43: 0xD2, 44: 0xA2}), "CRW1": GEN["CRW_1_first"]}
out = {}
for nm, x in D.items():
    res = {}
    for side in (0, 1):
        recs = [analyse(r, x, y, cy, s) for y, cy, cx, s in PAN if s == side]
        N = len(recs)
        loss = [q for q in recs if not q["keep"]]
        sites = collections.Counter()
        for q in loss:
            if q["sites"]:
                sites[max(q["sites"].items(), key=lambda t: t[1])[0]] += 1
        intact = sum(q["after0_donor_half_intact"] for q in recs) if side == 1 else None
        pre_damaged_losses = sum(1 for q in loss if not q["after0_donor_half_intact"]) if side == 1 else None
        res[side] = {"N": N, "keep": round(1 - len(loss) / N, 3), "conv": round(sum(q["conv"] for q in recs) / N, 3),
                     "losses": len(loss), "top_loss_sites": dict(sites.most_common(4)),
                     "losses_where_first_mover_already_damaged": pre_damaged_losses,
                     "intact_after_first_mover": intact}
    out[nm] = res
    print(nm, json.dumps(res), flush=True)
out["_cpu_s"] = round(time.process_time() - t0, 1)
(HERE / "t6_hijack.json").write_text(json.dumps(out, indent=1))
print("cpu", out["_cpu_s"])
