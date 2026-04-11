"""
Frontier-2: Number Field Discriminant Scaling with Degree
=========================================================
How does the minimum discriminant of number fields scale with degree?
The Minkowski bound gives theoretical lower bounds. Measure the empirical
scaling law from 9K LMFDB number fields and compare to theory.

Analysis:
  1. Group fields by degree, compute min/median/max |disc|
  2. Fit log(min|disc|) ~ alpha * degree + c  (exponential scaling)
  3. Compare to Minkowski bound: |disc| >= (pi/4)^r2 * n^n / n!
  4. Distribution shape within each degree (log-normal vs power-law)
  5. Class number correlation with |disc| at fixed degree (Cohen-Lenstra)
  6. Discriminant gap structure within each degree

Output: nf_disc_scaling_results.json

Usage:
    python nf_disc_scaling.py
"""

import json
import time
import sys
import math
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "number_fields" / "data" / "number_fields.json"
OUT_PATH = Path(__file__).resolve().parent / "nf_disc_scaling_results.json"


def load_data():
    """Load number fields from JSON."""
    with open(DATA_PATH) as f:
        raw = json.load(f)
    fields = []
    for r in raw:
        deg = r["degree"]
        disc_abs = int(r["disc_abs"])
        class_number = int(r["class_number"])
        fields.append({
            "label": r["label"],
            "degree": deg,
            "disc_abs": disc_abs,
            "disc_sign": r["disc_sign"],
            "class_number": class_number,
            "class_group": r.get("class_group", []),
            "galois_label": r.get("galois_label", ""),
            "regulator": float(r["regulator"]) if r.get("regulator") else None,
        })
    return fields


def minkowski_bound(n):
    """
    Minkowski bound on |disc| for a degree-n number field.
    |disc| >= (pi/4)^(n/2) * n^n / n!
    (using r2 = n/2 as worst-case, i.e. totally complex).
    For totally real (r2=0), bound is n^n/n!.
    We compute both.
    """
    log_nn_over_nfact = n * math.log(n) - sum(math.log(k) for k in range(1, n + 1))
    # Totally complex: r2 = n/2
    log_bound_complex = (n / 2) * math.log(math.pi / 4) + log_nn_over_nfact
    # Totally real: r2 = 0
    log_bound_real = log_nn_over_nfact
    return {
        "degree": n,
        "log_bound_totally_real": round(log_bound_real, 6),
        "log_bound_totally_complex": round(log_bound_complex, 6),
        "bound_totally_real": round(math.exp(log_bound_real), 2),
        "bound_totally_complex": round(math.exp(log_bound_complex), 2),
    }


def degree_statistics(fields):
    """Group by degree and compute min/median/max/mean of |disc|."""
    by_degree = defaultdict(list)
    for f in fields:
        if f["degree"] >= 2:  # skip degree 1 (trivial, disc=1)
            by_degree[f["degree"]].append(f)

    results = {}
    for deg in sorted(by_degree.keys()):
        group = by_degree[deg]
        discs = sorted([f["disc_abs"] for f in group])
        log_discs = [math.log(d) for d in discs if d > 0]
        results[deg] = {
            "count": len(group),
            "min_disc": discs[0],
            "median_disc": int(np.median(discs)),
            "max_disc": discs[-1],
            "mean_disc": round(float(np.mean(discs)), 2),
            "log_min_disc": round(math.log(discs[0]), 6) if discs[0] > 0 else None,
            "log_median_disc": round(float(np.median(log_discs)), 6),
            "log_max_disc": round(math.log(discs[-1]), 6),
        }
    return results, by_degree


def fit_scaling_law(deg_stats):
    """Fit log(min|disc|) ~ alpha * degree + c."""
    degrees = []
    log_min_discs = []
    for deg, s in sorted(deg_stats.items()):
        if s["log_min_disc"] is not None and deg >= 2:
            degrees.append(deg)
            log_min_discs.append(s["log_min_disc"])

    degrees = np.array(degrees, dtype=float)
    log_min_discs = np.array(log_min_discs)

    # Linear fit: log(min|disc|) = alpha * degree + c
    slope, intercept, r_value, p_value, std_err = stats.linregress(degrees, log_min_discs)

    # Also fit log(median|disc|)
    log_med_discs = np.array([deg_stats[int(d)]["log_median_disc"] for d in degrees])
    slope_med, intercept_med, r_med, p_med, se_med = stats.linregress(degrees, log_med_discs)

    return {
        "min_disc_fit": {
            "alpha": round(slope, 6),
            "intercept": round(intercept, 6),
            "r_squared": round(r_value ** 2, 6),
            "p_value": float(f"{p_value:.2e}"),
            "std_err": round(std_err, 6),
            "interpretation": f"min|disc| ~ exp({slope:.3f} * degree + {intercept:.3f})",
            "data_points": {int(d): round(v, 4) for d, v in zip(degrees, log_min_discs)},
        },
        "median_disc_fit": {
            "alpha": round(slope_med, 6),
            "intercept": round(intercept_med, 6),
            "r_squared": round(r_med ** 2, 6),
            "interpretation": f"median|disc| ~ exp({slope_med:.3f} * degree + {intercept_med:.3f})",
        },
    }


def compare_to_minkowski(deg_stats):
    """Compare empirical min|disc| to Minkowski bound at each degree."""
    comparisons = {}
    for deg in sorted(deg_stats.keys()):
        if deg < 2:
            continue
        mink = minkowski_bound(deg)
        emp_log_min = deg_stats[deg]["log_min_disc"]
        if emp_log_min is None:
            continue

        # Ratio: empirical / theoretical
        ratio_real = round(math.exp(emp_log_min - mink["log_bound_totally_real"]), 4)
        ratio_complex = round(math.exp(emp_log_min - mink["log_bound_totally_complex"]), 4)
        gap_real = round(emp_log_min - mink["log_bound_totally_real"], 6)
        gap_complex = round(emp_log_min - mink["log_bound_totally_complex"], 6)

        comparisons[deg] = {
            "empirical_log_min_disc": round(emp_log_min, 6),
            "minkowski_log_bound_real": mink["log_bound_totally_real"],
            "minkowski_log_bound_complex": mink["log_bound_totally_complex"],
            "log_gap_vs_real_bound": gap_real,
            "log_gap_vs_complex_bound": gap_complex,
            "ratio_empirical_over_real_bound": ratio_real,
            "ratio_empirical_over_complex_bound": ratio_complex,
            "minkowski_tight": ratio_real < 10,  # within one order of magnitude
        }
    return comparisons


def distribution_shape(by_degree):
    """Test whether within-degree discriminant distribution is log-normal or power-law."""
    results = {}
    for deg in sorted(by_degree.keys()):
        if deg < 2:
            continue
        discs = np.array([f["disc_abs"] for f in by_degree[deg]], dtype=float)
        if len(discs) < 30:
            results[deg] = {
                "n": len(discs),
                "test": "insufficient_data",
                "note": f"Only {len(discs)} fields at degree {deg}; need >= 30 for distribution test"
            }
            continue

        log_discs = np.log(discs)

        # Test log-normality: Shapiro-Wilk on log(disc)
        # For large N, use D'Agostino-Pearson
        if len(log_discs) > 5000:
            stat_ln, p_ln = stats.normaltest(log_discs)
            test_name = "dagostino_pearson"
        else:
            stat_ln, p_ln = stats.shapiro(log_discs)
            test_name = "shapiro_wilk"

        # Skewness and kurtosis of log(disc)
        skew = float(stats.skew(log_discs))
        kurt = float(stats.kurtosis(log_discs))

        # Power-law test: fit log(disc) ~ Pareto
        # If log-normal rejected, check if power-law fits better
        # Simple: fit exponent via MLE for Pareto
        xmin = discs.min()
        if xmin > 0:
            alpha_pareto = len(discs) / np.sum(np.log(discs / xmin))
        else:
            alpha_pareto = None

        results[deg] = {
            "n": len(discs),
            "log_normal_test": test_name,
            "log_normal_statistic": round(float(stat_ln), 6),
            "log_normal_p_value": float(f"{p_ln:.4e}"),
            "log_normal_rejected_at_005": p_ln < 0.05,
            "log_disc_skewness": round(skew, 4),
            "log_disc_kurtosis": round(kurt, 4),
            "pareto_alpha_mle": round(float(alpha_pareto), 4) if alpha_pareto else None,
            "shape_verdict": (
                "consistent_with_log_normal" if p_ln >= 0.05
                else "right_skewed" if skew > 1
                else "not_log_normal"
            ),
        }
    return results


def class_number_correlation(by_degree):
    """Test correlation between class_number and |disc| at fixed degree."""
    results = {}
    for deg in sorted(by_degree.keys()):
        if deg < 2:
            continue
        group = by_degree[deg]
        discs = np.array([f["disc_abs"] for f in group], dtype=float)
        class_nums = np.array([f["class_number"] for f in group], dtype=float)

        if len(discs) < 10:
            results[deg] = {"n": len(discs), "test": "insufficient_data"}
            continue

        # Spearman rank correlation (robust to non-normality)
        # Guard against constant arrays
        if np.std(class_nums) == 0 or np.std(discs) == 0:
            results[deg] = {
                "n": len(discs),
                "spearman_rho": None,
                "spearman_p_value": None,
                "significant_at_005": False,
                "log_log_spearman_rho": None,
                "fraction_class_number_1": round(float(np.mean(class_nums == 1)), 4),
                "median_class_number": int(np.median(class_nums)),
                "max_class_number": int(class_nums.max()),
                "cohen_lenstra_note": f"All class numbers identical (={int(class_nums[0])})",
            }
            continue
        rho, p_rho = stats.spearmanr(discs, class_nums)

        # Also log-log correlation
        log_d = np.log(discs[discs > 0])
        log_h = np.log(class_nums[(discs > 0) & (class_nums > 0)])
        min_len = min(len(log_d), len(log_h))
        if min_len > 10:
            rho_log, p_log = stats.spearmanr(log_d[:min_len], log_h[:min_len])
        else:
            rho_log, p_log = None, None

        # Fraction with class number 1 (Cohen-Lenstra predicts this)
        frac_h1 = round(float(np.mean(class_nums == 1)), 4)

        # Median class number
        median_h = int(np.median(class_nums))

        results[deg] = {
            "n": len(discs),
            "spearman_rho": round(float(rho), 6),
            "spearman_p_value": float(f"{p_rho:.4e}"),
            "significant_at_005": p_rho < 0.05,
            "log_log_spearman_rho": round(float(rho_log), 6) if rho_log is not None else None,
            "fraction_class_number_1": frac_h1,
            "median_class_number": median_h,
            "max_class_number": int(class_nums.max()),
            "cohen_lenstra_note": (
                "Positive correlation expected: h grows with |disc|^(1/2) on average"
                if deg == 2 else
                "Cohen-Lenstra predicts class group distribution depends on degree parity"
            ),
        }
    return results


def discriminant_gaps(by_degree):
    """Measure gaps between consecutive discriminants within each degree."""
    results = {}
    for deg in sorted(by_degree.keys()):
        if deg < 2:
            continue
        discs = sorted(set(f["disc_abs"] for f in by_degree[deg]))
        if len(discs) < 3:
            results[deg] = {"n_unique_discs": len(discs), "test": "insufficient_data"}
            continue

        discs = np.array(discs, dtype=float)
        gaps = np.diff(discs)

        # Normalized gaps: gap / mean_spacing
        mean_spacing = float(np.mean(gaps))
        norm_gaps = gaps / mean_spacing if mean_spacing > 0 else gaps

        # Compare to Poisson (random) expectation: gaps ~ Exponential(1)
        # vs GUE (repulsion): gaps ~ 0 near zero
        # KS test against exponential
        ks_stat, ks_p = stats.kstest(norm_gaps, 'expon', args=(0, 1))

        # Gap statistics
        results[deg] = {
            "n_unique_discs": len(discs),
            "n_gaps": len(gaps),
            "min_gap": int(gaps.min()),
            "median_gap": int(np.median(gaps)),
            "max_gap": int(gaps.max()),
            "mean_gap": round(float(np.mean(gaps)), 2),
            "std_gap": round(float(np.std(gaps)), 2),
            "cv_gap": round(float(np.std(gaps) / np.mean(gaps)), 4) if np.mean(gaps) > 0 else None,
            "ks_vs_exponential_stat": round(float(ks_stat), 6),
            "ks_vs_exponential_p": float(f"{ks_p:.4e}"),
            "gap_distribution": (
                "consistent_with_poisson" if ks_p >= 0.05
                else "structured_gaps"
            ),
            "smallest_5_gaps": [int(g) for g in sorted(gaps)[:5]],
            "largest_5_gaps": [int(g) for g in sorted(gaps)[-5:]],
        }
    return results


def odlyzko_bounds():
    """
    Known Odlyzko lower bounds on root discriminants (|disc|^{1/n}).
    These are tighter than Minkowski for large n.
    Asymptotic: rd >= 4*pi*e^gamma ~ 22.3816... (GRH)
               rd >= 4*pi*e^{gamma+1} ~ 60.84... (unconditional, Odlyzko)
    """
    # GRH bound: 4*pi*exp(gamma) where gamma = Euler-Mascheroni
    gamma = 0.5772156649
    grh_asymptotic = 4 * math.pi * math.exp(gamma)
    unconditional_asymptotic = 4 * math.pi * math.exp(gamma + 1)
    return {
        "grh_asymptotic_root_disc": round(grh_asymptotic, 6),
        "unconditional_asymptotic_root_disc": round(unconditional_asymptotic, 6),
        "note": "Odlyzko: rd = |disc|^{1/n} -> constant as n -> infinity. "
                "GRH bound ~ 22.38, unconditional ~ 60.84",
    }


def root_discriminant_analysis(by_degree, deg_stats):
    """Analyze root discriminant rd = |disc|^{1/n} across degrees."""
    results = {}
    for deg in sorted(by_degree.keys()):
        if deg < 2:
            continue
        discs = np.array([f["disc_abs"] for f in by_degree[deg]], dtype=float)
        root_discs = discs ** (1.0 / deg)

        results[deg] = {
            "min_root_disc": round(float(root_discs.min()), 6),
            "median_root_disc": round(float(np.median(root_discs)), 6),
            "mean_root_disc": round(float(np.mean(root_discs)), 6),
            "max_root_disc": round(float(root_discs.max()), 6),
        }

    # Fit: does min root discriminant converge to Odlyzko bound?
    degs = sorted(results.keys())
    min_rds = [results[d]["min_root_disc"] for d in degs]
    results["trend"] = {
        "degrees": degs,
        "min_root_discs": min_rds,
        "increasing": all(min_rds[i] <= min_rds[i + 1] for i in range(len(min_rds) - 1)),
        "note": "Root discriminant should increase toward Odlyzko bound as degree grows",
    }
    return results


def main():
    t0 = time.time()
    print("=" * 70)
    print("Number Field Discriminant Scaling with Degree")
    print("=" * 70)

    # Load data
    fields = load_data()
    print(f"Loaded {len(fields)} number fields")

    # 1. Degree statistics
    print("\n--- Degree Statistics ---")
    deg_stats, by_degree = degree_statistics(fields)
    for deg, s in sorted(deg_stats.items()):
        print(f"  degree {deg}: n={s['count']:>5}, "
              f"min|disc|={s['min_disc']:>12}, "
              f"median={s['median_disc']:>12}, "
              f"max={s['max_disc']:>12}, "
              f"log(min)={s['log_min_disc']:.3f}")

    # 2. Scaling law fit
    print("\n--- Scaling Law: log(min|disc|) ~ alpha * degree + c ---")
    scaling = fit_scaling_law(deg_stats)
    sf = scaling["min_disc_fit"]
    print(f"  alpha  = {sf['alpha']:.4f} +/- {sf['std_err']:.4f}")
    print(f"  interc = {sf['intercept']:.4f}")
    print(f"  R^2    = {sf['r_squared']:.4f}")
    print(f"  => {sf['interpretation']}")
    sf2 = scaling["median_disc_fit"]
    print(f"  median: alpha = {sf2['alpha']:.4f}, R^2 = {sf2['r_squared']:.4f}")

    # 3. Minkowski comparison
    print("\n--- Minkowski Bound Comparison ---")
    mink_comp = compare_to_minkowski(deg_stats)
    for deg, c in sorted(mink_comp.items()):
        print(f"  degree {deg}: empirical/real_bound = {c['ratio_empirical_over_real_bound']:>10.2f}, "
              f"empirical/complex_bound = {c['ratio_empirical_over_complex_bound']:>10.2f}, "
              f"tight={c['minkowski_tight']}")

    # 4. Odlyzko bounds + root discriminant
    print("\n--- Root Discriminant Analysis ---")
    odlyzko = odlyzko_bounds()
    print(f"  Odlyzko GRH asymptotic: {odlyzko['grh_asymptotic_root_disc']:.4f}")
    print(f"  Odlyzko unconditional:  {odlyzko['unconditional_asymptotic_root_disc']:.4f}")
    root_disc = root_discriminant_analysis(by_degree, deg_stats)
    for deg in sorted(k for k in root_disc.keys() if isinstance(k, int)):
        rd = root_disc[deg]
        print(f"  degree {deg}: min rd = {rd['min_root_disc']:.4f}, "
              f"median rd = {rd['median_root_disc']:.4f}")

    # 5. Distribution shape
    print("\n--- Within-Degree Distribution Shape ---")
    dist_shape = distribution_shape(by_degree)
    for deg, r in sorted(dist_shape.items()):
        if r.get("test") == "insufficient_data":
            print(f"  degree {deg}: insufficient data ({r['n']} fields)")
        else:
            print(f"  degree {deg}: {r['shape_verdict']} "
                  f"(p={r['log_normal_p_value']:.2e}, "
                  f"skew={r['log_disc_skewness']:.2f}, "
                  f"kurt={r['log_disc_kurtosis']:.2f})")

    # 6. Class number correlation
    print("\n--- Class Number vs |disc| (Cohen-Lenstra) ---")
    class_corr = class_number_correlation(by_degree)
    for deg, r in sorted(class_corr.items()):
        if r.get("test") == "insufficient_data":
            print(f"  degree {deg}: insufficient data")
        elif r["spearman_rho"] is None:
            print(f"  degree {deg}: constant class number, "
                  f"frac(h=1)={r['fraction_class_number_1']:.3f}, "
                  f"median(h)={r['median_class_number']}")
        else:
            sig = "*" if r["significant_at_005"] else ""
            print(f"  degree {deg}: rho={r['spearman_rho']:+.4f}{sig}, "
                  f"frac(h=1)={r['fraction_class_number_1']:.3f}, "
                  f"median(h)={r['median_class_number']}")

    # 7. Discriminant gaps
    print("\n--- Discriminant Gap Structure ---")
    gap_results = discriminant_gaps(by_degree)
    for deg, r in sorted(gap_results.items()):
        if r.get("test") == "insufficient_data":
            print(f"  degree {deg}: insufficient data")
        else:
            print(f"  degree {deg}: n_unique={r['n_unique_discs']}, "
                  f"min_gap={r['min_gap']}, median_gap={r['median_gap']}, "
                  f"CV={r['cv_gap']:.2f}, {r['gap_distribution']}")

    # Assemble results
    elapsed = round(time.time() - t0, 2)
    results = {
        "analysis": "Number Field Discriminant Scaling with Degree",
        "data_source": str(DATA_PATH),
        "n_fields": len(fields),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": elapsed,
        "degree_statistics": {str(k): v for k, v in deg_stats.items()},
        "scaling_law_fit": scaling,
        "minkowski_comparison": {str(k): v for k, v in mink_comp.items()},
        "odlyzko_bounds": odlyzko,
        "root_discriminant": {str(k): v for k, v in root_disc.items()},
        "distribution_shape": {str(k): v for k, v in dist_shape.items()},
        "class_number_correlation": {str(k): v for k, v in class_corr.items()},
        "discriminant_gaps": {str(k): v for k, v in gap_results.items()},
        "summary": {},  # filled below
    }

    # Build summary
    summary = {
        "scaling_exponent_alpha": sf["alpha"],
        "scaling_exponent_std_err": sf["std_err"],
        "scaling_r_squared": sf["r_squared"],
        "interpretation": (
            f"Minimum discriminant scales as exp({sf['alpha']:.3f} * degree). "
            f"Root discriminant increases with degree toward Odlyzko bound ({odlyzko['grh_asymptotic_root_disc']:.2f} GRH). "
        ),
        "minkowski_tightness": {
            str(deg): mink_comp[deg]["ratio_empirical_over_real_bound"]
            for deg in sorted(mink_comp.keys())
        },
        "distribution_verdicts": {
            str(deg): dist_shape[deg].get("shape_verdict", "insufficient_data")
            for deg in sorted(dist_shape.keys())
        },
        "class_number_correlations": {
            str(deg): {
                "rho": class_corr[deg].get("spearman_rho"),
                "significant": class_corr[deg].get("significant_at_005"),
            }
            for deg in sorted(class_corr.keys())
            if class_corr[deg].get("spearman_rho") is not None
        },
        "gap_structure": {
            str(deg): gap_results[deg].get("gap_distribution", "insufficient_data")
            for deg in sorted(gap_results.keys())
        },
    }
    results["summary"] = summary

    # Save (handle numpy types)
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")

    return results


if __name__ == "__main__":
    main()
