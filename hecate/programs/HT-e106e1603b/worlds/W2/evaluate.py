"""Evaluate HT-e106e1603b / W2 from rows.jsonl only; writes OUTCOME.json."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NS = (1000, 2000)
TOL_SUCCESS = 0.2
TOL_TWIN = 0.5
SLOPE_FRAC = 0.05
FAIL_LOW = 0.2


def series_stats(counts, n):
    x = np.asarray(counts, dtype=float) / n
    L = len(x)
    h = x[L // 2:]
    t = np.arange(L // 2, L, dtype=float)
    slope = float(np.polyfit(t, h, 1)[0]) * 1e4 if len(h) > 1 else float("nan")
    return float(h.mean()), slope


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"))]
    meta = [r for r in rows if r["arm"] == "META"]
    pc = [r for r in rows if r["arm"] == "POSITIVE_CONTROL"]
    anomalies = []

    pstars = [r["p_star_seed"] for r in pc]
    pc_detected = len(pc) >= 5 and all(p is not None and 0.01 <= p <= 0.2 for p in pstars)
    p_star = float(np.mean([p for p in pstars if p is not None])) if any(
        p is not None for p in pstars) else None

    per = {}
    truncated_core = False
    for r in rows:
        if r["arm"] in ("TREATMENT", "NULL_TWIN", "CONTROL", "CHEAT"):
            if r.get("truncated"):
                if r["arm"] in ("TREATMENT", "NULL_TWIN"):
                    truncated_core = True
                else:
                    anomalies.append(f"{r['arm']} seed {r['seed']} n {r['n']} truncated by compute guard")
            if not r["counts"]:
                continue
            rho, slope = series_stats(r["counts"], r["n"])
            per.setdefault((r["arm"], r["n"]), []).append(
                {"seed": r["seed"], "rho_star": rho, "slope_per_1e4": slope,
                 "avalanche": r.get("avalanche"), "capped": r.get("capped_relaxations")})

    stats = {"p_star": p_star, "p_star_per_seed": pstars}
    agg = {}
    for (arm, n), lst in sorted(per.items()):
        rho = float(np.mean([d["rho_star"] for d in lst]))
        sl = float(np.mean([d["slope_per_1e4"] for d in lst]))
        rel = abs(rho - p_star) / p_star if p_star else None
        agg[(arm, n)] = (rho, sl, rel)
        stats[f"{arm}_n{n}"] = {
            "n_seeds": len(lst), "rho_star_mean": rho, "slope_per_1e4_mean": sl,
            "rel_dist_to_p_star": rel, "per_seed": lst}

    def clause_ab(arm, n):
        if (arm, n) not in agg or p_star is None:
            return False
        rho, sl, rel = agg[(arm, n)]
        return rel <= TOL_SUCCESS and sl < SLOPE_FRAC * rho

    cheat_detected = all(clause_ab("CHEAT", n) for n in NS)
    twin_meets = any(clause_ab("NULL_TWIN", n) for n in NS)

    success_by_n, failure_by_n = {}, {}
    for n in NS:
        if ("TREATMENT", n) in agg and ("NULL_TWIN", n) in agg and p_star:
            rho, sl, rel = agg[("TREATMENT", n)]
            trel = agg[("NULL_TWIN", n)][2]
            success_by_n[n] = bool(rel <= TOL_SUCCESS and sl < SLOPE_FRAC * rho and trel > TOL_TWIN)
            failure_by_n[n] = {"rho_below_0.2_pstar": bool(rho < FAIL_LOW * p_star),
                               "nonstationary": bool(not sl < SLOPE_FRAC * rho),
                               "twin_within_20pct": bool(trel <= TOL_SUCCESS)}
        else:
            success_by_n[n] = False
    treatment_success = all(success_by_n.values())
    stats["success_by_n"] = {str(k): v for k, v in success_by_n.items()}
    stats["failure_criterion_by_n"] = {str(k): v for k, v in failure_by_n.items()}

    if truncated_core:
        outcome = "NOT_BUILT"
    elif not (pc_detected and cheat_detected):
        outcome = "INSTRUMENT_FAIL"
    elif twin_meets:
        outcome = "CONFOUNDED"
    elif treatment_success:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    # control anomalies
    for n in NS:
        if ("TREATMENT", n) in agg:
            caps = [d["capped"] for d in per[("TREATMENT", n)]]
            if any(caps):
                anomalies.append(f"TREATMENT n={n}: relaxations hitting 50-sweep cap per seed {caps}")
    for r in pc:
        for n in NS:
            fr = r["fail_frac"][str(n)]
            if fr[0] > 0.05 or fr[-1] < 0.95:
                anomalies.append(f"PC seed {r['seed']} n={n}: fail frac at grid ends {fr[0]:.2f},{fr[-1]:.2f}")

    tr = {n: agg.get(("TREATMENT", n)) for n in NS}
    notes = (
        f"p* (L2 crossing, mean of 5 seeds) = {p_star}. "
        + " ".join(f"n={n}: treatment rho*={tr[n][0]:.4g} (rel dist {tr[n][2]:.3g}), slope/1e4={tr[n][1]:.3g};"
                   for n in NS if tr[n] and p_star)
        + " " + " ".join(f"twin n={n} rho*={agg[('NULL_TWIN', n)][0]:.4g};" for n in NS
                         if ('NULL_TWIN', n) in agg)
        + " " + " ".join(f"control n={n} rho*={agg[('CONTROL', n)][0]:.4g};" for n in NS
                         if ('CONTROL', n) in agg)
        + f" Outcome by PREREG rule: {outcome}.")

    out = {
        "triplicateId": "HT-e106e1603b", "world": "W2", "outcome": outcome,
        "statistics": stats,
        "criterion_as_applied": (
            "For each n in {1000,2000} (both required): with seed means over 5 seeds, "
            "|rho*_T - p*|/p* <= 0.2 AND slope_T (OLS of |e|/n on injection index over last half, x1e4) "
            "< 0.05*rho*_T AND |rho*_twin - p*|/p* > 0.5; p* = mean of per-seed logistic crossings "
            "(n=1000 vs 2000) in [0.01,0.2]. Twin meets success if within 20% of p* with slope clause, any n."),
        "positive_control_detected": bool(pc_detected), "cheat_detected": bool(cheat_detected),
        "null_twin_meets_success": bool(twin_meets),
        "stupid_explanations_status": [
            {"text": "residue accumulates in trapping sets monotonically and the density 'at' p* is just where the run was stopped",
             "addressed_by_this_run": True,
             "how": "drift-slope clause over the last half of 30000 injections, per n and seed"},
            {"text": "the density equals p* because both are set by the same degree-3 majority arithmetic, not by self-organization",
             "addressed_by_this_run": False,
             "how": "needs the t=3-of-3 repeat named in alternative_explanation; not run in this probe"},
            {"text": "the twin fails merely because random flips inject errors, a trivially different drive",
             "addressed_by_this_run": False,
             "how": "the matched-volume twin is the only null; no twin that removes errors blindly was run"},
        ],
        "anomalies": anomalies,
        "core_minutes": (meta[-1]["cpu_s_total"] / 60.0) if meta else None,
        "attempts": meta[-1]["attempts"] if meta else None,
        "notes": notes,
    }
    with open(os.path.join(HERE, "OUTCOME.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                          "null_twin_meets_success", "core_minutes", "attempts")}))
    print(notes)


if __name__ == "__main__":
    main()
