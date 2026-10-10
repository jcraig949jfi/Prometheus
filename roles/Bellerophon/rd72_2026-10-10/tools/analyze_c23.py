"""BEL-RD-72 C2 / C3 analysis (rules: BEL_RD72_PREREG.md s7; committed before any E1 result).
    python3 analyze_c23.py C23_RESULTS E1_RESULTS OUT"""
import json, sys
from collections import defaultdict
from analyze_k import fisher_greater

f = lambda c, keys: sum((c.get("halves_func") or {}).get(k, 0) for k in keys)


def per(r):
    at = r["intervention"]["tick"]; post = [c for c in r["census"] if c["tick"] > at]
    t_re = next((c["tick"] for c in post if f(c, ("LO", "BOTH")) > 0), None)
    return {"world": r["pair"], "arm": r["arm"], "lane": r["lane"], "at": at, "affected": r["intervention"]["affected"],
            "lo_end": bool(post) and f(post[-1], ("LO", "BOTH")) > 0, "both": any(f(c, ("BOTH",)) > 0 for c in post),
            "t_re": (t_re - at) if t_re is not None else None, "survived": not r["summary"]["extinct"]}


def main(res, e1res, outp):
    tLO = {}
    for l in open(e1res):
        r = json.loads(l)
        if not r.get("void"):
            tLO[r["id"]] = next((c["tick"] for c in r["census"] if f(c, ("LO", "BOTH")) > 0), None)
    X = [per(json.loads(l)) for l in open(res) if not json.loads(l).get("void")]
    g = defaultdict(list)
    for x in X:
        g[(x["lane"], x["arm"])].append(x)
    cnt = lambda lane, arm, key: (sum(1 for x in g[(lane, arm)] if x[key]), len(g[(lane, arm)]))
    out = {"cells": {"%s|%s" % k: {"n": len(v), "lo_end": sum(x["lo_end"] for x in v), "both": sum(x["both"] for x in v),
                                   "survived": sum(x["survived"] for x in v), "affected_median": sorted(x["affected"] for x in v)[len(v) // 2]}
                     for k, v in sorted(g.items())}}
    (a, n), (b, m) = cnt("C2", "SHAM", "lo_end"), cnt("C2", "REMOVE", "lo_end")
    out["C2-a"] = {"sham_lo_end": [a, n], "remove_lo_end": [b, m], "p_sham_gt_remove": fisher_greater(a, n - a, b, m - b)}
    pairs = [(x["t_re"], tLO.get(x["world"])) for x in g[("C2", "REMOVE")] if x["t_re"] is not None and tLO.get(x["world"]) is not None]
    faster = sum(1 for re, orig in pairs if re < orig); slower = sum(1 for re, orig in pairs if re > orig)
    from math import comb
    N = faster + slower
    p = sum(comb(N, k) for k in range(faster, N + 1)) / 2 ** N if N else 1.0
    out["C2-b"] = {"regenerated": len(pairs), "of": len(g[("C2", "REMOVE")]), "faster": faster, "slower": slower, "p_sign": round(p, 6),
                   "holds": (p < 0.05) if N >= 5 else "NOT_TESTABLE"}
    (a, n), (b, m), (s, q) = cnt("C3", "A_PRESENT", "both"), cnt("C3", "ABLATE", "both"), cnt("C3", "SHAM", "both")
    p1, p2 = fisher_greater(a, n - a, b, m - b), fisher_greater(s, q - s, b, m - b)
    out["C3-P1"] = {"A_PRESENT": [a, n], "ABLATE": [b, m], "SHAM": [s, q], "p_A_gt_ABLATE": p1, "p_SHAM_gt_ABLATE": p2,
                    "holds": (p1 < 0.05 and p2 < 0.05) if a + s >= 5 else "NOT_TESTABLE"}
    (a, n), (b, m) = cnt("C3F", "IMPLANT", "both"), cnt("C3F", "IMPLANT_SHAM", "both")
    pf = fisher_greater(a, n - a, b, m - b)
    out["C3-P2"] = {"IMPLANT": [a, n], "IMPLANT_SHAM": [b, m], "p": pf, "holds": (pf < 0.05) if a + b >= 5 else "NOT_TESTABLE"}
    json.dump(out, open(outp, "w"), indent=1); print(json.dumps(out, indent=1)); return out


if __name__ == "__main__":
    main(*sys.argv[1:4])
