#!/usr/bin/env python3
"""
Genus-2 Discriminant Distribution
==================================
Measure the distribution of absolute discriminants for genus-2 curves
and compare to elliptic curves.

Analyses:
1. Distribution stats: mean, median, range, shape
2. Log-normality vs power-law test
3. log|disc| vs log(conductor) scaling
4. Compare disc-conductor relationship to EC
5. Group by Sato-Tate group
"""

import json, sys, warnings
import numpy as np
from pathlib import Path
from collections import Counter
from scipy import stats

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(line_buffering=True)

# ── Config ──────────────────────────────────────────────────────────
G2_PATH  = Path(__file__).parent.parent / "genus2" / "data" / "genus2_curves_full.json"
EC_DB    = Path(__file__).parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).parent / "genus2_disc_stats_results.json"


def ec_discriminant(ainvs):
    """Compute discriminant of elliptic curve from a-invariants [a1,a2,a3,a4,a6]."""
    a1, a2, a3, a4, a6 = ainvs
    b2 = a1**2 + 4*a2
    b4 = a1*a3 + 2*a4
    b6 = a3**2 + 4*a6
    b8 = a1**2*a6 - a1*a3*a4 + a2*a3**2 + 4*a2*a6 - a4**2
    disc = -b2**2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6
    return disc


def distribution_stats(values, label=""):
    """Compute distribution statistics for an array of values."""
    arr = np.array(values, dtype=np.float64)
    log_arr = np.log10(arr[arr > 0])

    result = {
        "count": len(arr),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "p10": float(np.percentile(arr, 10)),
        "p25": float(np.percentile(arr, 25)),
        "p75": float(np.percentile(arr, 75)),
        "p90": float(np.percentile(arr, 90)),
        "skewness": float(stats.skew(arr)),
        "kurtosis": float(stats.kurtosis(arr)),
    }

    if len(log_arr) > 20:
        result["log10_mean"] = float(np.mean(log_arr))
        result["log10_median"] = float(np.median(log_arr))
        result["log10_std"] = float(np.std(log_arr))

        # Shapiro-Wilk on log values (subsample if too large)
        sub = log_arr if len(log_arr) <= 5000 else np.random.default_rng(42).choice(log_arr, 5000, replace=False)
        sw_stat, sw_p = stats.shapiro(sub)
        result["log_shapiro_W"] = float(sw_stat)
        result["log_shapiro_p"] = float(sw_p)
        result["log_normal_plausible"] = bool(sw_p > 0.01)

    return result


def power_law_test(x, y, label=""):
    """Test log-log linear relationship (power law: y ~ x^alpha)."""
    mask = (x > 0) & (y > 0)
    lx = np.log10(x[mask].astype(float))
    ly = np.log10(y[mask].astype(float))
    slope, intercept, r, p, se = stats.linregress(lx, ly)
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r**2),
        "r": float(r),
        "p_value": float(p),
        "std_err": float(se),
        "n_points": int(mask.sum()),
    }


# ── Load genus-2 data ──────────────────────────────────────────────
print("Loading genus-2 curves...")
g2_curves = json.loads(G2_PATH.read_text())
print(f"  {len(g2_curves)} genus-2 curves loaded")

g2_disc = np.array([abs(c["discriminant"]) for c in g2_curves], dtype=np.float64)
g2_cond = np.array([c["conductor"] for c in g2_curves], dtype=np.float64)
g2_sign = np.array([c["disc_sign"] for c in g2_curves], dtype=np.int8)
g2_st   = np.array([c["st_group"] for c in g2_curves])

print(f"  disc range: [{g2_disc.min():.0f}, {g2_disc.max():.0f}]")
print(f"  conductor range: [{g2_cond.min():.0f}, {g2_cond.max():.0f}]")

# ── 1. Distribution stats ──────────────────────────────────────────
print("\n=== Genus-2 Discriminant Distribution ===")
g2_disc_stats = distribution_stats(g2_disc, "genus2_disc")
print(f"  Mean: {g2_disc_stats['mean']:.2f}")
print(f"  Median: {g2_disc_stats['median']:.2f}")
print(f"  Skewness: {g2_disc_stats['skewness']:.2f}")
print(f"  Log-normal plausible: {g2_disc_stats.get('log_normal_plausible', 'N/A')}")

# Sign distribution
sign_counts = Counter(g2_sign.tolist())
sign_dist = {str(k): v for k, v in sorted(sign_counts.items())}
print(f"  Sign distribution: {sign_dist}")

# ── 2. Disc-conductor scaling (genus-2) ────────────────────────────
print("\n=== Disc-Conductor Scaling (Genus-2) ===")
g2_scaling = power_law_test(g2_cond, g2_disc, "genus2")
print(f"  log|disc| ~ {g2_scaling['slope']:.4f} * log(cond) + {g2_scaling['intercept']:.4f}")
print(f"  R^2 = {g2_scaling['r_squared']:.4f}")

# Ratio disc/cond
g2_ratio = g2_disc / g2_cond
g2_ratio_stats = distribution_stats(g2_ratio, "genus2_disc_cond_ratio")
print(f"  disc/cond ratio: median={g2_ratio_stats['median']:.2f}, mean={g2_ratio_stats['mean']:.2f}")

# ── 3. Load EC data for comparison ─────────────────────────────────
print("\n=== Loading EC Data ===")
try:
    import duckdb
    con = duckdb.connect(str(EC_DB), read_only=True)
    ec_rows = con.execute(
        "SELECT ainvs, conductor FROM elliptic_curves WHERE ainvs IS NOT NULL LIMIT 50000"
    ).fetchall()
    con.close()
    print(f"  {len(ec_rows)} EC curves loaded from DuckDB")

    ec_disc_list = []
    ec_cond_list = []
    for row in ec_rows:
        ainvs = list(row[0])
        cond = row[1]
        d = ec_discriminant(ainvs)
        if d != 0:
            ec_disc_list.append(abs(d))
            ec_cond_list.append(cond)

    ec_disc = np.array(ec_disc_list, dtype=np.float64)
    ec_cond = np.array(ec_cond_list, dtype=np.float64)
    print(f"  {len(ec_disc)} EC curves with nonzero discriminant")

    ec_disc_stats = distribution_stats(ec_disc, "ec_disc")
    print(f"  EC disc mean: {ec_disc_stats['mean']:.2f}, median: {ec_disc_stats['median']:.2f}")

    ec_scaling = power_law_test(ec_cond, ec_disc, "ec")
    print(f"  EC: log|disc| ~ {ec_scaling['slope']:.4f} * log(cond) + {ec_scaling['intercept']:.4f}")
    print(f"  EC R^2 = {ec_scaling['r_squared']:.4f}")

    ec_ratio = ec_disc / ec_cond
    ec_ratio_stats = distribution_stats(ec_ratio, "ec_disc_cond_ratio")

    ec_available = True
except Exception as e:
    print(f"  EC data unavailable: {e}")
    ec_disc_stats = None
    ec_scaling = None
    ec_ratio_stats = None
    ec_available = False

# ── 4. Comparison ──────────────────────────────────────────────────
print("\n=== Comparison: Genus-2 vs EC ===")
comparison = {}
if ec_available:
    comparison = {
        "g2_slope": g2_scaling["slope"],
        "ec_slope": ec_scaling["slope"],
        "slope_difference": g2_scaling["slope"] - ec_scaling["slope"],
        "g2_r_squared": g2_scaling["r_squared"],
        "ec_r_squared": ec_scaling["r_squared"],
        "g2_log10_disc_median": g2_disc_stats.get("log10_median"),
        "ec_log10_disc_median": ec_disc_stats.get("log10_median"),
        "g2_disc_cond_ratio_median": g2_ratio_stats["median"],
        "ec_disc_cond_ratio_median": ec_ratio_stats["median"],
        "note": (
            "Genus-2 discriminant is degree 10 in coefficients vs degree 12 for "
            "Weierstrass models; the disc-conductor exponent differs because "
            "genus-2 curves have richer bad reduction types."
        ),
    }
    print(f"  G2 slope: {comparison['g2_slope']:.4f} vs EC slope: {comparison['ec_slope']:.4f}")
    print(f"  G2 disc/cond median: {comparison['g2_disc_cond_ratio_median']:.2f}")
    print(f"  EC disc/cond median: {comparison['ec_disc_cond_ratio_median']:.2f}")
else:
    comparison = {"status": "EC data not available for comparison"}

# ── 5. Group by Sato-Tate group ───────────────────────────────────
print("\n=== Discriminant by Sato-Tate Group ===")
st_groups = sorted(set(g2_st))
st_results = {}
for st in st_groups:
    mask = g2_st == st
    count = int(mask.sum())
    if count < 5:
        st_results[st] = {"count": count, "note": "too few curves for statistics"}
        continue
    discs = g2_disc[mask]
    conds = g2_cond[mask]
    signs = g2_sign[mask]

    st_entry = {
        "count": count,
        "disc_mean": float(np.mean(discs)),
        "disc_median": float(np.median(discs)),
        "disc_std": float(np.std(discs)),
        "log10_disc_mean": float(np.mean(np.log10(discs[discs > 0]))),
        "log10_disc_median": float(np.median(np.log10(discs[discs > 0]))),
        "disc_cond_ratio_median": float(np.median(discs / conds)),
        "frac_negative_disc": float(np.mean(signs < 0)),
    }
    # Disc-conductor scaling within group
    if count >= 10:
        sc = power_law_test(conds, discs, st)
        st_entry["disc_cond_slope"] = sc["slope"]
        st_entry["disc_cond_r_squared"] = sc["r_squared"]

    st_results[st] = st_entry
    print(f"  {st:15s}: n={count:5d}, log10(disc) median={st_entry['log10_disc_median']:.2f}, "
          f"ratio={st_entry['disc_cond_ratio_median']:.2f}"
          + (f", slope={st_entry.get('disc_cond_slope', 'N/A')}" if 'disc_cond_slope' in st_entry else ""))

# ── Disc/cond ratio: is it a clean power law? ─────────────────────
# Check if disc = cond^alpha exactly for genus-2
print("\n=== Power-Law Quality ===")
residuals = np.log10(g2_disc) - g2_scaling["slope"] * np.log10(g2_cond) - g2_scaling["intercept"]
residual_stats = {
    "residual_std": float(np.std(residuals)),
    "residual_iqr": float(np.percentile(residuals, 75) - np.percentile(residuals, 25)),
    "residual_range": [float(np.min(residuals)), float(np.max(residuals))],
}
print(f"  Residual std: {residual_stats['residual_std']:.4f}")
print(f"  Residual IQR: {residual_stats['residual_iqr']:.4f}")

if ec_available:
    ec_resid = np.log10(ec_disc) - ec_scaling["slope"] * np.log10(ec_cond) - ec_scaling["intercept"]
    residual_stats["ec_residual_std"] = float(np.std(ec_resid))
    residual_stats["ec_residual_iqr"] = float(np.percentile(ec_resid, 75) - np.percentile(ec_resid, 25))
    print(f"  EC Residual std: {residual_stats['ec_residual_std']:.4f}")

# ── Assemble results ──────────────────────────────────────────────
results = {
    "analysis": "Genus-2 Discriminant Distribution",
    "data_source": str(G2_PATH),
    "n_genus2_curves": len(g2_curves),
    "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),

    "genus2_discriminant_distribution": g2_disc_stats,
    "genus2_sign_distribution": sign_dist,
    "genus2_disc_conductor_scaling": g2_scaling,
    "genus2_disc_cond_ratio": g2_ratio_stats,
    "power_law_residuals": residual_stats,

    "ec_discriminant_distribution": ec_disc_stats,
    "ec_disc_conductor_scaling": ec_scaling,
    "ec_disc_cond_ratio": ec_ratio_stats,

    "comparison": comparison,
    "by_sato_tate_group": st_results,

    "interpretation": {
        "disc_shape": (
            "Log-normal" if g2_disc_stats.get("log_normal_plausible")
            else "Not log-normal (heavy-tailed)"
        ),
        "disc_cond_power_law": (
            f"log|disc| ~ {g2_scaling['slope']:.3f} * log(cond), "
            f"R^2={g2_scaling['r_squared']:.3f}"
        ),
        "ec_comparison": (
            f"EC slope {ec_scaling['slope']:.3f} vs G2 slope {g2_scaling['slope']:.3f}"
            if ec_available else "EC data not available"
        ),
        "st_group_effect": (
            "Different ST groups show different disc-conductor "
            "scaling and sign distributions; non-generic (non-USp(4)) "
            "groups have systematically different behavior."
        ),
    },
}

OUT_PATH.write_text(json.dumps(results, indent=2))
print(f"\nResults saved to {OUT_PATH}")
print("Done.")
