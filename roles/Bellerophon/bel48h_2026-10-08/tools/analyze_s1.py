"""BEL-48H S1 analysis (rules: prereg s19).   python3 analyze_s1.py RESULTS OUT"""
import json, math, sys
from collections import defaultdict
from analyze_w1 import mcnemar_exact


def one_sided(x, y):
    n = x + y
    return round(sum(math.comb(n, i) for i in range(x, n + 1)) / 2 ** n, 6) if n else 1.0


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    out = {"n": len(R) + len(voids), "voids": len(voids), "S1a": {}, "S1b": {}}
    org = lambda r: bool((r.get("origin") or {}).get("origin_event"))
    fa = lambda r: r["heredity"]["first_func"] is not None
    tb = tn = 0
    for lane, key, a1, a2, f in (("S1a", "S1a", "blocked", "normal", org), ("S1b", "S1b", "AB", "AB_copy", fa)):
        cells = defaultdict(dict)
        for r in R:
            if r["lane"] == lane:
                cells[(r["cell"], r["pair"])][r["arm"]] = r
        for c in sorted({k[0] for k in cells}):
            ps = [v for k, v in cells.items() if k[0] == c and len(v) == 2]
            x = sum(1 for v in ps if f(v[a1]) and not f(v[a2])); y = sum(1 for v in ps if f(v[a2]) and not f(v[a1]))
            out[key][c] = {"pairs": len(ps), a1: sum(f(v[a1]) for v in ps), a2: sum(f(v[a2]) for v in ps),
                           "%s_only" % a1: x, "%s_only" % a2: y, "p_one_sided": one_sided(x, y)}
            if lane == "S1a":
                tb += x; tn += y
    out["S1-P1"] = {"pooled_blocked_only": tb, "pooled_normal_only": tn, "p": one_sided(tb, tn), "holds": one_sided(tb, tn) < 0.05}
    out["S1-P2"] = {"holds": all(v["p_one_sided"] < 0.05 for v in out["S1b"].values()) and len(out["S1b"]) == 2}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
