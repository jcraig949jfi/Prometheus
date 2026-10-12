"""BEL-48H N1 analysis (rules: prereg s14; committed before the runs).   python3 analyze_n1.py RESULTS OUT"""
import json, random, sys
from collections import Counter, defaultdict
from analyze_w3 import classify


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    org = lambda r: bool((r.get("origin") or {}).get("origin_event"))
    plan_prec = {}
    per = defaultdict(lambda: {"VLOW": [], "HIGH": []})
    cls_of = {}
    for r in R:
        pid = r["pair"].split("|")[0]
        per[pid][r["arm"]].append(org(r)); cls_of[pid] = r["cell"]
    rate = lambda xs: sum(xs) / len(xs) if xs else 0.0
    out = {"n": len(R) + len(voids), "voids": len(voids), "classes": {}}
    diffs = {}
    for c in ("NEEDLE", "MOVE_RICH"):
        ps = [p for p in per if cls_of[p] == c]
        d = [rate(per[p]["HIGH"]) - rate(per[p]["VLOW"]) for p in ps]
        diffs[c] = d
        causes = {a: dict(Counter(classify(r["origin"]["origin_event"])["cause"] for r in R if r["cell"] == c and r["arm"] == a and org(r))) for a in ("VLOW", "HIGH")}
        out["classes"][c] = {"precursors": len(ps), "rate_VLOW": round(sum(rate(per[p]["VLOW"]) for p in ps) / max(1, len(ps)), 3),
                             "rate_HIGH": round(sum(rate(per[p]["HIGH"]) for p in ps) / max(1, len(ps)), 3),
                             "mean_diff_HIGH_minus_VLOW": round(sum(d) / max(1, len(d)), 3), "causes": causes}
    rng = random.Random(14)
    boots = []
    for _ in range(4000):
        a = [rng.choice(diffs["NEEDLE"]) for _ in diffs["NEEDLE"]]; b = [rng.choice(diffs["MOVE_RICH"]) for _ in diffs["MOVE_RICH"]]
        boots.append(sum(a) / len(a) - sum(b) / len(b))
    boots.sort()
    ci = [round(boots[99], 3), round(boots[3899], 3)]
    nd = out["classes"]["NEEDLE"]["mean_diff_HIGH_minus_VLOW"]; md = out["classes"]["MOVE_RICH"]["mean_diff_HIGH_minus_VLOW"]
    out["N-P1"] = {"needle_diff": nd, "holds": nd >= 0.2}
    out["N-P2"] = {"diff_of_diffs": round(nd - md, 3), "ci95": ci, "holds": ci[0] > 0}
    vl = out["classes"]["MOVE_RICH"]["causes"]["VLOW"]
    out["N-P3"] = {"move_rich_VLOW_causes": vl, "holds": sum(v for k, v in vl.items() if k in ("UPTAKE", "SELF_MOVE", "BORN_ASSEMBLY")) > vl.get("MUTATION", 0)}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
