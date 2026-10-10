"""BEL-RD-72 K analysis (rules: BEL_RD72_PREREG.md s3; committed before the runs).   python3 analyze_k.py RESULTS OUT"""
import json, math, sys
from collections import Counter, defaultdict


def fisher_greater(a, b, c, d):
    n1, n2, k = a + b, c + d, a + c
    if n1 == 0 or n2 == 0:
        return 1.0
    h = lambda x: math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n1 + n2, k)
    return round(sum(h(x) for x in range(a, min(n1, k) + 1)), 6)


def comp_any(r):
    return (r["comp"]["C"].get("gain", 0) or 0) > 0


def comp_sr(r):
    return (r["comp"]["C"].get("comp_func_births", 0) or 0) > 0 or (r["comp"].get("first_comp_sr") is not None)


def two_source(r):
    """competence-critical bytes of the first competent self-replicator (or the dominant) include founder bytes of BOTH
    transplant0 (X) and transplant1 (Y)."""
    a = (r["comp"].get("first_comp_sr") or {}).get("anatomy") or r["comp"].get("dominant") or {}
    m = set(a.get("ccrit_founder_mech") or [])
    return {"transplant0", "transplant1"} <= m


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    by = defaultdict(list)
    for r in R:
        by[(r["cell"], r["arm"])].append(r)
    out = {"n": len(R) + len(voids), "voids": len(voids), "cells": {}}
    for (c, a), rs in sorted(by.items()):
        out["cells"]["%s|%s" % (c, a)] = {"runs": len(rs), "comp_any": sum(map(comp_any, rs)), "comp_sr": sum(map(comp_sr, rs)),
                                          "extinct": sum(r["summary"]["extinct"] for r in rs),
                                          "exposure_median": sorted(r.get("exposure", 0) for r in rs)[len(rs) // 2] if rs else None,
                                          "two_source_of_comp_sr": sum(1 for r in rs if comp_sr(r) and two_source(r))}
    C = out["cells"]
    g = lambda c, k: C.get(c, {}).get(k, 0); n = lambda c: C.get(c, {}).get("runs", 0)
    cb = [g("XY_AL/%s|ON" % ops, "comp_sr") for ops in ("COPY_BYTE", "COPY_STRUCT")]
    out["K-P1"] = {"XY_AL_COPY_BYTE": cb[0], "XY_AL_COPY_STRUCT": cb[1], "holds": all(x <= 2 for x in cb)}
    xy = "XY_AL/PARTIAL_BYTE|ON"
    ps = {other: fisher_greater(g(xy, "comp_any"), n(xy) - g(xy, "comp_any"), g(other, "comp_any"), n(other) - g(other, "comp_any"))
          for other in ("X_ONLY/PARTIAL_BYTE|ON", "Y_ONLY/PARTIAL_BYTE|ON", "XY_AL/COPY_BYTE|ON")}
    out["K-P2"] = {"comp_any": {k: g(k, "comp_any") for k in [xy] + list(ps)}, "p": ps, "holds": all(p < 0.05 for p in ps.values())}
    srs = g(xy, "comp_sr"); ts = g(xy, "two_source_of_comp_sr")
    out["K-P3"] = {"two_source": [ts, srs], "holds": (ts >= 0.8 * srs) if srs else "NOT_TESTABLE"}
    off = "XY_AL/PARTIAL_BYTE|OFF"
    pOFF = fisher_greater(g(xy, "comp_any"), n(xy) - g(xy, "comp_any"), g(off, "comp_any"), n(off) - g(off, "comp_any"))
    out["K-P4"] = {"ON": g(xy, "comp_any"), "OFF": g(off, "comp_any"), "p": pOFF, "holds": pOFF < 0.05}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
