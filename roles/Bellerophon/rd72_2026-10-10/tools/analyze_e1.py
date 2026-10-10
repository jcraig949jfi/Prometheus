"""BEL-RD-72 E1 analysis (rules: BEL_RD72_PREREG.md s6; committed before the runs).   python3 analyze_e1.py RESULTS OUT
Per run, from the light census (FUNC counts per half-class): t_LO / t_HI / t_BOTH = first census with a FUNC tape that is
LO-or-BOTH / HI-or-BOTH / BOTH; retention = share of censuses after t_LO with a FUNC tape that is LO-or-BOTH; order of a
BOTH event = which half was FUNC-present at an earlier census (LO_FIRST, HI_FIRST, BOTH_PRIOR = both, NONE_PRIOR)."""
import json, math, sys
from collections import defaultdict


def fisher_greater(a, b, c, d):
    n1, n2, k = a + b, c + d, a + c
    if n1 == 0 or n2 == 0:
        return 1.0
    h = lambda x: math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n1 + n2, k)
    return round(sum(h(x) for x in range(a, min(n1, k) + 1)), 6)


def per_run(r):
    C = r["census"]
    f = lambda c, keys: sum((c.get("halves_func") or {}).get(k, 0) for k in keys)
    first = lambda keys: next((c["tick"] for c in C if f(c, keys) > 0), None)
    tLO, tHI, tB = first(("LO", "BOTH")), first(("HI", "BOTH")), first(("BOTH",))
    ret = None
    if tLO is not None:
        after = [c for c in C if c["tick"] > tLO]
        ret = round(sum(1 for c in after if f(c, ("LO", "BOTH")) > 0) / len(after), 3) if after else None
    order = None
    if tB is not None:
        pre = [c for c in C if c["tick"] < tB]
        lo = any(f(c, ("LO",)) > 0 for c in pre); hi = any(f(c, ("HI",)) > 0 for c in pre)
        order = "BOTH_PRIOR" if lo and hi else ("LO_FIRST" if lo else ("HI_FIRST" if hi else "NONE_PRIOR"))
    return {"id": r["id"], "survived": not r["summary"]["extinct"], "exposure": r.get("exposure", 0), "t_LO": tLO, "t_HI": tHI,
            "t_BOTH": tB, "retention_LO": ret, "order": order, "first_both": r.get("first_both")}


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    by = defaultdict(list)
    for r in R:
        by[r["cell"]].append(per_run(r))
    out = {"n": len(R) + len(voids), "voids": len(voids), "cells": {}, "runs": {c: v for c, v in by.items()}}
    for c, rs in sorted(by.items()):
        s = lambda key: sum(1 for x in rs if x[key] is not None)
        rets = sorted(x["retention_LO"] for x in rs if x["retention_LO"] is not None)
        out["cells"][c] = {"runs": len(rs), "survived": sum(x["survived"] for x in rs), "LO": s("t_LO"), "HI": s("t_HI"), "BOTH": s("t_BOTH"),
                           "retention_LO_median": rets[len(rets) // 2] if rets else None,
                           "order": {o: sum(1 for x in rs if x["order"] == o) for o in ("LO_FIRST", "HI_FIRST", "BOTH_PRIOR", "NONE_PRIOR")},
                           "exposure_median": sorted(x["exposure"] for x in rs)[len(rs) // 2] if rs else None}
    g = out["cells"]
    if "C1_ON" in g and "C1_OFF" in g:
        a, b = g["C1_ON"], g["C1_OFF"]
        out["E1_a_p_LO_ON_gt_OFF"] = fisher_greater(a["LO"], a["runs"] - a["LO"], b["LO"], b["runs"] - b["LO"])
        out["E1_b_p_BOTH_ON_gt_OFF"] = fisher_greater(a["BOTH"], a["runs"] - a["BOTH"], b["BOTH"], b["runs"] - b["BOTH"])
    out["replay_queue"] = sorted(x["id"] for rs in by.values() for x in rs if x["t_BOTH"] is not None)
    json.dump(out, open(outp, "w"), indent=1, sort_keys=True); print(json.dumps(out["cells"], indent=1)); return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
