"""Evaluator for HT-79e904e13a / W4. Reads rows.jsonl only; writes OUTCOME.json."""
import json
import os
import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPTS = int(os.environ.get("W4_ATTEMPTS", "1"))

SPEARMAN_SUCCESS = 0.8
TWIN_MAX_GROWTH = 0.1
SPEARMAN_FAIL = 0.5
TWIN_WITHIN = 0.5
PC_TOL = 0.10
NLEV = 8


def slope(H):
    T = np.arange(1, len(H) + 1, dtype=float)
    return float(np.polyfit(T, np.asarray(H, float), 1)[0])


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8") if l.strip()]
    by = {}
    for r in rows:
        by.setdefault(r["arm"], []).append(r)

    def level_means(arm, key_fn):
        out = []
        for li in range(NLEV):
            v = [key_fn(r) for r in by[arm] if r["level"] == li]
            out.append((float(np.mean(v)), float(np.std(v, ddof=1)), len(v)))
        return out

    def criterion(g_treat, contraction, g_twin):
        rho = float(spearmanr(g_treat, contraction).correlation)
        twin_ok = max(g_twin) <= TWIN_MAX_GROWTH
        success = (rho >= SPEARMAN_SUCCESS) and twin_ok
        within = [abs(gw - gt) <= TWIN_WITHIN * abs(gt) for gw, gt in zip(g_twin, g_treat)]
        failure = (rho < SPEARMAN_FAIL) or (sum(within) >= 5)
        return rho, twin_ok, success, within, failure

    # --- treatment ---
    gT = level_means("TREATMENT", lambda r: slope(r["H"]))
    cT = level_means("TREATMENT", lambda r: r["net_contraction"])
    lmT = level_means("TREATMENT", lambda r: r["lambda_max"])
    gW = level_means("NULL_TWIN", lambda r: slope(r["H"]))
    lmW = level_means("NULL_TWIN", lambda r: r["lambda_max"])
    cW = level_means("NULL_TWIN", lambda r: r["net_contraction"])
    gF = level_means("CONTROL", lambda r: slope(r["log_spread"]))
    g_t = [m for m, _, _ in gT]
    c_t = [m for m, _, _ in cT]
    g_w = [m for m, _, _ in gW]
    rho, twin_ok, success, within, failure = criterion(g_t, c_t, g_w)

    # null twin meets success (reading 8): twin growth ranks with treatment contraction
    rho_twin = float(spearmanr(g_w, c_t).correlation)
    null_twin_meets = bool(rho_twin >= SPEARMAN_SUCCESS)

    # lambda_max match
    lm_match = [abs(w[0] - t[0]) <= 0.1 * abs(t[0]) and t[0] > 0 for w, t in zip(lmW, lmT)]

    # --- positive control ---
    pc = [slope(r["H"]) for r in by["POSITIVE_CONTROL"]]
    known = by["POSITIVE_CONTROL"][0]["known_rate"]
    pc_mean = float(np.mean(pc))
    pc_detected = bool(abs(pc_mean - known) <= PC_TOL * known)

    # --- cheat ---
    gC = level_means("CHEAT", lambda r: slope(r["H"]))
    cC = level_means("CHEAT", lambda r: r["net_contraction"])
    gCw = level_means("CHEAT", lambda r: slope(r["H_twin"]))
    rhoC, twin_okC, successC, _, _ = criterion([m for m, _, _ in gC], [m for m, _, _ in cC], [m for m, _, _ in gCw])
    cheat_detected = bool(successC)

    # --- forward control ---
    rho_fwd = float(spearmanr([m for m, _, _ in gF], c_t).correlation)

    # --- diagnostics for stupid explanations ---
    ngrid = by["TREATMENT"][0]["n_grid"]
    max_frac = max(max(r["n_match"]) for r in by["TREATMENT"]) / ngrid
    infeas = sum(sum(r["n_infeasible_images"]) for r in by["TREATMENT"])
    # plateau diagnostic: fraction of total rise in log count reached by T=10
    def early_frac(r):
        H = np.asarray(r["H"])
        rise = H[-1] - H[0]
        return float((H[9] - H[0]) / rise) if abs(rise) > 1e-9 else float("nan")
    ef = [early_frac(r) for r in by["TREATMENT"]]
    ef_mean = float(np.nanmean(ef))

    if not (pc_detected and cheat_detected):
        outcome = "INSTRUMENT_FAIL"
    elif success and null_twin_meets:
        outcome = "CONFOUNDED"
    elif success:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    anomalies = []
    for li, (ok, t, w) in enumerate(zip(lm_match, lmT, lmW)):
        if not ok:
            anomalies.append(f"level {li}: twin lambda_max {w[0]:.3f} vs treatment {t[0]:.3f} not within 10%")
    if min(c_t) < 0:
        anomalies.append(f"treatment net contraction negative (net expansion) at {sum(c < 0 for c in c_t)} of 8 levels")
    if max(abs(m) for m, _, _ in cW) > 1e-6:
        anomalies.append("twin measured contraction not ~0")
    if infeas:
        anomalies.append(f"{infeas} infeasible (<=0) treatment images")

    cpu = max(r["cpu_s_cumulative"] for r in rows)

    def pack(lst):
        return [{"mean": m, "sd": s, "n": n} for m, s, n in lst]

    out = {
        "triplicateId": "HT-79e904e13a", "world": "W4", "outcome": outcome,
        "statistics": {
            "d_levels": [by["TREATMENT"][i * 10]["d"] for i in range(NLEV)] if False else
                        sorted({r["d"] for r in by["TREATMENT"]}),
            "treatment_backward_growth_nats_per_step": pack(gT),
            "treatment_net_contraction": pack(cT),
            "treatment_lambda_max": pack(lmT),
            "spearman_growth_vs_contraction_n8": rho,
            "null_twin_backward_growth_nats_per_step": pack(gW),
            "null_twin_lambda_max": pack(lmW),
            "null_twin_net_contraction": pack(cW),
            "null_twin_k": [next(r["k"] for r in by["NULL_TWIN"] if r["level"] == li) for li in range(NLEV)],
            "lambda_max_matched_within_10pct": lm_match,
            "twin_max_level_growth": max(g_w),
            "twin_within_50pct_of_treatment_per_level": within,
            "spearman_twin_growth_vs_treatment_contraction": rho_twin,
            "forward_control_growth_nats_per_step": pack(gF),
            "spearman_forward_growth_vs_contraction": rho_fwd,
            "positive_control_growth": {"mean": pc_mean, "sd": float(np.std(pc, ddof=1)), "n": len(pc),
                                        "known_rate": known, "rel_err": abs(pc_mean - known) / known},
            "cheat_spearman": rhoC, "cheat_twin_ok": twin_okC,
            "treatment_success": success, "treatment_failure": failure,
            "max_match_fraction_of_grid": max_frac,
            "mean_fraction_of_entropy_rise_reached_by_T10": ef_mean,
        },
        "criterion_as_applied": (
            "SUCCESS: Spearman(level-mean OLS slope of H(T)=log N_match+log cellvol over T=1..30, level-mean "
            "measured net contraction -mean log|det J|), n=8 levels x 10 seeds, >= 0.8 AND max over levels of "
            "seed-mean null-twin slope <= 0.1 nats/step. FAILURE: Spearman < 0.5 OR |g_twin-g_treat| <= 0.5|g_treat| "
            "at >= 5 of 8 levels. Null twin meets success iff Spearman(twin slope, treatment contraction) >= 0.8. "
            "PC detected iff |mean slope - 0.15388|/0.15388 <= 0.10. CHEAT detected iff full success criterion true on CHEAT rows."),
        "positive_control_detected": pc_detected, "cheat_detected": cheat_detected,
        "null_twin_meets_success": null_twin_meets,
        "stupid_explanations_status": [
            {"text": "grid resolution sets an entropy ceiling", "addressed_by_this_run": False,
             "how": f"only one grid size; max matched fraction of grid {max_frac:.4f}; mean fraction of entropy rise reached by T=10 = {ef_mean:.2f} (plateau diagnostic, not a resolution sweep)"},
            {"text": "radius r scaling produces the trend", "addressed_by_this_run": False,
             "how": "single r = side/30 in every arm; no r sweep"},
            {"text": "points leaving the feasible (positive) region counted as information loss", "addressed_by_this_run": True,
             "how": f"relaxation form keeps states >= d > 0; counted infeasible images = {infeas}"},
            {"text": "matched lambda_max in the twin is not achieved", "addressed_by_this_run": True,
             "how": f"twin lambda_max measured per level; matched within 10% at {sum(lm_match)} of 8 levels"},
        ],
        "anomalies": anomalies,
        "core_minutes": round((cpu + float(os.environ.get("W4_PRIOR_CPU_S", "0"))) / 60.0, 3),
        "attempts": ATTEMPTS,
        "notes": (f"Outcome {outcome}. Backward posterior entropy growth over T=1..30 in the coupled Ricker world "
                  f"ranged {min(g_t):.3f}..{max(g_t):.3f} nats/step across 8 dissipation levels whose measured net contraction "
                  f"ranged {min(c_t):.3f}..{max(c_t):.3f}; Spearman {rho:.3f}. Volume-preserving twin growth ranged "
                  f"{min(g_w):.3f}..{max(g_w):.3f}. Positive control slope {pc_mean:.4f} vs known {known:.4f}; cheat Spearman {rhoC:.3f}. "
                  f"Forward-spread Spearman with contraction {rho_fwd:.3f}. Only one grid and one r were used."),
    }
    open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8").write(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ["outcome", "positive_control_detected", "cheat_detected", "null_twin_meets_success", "anomalies", "core_minutes"]}, indent=1))
    print(json.dumps(out["statistics"], indent=1))


if __name__ == "__main__":
    main()
