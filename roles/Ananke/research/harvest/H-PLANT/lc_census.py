"""A7 light-cone census over C1 evolve rows (analytic; no engine)."""
import collections
import json

import hp_common as hc
from hp_common import Clock, save
from lightcone import bound

ck = Clock()
out = []
for r in hc.rows():
    if r["wave"] == "A0" or r["env"]["family"] not in ("XOR", "FLIP", "RELAY"):
        continue
    b = bound(r["cell_id"], M=64)
    held = r["result"].get("held") or {}
    out.append({"cell": r["cell_id"], "wave": r["wave"], "family": r["env"]["family"],
                "d": r["env"]["d"], "delta": r["env"]["delta"], "topology": r["physics"]["topology"],
                "update_mode": r["physics"]["update_mode"], "bound": b["acc_upper_bound"],
                "held_lo99": held.get("lo99") if isinstance(held, dict) else None})
summ = {}
for fam in ("XOR", "FLIP", "RELAY"):
    xs = [o for o in out if o["family"] == fam]
    lo = [o for o in xs if o["bound"] < 0.60]
    sig = [o for o in xs if o["held_lo99"] is not None and o["held_lo99"] > 0.55]
    summ[fam] = {"rows": len(xs), "bound_lt_.60": len(lo),
                 "frac_bound_lt_.60": round(len(lo) / max(1, len(xs)), 3),
                 "rows_held_lo99_gt_.55": len(sig),
                 "held_gt_.55_but_bound_lt_.60": sum(1 for o in sig if o["bound"] < 0.60)}
    print(fam, summ[fam])
save("lc_census.json", {"summary": summ, "rows": out, "compute": ck.done()})
print(ck.done())
