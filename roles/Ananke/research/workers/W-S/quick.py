"""Quick cross-tab of pattern x predictors per (offset, phase). python quick.py <rows json>"""
import json, sys
from collections import Counter
d = json.load(open(sys.argv[1]))
rows = d["rows"]
print(d["spec"], "normal", round(d["normal_acc"], 3), "KA_L", d["KA_L"])
keys = sys.argv[2].split(",") if len(sys.argv) > 2 else ["P1_first", "P2_dflight", "P3_cone", "P5_dleaf"]
for o in d["offsets"]:
    for q in (0, 1):
        rr = [r for r in rows if r["o"] == o and r["q"] == q]
        if not rr:
            continue
        print(f"o{o} q{q} n{len(rr)} pat", dict(Counter(r["pat"] for r in rr)),
              "tgt", dict(Counter(r.get("pat_tgt") for r in rr)))
        for k in keys:
            print("   ", k, dict(sorted(Counter((r["pat"], r[k]) for r in rr).items())))
