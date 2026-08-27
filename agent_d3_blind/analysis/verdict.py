"""Mechanical Phase 1 verdict: gates are read from prereg/gates.json and applied
to the ledgers without any post-hoc adjustment."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from classifiers import families                    # noqa: E402

G = json.load(open(os.path.join(ROOT, "prereg", "gates.json")))
C = G["constants"]
BASES = G["bases"]


def spearman(a, b):
    keys = sorted(set(a) | set(b))
    if len(keys) < 3:
        return 1.0
    xa = [a.get(k, 0) for k in keys]
    xb = [b.get(k, 0) for k in keys]

    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = ranks(xa), ranks(xb)
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    da = sum((ra[i] - ma) ** 2 for i in range(n)) ** 0.5
    db = sum((rb[i] - mb) ** 2 for i in range(n)) ** 0.5
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def order_metrics(o):
    ag = o["agg"]
    m = {}
    r1 = ag["1"]
    m["p_valid_r1"] = r1["valid"] / max(1, r1["n"])
    r3 = ag["3"]
    m["p_valid_r3"] = r3["valid"] / max(1, r3["n"])
    m["p_semdiff_given_valid_r1"] = r1["semdiff"] / max(1, r1["valid"])
    tot_valid = sum(v["valid"] for v in ag.values())
    tot_lc = sum(v["live_consumer"] for v in ag.values())
    m["frac_valid_with_live_consumer"] = tot_lc / max(1, tot_valid)
    shares, mx, n5 = families.charged_shares(o["fam_semdiff"])
    m["max_family_share_charged"] = mx
    m["n_families_ge_5pct"] = n5
    m["_shares"] = shares
    return m


def cond_ok(val, op, thr):
    if val is None:
        return False
    return val >= thr if op == ">=" else val <= thr


def eval_gate(gid, metrics):
    g = G["gates"][gid]
    conds = []
    for c in g["conds"]:
        v = metrics.get(c["key"])
        ok = cond_ok(v, c["op"], c["thr"])
        thr = c["thr"]
        lo, hi = thr * (1 - 0.20), thr * (1 + 0.20)
        ok_lo = cond_ok(v, c["op"], lo)
        ok_hi = cond_ok(v, c["op"], hi)
        margin = None if v is None else (v - thr if c["op"] == ">=" else thr - v)
        conds.append({"key": c["key"], "value": v, "op": c["op"], "thr": thr,
                      "pass": ok, "margin": margin,
                      "pass_at_-20%": ok_lo, "pass_at_+20%": ok_hi,
                      "knife_edge": ok and not (ok_lo and ok_hi)})
    return {"gate": gid, "name": g["name"],
            "pass": all(c["pass"] for c in conds),
            "knife_edge": any(c["knife_edge"] for c in conds),
            "conds": conds}


def basis_report(b):
    p = os.path.join(ROOT, "ledgers", "basis_%s.json" % b)
    if not os.path.exists(p):
        return None
    L = json.load(open(p))
    o0 = L["orders"]["0"]
    d0 = L["order0"]
    m = order_metrics(o0)
    om = {k: order_metrics(L["orders"][k]) for k in L["orders"]}
    m["n_semantic_classes"] = d0["n_semantic_classes_total"]
    m["giant_component_frac"] = d0["giant_component_frac"]
    # order robustness
    sub_gates = ["G1", "G2", "G4", "G6"]
    verds = {k: {g: eval_gate(g, om[k])["pass"] for g in sub_gates} for k in om}
    agree = 1.0 if len({tuple(sorted(v.items())) for v in verds.values()}) == 1 else 0.0
    sp = []
    ks = sorted(om)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            sp.append(spearman(L["orders"][ks[i]]["fam_semdiff"],
                               L["orders"][ks[j]]["fam_semdiff"]))
    m["order_gate_agreement"] = agree
    m["min_family_spearman"] = min(sp) if sp else 1.0
    # M0
    m0 = d0["m0"]
    covs = {v: m0[v]["coverage"] for v in m0}
    best = max(covs, key=lambda v: covs[v])
    m["best_m0_target_coverage"] = covs[best]
    m["best_m0_far_coverage"] = m0[best]["far_coverage"]
    m["n_m0_within_half_of_best"] = sum(1 for v in covs
                                        if covs[v] >= 0.5 * covs[best] and covs[v] > 0)
    ac = os.path.join(ROOT, "results", "anti_cheat.json")
    static_pass = 1.0
    if os.path.exists(ac):
        A = json.load(open(ac))
        static_pass = 1.0 if all(r["pass"] for r in A["static"]) else 0.0
    m["static_no_label_test_pass"] = static_pass
    m["n_witnesses_constructed"] = sum(1 for w in d0["witnesses"] if w["constructed"])
    reached = set()
    for v in m0:
        reached |= set(m0[v]["witnesses_reached"])
    m["n_witness_classes_reached_by_m0"] = len(reached)
    gates = {g: eval_gate(g, m) for g in G["gates"]}
    return {"basis": b, "metrics": {k: v for k, v in m.items() if not k.startswith("_")},
            "family_shares": m["_shares"], "gates": gates,
            "order_verdicts": verds, "order_spearman": sp,
            "best_m0": best, "m0_coverage": covs,
            "witness_reached": sorted(reached),
            "probe_stability": d0["probe_stability"],
            "witnesses": d0["witnesses"],
            "target_pool_sizes": d0["target_pool_sizes"],
            "extra": {"n_classes_chain": d0["n_classes_chain"],
                      "graph_nodes": d0["graph_nodes"],
                      "graph_edges": d0["graph_edges"],
                      "fresh_pool_classes": d0["fresh_pool_classes"],
                      "n_distinct_out_artifacts": o0["n_distinct_out_artifacts"],
                      "n_structs_radius": o0["n_structs_radius"],
                      "n_seeds": o0["n_seeds"],
                      "agg": o0["agg"], "opfam": o0["opfam"],
                      "fam_all": o0["fam_all"],
                      "secs": L["secs"], "meter": L["total_meter_runs"]}}


def overall(reports):
    live = [r for r in reports if r]
    if not live:
        return "SUBSTRATE_INVALID", "no basis produced a ledger"
    ac = os.path.join(ROOT, "results", "anti_cheat.json")
    if not os.path.exists(ac) or not json.load(open(ac))["all_pass"]:
        return "SUBSTRATE_INVALID", "anti-cheat battery did not pass"

    def gp(r, g):
        return r["gates"][g]["pass"]
    if any(all(gp(r, g) for g in G["gates"]) for r in live):
        return "WORLD_PHASE_READY", "at least one basis passed G1-G10"
    if all(not (gp(r, "G1") and gp(r, "G2")) for r in live):
        return "VIABILITY_COLLAPSE", "no basis satisfied both G1 and G2"
    if all(not (gp(r, "G3") and gp(r, "G4") and gp(r, "G5")) for r in live):
        return "PHENOTYPE_POVERTY", "no basis satisfied G3, G4 and G5"
    if all(not (gp(r, "G6") and gp(r, "G7")) for r in live):
        return "TAXONOMY_BIASED", "no basis satisfied G6 and G7"
    survivors = [r for r in live if all(gp(r, g) for g in ("G1", "G2", "G3", "G4",
                                                           "G5", "G6", "G7"))]
    if survivors and all(not gp(r, "G9") for r in survivors):
        return "M0_UNFAIR", "substrate preconditions passed but M0 fairness failed"
    if survivors and all(not (gp(r, "G8") and gp(r, "G10")) for r in survivors):
        return "M0_COVERAGE_INSUFFICIENT", "substrate passed but M0 coverage/witness access failed"
    return "PHENOTYPE_POVERTY", "no basis passed the full precondition set"


def main():
    reports = [basis_report(b) for b in BASES]
    verdict, why = overall(reports)
    out = {"prereg_version": G["prereg_version"], "verdict": verdict, "reason": why,
           "bases": {r["basis"]: {"gates": {g: r["gates"][g]["pass"] for g in r["gates"]},
                                  "knife_edge": [g for g in r["gates"]
                                                 if r["gates"][g]["knife_edge"]],
                                  "metrics": r["metrics"]}
                     for r in reports if r}}
    RES = os.path.join(ROOT, "results")
    json.dump(out, open(os.path.join(RES, "phase1_verdict.json"), "w"), indent=1)
    json.dump({r["basis"]: r for r in reports if r},
              open(os.path.join(RES, "basis_reports.json"), "w"), indent=1)
    json.dump({r["basis"]: {"gates": {g: r["gates"][g] for g in r["gates"]}}
               for r in reports if r},
              open(os.path.join(RES, "threshold_sensitivity.json"), "w"), indent=1)
    json.dump({r["basis"]: {"order_verdicts": r["order_verdicts"],
                            "spearman_pairs": r["order_spearman"],
                            "min_spearman": r["metrics"]["min_family_spearman"]}
               for r in reports if r},
              open(os.path.join(RES, "order_robustness.json"), "w"), indent=1)
    json.dump({r["basis"]: {"family_shares_charged": r["family_shares"],
                            "family_counts_all_children": r["extra"]["fam_all"],
                            "op_family_counts": r["extra"]["opfam"]}
               for r in reports if r},
              open(os.path.join(RES, "classifier_audit.json"), "w"), indent=1)
    json.dump({r["basis"]: {"coverage": r["m0_coverage"], "best": r["best_m0"],
                            "witness_classes_reached": r["witness_reached"]}
               for r in reports if r},
              open(os.path.join(RES, "m0_comparison.json"), "w"), indent=1)
    print(json.dumps({"verdict": verdict, "reason": why,
                      "per_basis": {r["basis"]: sum(1 for g in r["gates"]
                                                    if r["gates"][g]["pass"])
                                    for r in reports if r}}, indent=1))


if __name__ == "__main__":
    main()
