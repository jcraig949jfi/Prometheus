"""BEL-RD-72 D1 analysis (rules: BEL_RD72_PREREG.md s2; committed before the runs).   python3 analyze_d1.py RESULTS OUT"""
import json, math, sys
from collections import Counter, defaultdict


def one_sided(x, y):
    n = x + y
    return round(sum(math.comb(n, i) for i in range(x, n + 1)) / 2 ** n, 6) if n else 1.0


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    org = lambda r: bool((r.get("origin") or {}).get("origin_event"))
    out = {"n": len(R) + len(voids), "voids": len(voids), "substrates": {}}
    match = []
    for s in sorted({r["cell"] for r in R}):
        uf = sum((Counter(r["UF"]) for r in R if r["lane"] == "D1_UF" and r["cell"] == s), Counter())
        ratio = uf["FUNC_LOSS"] / uf["FUNC_GAIN"] if uf["FUNC_GAIN"] else None
        pred = "INCREASE" if ratio is not None and ratio >= 1.25 else ("NO_INCREASE" if ratio is not None and ratio <= 0.8 else "NO_PREDICTION")
        pairs = defaultdict(dict)
        for r in R:
            if r["lane"] == "D1_U" and r["cell"] == s:
                pairs[r["pair"]][r["arm"]] = r
        ps = [v for v in pairs.values() if len(v) == 2]
        bo = sum(1 for v in ps if org(v["blocked"]) and not org(v["normal"])); no = sum(1 for v in ps if org(v["normal"]) and not org(v["blocked"]))
        p = one_sided(bo, no)
        observed = "INCREASE" if p < 0.05 else "NO_INCREASE"
        ok = None if pred == "NO_PREDICTION" else (pred == observed)
        match.append(ok)
        out["substrates"][s] = {"FUNC_LOSS": uf["FUNC_LOSS"], "FUNC_GAIN": uf["FUNC_GAIN"], "ratio": round(ratio, 3) if ratio else None,
                                "prediction": pred, "origins": {a: sum(org(v[a]) for v in ps) for a in ("normal", "blocked")},
                                "blocked_only": bo, "normal_only": no, "p_one_sided": p, "observed": observed, "match": ok}
    t = [m for m in match if m is not None]
    out["D1-P1"] = {"holds": (all(t) if t else "NOT_TESTABLE"), "testable": len(t), "matches": sum(1 for m in t if m)}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
