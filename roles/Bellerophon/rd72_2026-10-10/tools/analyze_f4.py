"""BEL-RD-72 F4 analysis (prereg s13).   python3 analyze_f4.py F4_RESULTS F4_PLAN F1_RESULTS OUT.json
crossed / keep as analyze_f1.per_run (keep = FUNC BOTH at the tick-2,000 census).
F4-X1: KO1 crossed at LOW > the matched F1 KO1 at MED (0/20 there)   Fisher one-sided p < 0.05
F4-R:  W0 keep at LOW > MED on fresh seeds                           Fisher one-sided p < 0.05 (replicates F3-P1)
Reported: KO2_LOW and ECHOH_LOW crossed / FUNC end; first-crossing ticks."""
import json, sys
from analyze_f1 import per_run, fisher


def analyze(rows, plan, f1rows):
    PL = {p["id"]: p for p in plan}; F1 = {r["id"]: r for r in f1rows}
    cells = {}
    def add(key, r):
        x = per_run(r); c = cells.setdefault(key, {"n": 0, "crossed": 0, "keep": 0, "func_end": 0, "first": []})
        c["n"] += 1; c["crossed"] += x["crossed"]; c["keep"] += bool(x["both_end"] and x["func_end"]); c["func_end"] += x["func_end"]
        if x["crossed"]:
            c["first"].append(x["first_cross"])
    for r in rows:
        if r.get("void"):
            continue
        p = PL[r["id"]]; add(p["cell"], r)
        if p.get("f1_id") and p["cell"] == "KO1_LOW":
            add("KO1_MED_F1", F1[p["f1_id"]])
    g = lambda k, f: (cells.get(k, {}).get(f, 0), cells.get(k, {}).get("n", 0))
    out = {"cells": {k: dict(v, first=sorted(v["first"])) for k, v in sorted(cells.items())}}
    px = fisher(g("KO1_LOW", "crossed"), g("KO1_MED_F1", "crossed")); pr = fisher(g("W0R_LOW", "keep"), g("W0R_MED", "keep"))
    out["F4-X1"] = {"LOW": g("KO1_LOW", "crossed"), "MED": g("KO1_MED_F1", "crossed"), "p": px, "holds": bool(px < 0.05)}
    out["F4-R"] = {"LOW": g("W0R_LOW", "keep"), "MED": g("W0R_MED", "keep"), "p": pr, "holds": bool(pr < 0.05)}
    return out


if __name__ == "__main__":
    ld = lambda p: [json.loads(l) for l in open(p)]
    o = analyze(ld(sys.argv[1]), json.load(open(sys.argv[2])), ld(sys.argv[3])); json.dump(o, open(sys.argv[4], "w"), indent=1)
    print(json.dumps(o, indent=1))
