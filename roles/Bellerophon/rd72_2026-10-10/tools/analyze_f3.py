"""BEL-RD-72 F3 analysis (prereg s12).   python3 analyze_f3.py F3_RESULTS F3_PLAN F1_RESULTS OUT.json
keep = a FUNC BOTH at the tick-2,000 census (analyze_f1.per_run both_end AND func_end). MED = the matched F1 W0 worlds.
F3-P0: keep at VLOW-ON > MED-ON (F1)  (Fisher one-sided p < 0.05)
F3-P1: keep at LOW-ON  > MED-ON       (same test; the dose step)
Reported: keep at VLOW-OFF vs VLOW-ON (does maintenance at low mutation still need payment?), last census with a FUNC BOTH."""
import json, sys
from analyze_f1 import per_run, fisher


def analyze(f3rows, f3plan, f1rows):
    PL = {p["id"]: p for p in f3plan}; F1 = {r["id"]: r for r in f1rows}
    cells = {}
    def add(key, r):
        x = per_run(r); c = cells.setdefault(key, {"n": 0, "keep": 0, "func_end": 0, "last_both": []})
        c["n"] += 1; c["keep"] += bool(x["both_end"] and x["func_end"]); c["func_end"] += x["func_end"]
        b = [k["tick"] for k in r["census"] if (k.get("halves_func") or {}).get("BOTH")]
        c["last_both"].append(max(b) if b else 0)
    med_ids = set()
    for r in f3rows:
        if r.get("void"):
            continue
        p = PL[r["id"]]; add(p["cell"] + "|" + p["arm"], r)
        if p["arm"] == "ON":
            med_ids.add(p["f1_id"])
    for i in sorted(med_ids):
        add("W0_MED|ON", F1[i])
    g = lambda k: (cells.get(k, {}).get("keep", 0), cells.get(k, {}).get("n", 0))
    out = {"cells": {k: dict(v, last_both=sorted(v["last_both"])) for k, v in sorted(cells.items())}}
    p0 = fisher(g("W0_VLOW|ON"), g("W0_MED|ON")); p1 = fisher(g("W0_LOW|ON"), g("W0_MED|ON"))
    out["F3-P0"] = {"VLOW": g("W0_VLOW|ON"), "MED": g("W0_MED|ON"), "p": p0, "holds": bool(p0 < 0.05)}
    out["F3-P1"] = {"LOW": g("W0_LOW|ON"), "MED": g("W0_MED|ON"), "p": p1, "holds": bool(p1 < 0.05)}
    out["VLOW_OFF_vs_ON"] = {"OFF": g("W0_VLOW|OFF"), "ON": g("W0_VLOW|ON")}
    return out


if __name__ == "__main__":
    ld = lambda p: [json.loads(l) for l in open(p)]
    o = analyze(ld(sys.argv[1]), json.load(open(sys.argv[2])), ld(sys.argv[3])); json.dump(o, open(sys.argv[4], "w"), indent=1)
    print(json.dumps(o, indent=1))
