"""BEL-RD-72 F1 analysis (prereg s10).   python3 analyze_f1.py F1_RESULTS F1_PLAN OUT.json
Per world: crossed = a census tick in (0, 2000] with a FUNC BOTH tape (for W0: BOTH FUNC kept at the last census instead);
first_cross = that tick; func_end = FUNC alive at the last census; established = FUNC at the tick-500 census.
F1-P0  control validity: W0-ON worlds with FUNC at the end keep a FUNC BOTH at the end in >= 50% (reported with n)
F1-P1  KO1-ON crossed > REP-ON crossed (Fisher one-sided p < 0.05)
F1-P2  KO1-ON crossed > KO1-OFF crossed (Fisher one-sided p < 0.05)
Reported per cell: crossed, func_end, established, median first_cross; KO1 by founder halves class (LO / HI / NONE)."""
import json, sys
from scipy.stats import fisher_exact


def per_run(r):
    cen = r["census"]
    bf = lambda c: (c.get("halves_func") or {}).get("BOTH", 0) > 0
    fn = lambda c: sum((c.get("halves_func") or {}).values()) > 0
    last = cen[-1] if cen else None
    first = next((c["tick"] for c in cen if bf(c)), None)
    c500 = next((c for c in cen if c["tick"] == 500), None)
    return {"crossed": first is not None, "first_cross": first, "both_end": bool(last and bf(last) and last["tick"] == 2000),
            "func_end": bool(last and fn(last) and last["tick"] == 2000), "established": bool(c500 and fn(c500))}


def fisher(a, b):
    return round(fisher_exact([[a[0], a[1] - a[0]], [b[0], b[1] - b[0]]], alternative="greater")[1], 6)


def analyze(rows, plan):
    PL = {p["id"]: p for p in plan}
    cells = {}
    for r in rows:
        if r.get("void"):
            continue
        p = PL[r["id"]]; x = per_run(r)
        c = cells.setdefault(p["cell"] + "|" + p["arm"], {"n": 0, "crossed": 0, "func_end": 0, "established": 0, "both_end": 0,
                                                          "first": [], "by_founder": {}})
        c["n"] += 1; c["crossed"] += x["crossed"]; c["func_end"] += x["func_end"]; c["established"] += x["established"]
        c["both_end"] += x["both_end"] and x["func_end"]
        if x["crossed"]:
            c["first"].append(x["first_cross"])
        b = c["by_founder"].setdefault(p.get("founder_halves"), [0, 0]); b[0] += x["crossed"]; b[1] += 1
    med = lambda v: sorted(v)[len(v) // 2] if v else None
    out = {"cells": {k: dict({kk: vv for kk, vv in c.items() if kk != "first"}, median_first_cross=med(c["first"]))
                     for k, c in sorted(cells.items())}}
    g = lambda k, f: (cells.get(k, {}).get(f, 0), cells.get(k, {}).get("n", 0))
    w = cells.get("W0|ON", {"func_end": 0, "both_end": 0})
    out["F1-P0"] = {"func_end": w["func_end"], "both_end": w["both_end"],
                    "holds": (w["both_end"] >= 0.5 * w["func_end"]) if w["func_end"] else "NOT_TESTABLE"}
    out["F1-P1"] = {"KO1_ON": g("KO1|ON", "crossed"), "REP_ON": g("REP|ON", "crossed"), "p": fisher(g("KO1|ON", "crossed"), g("REP|ON", "crossed"))}
    out["F1-P1"]["holds"] = out["F1-P1"]["p"] < 0.05
    out["F1-P2"] = {"KO1_ON": g("KO1|ON", "crossed"), "KO1_OFF": g("KO1|OFF", "crossed"), "p": fisher(g("KO1|ON", "crossed"), g("KO1|OFF", "crossed"))}
    out["F1-P2"]["holds"] = out["F1-P2"]["p"] < 0.05
    return out


if __name__ == "__main__":
    rows = [json.loads(l) for l in open(sys.argv[1])]; plan = json.load(open(sys.argv[2]))
    o = analyze(rows, plan); json.dump(o, open(sys.argv[3], "w"), indent=1); print(json.dumps(o, indent=1))
