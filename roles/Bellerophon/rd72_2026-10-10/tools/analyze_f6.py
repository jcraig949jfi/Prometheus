"""BEL-RD-72 F6 analysis (prereg s15).   python3 analyze_f6.py F6_RESULTS F6_PLAN OUT.json
keep = a FUNC BOTH at the tick-2,000 census (analyze_f1.per_run both_end AND func_end).
F6-P1: CM keep VLOW > MED   (Fisher one-sided p < 0.05)
F6-P2: WM keep VLOW > MED   (same)
Each test is NOT_TESTABLE if the two arms together have < 10 worlds with FUNC at the end (extinction, not maintenance)."""
import json, sys
from analyze_f1 import per_run, fisher


def analyze(rows, plan):
    PL = {p["id"]: p for p in plan}; cells = {}
    for r in rows:
        if r.get("void"):
            continue
        x = per_run(r); c = cells.setdefault(PL[r["id"]]["cell"], {"n": 0, "keep": 0, "func_end": 0, "established": 0})
        c["n"] += 1; c["keep"] += bool(x["both_end"] and x["func_end"]); c["func_end"] += x["func_end"]; c["established"] += x["established"]
    out = {"cells": cells}
    for name, a, b in (("F6-P1", "CM_VLOW", "CM_MED"), ("F6-P2", "WM_VLOW", "WM_MED")):
        A = (cells.get(a, {}).get("keep", 0), cells.get(a, {}).get("n", 0)); B = (cells.get(b, {}).get("keep", 0), cells.get(b, {}).get("n", 0))
        fe = cells.get(a, {}).get("func_end", 0) + cells.get(b, {}).get("func_end", 0)
        p = fisher(A, B)
        out[name] = {"VLOW": A, "MED": B, "p": p, "func_end_both_arms": fe, "holds": bool(p < 0.05) if fe >= 10 else "NOT_TESTABLE"}
    return out


if __name__ == "__main__":
    o = analyze([json.loads(l) for l in open(sys.argv[1])], json.load(open(sys.argv[2])))
    json.dump(o, open(sys.argv[3], "w"), indent=1); print(json.dumps(o, indent=1))
