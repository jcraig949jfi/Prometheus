"""
Sha-Selmer Rank Mismatch Defect
================================
Does EC Sha size predict genus-2 Selmer rank beyond what MW rank explains?

Approach:
1. Load EC data (31K from charon DuckDB: sha, rank, conductor)
2. Load genus-2 data (66K: two_selmer_rank, analytic_rank, conductor)
3. Match by conductor: pair EC curves with genus-2 curves
4. For matched pairs: regress genus-2 two_selmer_rank on EC sha + EC rank
5. F-test: does EC sha add predictive power beyond EC rank alone?
6. Report residual variance sigma^2 with and without sha

Output: sha_selmer_mismatch_results.json
"""

import json
import os
import sys
import numpy as np
from collections import defaultdict

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "genus2", "data")
OUT_PATH = os.path.join(BASE, "sha_selmer_mismatch_results.json")

# DuckDB path
CHARON_DB = os.path.join(os.path.dirname(os.path.dirname(BASE)), "charon", "data", "charon.duckdb")


def load_ec_data():
    """Load EC curves from charon DuckDB."""
    import duckdb
    con = duckdb.connect(CHARON_DB, read_only=True)
    df = con.execute("""
        SELECT conductor, rank, sha
        FROM elliptic_curves
        WHERE sha IS NOT NULL AND rank IS NOT NULL
    """).fetchall()
    con.close()

    # Group by conductor: list of (rank, sha) per conductor
    ec_by_cond = defaultdict(list)
    for cond, rank, sha in df:
        ec_by_cond[int(cond)].append({"rank": int(rank), "sha": int(sha)})
    return ec_by_cond


def load_genus2_data():
    """Load genus-2 curves, merging two_selmer_rank from full + MW rank from lmfdb."""
    full = json.load(open(os.path.join(DATA_DIR, "genus2_curves_full.json")))
    lmfdb_data = json.load(open(os.path.join(DATA_DIR, "genus2_curves_lmfdb.json")))
    lmfdb = lmfdb_data["records"]

    # Group by conductor
    full_by_cond = defaultdict(list)
    for f in full:
        full_by_cond[f["conductor"]].append(f)

    lmfdb_by_cond = defaultdict(list)
    for l in lmfdb:
        lmfdb_by_cond[l["conductor"]].append(l)

    # Merge and group by conductor
    g2_by_cond = defaultdict(list)
    for cond in full_by_cond:
        fg = full_by_cond[cond]
        lg = lmfdb_by_cond.get(cond, [])
        if len(fg) != len(lg):
            continue
        fg_s = sorted(fg, key=lambda x: str(sorted(x["torsion"])))
        lg_s = sorted(lg, key=lambda x: x["torsion"])
        for f, l in zip(fg_s, lg_s):
            g2_by_cond[int(cond)].append({
                "two_selmer_rank": f["two_selmer_rank"],
                "mw_rank": int(l["rank"]),
                "label": l["label"],
            })
    return g2_by_cond


def build_matched_pairs(ec_by_cond, g2_by_cond):
    """For each conductor appearing in both datasets, create all pairings."""
    shared_conds = set(ec_by_cond.keys()) & set(g2_by_cond.keys())

    pairs = []
    for cond in sorted(shared_conds):
        ec_list = ec_by_cond[cond]
        g2_list = g2_by_cond[cond]
        # Aggregate EC data for this conductor: mean sha, mean rank
        ec_sha_mean = np.mean([e["sha"] for e in ec_list])
        ec_rank_mean = np.mean([e["rank"] for e in ec_list])
        ec_sha_max = max(e["sha"] for e in ec_list)
        ec_rank_max = max(e["rank"] for e in ec_list)
        n_ec = len(ec_list)
        for g in g2_list:
            pairs.append({
                "conductor": cond,
                "g2_selmer": g["two_selmer_rank"],
                "g2_mw_rank": g["mw_rank"],
                "ec_sha_mean": ec_sha_mean,
                "ec_rank_mean": ec_rank_mean,
                "ec_sha_max": ec_sha_max,
                "ec_rank_max": ec_rank_max,
                "n_ec": n_ec,
            })
    return pairs


def ols_regression(X, y):
    """OLS regression. Returns beta, residuals, sigma2, R2."""
    n, p = X.shape
    # Add intercept
    X_int = np.column_stack([np.ones(n), X])
    try:
        beta = np.linalg.lstsq(X_int, y, rcond=None)[0]
    except np.linalg.LinAlgError:
        return None
    y_hat = X_int @ beta
    residuals = y - y_hat
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    sigma2 = ss_res / (n - p - 1) if n > p + 1 else float("inf")
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {
        "beta": beta.tolist(),
        "sigma2": float(sigma2),
        "r2": float(r2),
        "ss_res": float(ss_res),
        "n": n,
        "p": p,
    }


def f_test_nested(ss_res_reduced, p_reduced, ss_res_full, p_full, n):
    """F-test for nested models. Returns F-statistic and p-value."""
    from scipy import stats
    df1 = p_full - p_reduced
    df2 = n - p_full - 1
    if df1 <= 0 or df2 <= 0:
        return float("nan"), float("nan")
    f_stat = ((ss_res_reduced - ss_res_full) / df1) / (ss_res_full / df2)
    p_val = 1 - stats.f.cdf(f_stat, df1, df2)
    return float(f_stat), float(p_val)


def main():
    print("Loading EC data from charon DuckDB...")
    ec_by_cond = load_ec_data()
    print(f"  EC conductors: {len(ec_by_cond)}, total curves: {sum(len(v) for v in ec_by_cond.values())}")

    print("Loading genus-2 data...")
    g2_by_cond = load_genus2_data()
    print(f"  G2 conductors: {len(g2_by_cond)}, total curves: {sum(len(v) for v in g2_by_cond.values())}")

    print("Building matched pairs...")
    pairs = build_matched_pairs(ec_by_cond, g2_by_cond)
    print(f"  Matched pairs: {len(pairs)} across {len(set(p['conductor'] for p in pairs))} conductors")

    if len(pairs) < 10:
        result = {
            "status": "insufficient_data",
            "n_pairs": len(pairs),
            "n_shared_conductors": len(set(p["conductor"] for p in pairs)),
            "note": "Too few conductor matches for regression"
        }
        json.dump(result, open(OUT_PATH, "w"), indent=2)
        print(f"Insufficient data ({len(pairs)} pairs). Saved to {OUT_PATH}")
        return

    # Extract arrays
    y = np.array([p["g2_selmer"] for p in pairs], dtype=float)
    ec_rank = np.array([p["ec_rank_mean"] for p in pairs], dtype=float)
    ec_sha = np.array([p["ec_sha_mean"] for p in pairs], dtype=float)
    g2_mw = np.array([p["g2_mw_rank"] for p in pairs], dtype=float)
    ec_sha_max = np.array([p["ec_sha_max"] for p in pairs], dtype=float)

    print(f"\nTarget: genus-2 two_selmer_rank")
    print(f"  mean={np.mean(y):.3f}, std={np.std(y):.3f}, range=[{np.min(y)}, {np.max(y)}]")
    print(f"EC sha mean: mean={np.mean(ec_sha):.3f}, std={np.std(ec_sha):.3f}")
    print(f"EC rank mean: mean={np.mean(ec_rank):.3f}, std={np.std(ec_rank):.3f}")

    # ---- Model 1: Baseline — EC rank only ----
    print("\n--- Model 1: g2_selmer ~ ec_rank ---")
    X_base = ec_rank.reshape(-1, 1)
    m1 = ols_regression(X_base, y)
    print(f"  R² = {m1['r2']:.6f}, σ² = {m1['sigma2']:.6f}")

    # ---- Model 2: EC rank + EC sha (mean) ----
    print("--- Model 2: g2_selmer ~ ec_rank + ec_sha_mean ---")
    X_full = np.column_stack([ec_rank, ec_sha])
    m2 = ols_regression(X_full, y)
    print(f"  R² = {m2['r2']:.6f}, σ² = {m2['sigma2']:.6f}")

    # ---- Model 3: EC rank + EC sha (max) ----
    print("--- Model 3: g2_selmer ~ ec_rank + ec_sha_max ---")
    X_full_max = np.column_stack([ec_rank, ec_sha_max])
    m3 = ols_regression(X_full_max, y)
    print(f"  R² = {m3['r2']:.6f}, σ² = {m3['sigma2']:.6f}")

    # ---- Model 4: EC rank + EC sha + g2_mw_rank (ceiling check) ----
    print("--- Model 4: g2_selmer ~ ec_rank + ec_sha + g2_mw_rank ---")
    X_ceiling = np.column_stack([ec_rank, ec_sha, g2_mw])
    m4 = ols_regression(X_ceiling, y)
    print(f"  R² = {m4['r2']:.6f}, σ² = {m4['sigma2']:.6f}")

    # ---- Model 5: g2_mw_rank only (natural baseline) ----
    print("--- Model 5: g2_selmer ~ g2_mw_rank ---")
    X_mw = g2_mw.reshape(-1, 1)
    m5 = ols_regression(X_mw, y)
    print(f"  R² = {m5['r2']:.6f}, σ² = {m5['sigma2']:.6f}")

    # ---- Model 6: g2_mw_rank + ec_sha (key test: does sha add beyond MW rank?) ----
    print("--- Model 6: g2_selmer ~ g2_mw_rank + ec_sha ---")
    X_mw_sha = np.column_stack([g2_mw, ec_sha])
    m6 = ols_regression(X_mw_sha, y)
    print(f"  R² = {m6['r2']:.6f}, σ² = {m6['sigma2']:.6f}")

    # F-tests
    print("\n--- F-tests ---")
    n = len(y)

    # F-test: Model 1 vs Model 2 (does sha_mean help beyond ec_rank?)
    f12, p12 = f_test_nested(m1["ss_res"], 1, m2["ss_res"], 2, n)
    print(f"  M1 vs M2 (sha_mean|ec_rank): F={f12:.4f}, p={p12:.6f}")

    # F-test: Model 1 vs Model 3 (does sha_max help beyond ec_rank?)
    f13, p13 = f_test_nested(m1["ss_res"], 1, m3["ss_res"], 2, n)
    print(f"  M1 vs M3 (sha_max|ec_rank):  F={f13:.4f}, p={p13:.6f}")

    # F-test: Model 5 vs Model 6 (does ec_sha help beyond g2_mw_rank?)
    f56, p56 = f_test_nested(m5["ss_res"], 1, m6["ss_res"], 2, n)
    print(f"  M5 vs M6 (sha|g2_mw_rank):   F={f56:.4f}, p={p56:.6f}")

    # Normalize sigma2 by variance of y
    var_y = float(np.var(y))
    norm_sigma2_m1 = m1["sigma2"] / var_y if var_y > 0 else float("inf")
    norm_sigma2_m2 = m2["sigma2"] / var_y if var_y > 0 else float("inf")
    norm_sigma2_m5 = m5["sigma2"] / var_y if var_y > 0 else float("inf")
    norm_sigma2_m6 = m6["sigma2"] / var_y if var_y > 0 else float("inf")

    print(f"\n--- Normalized residual variance (σ²/Var(y)) ---")
    print(f"  M1 (ec_rank):          {norm_sigma2_m1:.4f}")
    print(f"  M2 (ec_rank+sha):      {norm_sigma2_m2:.4f}")
    print(f"  M5 (g2_mw):            {norm_sigma2_m5:.4f}")
    print(f"  M6 (g2_mw+sha):        {norm_sigma2_m6:.4f}")

    # Conductor-level aggregation test
    print("\n--- Conductor-level aggregation ---")
    cond_data = defaultdict(lambda: {"g2_selmer": [], "ec_sha": [], "ec_rank": [], "g2_mw": []})
    for p in pairs:
        c = p["conductor"]
        cond_data[c]["g2_selmer"].append(p["g2_selmer"])
        cond_data[c]["ec_sha"].append(p["ec_sha_mean"])
        cond_data[c]["ec_rank"].append(p["ec_rank_mean"])
        cond_data[c]["g2_mw"].append(p["g2_mw_rank"])

    cond_means = []
    for c, d in cond_data.items():
        cond_means.append({
            "conductor": c,
            "g2_selmer": np.mean(d["g2_selmer"]),
            "ec_sha": np.mean(d["ec_sha"]),
            "ec_rank": np.mean(d["ec_rank"]),
            "g2_mw": np.mean(d["g2_mw"]),
        })
    print(f"  Unique conductors: {len(cond_means)}")

    if len(cond_means) >= 10:
        y_c = np.array([c["g2_selmer"] for c in cond_means])
        ec_r_c = np.array([c["ec_rank"] for c in cond_means]).reshape(-1, 1)
        ec_s_c = np.array([c["ec_sha"] for c in cond_means])
        g2_m_c = np.array([c["g2_mw"] for c in cond_means])

        mc_base = ols_regression(ec_r_c, y_c)
        mc_full = ols_regression(np.column_stack([ec_r_c, ec_s_c]), y_c)
        mc_mw = ols_regression(g2_m_c.reshape(-1, 1), y_c)
        mc_mw_sha = ols_regression(np.column_stack([g2_m_c, ec_s_c]), y_c)

        fc_12, pc_12 = f_test_nested(mc_base["ss_res"], 1, mc_full["ss_res"], 2, len(y_c))
        fc_56, pc_56 = f_test_nested(mc_mw["ss_res"], 1, mc_mw_sha["ss_res"], 2, len(y_c))

        print(f"  Cond-level: ec_rank R²={mc_base['r2']:.6f}, +sha R²={mc_full['r2']:.6f}")
        print(f"  Cond-level: g2_mw R²={mc_mw['r2']:.6f}, +sha R²={mc_mw_sha['r2']:.6f}")
        print(f"  F-test sha|ec_rank: F={fc_12:.4f}, p={pc_12:.6f}")
        print(f"  F-test sha|g2_mw:   F={fc_56:.4f}, p={pc_56:.6f}")

        cond_level = {
            "n_conductors": len(cond_means),
            "ec_rank_only": {"r2": mc_base["r2"], "sigma2": mc_base["sigma2"]},
            "ec_rank_sha": {"r2": mc_full["r2"], "sigma2": mc_full["sigma2"]},
            "g2_mw_only": {"r2": mc_mw["r2"], "sigma2": mc_mw["sigma2"]},
            "g2_mw_sha": {"r2": mc_mw_sha["r2"], "sigma2": mc_mw_sha["sigma2"]},
            "f_test_sha_given_ec_rank": {"F": fc_12, "p": pc_12},
            "f_test_sha_given_g2_mw": {"F": fc_56, "p": pc_56},
        }
    else:
        cond_level = {"n_conductors": len(cond_means), "note": "too few for regression"}

    # Sha-binned analysis
    print("\n--- Sha-binned analysis ---")
    sha_bins = defaultdict(list)
    for p in pairs:
        sha_val = int(p["ec_sha_max"])
        sha_bins[sha_val].append(p["g2_selmer"])

    sha_summary = {}
    for sha_val in sorted(sha_bins.keys()):
        vals = sha_bins[sha_val]
        sha_summary[str(sha_val)] = {
            "n": len(vals),
            "mean_selmer": float(np.mean(vals)),
            "std_selmer": float(np.std(vals)) if len(vals) > 1 else 0.0,
        }
        if len(vals) >= 5:
            print(f"  sha={sha_val}: n={len(vals)}, mean_selmer={np.mean(vals):.3f} ± {np.std(vals):.3f}")

    # Determine verdict
    sha_significant = (p12 < 0.05) or (p56 < 0.05)
    delta_r2 = m2["r2"] - m1["r2"]
    delta_r2_mw = m6["r2"] - m5["r2"]

    if sha_significant and max(delta_r2, delta_r2_mw) > 0.01:
        verdict = "SIGNAL"
        detail = f"EC Sha adds predictive power (ΔR²={max(delta_r2, delta_r2_mw):.4f}, p<0.05)"
    elif sha_significant:
        verdict = "WEAK_SIGNAL"
        detail = f"Statistically significant but tiny effect (ΔR²={max(delta_r2, delta_r2_mw):.6f})"
    else:
        verdict = "NULL"
        detail = f"EC Sha does not predict genus-2 Selmer beyond rank (p={min(p12, p56):.4f})"

    print(f"\n=== VERDICT: {verdict} ===")
    print(f"    {detail}")

    result = {
        "challenge": "sha_selmer_mismatch_defect",
        "question": "Does EC Sha size predict genus-2 Selmer rank beyond what MW rank explains?",
        "verdict": verdict,
        "detail": detail,
        "data": {
            "n_ec_conductors": len(ec_by_cond),
            "n_g2_conductors": len(g2_by_cond),
            "n_shared_conductors": len(set(p["conductor"] for p in pairs)),
            "n_matched_pairs": len(pairs),
        },
        "descriptive": {
            "g2_selmer": {"mean": float(np.mean(y)), "std": float(np.std(y)), "min": float(np.min(y)), "max": float(np.max(y))},
            "ec_sha_mean": {"mean": float(np.mean(ec_sha)), "std": float(np.std(ec_sha))},
            "ec_rank_mean": {"mean": float(np.mean(ec_rank)), "std": float(np.std(ec_rank))},
        },
        "models": {
            "M1_ec_rank": {"r2": m1["r2"], "sigma2": m1["sigma2"], "sigma2_norm": norm_sigma2_m1, "beta": m1["beta"]},
            "M2_ec_rank_sha_mean": {"r2": m2["r2"], "sigma2": m2["sigma2"], "sigma2_norm": norm_sigma2_m2, "beta": m2["beta"]},
            "M3_ec_rank_sha_max": {"r2": m3["r2"], "sigma2": m3["sigma2"], "beta": m3["beta"]},
            "M4_ec_rank_sha_g2mw": {"r2": m4["r2"], "sigma2": m4["sigma2"], "beta": m4["beta"]},
            "M5_g2_mw_rank": {"r2": m5["r2"], "sigma2": m5["sigma2"], "sigma2_norm": norm_sigma2_m5, "beta": m5["beta"]},
            "M6_g2_mw_sha": {"r2": m6["r2"], "sigma2": m6["sigma2"], "sigma2_norm": norm_sigma2_m6, "beta": m6["beta"]},
        },
        "f_tests": {
            "M1_vs_M2_sha_mean_given_ec_rank": {"F": f12, "p": p12},
            "M1_vs_M3_sha_max_given_ec_rank": {"F": f13, "p": p13},
            "M5_vs_M6_sha_given_g2_mw": {"F": f56, "p": p56},
        },
        "sha_binned": sha_summary,
        "conductor_level": cond_level,
    }

    json.dump(result, open(OUT_PATH, "w"), indent=2)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
