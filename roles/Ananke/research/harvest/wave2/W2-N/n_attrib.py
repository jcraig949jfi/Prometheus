"""W2-N: per-row attribution of the 22 AUDIT3 disagreements (same estimator across namespaces vs estimator change).
For each W-U-DETERMINED row: REL2_WO = W-O's recorded W-N PCT certificate ('rel', namespace 0x600, real pairs at
run time); REL2_WZ = the same PCT rule on W-Z pairs (0x680); H2_WZ = W-Z's exact label (BOOTT); WU = W-U label.
  seed flip      : REL2_WZ != REL2_WO           (same estimator, different namespace)
  estimator only : REL2_WZ == REL2_WO but H2_WZ != WU  (BOOTT certifies what PCT did not, or W-U bound dropped)
Output out/attrib.json"""
import collections, csv, json
import numpy as np
import n_decomp as N

rows = list(csv.DictReader(open(N.WK / "W-Z" / "out" / "row_table.csv")))
wo = {r["vid"]: r for r in csv.DictReader(open(N.WK / "W-O" / "out" / "rerun_table.csv"))}
arms = N.load_arms()
out, tab = [], collections.Counter()
for r in rows:
    if r["WU_status"] != "DETERMINED":
        continue
    x = arms[(r["gid"], r["arm"])]
    a, s = x["a"][x["ok"]], x["s"][x["ok"]]
    rel2_wz = N.wn_rule(a, s)
    rel2_wo = wo[r["vid"]]["rel"]
    dis = r["new"] != r["WU_rel3"]
    cls = ("seed_flip" if rel2_wz != rel2_wo else "estimator_only") if dis else \
          ("agree_but_rel2_flipped" if rel2_wz != rel2_wo else "agree")
    tab[cls] += 1
    out.append({"vid": r["vid"], "gid": r["gid"], "arm": r["arm"], "REL2_WO": rel2_wo, "REL2_WZ": rel2_wz,
                "WU": r["WU_rel3"], "H2_WZ": r["new"], "class": cls})
print(dict(tab))
for o in out:
    if o["class"] in ("seed_flip", "estimator_only"):
        print(o)
# REL2-vs-REL2 between namespaces over all 301 det rows (same estimator): the clean seed-only flip rate
flip = sum(o["REL2_WZ"] != o["REL2_WO"] for o in out)
print("REL2 PCT label differs between namespaces:", flip, "/", len(out))
print("REL2 transitions:", collections.Counter((o["REL2_WO"], o["REL2_WZ"]) for o in out if o["REL2_WZ"] != o["REL2_WO"]))
json.dump({"counts": dict(tab), "rows": out}, open(N.OUT / "attrib.json", "w"), indent=1)
