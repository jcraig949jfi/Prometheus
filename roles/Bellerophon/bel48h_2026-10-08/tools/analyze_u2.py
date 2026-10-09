"""BEL-48H U2 analysis (rules: prereg s16).   python3 analyze_u2.py RESULTS OUT"""
import json, math, sys
from collections import Counter, defaultdict


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    org = lambda r: bool((r.get("origin") or {}).get("origin_event"))
    pairs = defaultdict(dict)
    for r in R:
        pairs[(r["cell"], r["pair"])][r["arm"]] = r
    ps = [v for v in pairs.values() if len(v) == 2]
    bo = sum(1 for v in ps if org(v["blocked"]) and not org(v["normal"])); no = sum(1 for v in ps if org(v["normal"]) and not org(v["blocked"]))
    n = bo + no
    p = sum(math.comb(n, i) for i in range(bo, n + 1)) / 2 ** n if n else 1.0
    out = {"n": len(R) + len(voids), "voids": len(voids), "pairs": len(ps),
           "origins": {a: sum(org(v[a]) for v in ps) for a in ("normal", "blocked")},
           "blocked_only": bo, "normal_only": no, "p_one_sided": round(p, 6),
           "extinct": {a: sum(v[a]["summary"]["extinct"] for v in ps) for a in ("normal", "blocked")},
           "uptake_origins": {a: sum(1 for v in ps if org(v[a]) and v[a]["origin"]["origin_event"]["kind"] == "UPTAKE") for a in ("normal", "blocked")}}
    out["U2-P1"] = {"holds": p < 0.05 and bo > no}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
