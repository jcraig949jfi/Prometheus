"""BEL-48H P1 analysis (rules: prereg s18).   python3 analyze_p1.py RESULTS OUT"""
import json, sys
from collections import defaultdict
from analyze_w5 import sign_one_sided
from analyze_w5b3 import e_share


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    by = defaultdict(lambda: defaultdict(dict))
    for r in R:
        by[r["cell"]][r["pair"]][r["arm"]] = r
    rows = {}
    for cell, seeds in sorted(by.items()):
        on, off = [], []
        for k, arms in seeds.items():
            for cp, acc in (("ON", on), ("OFF", off)):
                v = [e_share(arms[a])[0] for a in ("%s_ES" % cp, "%s_SE" % cp) if a in arms]
                v = [x for x in v if x is not None]
                if v:
                    acc.append(sum(v) / len(v))
        rows[cell] = {"ON_mean": round(sum(on) / len(on), 3) if on else None, "OFF_mean": round(sum(off) / len(off), 3) if off else None,
                      "n_on": len(on), "n_off": len(off)}
    dec = [v for v in rows.values() if v["ON_mean"] is not None and v["OFF_mean"] is not None]
    lt = sum(1 for v in dec if v["ON_mean"] < v["OFF_mean"]); gt = sum(1 for v in dec if v["ON_mean"] > v["OFF_mean"])
    out = {"n": len(R) + len(voids), "voids": len(voids), "pairings": rows, "decided": len(dec), "ON_lt_OFF": lt, "ON_gt_OFF": gt,
           "p_one_sided": sign_one_sided(lt, gt)}
    out["P1-P1"] = {"holds": out["p_one_sided"] < 0.05 and lt > gt}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
