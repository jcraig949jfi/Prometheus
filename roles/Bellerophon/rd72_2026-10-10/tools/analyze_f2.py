"""BEL-RD-72 F2 analysis (prereg s11).   python3 analyze_f2.py F2_RESULTS F2_PLAN F1_RESULTS OUT.json
Per run (analyze_f1.per_run): crossed, both_end (a FUNC BOTH at the tick-2,000 census), func_end, established.
Comparator: the matched F1 world (same seed / founder, kernel payment).
F2-P0 (maintenance): W0 both_end, PAIRED > F1 ON (Fisher one-sided over the 20 + 20 worlds, p < 0.05)
F2-P1 (crossing from distance 1): KO1 crossed, PAIRED > F1 ON (Fisher one-sided, p < 0.05)
Reported: per cell crossed / both_end / func_end / established for both rules, matched-pair discordance, the second-check
denial fraction pp_denied / pp_correct."""
import json, sys
from analyze_f1 import per_run, fisher


def analyze(f2rows, f2plan, f1rows):
    PL = {p["id"]: p for p in f2plan}; F1 = {r["id"]: r for r in f1rows}
    cells = {}
    for r in f2rows:
        if r.get("void"):
            continue
        p = PL[r["id"]]; a = per_run(r); b = per_run(F1[p["f1_id"]])
        c = cells.setdefault(p["cell"], {"n": 0, "PAIRED": {"crossed": 0, "both_end": 0, "func_end": 0, "established": 0},
                                         "KERNEL": {"crossed": 0, "both_end": 0, "func_end": 0, "established": 0},
                                         "pp_correct": 0, "pp_denied": 0, "discord_both_end": [0, 0]})
        c["n"] += 1
        for k in ("crossed", "func_end", "established"):
            c["PAIRED"][k] += a[k]; c["KERNEL"][k] += b[k]
        ab, bb = a["both_end"] and a["func_end"], b["both_end"] and b["func_end"]
        c["PAIRED"]["both_end"] += ab; c["KERNEL"]["both_end"] += bb
        c["discord_both_end"][0] += ab and not bb; c["discord_both_end"][1] += bb and not ab
        c["pp_correct"] += (r.get("pp") or {}).get("pp_correct", 0); c["pp_denied"] += (r.get("pp") or {}).get("pp_denied", 0)
    out = {"cells": cells}
    g = lambda cell, rule, k: (cells.get(cell, {}).get(rule, {}).get(k, 0), cells.get(cell, {}).get("n", 0))
    p0 = fisher(g("W0", "PAIRED", "both_end"), g("W0", "KERNEL", "both_end"))
    p1 = fisher(g("KO1", "PAIRED", "crossed"), g("KO1", "KERNEL", "crossed"))
    out["F2-P0"] = {"paired": g("W0", "PAIRED", "both_end"), "kernel": g("W0", "KERNEL", "both_end"), "p": p0, "holds": bool(p0 < 0.05)}
    out["F2-P1"] = {"paired": g("KO1", "PAIRED", "crossed"), "kernel": g("KO1", "KERNEL", "crossed"), "p": p1, "holds": bool(p1 < 0.05)}
    return out


if __name__ == "__main__":
    ld = lambda p: [json.loads(l) for l in open(p)]
    o = analyze(ld(sys.argv[1]), json.load(open(sys.argv[2])), ld(sys.argv[3])); json.dump(o, open(sys.argv[4], "w"), indent=1)
    print(json.dumps(o, indent=1))
