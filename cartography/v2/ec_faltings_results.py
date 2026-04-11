"""
EC Faltings Height Distribution by Rank and CM
================================================
Faltings height h_F(E) measures arithmetic complexity of an elliptic curve.
BSD connects it to L'(E,1). We measure distribution, rank dependence,
conductor scaling, j-height comparison, and CM vs non-CM separation.
"""

import json
import numpy as np
from scipy import stats
import duckdb

DB_PATH = "charon/data/charon.duckdb"
OUT_PATH = "cartography/v2/ec_faltings_results.json"


def load_data():
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute("""
        SELECT faltings_height, rank, conductor, cm, jinv_num, jinv_den, regulator
        FROM elliptic_curves
        WHERE faltings_height IS NOT NULL
    """).fetchdf()
    con.close()
    # j-invariant height: log(max(|num|, |den|))
    df["j_height"] = np.log(np.maximum(np.abs(df["jinv_num"]), np.abs(df["jinv_den"])).clip(1))
    df["log_conductor"] = np.log(df["conductor"].astype(float))
    df["is_cm"] = df["cm"] != 0
    return df


def distribution_by_rank(df):
    results = {}
    for r in sorted(df["rank"].unique()):
        sub = df[df["rank"] == r]["faltings_height"]
        results[str(r)] = {
            "count": int(len(sub)),
            "mean": float(sub.mean()),
            "median": float(sub.median()),
            "std": float(sub.std()),
            "min": float(sub.min()),
            "max": float(sub.max()),
            "q25": float(sub.quantile(0.25)),
            "q75": float(sub.quantile(0.75)),
            "skewness": float(stats.skew(sub)),
            "kurtosis": float(stats.kurtosis(sub)),
        }
    # Rank 0 vs 1 KS test
    r0 = df[df["rank"] == 0]["faltings_height"]
    r1 = df[df["rank"] == 1]["faltings_height"]
    ks_stat, ks_p = stats.ks_2samp(r0, r1)
    # Rank 0 vs 2
    r2 = df[df["rank"] == 2]["faltings_height"]
    ks02_stat, ks02_p = stats.ks_2samp(r0, r2)
    results["ks_test_rank0_vs_rank1"] = {"statistic": float(ks_stat), "p_value": float(ks_p)}
    results["ks_test_rank0_vs_rank2"] = {"statistic": float(ks02_stat), "p_value": float(ks02_p)}
    # Mean shift per rank
    means = [results[str(r)]["mean"] for r in sorted(df["rank"].unique())]
    results["mean_shift_rank0_to_rank1"] = means[1] - means[0] if len(means) > 1 else None
    results["mean_shift_rank1_to_rank2"] = means[2] - means[1] if len(means) > 2 else None
    return results


def conductor_scaling(df):
    """h_F vs log(conductor) scaling law via OLS."""
    x = df["log_conductor"].values
    y = df["faltings_height"].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    result = {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value**2),
        "p_value": float(p_value),
        "std_err": float(std_err),
        "interpretation": f"h_F ~ {slope:.4f} * log(N) + {intercept:.4f}",
    }
    # Per-rank slopes
    for r in sorted(df["rank"].unique()):
        sub = df[df["rank"] == r]
        s, i, rv, pv, se = stats.linregress(sub["log_conductor"].values, sub["faltings_height"].values)
        result[f"rank_{r}_slope"] = float(s)
        result[f"rank_{r}_r_squared"] = float(rv**2)
    return result


def j_height_comparison(df):
    """Correlation between Faltings height and naive j-invariant height."""
    x = df["j_height"].values
    y = df["faltings_height"].values
    corr, p_corr = stats.pearsonr(x, y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    # Residual statistics
    predicted = slope * x + intercept
    residuals = y - predicted
    return {
        "pearson_r": float(corr),
        "pearson_p": float(p_corr),
        "regression_slope": float(slope),
        "regression_intercept": float(intercept),
        "regression_r_squared": float(r_value**2),
        "residual_mean": float(residuals.mean()),
        "residual_std": float(residuals.std()),
        "interpretation": "j-height vs Faltings height linear relationship strength",
    }


def cm_analysis(df):
    """CM vs non-CM Faltings height comparison."""
    cm = df[df["is_cm"]]["faltings_height"]
    ncm = df[~df["is_cm"]]["faltings_height"]
    ks_stat, ks_p = stats.ks_2samp(cm, ncm)
    mw_stat, mw_p = stats.mannwhitneyu(cm, ncm, alternative="two-sided")
    result = {
        "cm_count": int(len(cm)),
        "non_cm_count": int(len(ncm)),
        "cm_mean": float(cm.mean()),
        "non_cm_mean": float(ncm.mean()),
        "cm_median": float(cm.median()),
        "non_cm_median": float(ncm.median()),
        "cm_std": float(cm.std()),
        "non_cm_std": float(ncm.std()),
        "mean_difference": float(cm.mean() - ncm.mean()),
        "ks_test": {"statistic": float(ks_stat), "p_value": float(ks_p)},
        "mann_whitney": {"statistic": float(mw_stat), "p_value": float(mw_p)},
    }
    # Per CM discriminant
    cm_discs = {}
    for d in sorted(df[df["is_cm"]]["cm"].unique()):
        sub = df[df["cm"] == d]["faltings_height"]
        if len(sub) >= 2:
            cm_discs[str(d)] = {
                "count": int(len(sub)),
                "mean": float(sub.mean()),
                "median": float(sub.median()),
            }
    result["per_cm_discriminant"] = cm_discs
    return result


def regulator_correlation(df):
    """h_F vs regulator for rank >= 1."""
    sub = df[(df["rank"] >= 1) & (df["regulator"].notna()) & (df["regulator"] > 0)]
    log_reg = np.log(sub["regulator"].values)
    hf = sub["faltings_height"].values
    corr, p_corr = stats.pearsonr(log_reg, hf)
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_reg, hf)
    return {
        "count": int(len(sub)),
        "pearson_r": float(corr),
        "pearson_p": float(p_corr),
        "regression_slope": float(slope),
        "regression_r_squared": float(r_value**2),
        "interpretation": "Faltings height vs log(regulator) for rank >= 1 curves",
    }


def main():
    df = load_data()
    results = {
        "experiment": "EC Faltings Height Distribution by Rank and CM",
        "total_curves": int(len(df)),
        "global_stats": {
            "mean": float(df["faltings_height"].mean()),
            "median": float(df["faltings_height"].median()),
            "std": float(df["faltings_height"].std()),
            "min": float(df["faltings_height"].min()),
            "max": float(df["faltings_height"].max()),
        },
        "by_rank": distribution_by_rank(df),
        "conductor_scaling": conductor_scaling(df),
        "j_height_comparison": j_height_comparison(df),
        "cm_analysis": cm_analysis(df),
        "regulator_correlation": regulator_correlation(df),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {OUT_PATH}")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
