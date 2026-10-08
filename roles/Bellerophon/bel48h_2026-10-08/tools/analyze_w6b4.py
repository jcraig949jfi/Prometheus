"""BEL-48H W6 block 4 analysis (rules: prereg s13; committed before the runs).
    python3 analyze_w6b4.py U_RESULTS R_RESULTS X_RESULTS OUT"""
import json, sys
from collections import Counter, defaultdict
from analyze_w1 import mcnemar_exact
from analyze_w2 import wilson
from analyze_w3 import classify
import analyze_w5b3


def load(p):
    R = [json.loads(l) for l in open(p)]
    return [r for r in R if not r.get("void")], sum(1 for r in R if r.get("void"))


def main(up, rp, xp, outp):
    out = {}
    U, uv = load(up)
    org = lambda r: bool((r.get("origin") or {}).get("origin_event"))
    pairs = defaultdict(dict)
    for r in U:
        pairs[(r["cell"], r["pair"])][r["arm"]] = r
    ps = [v for v in pairs.values() if len(v) == 2]
    cnt = {a: sum(org(v[a]) for v in ps) for a in ("normal", "blocked")}
    no = sum(1 for v in ps if org(v["normal"]) and not org(v["blocked"])); bo = sum(1 for v in ps if org(v["blocked"]) and not org(v["normal"]))
    causes = {a: Counter(classify(v[a]["origin"]["origin_event"])["cause"] for v in ps if org(v[a])) for a in ("normal", "blocked")}
    acted = sum(1 for v in ps if (v["blocked"]["origin"]["O"] or {}).get("blocked_bytes", 0) > 0)
    out["U"] = {"pairs": len(ps), "voids": uv, "origins": cnt, "wilson": {a: wilson(cnt[a], len(ps)) for a in cnt},
                "mcnemar": {"normal_only": no, "blocked_only": bo, "p": mcnemar_exact(no, bo)},
                "causes": {a: dict(c) for a, c in causes.items()}, "ablation_acted_runs": acted,
                "per_cell": {c: {a: sum(org(v[a]) for (cc, k), v in pairs.items() if cc == c and len(v) == 2) for a in ("normal", "blocked")}
                             for c in sorted({k[0] for k in pairs})}}
    out["U-P1"] = {"uptake_origins_blocked": causes["blocked"].get("UPTAKE", 0), "uptake_origins_normal": causes["normal"].get("UPTAKE", 0),
                   "holds": causes["blocked"].get("UPTAKE", 0) == 0 and causes["normal"].get("UPTAKE", 0) >= 5}
    out["U-P2"] = {"ratio_blocked_over_normal": round(cnt["blocked"] / cnt["normal"], 3) if cnt["normal"] else None,
                   "holds": bool(cnt["normal"]) and cnt["blocked"] >= 0.7 * cnt["normal"]}
    mn = causes["normal"]; mb = causes["blocked"]
    out["U-P3"] = {"mutation_share": {"normal": round(mn.get("MUTATION", 0) / max(1, sum(mn.values())), 3), "blocked": round(mb.get("MUTATION", 0) / max(1, sum(mb.values())), 3)}}
    Rr, rv = load(rp)
    ok = sum(1 for r in Rr if r.get("replay_identical")); chk = sum(1 for r in Rr if "replay_identical" in r)
    out["R"] = {"replayed": len(Rr), "voids": rv, "checked": chk, "identical": ok, "by_window": dict(Counter(r["cell"] for r in Rr if r.get("replay_identical"))),
                "mismatch_ids": [r["id"] for r in Rr if "replay_identical" in r and not r["replay_identical"]][:30]}
    out["R-P1"] = {"holds": chk == len(Rr) and ok == chk and rv == 0}
    analyze_w5b3.main(xp, outp + ".x.json")
    X = json.load(open(outp + ".x.json"))
    med = X["levels"].get("MED", {})
    out["X"] = X
    out["X-P6"] = {"holds": X["W5-P6"]["holds"], **{k: X["W5-P6"][k] for k in ("ON_E_majority", "ON_S_majority", "p")}}
    from analyze_w5 import sign_one_sided
    out["X-P7"] = {"MED_ON_lt_OFF": med.get("ON_lt_OFF"), "MED_ON_gt_OFF": med.get("ON_gt_OFF"),
                   "p": sign_one_sided(med.get("ON_lt_OFF", 0), med.get("ON_gt_OFF", 0)),
                   "holds": sign_one_sided(med.get("ON_lt_OFF", 0), med.get("ON_gt_OFF", 0)) < 0.05}
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "X"}, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:5])
