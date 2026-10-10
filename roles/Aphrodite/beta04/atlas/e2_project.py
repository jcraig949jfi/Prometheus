"""E2 COMPUTE PROJECTION (A1-B.10) and POWER / minimum detectable effect of the 5-cluster FRONTIER design.

  python -m atlas.e2_project --timing runs/e2_timing_pilot_v2/TIMING_RAW.json [--out runs/e2] [--qualified N]

Inputs: per-run CPU at B = 2e5 measured on EXPOSED pilot_v2 R3 families (atlas.e2_driver timing; full budget,
stop_on_hit=False, i.e. the CONSERVATIVE cost: a production run stops at its first qualified program). If the
production qualification phase has run (outcome-free), the number of D-BEH-qualified families is read from
<out>/qual/*.json; otherwise every scenario in QUAL_SCENARIOS is reported and the decision uses the UPPER BOUND
(all 15 qualified).

Truncation (frozen order, A1-B.10): while the 1x screen projection > 24 core-h: (1) drop chain_strict; (2) 6 seeds;
(3) drop desert_ref on families whose admission evidence shows from-scratch failure (every admitted R3/R4 family
passed rule 3(b), base 1e6 NOT solved, so step 3 removes desert_ref everywhere). Each step taken is recorded.

Power. FRONTIER YES_SCREEN needs >= 5 informative units and both exact one-sided sign-flip p < 0.05. With 5 units the
smallest attainable p is 1/32 = 0.031 and any unit with difference <= 0 makes p >= 2/32, so YES_SCREEN <=> ALL 5
clusters show X3 > chain_neutral AND X3 > X3G (cluster totals). Under per-seed hit probability p1 for X3 and p0 for
both comparators (independent binomials, 8 seeds per family, cluster sizes as planned), power = prod_c
P(X_c > Y_c and X_c > Z_c), X_c ~ Bin(n_c, p1), Y_c, Z_c ~ Bin(n_c, p0) iid. MDE = the smallest p1 (grid 0.005) with
power >= 0.80. If fewer than 5 clusters contain a D-BEH-qualified family, YES_SCREEN is impossible (power 0).
"""
import argparse
import json
from math import comb
from pathlib import Path
from typing import Dict, List, Sequence

CAP_CORE_H = 24.0
N_FAMILIES = 15
QUAL_SCENARIOS = [15, 12, 9, 6, 3, 0]
CLUSTER_SIZES_ALL = [6, 3, 2, 2, 2]          # production R3/R4 skeleton clusters (e2_driver.cluster_of)
KCAL_SEEDS = 3
KCAL_ITERATIONS_ASSUMED = 2                   # pilot: X3G at K = X3 cells realised 0.90x -> one ratio step
ATLAS_FAMILIES = 53


def binom_pmf(n: int, p: float) -> List[float]:
    return [comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def p_beats_both(n: int, p1: float, p0: float) -> float:
    x = binom_pmf(n, p1)
    y = binom_pmf(n, p0)
    cdf_below, acc = [], 0.0
    for k in range(n + 1):
        cdf_below.append(acc)                 # P(Y < k)
        acc += y[k]
    return sum(x[k] * cdf_below[k] ** 2 for k in range(n + 1))


def power(cluster_sizes: Sequence[int], seeds: int, p1: float, p0: float) -> float:
    if len(cluster_sizes) < 5:
        return 0.0
    pw = 1.0
    for m in cluster_sizes:
        pw *= p_beats_both(m * seeds, p1, p0)
    return pw


def mde(cluster_sizes: Sequence[int], seeds: int, p0: float, target: float = 0.80) -> Dict:
    grid = [round(p0 + 0.005 * i, 3) for i in range(1, 400) if p0 + 0.005 * i <= 1.0]
    for p1 in grid:
        pw = power(cluster_sizes, seeds, p1, p0)
        if pw >= target:
            return {"p0": p0, "mde_p1": p1, "difference": round(p1 - p0, 3), "power_at_mde": round(pw, 3)}
    return {"p0": p0, "mde_p1": None, "difference": None, "power_at_mde": None}


def per_run_costs(timing: Dict) -> Dict[str, float]:
    arms = {}
    for f, r in timing["families"].items():
        for a, v in r["arms"].items():
            if v and v.get("cpu_s_per_2e5"):
                arms.setdefault(a, []).append(v["cpu_s_per_2e5"])
    return {a: sum(v) / len(v) for a, v in arms.items()}


def screen_cost(cost: Dict[str, float], qual_cpu: float, kcal_cpu: float, n_qual: int, arms: Sequence[str],
                seeds: int, desert_families: int = N_FAMILIES) -> float:
    s = N_FAMILIES * qual_cpu
    for a in arms:
        if a in ("D1-X3", "X3G"):
            s += n_qual * seeds * cost[a]
        elif a == "desert_ref":
            s += desert_families * seeds * cost[a]
        else:
            s += N_FAMILIES * seeds * cost[a]
    if "X3G" in arms:
        s += n_qual * kcal_cpu
    return s / 3600.0


def truncate(cost, qual_cpu, kcal_cpu, n_qual) -> Dict:
    arms = ["credit_blind", "chain_strict", "chain_neutral", "D1-X3", "X3G", "desert_ref"]
    seeds = 8
    desert = N_FAMILIES
    steps = []
    h = screen_cost(cost, qual_cpu, kcal_cpu, n_qual, arms, seeds, desert)
    hist = [{"step": "none", "core_h": round(h, 2)}]
    if h > CAP_CORE_H:
        arms = [a for a in arms if a != "chain_strict"]
        steps.append("1: drop chain_strict")
        h = screen_cost(cost, qual_cpu, kcal_cpu, n_qual, arms, seeds, desert)
        hist.append({"step": steps[-1], "core_h": round(h, 2)})
    if h > CAP_CORE_H:
        seeds = 6
        steps.append("2: 6 seeds")
        h = screen_cost(cost, qual_cpu, kcal_cpu, n_qual, arms, seeds, desert)
        hist.append({"step": steps[-1], "core_h": round(h, 2)})
    if h > CAP_CORE_H:
        desert = 0
        steps.append("3: drop desert_ref on all 15 (admission rule 3(b): base 1e6 not solved)")
        h = screen_cost(cost, qual_cpu, kcal_cpu, n_qual, [a for a in arms if a != "desert_ref"], seeds, desert)
        hist.append({"step": steps[-1], "core_h": round(h, 2)})
    return {"qualified_families": n_qual, "truncation_steps": steps, "history": hist, "final_core_h": round(h, 2),
            "within_cap": h <= CAP_CORE_H, "arms": arms if desert else [a for a in arms if a != "desert_ref"],
            "seeds": seeds}


def project(timing: Dict, n_qual_actual=None) -> Dict:
    cost = per_run_costs(timing)
    fams = timing["families"].values()
    qual_cpu = sum(r["qual_cpu_s"] for r in fams) / len(timing["families"])
    atlas_cpu = sum(r["atlas_cpu_s"] for r in fams) / len(timing["families"])
    kc = [r["kcal_probe"] for r in fams]
    x3_seed = sum(k["x3_cpu_s"] for k in kc) / len(kc)
    x3g_seed = sum(k["x3g_cpu_s"] for k in kc) / len(kc)
    kcal_cpu = KCAL_SEEDS * x3_seed + KCAL_SEEDS * KCAL_ITERATIONS_ASSUMED * x3g_seed
    kcal_cpu_ub = KCAL_SEEDS * x3_seed + KCAL_SEEDS * 3 * x3g_seed
    per_family_seed = sum(cost.values())
    scen = {str(q): truncate(cost, qual_cpu, kcal_cpu, q) for q in QUAL_SCENARIOS}
    decision_q = n_qual_actual if n_qual_actual is not None else max(QUAL_SCENARIOS)
    pw = {}
    for seeds in (8, 6):
        pw["seeds_%d" % seeds] = {"cluster_sizes_all_qualified": CLUSTER_SIZES_ALL,
                                  "mde_80pct": [mde(CLUSTER_SIZES_ALL, seeds, p0) for p0 in
                                                (0.0, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5)],
                                  "power_at_C013_D1_rates": round(power(CLUSTER_SIZES_ALL, seeds, 0.10, 1 / 45), 4)}
    worst = [1, 1, 1, 1, 1]
    return {
        "per_run_cpu_s_at_2e5_full_budget": {a: round(v, 1) for a, v in cost.items()},
        "per_family_seed_all_6_arms_cpu_s": round(per_family_seed, 1),
        "descriptor_qualification_cpu_s_per_family": round(qual_cpu, 1),
        "k_calibration_cpu_s_per_qualified_family": {"assumed_2_iterations": round(kcal_cpu, 1),
                                                     "upper_bound_3_iterations": round(kcal_cpu_ub, 1)},
        "atlas_cpu_s_per_family_measured": round(atlas_cpu, 1),
        "atlas_mode_core_h": {"53 x measured mean": round(ATLAS_FAMILIES * atlas_cpu / 3600, 2),
                              "allowance (5 oversize R2 witnesses at 300 s)":
                                  round(((ATLAS_FAMILIES - 5) * atlas_cpu + 5 * 300) / 3600, 2)},
        "screen_projection_by_qualified_count": scen,
        "decision": {"qualified_used": decision_q,
                     "basis": "production qualification phase (outcome-free)" if n_qual_actual is not None else
                     "UPPER BOUND: all 15 D-BEH-qualified (the qual phase has not run on production)",
                     **scen.get(str(decision_q), truncate(cost, qual_cpu, kcal_cpu, decision_q))},
        "power_frontier_5_clusters": pw,
        "power_notes": [
            "YES_SCREEN requires every one of the 5 clusters to show X3 > chain_neutral AND X3 > X3G "
            "(min attainable p = 1/32).",
            "If any cluster has no D-BEH-qualified family, units < 5 and the readout is INCONCLUSIVE_CENSORED "
            "whatever the effect (power 0).",
            "C-013 D1 at B = 2e5 (N = 15): chain_strict 4/45, chain_neutral 1/45, X3 0, X3G 0 -- an under-powered "
            "null; power_at_C013_D1_rates uses p0 = 1/45 and a hypothetical X3 rate 0.10.",
            "Smallest clusters (2 families x 8 seeds = 16 runs) dominate the power: worst case all clusters of size "
            "1 would need p1 >> p0 per family.",
        ],
        "assumptions": [
            "per-run cost = full-budget cost (stop_on_hit=False) measured with 2 concurrent workers on 2 EXPOSED "
            "pilot_v2 R3 families (fp map_of_filter, fs post_fold); production runs that hit stop earlier",
            "K calibration = %d seeds x (X3 + %d X3G iterations) at the full budget" % (KCAL_SEEDS,
                                                                                        KCAL_ITERATIONS_ASSUMED),
            "unqualified families skip D1-X3, X3G and K calibration (INSTRUMENT_UNVALIDATED)",
            "atlas mode is separate from the 1x screen budget",
        ],
        "worst_case_cluster_size_1_mde": mde(worst, 8, 0.0),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing", required=True)
    ap.add_argument("--out", default=None, help="E2 out dir: read <out>/qual/*.json for the qualified count")
    ap.add_argument("--qualified", type=int, default=None)
    ap.add_argument("--write", default=None)
    a = ap.parse_args(argv)
    t = json.loads(Path(a.timing).read_text())
    nq = a.qualified
    if nq is None and a.out:
        qs = list((Path(a.out) / "qual").glob("*.json"))
        if len(qs) == N_FAMILIES:
            nq = sum(json.loads(q.read_text())["qualified"] for q in qs)
    rep = project(t, nq)
    if a.write:
        Path(a.write).write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
