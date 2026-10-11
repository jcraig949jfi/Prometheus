"""BEL-48H U3 + P2 analysis (rules: prereg s20).   python3 analyze_u3p2.py U3_RESULTS P2_RESULTS OUT"""
import json, math, sys
from collections import Counter, defaultdict
import analyze_p1


def one_sided(x, y):
    n = x + y
    return round(sum(math.comb(n, i) for i in range(x, n + 1)) / 2 ** n, 6) if n else 1.0


def shape(e):
    t = bytes.fromhex(e["new"])
    return "0xA0" if any(t[p] == 0xA0 for p in e["critical"]) else "other"


def main(up, pp, outp):
    R = [json.loads(l) for l in open(up)]
    uv = sum(1 for r in R if r.get("void")); R = [r for r in R if not r.get("void")]
    org = lambda r: (r.get("origin") or {}).get("origin_event")
    tri = defaultdict(dict)
    for r in R:
        tri[(r["cell"], r["pair"])][r["arm"]] = r
    ts = [v for v in tri.values() if len(v) == 3]
    out = {"U3": {"triples": len(ts), "voids": uv, "origins": {a: sum(bool(org(v[a])) for v in ts) for a in ("normal", "block_all", "block_selfcopy")},
                  "shape_0xA0": {a: sum(1 for v in ts if org(v[a]) and shape(org(v[a])) == "0xA0") for a in ("normal", "block_all", "block_selfcopy")}}}
    for arm in ("block_all", "block_selfcopy"):
        x = sum(1 for v in ts if org(v[arm]) and not org(v["normal"])); y = sum(1 for v in ts if org(v["normal"]) and not org(v[arm]))
        out["U3"][arm + "_vs_normal"] = {"arm_only": x, "normal_only": y, "p_one_sided": one_sided(x, y)}
    sa = out["U3"]["shape_0xA0"]
    out["U3-P1"] = {"holds": out["U3"]["block_all_vs_normal"]["p_one_sided"] < 0.05}
    out["U3-P2"] = {"holds": out["U3"]["block_selfcopy_vs_normal"]["p_one_sided"] < 0.05}
    ga = sa["block_all"] - sa["normal"]; gs = sa["block_selfcopy"] - sa["normal"]
    out["U3-P3"] = {"gain_0xA0_all": ga, "gain_0xA0_selfcopy": gs, "holds": ga > 0 and gs >= 0.5 * ga}
    analyze_p1.main(pp, outp + ".p2.json")
    P2 = json.load(open(outp + ".p2.json"))
    lt, gt = P2["ON_lt_OFF"], P2["ON_gt_OFF"]
    n = lt + gt
    p2 = round(min(1.0, 2 * sum(math.comb(n, i) for i in range(0, min(lt, gt) + 1)) / 2 ** n), 6) if n else 1.0
    out["P2"] = {"decided": P2["decided"], "ON_lt_OFF": lt, "ON_gt_OFF": gt, "p_two_sided": p2, "pairings": P2["pairings"]}
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "P2"}, indent=1, default=str)); print({k: out["P2"][k] for k in ("decided", "ON_lt_OFF", "ON_gt_OFF", "p_two_sided")})


if __name__ == "__main__":
    main(*sys.argv[1:4])
