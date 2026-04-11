#!/usr/bin/env python3
"""
Regulator-Class Number Convexity for Real Quadratic Fields
===========================================================
Plot class number h against regulator R for real quadratic fields Q(sqrt(D)).
Compute the convexity parameter of the boundary envelope in (log R, log h) space.

Key identity: h * R = sqrt(D) * L(1, chi_D) / 2  (Dirichlet class number formula)

Analysis:
  1. Load degree-2 NF with positive discriminant (real quadratic) from LMFDB
  2. Extract h (class_number) and R (regulator)
  3. Scatter in (log R, log h) space
  4. Boundary envelope: for each R-bin, find max h, 95th percentile, median
  5. Fit upper boundary: convex, concave, or linear?
  6. Multiple convexity measures: quadratic 2a, geometric curvature, deviation index
  7. Verify h*R ~ sqrt(disc) relationship (Dirichlet class number formula)

Data: LMFDB PostgreSQL (devmirror.lmfdb.xyz) + local fallback
Output: nf_regulator_convexity_results.json + .png
"""

import json
import math
import time
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parent.parent.parent
LOCAL_NF = ROOT / "cartography" / "number_fields" / "data" / "number_fields.json"
OUTPUT = Path(__file__).resolve().parent / "nf_regulator_convexity_results.json"
PLOT_PATH = Path(__file__).resolve().parent / "nf_regulator_convexity.png"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def fetch_lmfdb_data(max_rows=200000):
    """Fetch real quadratic fields from LMFDB PostgreSQL mirror."""
    try:
        import psycopg2
        con = psycopg2.connect(
            host='devmirror.lmfdb.xyz', port=5432,
            dbname='lmfdb', user='lmfdb', password='lmfdb',
            connect_timeout=15
        )
        cur = con.cursor()
        cur.execute(f"""
            SELECT disc_abs, class_number, regulator
            FROM nf_fields
            WHERE degree = 2 AND disc_sign = 1
              AND regulator IS NOT NULL AND class_number IS NOT NULL
            ORDER BY disc_abs
            LIMIT {max_rows}
        """)
        rows = cur.fetchall()
        con.close()
        fields = []
        for disc_abs, h, reg in rows:
            fields.append({
                "disc": int(disc_abs),
                "h": int(h),
                "R": float(reg),
            })
        print(f"  LMFDB: loaded {len(fields)} real quadratic fields")
        return fields
    except Exception as e:
        print(f"  LMFDB fetch failed: {e}")
        return None


def load_local_data():
    """Fallback: load from local JSON."""
    with open(LOCAL_NF) as f:
        data = json.load(f)
    fields = []
    for d in data:
        if d["degree"] == 2 and d.get("disc_sign") == 1 and d.get("regulator"):
            fields.append({
                "disc": int(d["disc_abs"]),
                "h": int(d["class_number"]),
                "R": float(d["regulator"]),
            })
    print(f"  Local: loaded {len(fields)} real quadratic fields")
    return fields


# ---------------------------------------------------------------------------
# Boundary envelope computation
# ---------------------------------------------------------------------------

def compute_envelope(log_R, log_h, n_bins=50, use_percentile=True):
    """Compute upper/lower/median boundary envelope in log-log space.

    Uses percentile-based bins (equal count) for robustness.
    """
    if use_percentile:
        bin_edges = np.percentile(log_R, np.linspace(0, 100, n_bins + 1))
    else:
        bin_edges = np.linspace(log_R.min(), log_R.max(), n_bins + 1)

    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    upper_max = np.full(n_bins, np.nan)
    upper_95 = np.full(n_bins, np.nan)
    upper_99 = np.full(n_bins, np.nan)
    lower_min = np.full(n_bins, np.nan)
    median_v = np.full(n_bins, np.nan)
    counts = np.zeros(n_bins, dtype=int)

    for i in range(n_bins):
        mask = (log_R >= bin_edges[i]) & (log_R < bin_edges[i + 1])
        n = mask.sum()
        if n < 5:
            continue
        vals = log_h[mask]
        upper_max[i] = np.max(vals)
        upper_95[i] = np.percentile(vals, 95)
        upper_99[i] = np.percentile(vals, 99)
        lower_min[i] = np.min(vals)
        median_v[i] = np.median(vals)
        counts[i] = n

    return {
        "bin_centers": bin_centers,
        "upper_max": upper_max,
        "upper_95": upper_95,
        "upper_99": upper_99,
        "lower_min": lower_min,
        "median": median_v,
        "counts": counts,
    }


# ---------------------------------------------------------------------------
# Convexity fitting
# ---------------------------------------------------------------------------

def fit_boundary(x, y, label="boundary"):
    """Fit linear, quadratic, cubic to a boundary curve.
    Returns convexity metrics.
    """
    valid = ~np.isnan(y) & ~np.isnan(x)
    x_v, y_v = x[valid], y[valid]
    if len(x_v) < 6:
        return None

    # Linear
    slope, intercept, r_val, p_val, se = stats.linregress(x_v, y_v)
    y_lin = slope * x_v + intercept
    ss_tot = np.sum((y_v - np.mean(y_v)) ** 2)
    r2_lin = 1 - np.sum((y_v - y_lin) ** 2) / ss_tot if ss_tot > 0 else 0

    # Quadratic
    c2 = np.polyfit(x_v, y_v, 2)
    y_q = np.polyval(c2, x_v)
    r2_quad = 1 - np.sum((y_v - y_q) ** 2) / ss_tot if ss_tot > 0 else 0

    # Cubic
    c3 = np.polyfit(x_v, y_v, 3)
    y_c = np.polyval(c3, x_v)
    r2_cub = 1 - np.sum((y_v - y_c) ** 2) / ss_tot if ss_tot > 0 else 0

    # Numerical second derivative (finite differences)
    dx = np.diff(x_v)
    dy = np.diff(y_v)
    deriv1 = dy / dx
    mid1 = 0.5 * (x_v[:-1] + x_v[1:])
    dx2 = np.diff(mid1)
    d2y = np.diff(deriv1)
    deriv2 = d2y / dx2
    mid2 = 0.5 * (mid1[:-1] + mid1[1:])

    # Geometric curvature: kappa = y'' / (1 + y'^2)^(3/2)
    deriv1_mid = 0.5 * (deriv1[:-1] + deriv1[1:])
    kappa = deriv2 / (1 + deriv1_mid ** 2) ** 1.5

    return {
        "label": label,
        "n_points": int(len(x_v)),
        "linear": {
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r2_lin),
        },
        "quadratic": {
            "coeffs": [float(c) for c in c2],
            "a": float(c2[0]),
            "b": float(c2[1]),
            "c": float(c2[2]),
            "r_squared": float(r2_quad),
            "convexity_2a": float(2 * c2[0]),
        },
        "cubic": {
            "coeffs": [float(c) for c in c3],
            "r_squared": float(r2_cub),
        },
        "numerical": {
            "second_derivative_mean": float(np.mean(deriv2)),
            "second_derivative_median": float(np.median(deriv2)),
            "second_derivative_std": float(np.std(deriv2)),
            "geometric_curvature_mean": float(np.mean(kappa)),
            "geometric_curvature_median": float(np.median(kappa)),
        },
        "shape": ("convex" if 2 * c2[0] > 0.01
                   else "concave" if 2 * c2[0] < -0.01
                   else "approximately_linear"),
    }


def convex_hull_analysis(log_R, log_h):
    """Analyze convexity via the convex hull of the point cloud."""
    pts = np.column_stack([log_R, log_h])
    hull = ConvexHull(pts)

    # Extract upper boundary of hull
    hull_pts = pts[hull.vertices]
    hull_pts = hull_pts[hull_pts[:, 0].argsort()]

    # Split into upper and lower by comparing to centroid
    cy = np.mean(log_h)
    upper_hull = hull_pts[hull_pts[:, 1] >= cy]
    upper_hull = upper_hull[upper_hull[:, 0].argsort()]

    # Bowing ratio: hull area / bounding box area
    x_range = log_R.max() - log_R.min()
    y_range = log_h.max() - log_h.min()
    bbox_area = x_range * y_range
    hull_area = hull.volume  # 2D: volume = area
    bowing_ratio = hull_area / bbox_area if bbox_area > 0 else 0

    # Fit upper hull
    upper_fit = None
    if len(upper_hull) > 5:
        c2 = np.polyfit(upper_hull[:, 0], upper_hull[:, 1], 2)
        upper_fit = {
            "n_vertices": int(len(upper_hull)),
            "quadratic_a": float(c2[0]),
            "convexity_2a": float(2 * c2[0]),
        }

    return {
        "hull_area": float(hull_area),
        "bbox_area": float(bbox_area),
        "bowing_ratio": float(bowing_ratio),
        "n_hull_vertices": int(len(hull.vertices)),
        "upper_hull_fit": upper_fit,
    }


# ---------------------------------------------------------------------------
# Class number formula verification
# ---------------------------------------------------------------------------

def verify_class_number_formula(fields):
    """Verify h * R = sqrt(D) * L(1, chi_D) / 2."""
    discs = np.array([f["disc"] for f in fields], dtype=float)
    h_vals = np.array([f["h"] for f in fields], dtype=float)
    R_vals = np.array([f["R"] for f in fields])
    hR = h_vals * R_vals
    sqrtD = np.sqrt(discs)

    # Ratio = L(1, chi_D) / 2
    ratio = hR / sqrtD

    # Fit log(hR) = alpha * log(D) + beta
    log_D = np.log(discs)
    log_hR = np.log(hR)
    slope, intercept, r_val, p_val, se = stats.linregress(log_D, log_hR)

    # Quadratic deviation in log(hR) vs log(D)
    c2 = np.polyfit(log_D, log_hR, 2)

    # Check if L(1,chi_D)/2 grows with log(D) (Siegel's theorem average)
    log_log_D = np.log(np.maximum(log_D, 1e-10))
    slope_L, intercept_L, r_L, _, _ = stats.linregress(log_D, np.log(np.maximum(ratio, 1e-10)))

    return {
        "hR_over_sqrtD": {
            "mean": float(np.mean(ratio)),
            "median": float(np.median(ratio)),
            "std": float(np.std(ratio)),
            "min": float(np.min(ratio)),
            "max": float(np.max(ratio)),
            "p25": float(np.percentile(ratio, 25)),
            "p75": float(np.percentile(ratio, 75)),
        },
        "log_hR_vs_log_D": {
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_val ** 2),
            "quadratic_coeffs": [float(c) for c in c2],
            "note": "slope ~0.5 confirms h*R ~ sqrt(D); deviation = L-function growth",
        },
        "L_value_growth": {
            "log_ratio_vs_log_D_slope": float(slope_L),
            "r_squared": float(r_L ** 2),
            "note": "L(1,chi_D)/2 grows slowly with D (Siegel average ~ log D)",
        },
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def make_plot(fields, envelope, upper_max_fit, upper_95_fit, hull_info, formula):
    """Generate 4-panel diagnostic plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        valid = [f for f in fields if f["h"] > 0 and f["R"] > 0]
        log_R = np.array([math.log(f["R"]) for f in valid])
        log_h = np.array([math.log(f["h"]) for f in valid])
        discs = np.array([f["disc"] for f in valid], dtype=float)
        hR = np.array([f["h"] * f["R"] for f in valid])

        bc = envelope["bin_centers"]
        vm = ~np.isnan(envelope["upper_max"])

        fig, axes = plt.subplots(2, 2, figsize=(14, 11))
        fig.suptitle("Regulator-Class Number Convexity: Real Quadratic Fields",
                      fontsize=14, fontweight='bold')

        # (0,0): Scatter + envelopes in log-log space
        ax = axes[0, 0]
        ax.scatter(log_R, log_h, s=0.5, alpha=0.08, c='steelblue', rasterized=True)
        ax.plot(bc[vm], envelope["upper_max"][vm], 'r-', lw=2, label='Max envelope')
        ax.plot(bc[vm], envelope["upper_95"][vm], 'm-', lw=1.5, label='95th pctile')
        ax.plot(bc[vm], envelope["median"][vm], 'orange', lw=1.5, ls='--', label='Median')
        # Quadratic fit overlay on upper max
        if upper_max_fit:
            c2 = upper_max_fit["quadratic"]["coeffs"]
            x_fit = np.linspace(bc[vm].min(), bc[vm].max(), 100)
            y_fit = np.polyval(c2, x_fit)
            ax.plot(x_fit, y_fit, 'r--', lw=1.5,
                    label=f'Quad (2a={upper_max_fit["quadratic"]["convexity_2a"]:.3f})')
        ax.set_xlabel("log(R)")
        ax.set_ylabel("log(h)")
        ax.set_title("log(h) vs log(R) with boundary envelopes")
        ax.legend(fontsize=7, loc='upper right')

        # (0,1): h*R vs sqrt(D)
        ax = axes[0, 1]
        ax.scatter(np.sqrt(discs), hR, s=0.5, alpha=0.08, c='steelblue', rasterized=True)
        x_line = np.linspace(0, np.sqrt(discs.max()), 200)
        # Use median ratio for reference line
        med_ratio = formula["hR_over_sqrtD"]["median"]
        ax.plot(x_line, med_ratio * x_line, 'r--', lw=1.5,
                label=f'h*R = {med_ratio:.2f}*sqrt(D)')
        ax.set_xlabel("sqrt(D)")
        ax.set_ylabel("h * R")
        ax.set_title(f"Class Number Formula: h*R vs sqrt(D)")
        ax.legend(fontsize=8)

        # (1,0): L(1,chi_D)/2 distribution
        ax = axes[1, 0]
        ratio = hR / np.sqrt(discs)
        ax.hist(ratio, bins=150, density=True, alpha=0.7, color='steelblue',
                range=(0, np.percentile(ratio, 99)))
        ax.axvline(np.median(ratio), color='red', ls='--', lw=1.5,
                   label=f'Median = {np.median(ratio):.3f}')
        ax.axvline(np.mean(ratio), color='orange', ls='--', lw=1.5,
                   label=f'Mean = {np.mean(ratio):.3f}')
        ax.set_xlabel("h*R / sqrt(D)  =  L(1, chi_D) / 2")
        ax.set_ylabel("Density")
        ax.set_title("Distribution of L(1, chi_D)/2")
        ax.legend(fontsize=8)

        # (1,1): Numerical second derivative of upper boundary
        ax = axes[1, 1]
        bc_v = bc[vm]
        up_v = envelope["upper_max"][vm]
        up95 = envelope["upper_95"][vm]
        if len(bc_v) > 4:
            for arr, color, label in [(up_v, 'red', 'Max'), (up95, 'purple', '95th')]:
                dx = np.diff(bc_v)
                dy = np.diff(arr)
                d1 = dy / dx
                mid1 = 0.5 * (bc_v[:-1] + bc_v[1:])
                dx2 = np.diff(mid1)
                d2 = np.diff(d1)
                d2v = d2 / dx2
                mid2 = 0.5 * (mid1[:-1] + mid1[1:])
                ax.plot(mid2, d2v, 'o-', ms=3, color=color, alpha=0.7, label=label)
            ax.axhline(0, color='gray', ls='--', alpha=0.5)
            ax.set_xlabel("log(R)")
            ax.set_ylabel("d^2(log h)/d(log R)^2")
            ax.set_title("Numerical Second Derivative of Upper Boundary")
            ax.legend(fontsize=8)

        plt.tight_layout()
        plt.savefig(PLOT_PATH, dpi=150)
        plt.close()
        print(f"  Plot saved to {PLOT_PATH}")
        return True
    except Exception as e:
        print(f"  Plot failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print("=" * 70)
    print("  Regulator-Class Number Convexity: Real Quadratic Fields")
    print("=" * 70)

    # ----- Load data -----
    print("\n[1] Loading data...")
    fields = fetch_lmfdb_data(max_rows=200000)
    if not fields:
        fields = load_local_data()
    source = "lmfdb" if len(fields) > 5000 else "local"

    print(f"  Source: {source} ({len(fields)} fields)")
    print(f"  Disc range: [{min(f['disc'] for f in fields)}, {max(f['disc'] for f in fields)}]")
    print(f"  h range: [{min(f['h'] for f in fields)}, {max(f['h'] for f in fields)}]")
    print(f"  R range: [{min(f['R'] for f in fields):.4f}, {max(f['R'] for f in fields):.4f}]")

    fields_valid = [f for f in fields if f["h"] > 0 and f["R"] > 0]
    print(f"  Valid (h>0, R>0): {len(fields_valid)}")

    # ----- Log coordinates -----
    print("\n[2] Computing log-space coordinates...")
    log_R = np.array([math.log(f["R"]) for f in fields_valid])
    log_h = np.array([math.log(f["h"]) for f in fields_valid])

    h1_count = sum(1 for f in fields_valid if f["h"] == 1)
    print(f"  h=1 count: {h1_count} ({100*h1_count/len(fields_valid):.1f}%)")
    print(f"  log(R) range: [{log_R.min():.3f}, {log_R.max():.3f}]")
    print(f"  log(h) range: [{log_h.min():.3f}, {log_h.max():.3f}]")

    # ----- Boundary envelope -----
    print("\n[3] Computing boundary envelope (50 percentile bins)...")
    envelope = compute_envelope(log_R, log_h, n_bins=50, use_percentile=True)
    valid_mask = envelope["counts"] >= 5
    print(f"  Populated bins: {valid_mask.sum()}/50")

    # ----- Fit convexity of various boundaries -----
    print("\n[4] Fitting boundary convexity...")
    bc = envelope["bin_centers"]

    upper_max_fit = fit_boundary(bc, envelope["upper_max"], "upper_max")
    upper_95_fit = fit_boundary(bc, envelope["upper_95"], "upper_95")
    upper_99_fit = fit_boundary(bc, envelope["upper_99"], "upper_99")
    median_fit = fit_boundary(bc, envelope["median"], "median")

    for name, fit in [("Upper Max", upper_max_fit), ("Upper 95th", upper_95_fit),
                       ("Upper 99th", upper_99_fit), ("Median", median_fit)]:
        if fit:
            print(f"  {name}:")
            print(f"    Linear slope: {fit['linear']['slope']:.4f} (R²={fit['linear']['r_squared']:.4f})")
            print(f"    Quadratic convexity (2a): {fit['quadratic']['convexity_2a']:.4f} "
                  f"(R²={fit['quadratic']['r_squared']:.4f})")
            print(f"    Numerical 2nd deriv mean: {fit['numerical']['second_derivative_mean']:.4f}")
            print(f"    Geometric curvature mean: {fit['numerical']['geometric_curvature_mean']:.4f}")
            print(f"    Shape: {fit['shape']}")

    # ----- Convex hull analysis -----
    print("\n[5] Convex hull analysis...")
    hull_info = convex_hull_analysis(log_R, log_h)
    print(f"  Hull area / BBox area (bowing ratio): {hull_info['bowing_ratio']:.4f}")
    if hull_info["upper_hull_fit"]:
        print(f"  Upper hull convexity (2a): {hull_info['upper_hull_fit']['convexity_2a']:.4f}")

    # ----- Class number formula -----
    print("\n[6] Verifying h*R = sqrt(D) * L(1,chi_D) / 2...")
    formula = verify_class_number_formula(fields_valid)
    print(f"  h*R/sqrt(D) median: {formula['hR_over_sqrtD']['median']:.4f}")
    print(f"  h*R/sqrt(D) mean: {formula['hR_over_sqrtD']['mean']:.4f}")
    print(f"  log(hR) vs log(D) slope: {formula['log_hR_vs_log_D']['slope']:.4f} (expected ~0.5)")
    print(f"  R²: {formula['log_hR_vs_log_D']['r_squared']:.4f}")
    print(f"  L-value growth (log ratio vs log D): {formula['L_value_growth']['log_ratio_vs_log_D_slope']:.4f}")

    # ----- Composite convexity summary -----
    print("\n[7] Convexity summary...")
    # The main convexity parameter is the quadratic coefficient of the upper boundary
    primary_convexity = upper_max_fit["quadratic"]["convexity_2a"] if upper_max_fit else None
    p95_convexity = upper_95_fit["quadratic"]["convexity_2a"] if upper_95_fit else None
    numerical_convexity = upper_max_fit["numerical"]["second_derivative_mean"] if upper_max_fit else None

    # The upper boundary in log-log has slope ~ -1 (from h*R ~ sqrt(D))
    # The "convexity" measures deviation from this linear relationship.
    # The class number formula h*R = sqrt(D)*L(1,chi)/2 constrains (h,R) to a family
    # of hyperbolae parametrized by D. The boundary deviates from strict -1 slope
    # because L(1,chi_D) varies.

    # Absolute convexity (|2a|) for comparison with expected 1.45
    abs_convexity = abs(primary_convexity) if primary_convexity else None

    print(f"  Primary (upper max, 2a): {primary_convexity:.4f}")
    print(f"  95th percentile (2a): {p95_convexity:.4f}")
    print(f"  Numerical mean 2nd deriv: {numerical_convexity:.4f}")
    print(f"  |2a|: {abs_convexity:.4f}")
    if abs_convexity:
        print(f"  vs expected ~1.45: ratio = {abs_convexity/1.45:.3f}")

    # ----- Plot -----
    print("\n[8] Generating plot...")
    plot_ok = make_plot(fields_valid, envelope, upper_max_fit, upper_95_fit,
                        hull_info, formula)

    # ----- Assemble results -----
    elapsed = time.time() - t0

    results = {
        "task": "List2 #11: Regulator-Class Number Convexity",
        "description": (
            "Convexity of boundary envelope in (log R, log h) space for real quadratic "
            "fields. The upper boundary measures the maximum class number achievable at "
            "each regulator value, constrained by h*R = sqrt(D)*L(1,chi_D)/2."
        ),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "data": {
            "source": source,
            "n_fields": len(fields),
            "n_valid": len(fields_valid),
            "disc_range": [min(f["disc"] for f in fields), max(f["disc"] for f in fields)],
            "h_range": [min(f["h"] for f in fields_valid), max(f["h"] for f in fields_valid)],
            "R_range": [round(min(f["R"] for f in fields_valid), 6),
                        round(max(f["R"] for f in fields_valid), 6)],
            "h1_fraction": round(h1_count / len(fields_valid), 4),
        },
        "boundary_envelope": {
            "n_bins": 50,
            "bin_method": "percentile (equal count)",
            "bin_centers": [round(x, 4) for x in bc.tolist()],
            "upper_max": [round(x, 4) if not np.isnan(x) else None
                          for x in envelope["upper_max"].tolist()],
            "upper_95": [round(x, 4) if not np.isnan(x) else None
                         for x in envelope["upper_95"].tolist()],
            "median": [round(x, 4) if not np.isnan(x) else None
                       for x in envelope["median"].tolist()],
            "counts": envelope["counts"].tolist(),
        },
        "convexity": {
            "upper_max": upper_max_fit,
            "upper_95th_percentile": upper_95_fit,
            "upper_99th_percentile": upper_99_fit,
            "median": median_fit,
            "convex_hull": hull_info,
            "summary": {
                "primary_convexity_2a": primary_convexity,
                "p95_convexity_2a": p95_convexity,
                "numerical_2nd_derivative_mean": numerical_convexity,
                "boundary_shape": upper_max_fit["shape"] if upper_max_fit else "unknown",
                "upper_boundary_slope": upper_max_fit["linear"]["slope"] if upper_max_fit else None,
                "note": (
                    "The upper boundary in (log R, log h) has slope ~ -1 reflecting "
                    "the constraint h*R ~ sqrt(D). The quadratic correction 2a measures "
                    "curvature: negative = concave (bowing inward), positive = convex "
                    "(bowing outward). Concavity here means the max class number "
                    "falls faster than a power law at large R."
                ),
            },
        },
        "class_number_formula": formula,
        "plot": str(PLOT_PATH) if plot_ok else None,
        "elapsed_seconds": round(elapsed, 2),
    }

    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {OUTPUT}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
