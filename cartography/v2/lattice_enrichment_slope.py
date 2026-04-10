"""
Enrichment Slope Inversion for Lattice Packings
=================================================
Frontier2 Part2 #18

The enrichment slope = 0.044*rank^2 - 0.242 was measured on genus-2 curves.
Does the same relationship hold for LATTICES?

Method:
1. Load 39,293 lattices from LMFDB lat_lattices dump.
2. Group by dimension (the lattice analogue of "rank").
3. For each dimension group with 50+ lattices, compute within-group
   mod-p fingerprint enrichment at p=2,3,5,7,11 using theta series
   first 20 terms.
4. Compute the enrichment slope (enrichment vs p) per dimension.
5. Fit slope(dim) and compare to 0.044*dim^2 - 0.242.

Enrichment = within-group match rate / random baseline match rate
where match = two lattices share the same mod-p fingerprint on
first 20 theta-series coefficients.
"""

import json
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
LATTICE_FILE = ROOT / "cartography" / "lmfdb_dump" / "lat_lattices.json"
OUT_FILE = Path(__file__).with_name("lattice_enrichment_slope_results.json")

PRIMES = [2, 3, 5, 7, 11]
FP_LEN = 20       # fingerprint window: first 20 theta-series terms
MIN_GROUP = 50     # minimum group size
MAX_PAIRS = 50000  # max pairs to sample per group (for speed)

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# Fingerprinting
# ---------------------------------------------------------------------------
def mod_p_fingerprint(theta_series, p, length=FP_LEN):
    """Compute mod-p fingerprint on first `length` theta-series coefficients."""
    usable = theta_series[:length]
    if len(usable) < length:
        return None
    return tuple(t % p for t in usable)


# ---------------------------------------------------------------------------
# Within-group match rate
# ---------------------------------------------------------------------------
def within_group_match_rate(fingerprints, max_pairs=MAX_PAIRS):
    """
    Compute fraction of pairs that share the same fingerprint.
    If group is large, subsample pairs.
    """
    n = len(fingerprints)
    if n < 2:
        return 0.0, 0

    n_total_pairs = n * (n - 1) // 2

    if n_total_pairs <= max_pairs:
        # Enumerate all pairs
        matches = 0
        total = 0
        for i in range(n):
            for j in range(i + 1, n):
                if fingerprints[i] is not None and fingerprints[j] is not None:
                    total += 1
                    if fingerprints[i] == fingerprints[j]:
                        matches += 1
        return matches / total if total > 0 else 0.0, total
    else:
        # Subsample
        indices = list(range(n))
        matches = 0
        total = 0
        for _ in range(max_pairs):
            i, j = random.sample(indices, 2)
            if fingerprints[i] is not None and fingerprints[j] is not None:
                total += 1
                if fingerprints[i] == fingerprints[j]:
                    matches += 1
        return matches / total if total > 0 else 0.0, total


def random_baseline_match_rate(all_fingerprints, max_pairs=MAX_PAIRS):
    """
    Compute match rate across ALL lattices (random baseline).
    Subsample for speed.
    """
    n = len(all_fingerprints)
    if n < 2:
        return 0.0, 0

    matches = 0
    total = 0
    indices = list(range(n))
    for _ in range(max_pairs):
        i, j = random.sample(indices, 2)
        if all_fingerprints[i] is not None and all_fingerprints[j] is not None:
            total += 1
            if all_fingerprints[i] == all_fingerprints[j]:
                matches += 1
    return matches / total if total > 0 else 0.0, total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("Enrichment Slope Inversion for Lattice Packings")
    print("=" * 70)

    # Load data
    print(f"\nLoading lattices from {LATTICE_FILE}...")
    with open(LATTICE_FILE) as f:
        data = json.load(f)

    records = data["records"]
    print(f"Loaded {len(records)} lattices")

    # Group by dimension
    dim_groups = defaultdict(list)
    for r in records:
        dim = r["dim"]
        ts = r.get("theta_series")
        if ts and len(ts) >= FP_LEN:
            dim_groups[dim].append(ts)

    print(f"\nDimension groups:")
    eligible_dims = []
    for d in sorted(dim_groups.keys()):
        n = len(dim_groups[d])
        flag = " [ELIGIBLE]" if n >= MIN_GROUP else ""
        print(f"  dim={d}: {n} lattices{flag}")
        if n >= MIN_GROUP:
            eligible_dims.append(d)

    print(f"\nEligible dimensions (>={MIN_GROUP} lattices): {eligible_dims}")

    # ---------------------------------------------------------------------------
    # Compute enrichment per dimension per prime
    # ---------------------------------------------------------------------------
    results_by_dim = {}

    for dim in eligible_dims:
        theta_list = dim_groups[dim]
        n_lattices = len(theta_list)
        print(f"\n{'='*50}")
        print(f"Dimension {dim}: {n_lattices} lattices")
        print(f"{'='*50}")

        dim_result = {
            "dim": dim,
            "n_lattices": n_lattices,
            "enrichment_by_prime": {},
        }

        for p in PRIMES:
            # Compute fingerprints for this group
            fps_group = [mod_p_fingerprint(ts, p) for ts in theta_list]
            valid_fps = [fp for fp in fps_group if fp is not None]

            # Within-group match rate
            within_rate, within_pairs = within_group_match_rate(fps_group)

            # Random baseline: sample from ALL lattices at this prime
            all_theta = []
            for d2 in dim_groups:
                all_theta.extend(dim_groups[d2])
            all_fps = [mod_p_fingerprint(ts, p) for ts in all_theta]
            random_rate, random_pairs = random_baseline_match_rate(all_fps)

            # Enrichment ratio
            if random_rate > 0:
                enrichment = within_rate / random_rate
            else:
                # Use Laplace smoothing
                enrichment = within_rate * (random_pairs + 1) if within_rate > 0 else 1.0

            dim_result["enrichment_by_prime"][str(p)] = {
                "within_rate": round(within_rate, 8),
                "within_pairs": within_pairs,
                "random_rate": round(random_rate, 8),
                "random_pairs": random_pairs,
                "enrichment": round(enrichment, 6),
                "n_valid_fps": len(valid_fps),
                "n_distinct_fps": len(set(valid_fps)),
            }

            print(f"  p={p:2d}: within={within_rate:.6f} random={random_rate:.6f} "
                  f"enrichment={enrichment:.4f} (distinct fps: {len(set(valid_fps))})")

        results_by_dim[str(dim)] = dim_result

    # ---------------------------------------------------------------------------
    # Compute enrichment slope per dimension
    # enrichment_slope = slope of linear fit: enrichment(p) vs p
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Enrichment Slopes (enrichment vs prime)")
    print(f"{'='*70}")

    slope_data = []
    for dim in eligible_dims:
        dr = results_by_dim[str(dim)]
        primes_arr = []
        enrich_arr = []
        for p in PRIMES:
            e = dr["enrichment_by_prime"][str(p)]["enrichment"]
            primes_arr.append(p)
            enrich_arr.append(e)

        primes_arr = np.array(primes_arr, dtype=float)
        enrich_arr = np.array(enrich_arr, dtype=float)

        # Linear fit: enrichment = slope * p + intercept
        if len(primes_arr) >= 2:
            slope, intercept, r_value, p_value, std_err = sp_stats.linregress(
                primes_arr, enrich_arr
            )
        else:
            slope = intercept = r_value = p_value = std_err = 0.0

        # Also fit log(enrichment) vs log(p) for power law
        log_p = np.log(primes_arr)
        log_e = np.log(np.maximum(enrich_arr, 1e-10))
        if len(log_p) >= 2 and np.all(enrich_arr > 0):
            alpha, log_A, r_pow, p_pow, _ = sp_stats.linregress(log_p, log_e)
            A_pow = np.exp(log_A)
        else:
            alpha = log_A = r_pow = p_pow = A_pow = 0.0

        entry = {
            "dim": dim,
            "enrichment_slope": round(float(slope), 6),
            "enrichment_intercept": round(float(intercept), 6),
            "r_squared_linear": round(float(r_value**2), 6),
            "p_value_linear": float(p_value),
            "std_err": round(float(std_err), 6),
            "power_law_alpha": round(float(alpha), 6),
            "power_law_A": round(float(A_pow), 6),
            "r_squared_power": round(float(r_pow**2), 6),
            "enrichments": {str(p): round(e, 6) for p, e in zip(PRIMES, enrich_arr)},
        }
        slope_data.append(entry)
        dr["slope_fit"] = entry

        # Predicted slope from genus-2 formula
        predicted = 0.044 * dim**2 - 0.242
        diff = float(slope) - predicted

        print(f"  dim={dim}: slope={slope:+.6f} (predicted={predicted:+.4f}, "
              f"diff={diff:+.6f}) R²={r_value**2:.4f}")

    # ---------------------------------------------------------------------------
    # Fit slope(dim) relationship
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Fitting slope(dim) relationship")
    print(f"{'='*70}")

    dims_arr = np.array([s["dim"] for s in slope_data], dtype=float)
    slopes_arr = np.array([s["enrichment_slope"] for s in slope_data], dtype=float)

    fit_results = {}

    # Linear: slope = a * dim + b
    if len(dims_arr) >= 2:
        a_lin, b_lin, r_lin, p_lin, se_lin = sp_stats.linregress(dims_arr, slopes_arr)
        fit_results["linear"] = {
            "formula": f"slope = {a_lin:.6f} * dim + {b_lin:.6f}",
            "a": round(float(a_lin), 6),
            "b": round(float(b_lin), 6),
            "r_squared": round(float(r_lin**2), 6),
            "p_value": float(p_lin),
        }
        print(f"  Linear: slope = {a_lin:.6f}*dim + {b_lin:.6f} (R²={r_lin**2:.4f})")

    # Quadratic: slope = a * dim^2 + b * dim + c
    if len(dims_arr) >= 3:
        coeffs_q = np.polyfit(dims_arr, slopes_arr, 2)
        y_pred_q = np.polyval(coeffs_q, dims_arr)
        ss_res = np.sum((slopes_arr - y_pred_q)**2)
        ss_tot = np.sum((slopes_arr - np.mean(slopes_arr))**2)
        r2_q = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        fit_results["quadratic"] = {
            "formula": f"slope = {coeffs_q[0]:.6f}*dim² + {coeffs_q[1]:.6f}*dim + {coeffs_q[2]:.6f}",
            "a": round(float(coeffs_q[0]), 6),
            "b": round(float(coeffs_q[1]), 6),
            "c": round(float(coeffs_q[2]), 6),
            "r_squared": round(float(r2_q), 6),
        }
        print(f"  Quadratic: slope = {coeffs_q[0]:.6f}*dim² + {coeffs_q[1]:.6f}*dim + {coeffs_q[2]:.6f} (R²={r2_q:.4f})")

    # Power law: slope = A * dim^alpha
    if len(dims_arr) >= 2 and np.all(slopes_arr > 0):
        log_d = np.log(dims_arr)
        log_s = np.log(slopes_arr)
        alpha_d, log_A_d, r_d, p_d, _ = sp_stats.linregress(log_d, log_s)
        A_d = np.exp(log_A_d)
        fit_results["power_law"] = {
            "formula": f"slope = {A_d:.6f} * dim^{alpha_d:.4f}",
            "A": round(float(A_d), 6),
            "alpha": round(float(alpha_d), 4),
            "r_squared": round(float(r_d**2), 6),
            "p_value": float(p_d),
        }
        print(f"  Power law: slope = {A_d:.6f} * dim^{alpha_d:.4f} (R²={r_d**2:.4f})")
    elif len(dims_arr) >= 2:
        # Some slopes may be negative, try with absolute values
        abs_slopes = np.abs(slopes_arr)
        signs = np.sign(slopes_arr)
        if np.all(abs_slopes > 0):
            log_d = np.log(dims_arr)
            log_s = np.log(abs_slopes)
            alpha_d, log_A_d, r_d, p_d, _ = sp_stats.linregress(log_d, log_s)
            A_d = np.exp(log_A_d)
            dominant_sign = "positive" if np.sum(signs > 0) > np.sum(signs < 0) else "negative"
            fit_results["power_law_abs"] = {
                "formula": f"|slope| = {A_d:.6f} * dim^{alpha_d:.4f} (mostly {dominant_sign})",
                "A": round(float(A_d), 6),
                "alpha": round(float(alpha_d), 4),
                "r_squared": round(float(r_d**2), 6),
                "dominant_sign": dominant_sign,
            }
            print(f"  Power law (|slope|): {A_d:.6f} * dim^{alpha_d:.4f} "
                  f"(R²={r_d**2:.4f}, mostly {dominant_sign})")

    # ---------------------------------------------------------------------------
    # Test genus-2 formula: slope = 0.044*dim^2 - 0.242
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Testing genus-2 formula: slope = 0.044*dim² - 0.242")
    print(f"{'='*70}")

    predicted_slopes = 0.044 * dims_arr**2 - 0.242
    residuals = slopes_arr - predicted_slopes
    ss_res_g2 = np.sum(residuals**2)
    ss_tot_g2 = np.sum((slopes_arr - np.mean(slopes_arr))**2)
    r2_g2 = 1 - ss_res_g2 / ss_tot_g2 if ss_tot_g2 > 0 else 0
    rmse_g2 = np.sqrt(np.mean(residuals**2))
    mae_g2 = np.mean(np.abs(residuals))

    genus2_test = {
        "formula": "slope = 0.044*dim² - 0.242",
        "r_squared": round(float(r2_g2), 6),
        "rmse": round(float(rmse_g2), 6),
        "mae": round(float(mae_g2), 6),
        "per_dim_comparison": [],
    }

    for i, dim in enumerate(dims_arr):
        genus2_test["per_dim_comparison"].append({
            "dim": int(dim),
            "observed_slope": round(float(slopes_arr[i]), 6),
            "predicted_slope": round(float(predicted_slopes[i]), 6),
            "residual": round(float(residuals[i]), 6),
        })
        print(f"  dim={int(dim):2d}: observed={slopes_arr[i]:+.6f} "
              f"predicted={predicted_slopes[i]:+.4f} "
              f"residual={residuals[i]:+.6f}")

    print(f"\n  Genus-2 formula fit: R²={r2_g2:.4f}, RMSE={rmse_g2:.6f}, MAE={mae_g2:.6f}")

    # ---------------------------------------------------------------------------
    # Bootstrap confidence intervals on slopes
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Bootstrap Confidence Intervals on Enrichment Slopes")
    print(f"{'='*70}")

    N_BOOT = 1000
    bootstrap_results = {}

    for dim in eligible_dims:
        theta_list = dim_groups[dim]
        n_lat = len(theta_list)

        boot_slopes = []
        for b in range(N_BOOT):
            # Resample lattices within this dimension
            boot_indices = random.choices(range(n_lat), k=n_lat)
            boot_theta = [theta_list[i] for i in boot_indices]

            # Compute enrichment at each prime (within-group only, skip random baseline for speed)
            boot_enrichments = []
            for p in PRIMES:
                fps = [mod_p_fingerprint(ts, p) for ts in boot_theta]
                # Count distinct fingerprints
                valid = [fp for fp in fps if fp is not None]
                if len(valid) < 2:
                    boot_enrichments.append(1.0)
                    continue
                fp_counts = Counter(valid)
                n_valid = len(valid)
                n_distinct = len(fp_counts)
                # Expected under uniform: n_valid / n_distinct
                expected = n_valid / n_distinct if n_distinct > 0 else 1.0
                # Average bucket size for a random element
                avg_bucket = sum(c * c for c in fp_counts.values()) / n_valid
                enrichment = avg_bucket / expected if expected > 0 else 1.0
                boot_enrichments.append(enrichment)

            # Fit slope
            if len(boot_enrichments) == len(PRIMES):
                p_arr = np.array(PRIMES, dtype=float)
                e_arr = np.array(boot_enrichments, dtype=float)
                sl, _, _, _, _ = sp_stats.linregress(p_arr, e_arr)
                boot_slopes.append(float(sl))

        if boot_slopes:
            ci_low = np.percentile(boot_slopes, 2.5)
            ci_high = np.percentile(boot_slopes, 97.5)
            boot_mean = np.mean(boot_slopes)
            bootstrap_results[str(dim)] = {
                "mean": round(float(boot_mean), 6),
                "ci_2.5": round(float(ci_low), 6),
                "ci_97.5": round(float(ci_high), 6),
                "std": round(float(np.std(boot_slopes)), 6),
            }
            print(f"  dim={dim}: slope={boot_mean:.6f} CI=[{ci_low:.6f}, {ci_high:.6f}]")

    # ---------------------------------------------------------------------------
    # Verdict
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("VERDICT")
    print(f"{'='*70}")

    # Is the genus-2 formula universal?
    if r2_g2 > 0.8:
        verdict = "CONFIRMED: genus-2 formula slope=0.044*dim²-0.242 transfers to lattices"
        universal = True
    elif r2_g2 > 0.3:
        verdict = "PARTIAL: qualitative trend matches but coefficients differ"
        universal = False
    else:
        verdict = "REJECTED: genus-2 formula does NOT hold for lattices"
        universal = False

    # What formula does hold?
    best_fit_name = None
    best_r2 = -1
    for name, res in fit_results.items():
        r2 = res.get("r_squared", 0)
        if r2 > best_r2:
            best_r2 = r2
            best_fit_name = name

    if best_fit_name:
        best_formula = fit_results[best_fit_name].get("formula", "N/A")
        print(f"  Best lattice-specific fit: {best_formula} (R²={best_r2:.4f})")
    else:
        best_formula = "N/A"

    print(f"  Genus-2 formula R² on lattices: {r2_g2:.4f}")
    print(f"  Verdict: {verdict}")

    # Are enrichment slopes even monotonically increasing with dim?
    monotonic = all(slopes_arr[i] <= slopes_arr[i+1] for i in range(len(slopes_arr)-1))
    print(f"  Slopes monotonically increasing with dim: {monotonic}")

    # ---------------------------------------------------------------------------
    # Save results
    # ---------------------------------------------------------------------------
    output = {
        "experiment": "Enrichment Slope Inversion for Lattice Packings",
        "timestamp": datetime.now().isoformat(),
        "data_source": "LMFDB lat_lattices (39,293 lattices)",
        "method": {
            "fingerprint": f"mod-p on first {FP_LEN} theta-series coefficients",
            "primes": PRIMES,
            "enrichment": "within-group match rate / random baseline match rate",
            "slope": "linear regression of enrichment vs prime",
            "min_group_size": MIN_GROUP,
            "max_pairs_sampled": MAX_PAIRS,
            "bootstrap_iterations": N_BOOT,
        },
        "eligible_dimensions": eligible_dims,
        "results_by_dimension": results_by_dim,
        "slope_fits": slope_data,
        "slope_vs_dim_models": fit_results,
        "genus2_formula_test": genus2_test,
        "bootstrap_confidence": bootstrap_results,
        "verdict": {
            "genus2_formula_holds": universal,
            "genus2_r_squared": round(float(r2_g2), 6),
            "best_lattice_fit": best_fit_name,
            "best_lattice_r_squared": round(float(best_r2), 6),
            "best_lattice_formula": best_formula,
            "slopes_monotonic_with_dim": bool(monotonic),
            "summary": verdict,
        },
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {OUT_FILE}")
    return output


if __name__ == "__main__":
    main()
