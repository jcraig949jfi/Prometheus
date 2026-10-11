"""BEL-RD-72 F5 analysis (prereg s14).   python3 analyze_f5.py F5_RESULTS F5_PLAN OUT.json
keep3000 = a FUNC BOTH at the tick-3,000 census; crossed = a FUNC BOTH at any census.
F5-P1: KO1 keep3000, PHASED > MED (Fisher one-sided p < 0.05)
Reported: crossings per cell (and whether the first crossing came before or after the switch at 1,000), ECHOH cells,
FUNC at end."""
import json, sys
from analyze_f1 import fisher


def analyze(rows, plan):
    PL = {p["id"]: p for p in plan}; cells = {}
    for r in rows:
        if r.get("void"):
            continue
        p = PL[r["id"]]; cen = r["census"]
        bf = lambda c: (c.get("halves_func") or {}).get("BOTH", 0) > 0
        last = cen[-1] if cen else {"tick": 0}
        first = next((c["tick"] for c in cen if bf(c)), None)
        c = cells.setdefault(p["cell"], {"n": 0, "crossed": 0, "keep3000": 0, "func_end": 0, "first_before_switch": 0, "first": []})
        c["n"] += 1; c["crossed"] += first is not None
        c["keep3000"] += bool(last["tick"] == 3000 and bf(last))
        c["func_end"] += bool(last["tick"] == 3000 and sum((last.get("halves_func") or {}).values()) > 0)
        if first is not None:
            c["first"].append(first); c["first_before_switch"] += first < 1000
    g = lambda k: (cells.get(k, {}).get("keep3000", 0), cells.get(k, {}).get("n", 0))
    p1 = fisher(g("KO1_PHASED"), g("KO1_MED"))
    return {"cells": {k: dict(v, first=sorted(v["first"])) for k, v in sorted(cells.items())},
            "F5-P1": {"PHASED": g("KO1_PHASED"), "MED": g("KO1_MED"), "p": p1, "holds": bool(p1 < 0.05)}}


if __name__ == "__main__":
    o = analyze([json.loads(l) for l in open(sys.argv[1])], json.load(open(sys.argv[2])))
    json.dump(o, open(sys.argv[3], "w"), indent=1); print(json.dumps(o, indent=1))
