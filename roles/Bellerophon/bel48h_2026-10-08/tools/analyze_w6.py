"""BEL-48H W6 block 1 analysis (rules: prereg s9; committed before the runs).   python3 analyze_w6.py RESULTS OUT"""
import json, sys
from collections import Counter
from analyze_w2 import wilson
from analyze_w3 import classify


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    out = {"n": len(R) + len(voids), "voids": len(voids)}
    C1 = [r for r in R if r["lane"] == "C1"]
    rows = []
    for r in C1:
        e = (r.get("origin") or {}).get("origin_event")
        if e:
            c = classify(e); c.update(cell=r["cell"], id=r["id"], ldir=(r.get("reach") or {}).get("ldir_critical")); rows.append(c)
    n = len(rows)
    out["C1"] = {"runs": len(C1), "origins": n, "per_cell": dict(Counter(x["cell"] for x in rows)),
                 "cause": dict(Counter(x["cause"] for x in rows)), "pathway": dict(Counter(x["pathway"] for x in rows)),
                 "steps": dict(Counter(x["steps"] for x in rows)), "precursor0": sum(1 for x in rows if x["precursor"] == 0),
                 "assisted": sum(1 for x in rows if x["assisted"]), "rows": rows}
    mut = sum(1 for x in rows if x["cause"] == "MUTATION")
    inplace = [x for x in rows if x["steps"] is not None]
    one = sum(1 for x in inplace if x["steps"] == 1)
    p0 = out["C1"]["precursor0"]; asd = out["C1"]["assisted"]
    upt = [x for x in rows if x["cause"] == "UPTAKE" and (x["steps"] or 0) >= 1]
    ld = sum(1 for x in rows if x["ldir"])
    out["C1-P1"] = {"mutation": [mut, n], "wilson": wilson(mut, n), "holds": n > 0 and mut / n >= 0.5}
    out["C1-P2"] = {"one_step": [one, len(inplace)], "wilson": wilson(one, len(inplace)), "holds": bool(inplace) and one / len(inplace) >= 0.5}
    out["C1-P3"] = {"precursor_zero": [p0, n], "wilson": wilson(p0, n), "holds": n > 0 and p0 / n >= 0.6}
    out["C1-P4"] = {"uptake_reversion_confirmed": len(upt), "uptake_any": sum(1 for x in rows if x["cause"] == "UPTAKE"), "holds": len(upt) >= 1}
    out["C1-P5"] = {"assisted": [asd, n], "wilson": wilson(asd, n), "holds": n > 0 and asd / n >= 0.5}
    out["C1-P6"] = {"ldir": [ld, n], "holds": n > 0 and ld / n >= 0.95}
    C2 = [r for r in R if r["lane"] == "C2"]
    def first_alive(r):
        d = r["heredity"]["event_alive_descendants"]
        return d.get("0", 0) > 0
    fa = sum(1 for r in C2 if r["heredity"]["func_alive"] > 0)
    fl = sum(1 for r in C2 if r["heredity"]["n_events"] > 0 and first_alive(r))
    ev = sum(1 for r in C2 if r["heredity"]["n_events"] > 0)
    nolin = sum(1 for r in C2 if r["heredity"]["func_alive"] > 0 and not any(v > 0 for v in r["heredity"]["event_alive_descendants"].values()))
    out["C2"] = {"runs": len(C2), "func_alive_end": fa, "first_event_lineage_alive": [fl, ev], "func_without_any_event_lineage": nolin}
    out["C2-P1"] = {"holds": len(C2) > 0 and fa / len(C2) >= 0.95 and ev > 0 and fl / ev < 0.5 and nolin / len(C2) >= 0.2}
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "C1" or True}, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main(*sys.argv[1:3])
