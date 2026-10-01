"""W2-AC: W-Z AUDIT3 group classes (Pb: 35/124 CARRIER-NAMED) at the specimen unit. numpy only."""
import collections, csv, json, pathlib
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
R = list(csv.DictReader(open(ROOT / "roles/Ananke/research/workers/W-Z/out/group_table.csv")))
rng = np.random.default_rng(0xAC3)
out = {"groups": len(R), "specimens": len({r["specimen"] for r in R})}
for lab in ("CARRIER-NAMED", "NO-CARRIER-FOUND", "CARRIER-PARTIAL"):
    by = collections.defaultdict(list)
    for r in R:
        by[r["specimen"]].append(int(r["class"] == lab))
    sp = list(by.values()); ks = np.array([sum(v) for v in sp], float); ns = np.array([len(v) for v in sp], float)
    idx = rng.integers(len(sp), size=(20000, len(sp)))
    ratio = ks[idx].sum(1) / ns[idx].sum(1)
    p = ks.sum() / ns.sum()
    out[lab] = {"k_groups": int(ks.sum()), "p_groups": round(p, 3),
                "cluster95": [round(float(np.quantile(ratio, .025)), 3), round(float(np.quantile(ratio, .975)), 3)],
                "deff_boot": round(float(ratio.var() / (p * (1 - p) / ns.sum())), 2),
                "specimens_with_any": int((ks > 0).sum()), "specimens_all": int((ks == ns).sum()),
                "by_priority": {pr: [sum(r["class"] == lab for r in R if r["priority"] == pr),
                                     sum(1 for r in R if r["priority"] == pr)] for pr in ("AMBIG", "REST")},
                "by_family": {f: [sum(r["class"] == lab for r in R if r["family"] == f),
                                  sum(1 for r in R if r["family"] == f),
                                  len({r["specimen"] for r in R if r["family"] == f and r["class"] == lab}),
                                  len({r["specimen"] for r in R if r["family"] == f})] for f in ("RELAY", "HOLD", "MAJ")}}
json.dump(out, open(HERE / "out/wz_units.json", "w"), indent=1)
print(json.dumps(out, indent=1))
