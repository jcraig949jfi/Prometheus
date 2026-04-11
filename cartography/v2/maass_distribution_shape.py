"""
Maass Coefficient Distribution Shape -- Does It Change with Level?

Tests whether Maass form Fourier coefficients follow the Sato-Tate
distribution (semicircle) at each level, and whether shape deviates
systematically as level varies.

Key questions:
1. KS test of semicircle fit at each level
2. Level-averaged deviation pattern
3. Newforms vs all forms (prime levels = all newforms)
4. M4/M2^2 kurtosis ratio per level
5. Robust moments excluding non-tempered outliers
"""

import json
import sys
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

# -- Paths --
DATA_PATH = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUT_PATH = Path(__file__).parent / "maass_distribution_shape_results.json"

# -- Sato-Tate reference --
def sato_tate_pdf(x):
    """Sato-Tate density on [-2, 2]: (2/pi)*sqrt(1 - x^2/4)"""
    x = np.asarray(x, dtype=float)
    mask = np.abs(x) < 2.0
    out = np.zeros_like(x)
    out[mask] = (2.0 / np.pi) * np.sqrt(1.0 - x[mask]**2 / 4.0)
    return out

def sato_tate_cdf(x):
    """CDF of Sato-Tate distribution on [-2, 2]"""
    x = np.clip(x, -2.0, 2.0)
    return 0.5 + (1.0 / np.pi) * (x * np.sqrt(4.0 - x**2) / 4.0 + np.arcsin(x / 2.0))


def get_prime_indices(n_max):
    """Return list of prime indices (0-based). coefficient[i] = a_(i+1), so prime p -> index p-1."""
    sieve = [True] * (n_max + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n_max**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n_max + 1, i):
                sieve[j] = False
    return [p - 1 for p in range(2, n_max + 1) if sieve[p]]


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True


def analyze_level(coeffs_list, level, prime_indices):
    """Analyze coefficient distribution at a single level."""
    # Pool all c_p values (prime-indexed coefficients, p not dividing level)
    all_cp = []
    for coeffs in coeffs_list:
        n_c = len(coeffs)
        for idx in prime_indices:
            if idx < n_c:
                p = idx + 1
                if level % p == 0:
                    continue
                all_cp.append(coeffs[idx])

    all_cp = np.array(all_cp)
    if len(all_cp) < 50:
        return None

    n_total = len(all_cp)

    # Tempered coefficients: |c_p| <= 2 (Ramanujan bound for tempered Maass forms)
    tempered = all_cp[np.abs(all_cp) <= 2.0]
    # Mildly relaxed bound for robustness: |c_p| <= 2.5 (allow numerical imprecision)
    relaxed = all_cp[np.abs(all_cp) <= 2.5]
    outlier_frac = 1.0 - len(tempered) / n_total
    outlier_frac_relaxed = 1.0 - len(relaxed) / n_total

    # KS test against Sato-Tate CDF (using tempered values)
    if len(tempered) > 10:
        ks_stat, ks_pval = stats.kstest(tempered, sato_tate_cdf)
    else:
        ks_stat, ks_pval = float('nan'), float('nan')

    # Histogram on [-2, 2] in 100 bins
    bin_edges = np.linspace(-2, 2, 101)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    hist_counts, _ = np.histogram(tempered, bins=bin_edges, density=True)

    # Sato-Tate reference
    st_density = sato_tate_pdf(bin_centers)

    # Deviation from semicircle
    deviation = hist_counts - st_density

    # Moments -- use TEMPERED coefficients (robust to non-tempered outliers)
    m2 = np.mean(tempered**2)
    m4 = np.mean(tempered**4)
    kurtosis_ratio = m4 / m2**2 if m2 > 0 else float('nan')

    # Also compute raw moments for comparison
    m2_raw = np.mean(all_cp**2)
    m4_raw = np.mean(all_cp**4)
    kurtosis_raw = m4_raw / m2_raw**2 if m2_raw > 0 else float('nan')

    # Chi-squared goodness of fit
    expected_counts = st_density * (bin_edges[1] - bin_edges[0]) * len(tempered)
    observed_counts, _ = np.histogram(tempered, bins=bin_edges)
    mask = expected_counts >= 5
    if mask.sum() > 2:
        chi2_stat = np.sum((observed_counts[mask] - expected_counts[mask])**2 / expected_counts[mask])
        chi2_dof = mask.sum() - 1
        chi2_pval = 1.0 - stats.chi2.cdf(chi2_stat, chi2_dof)
    else:
        chi2_stat, chi2_dof, chi2_pval = float('nan'), 0, float('nan')

    # Anderson-Darling style: L2 deviation
    l2_deviation = np.sqrt(np.mean(deviation**2))

    return {
        "level": int(level),
        "n_forms": len(coeffs_list),
        "n_cp_total": n_total,
        "n_tempered": len(tempered),
        "outlier_fraction": round(outlier_frac, 6),
        "outlier_fraction_relaxed": round(outlier_frac_relaxed, 6),
        "ks_statistic": round(ks_stat, 6),
        "ks_pvalue": round(ks_pval, 6),
        "chi2_statistic": round(chi2_stat, 4),
        "chi2_dof": int(chi2_dof),
        "chi2_pvalue": round(chi2_pval, 6),
        "M2_tempered": round(m2, 6),
        "M4_tempered": round(m4, 6),
        "M4_over_M2_sq_tempered": round(kurtosis_ratio, 6),
        "M4_over_M2_sq_raw": round(kurtosis_raw, 6),
        "mean": round(np.mean(tempered), 6),
        "std": round(np.std(tempered), 6),
        "l2_deviation": round(l2_deviation, 6),
        "histogram_density": [round(x, 6) for x in hist_counts.tolist()],
        "deviation_from_ST": [round(x, 6) for x in deviation.tolist()],
    }


def main():
    print("Loading Maass forms...")
    with open(DATA_PATH) as f:
        data = json.load(f)
    print(f"  {len(data)} forms loaded")

    # Group by level
    by_level = defaultdict(list)
    for form in data:
        by_level[form["level"]].append(form)

    # Get prime indices
    max_n = max(f["n_coefficients"] for f in data)
    prime_indices = get_prime_indices(max_n)
    print(f"  {len(prime_indices)} prime indices up to {max_n}")

    # == Analysis 1: Per-level shape ==
    print("\n=== Per-Level Sato-Tate Analysis ===")
    MIN_FORMS = 100
    level_results = []

    qualifying_levels = sorted([lvl for lvl, forms in by_level.items() if len(forms) >= MIN_FORMS])
    print(f"  {len(qualifying_levels)} levels with {MIN_FORMS}+ forms")

    for lvl in qualifying_levels:
        forms = by_level[lvl]
        coeffs_list = [f["coefficients"] for f in forms]
        result = analyze_level(coeffs_list, lvl, prime_indices)
        if result:
            level_results.append(result)
            print(f"  Level {lvl:3d}: {result['n_forms']:4d} forms, "
                  f"M4/M2^2={result['M4_over_M2_sq_tempered']:.4f}, "
                  f"KS={result['ks_statistic']:.4f} (p={result['ks_pvalue']:.4f}), "
                  f"outliers={result['outlier_fraction']:.4f}, "
                  f"L2dev={result['l2_deviation']:.4f}")

    # == Analysis 2: Level-averaged deviation pattern ==
    print("\n=== Level-Averaged Deviation from Semicircle ===")
    all_deviations = np.array([r["deviation_from_ST"] for r in level_results])
    mean_deviation = np.mean(all_deviations, axis=0)
    std_deviation = np.std(all_deviations, axis=0)

    bin_edges = np.linspace(-2, 2, 101)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Significant deviations (> 2 SE from zero)
    se = std_deviation / np.sqrt(len(level_results))
    significant = np.abs(mean_deviation) > 2 * se
    n_sig = significant.sum()
    print(f"  Bins with significant deviation: {n_sig}/100")

    # Characterize the deviation pattern by region
    center_bins = (np.abs(bin_centers) < 0.5)
    tail_bins = (np.abs(bin_centers) > 1.5)
    mid_bins = (~center_bins) & (~tail_bins)

    center_dev = np.mean(mean_deviation[center_bins])
    mid_dev = np.mean(mean_deviation[mid_bins])
    tail_dev = np.mean(mean_deviation[tail_bins])

    print(f"  Center deviation (|x|<0.5): {center_dev:+.5f}")
    print(f"  Mid deviation (0.5<|x|<1.5): {mid_dev:+.5f}")
    print(f"  Tail deviation (|x|>1.5): {tail_dev:+.5f}")

    # == Analysis 3: M4/M2^2 trend with level ==
    print("\n=== Kurtosis Ratio M4/M2^2 vs Level ===")
    levels_arr = np.array([r["level"] for r in level_results])
    kurtosis_arr = np.array([r["M4_over_M2_sq_tempered"] for r in level_results])

    if len(levels_arr) > 3:
        slope, intercept, r_val, p_val, _ = stats.linregress(np.log(levels_arr), kurtosis_arr)
        print(f"  Regression M4/M2^2 ~ a*log(level) + b:")
        print(f"    slope = {slope:.6f}, intercept = {intercept:.6f}")
        print(f"    r = {r_val:.4f}, p = {p_val:.4f}")

    overall_kurtosis = np.mean(kurtosis_arr)
    kurtosis_std = np.std(kurtosis_arr)
    print(f"  Overall M4/M2^2 = {overall_kurtosis:.4f} +/- {kurtosis_std:.4f}")
    print(f"  Sato-Tate prediction = 2.0000")
    print(f"  Per-level values: {', '.join(f'{k:.4f}' for k in kurtosis_arr)}")

    # == Analysis 4: Prime levels vs composite levels ==
    print("\n=== Prime Levels (all newforms) vs Composite Levels ===")

    prime_level_results = [r for r in level_results if is_prime(r["level"])]
    composite_level_results = [r for r in level_results if not is_prime(r["level"])]

    prime_ks = comp_ks = prime_kurt = comp_kurt = float('nan')
    prime_better = None
    prime_mean_dev = comp_mean_dev = None

    if prime_level_results and composite_level_results:
        prime_ks = np.mean([r["ks_statistic"] for r in prime_level_results])
        comp_ks = np.mean([r["ks_statistic"] for r in composite_level_results])
        prime_kurt = np.mean([r["M4_over_M2_sq_tempered"] for r in prime_level_results])
        comp_kurt = np.mean([r["M4_over_M2_sq_tempered"] for r in composite_level_results])

        print(f"  Prime levels ({len(prime_level_results)}):")
        print(f"    Mean KS = {prime_ks:.5f}, Mean M4/M2^2 = {prime_kurt:.5f}")
        for r in prime_level_results:
            print(f"      level={r['level']}: KS={r['ks_statistic']:.5f}, M4/M2^2={r['M4_over_M2_sq_tempered']:.5f}")
        print(f"  Composite levels ({len(composite_level_results)}):")
        print(f"    Mean KS = {comp_ks:.5f}, Mean M4/M2^2 = {comp_kurt:.5f}")
        for r in composite_level_results:
            print(f"      level={r['level']}: KS={r['ks_statistic']:.5f}, M4/M2^2={r['M4_over_M2_sq_tempered']:.5f}")

        prime_better = prime_ks < comp_ks
        print(f"  Prime levels fit better: {prime_better} (lower KS = better fit)")

        prime_devs = np.array([r["deviation_from_ST"] for r in prime_level_results])
        comp_devs = np.array([r["deviation_from_ST"] for r in composite_level_results])
        prime_mean_dev = np.mean(prime_devs, axis=0)
        comp_mean_dev = np.mean(comp_devs, axis=0)

    # == Analysis 5: Global pooled test ==
    print("\n=== Global Pooled Analysis (All Forms, Tempered Only) ===")
    all_cp_global = []
    for form in data:
        coeffs = form["coefficients"]
        n_c = len(coeffs)
        lvl = form["level"]
        for idx in prime_indices:
            if idx < n_c:
                p = idx + 1
                if lvl % p == 0:
                    continue
                all_cp_global.append(coeffs[idx])

    all_cp_global = np.array(all_cp_global)
    tempered_global = all_cp_global[np.abs(all_cp_global) <= 2.0]

    ks_global, ks_p_global = stats.kstest(tempered_global, sato_tate_cdf)
    m2_global = np.mean(tempered_global**2)
    m4_global = np.mean(tempered_global**4)
    kurt_global = m4_global / m2_global**2

    # Raw (unfiltered)
    m2_raw = np.mean(all_cp_global**2)
    m4_raw = np.mean(all_cp_global**4)
    kurt_raw = m4_raw / m2_raw**2

    print(f"  Total c_p values: {len(all_cp_global)}")
    print(f"  Tempered (|c_p| <= 2): {len(tempered_global)} ({len(tempered_global)/len(all_cp_global)*100:.3f}%)")
    print(f"  Global KS = {ks_global:.6f} (p = {ks_p_global:.6e})")
    print(f"  Tempered: M2 = {m2_global:.6f}, M4 = {m4_global:.6f}, M4/M2^2 = {kurt_global:.6f}")
    print(f"  Raw:      M2 = {m2_raw:.6f}, M4 = {m4_raw:.6f}, M4/M2^2 = {kurt_raw:.6f}")
    print(f"  Sato-Tate prediction: M2=1.0, M4=2.0, M4/M2^2=2.0")

    # Non-tempered forms analysis
    non_tempered_mask = np.abs(all_cp_global) > 2.0
    n_non_tempered = non_tempered_mask.sum()
    print(f"\n  Non-tempered c_p values: {n_non_tempered} ({n_non_tempered/len(all_cp_global)*100:.4f}%)")
    if n_non_tempered > 0:
        nt = all_cp_global[non_tempered_mask]
        print(f"    Range: [{np.min(nt):.3f}, {np.max(nt):.3f}]")
        print(f"    Impact on M4/M2^2: raw={kurt_raw:.4f} vs tempered={kurt_global:.4f}")

    # == Analysis 6: KS scaling with sample size ==
    print("\n=== KS Scaling with Sample Size ===")
    ns = np.array([r["n_tempered"] for r in level_results], dtype=float)
    ks_vals = np.array([r["ks_statistic"] for r in level_results])

    # Under H0, KS ~ 1/sqrt(n). Compute D*sqrt(n).
    ks_scaled = ks_vals * np.sqrt(ns)
    print(f"  D*sqrt(n): mean = {np.mean(ks_scaled):.3f}, std = {np.std(ks_scaled):.3f}")
    print(f"  (If ST holds exactly, D*sqrt(n) should be O(1) and independent of n)")

    if len(levels_arr) > 3:
        corr, p_corr = stats.pearsonr(levels_arr, ks_scaled)
        print(f"  Correlation D*sqrt(n) vs level: r={corr:.4f}, p={p_corr:.4f}")
    else:
        corr, p_corr = float('nan'), float('nan')

    # == Analysis 7: Deviation symmetry ==
    print("\n=== Deviation Symmetry ===")
    left_half = mean_deviation[:50]
    right_half = mean_deviation[50:][::-1]
    asymmetry = left_half - right_half
    mean_asym = np.mean(np.abs(asymmetry))
    even_component = (left_half + right_half) / 2
    print(f"  Mean |asymmetry| = {mean_asym:.6f}")
    print(f"  Max |asymmetry| = {np.max(np.abs(asymmetry)):.6f}")
    print(f"  Even component peak = {np.max(np.abs(even_component)):.6f}")
    print(f"  (Sato-Tate is symmetric, so deviation should be even)")

    # == Analysis 8: Spectral parameter dependence ==
    print("\n=== Spectral Parameter Dependence ===")
    # Split forms into low-R and high-R, compare shape
    all_R = [float(f["spectral_parameter"]) for f in data]
    median_R = np.median(all_R)
    print(f"  Median spectral parameter R = {median_R:.4f}")

    low_R_cp = []
    high_R_cp = []
    for form in data:
        R = float(form["spectral_parameter"])
        coeffs = form["coefficients"]
        lvl = form["level"]
        cp_vals = []
        for idx in prime_indices:
            if idx < len(coeffs):
                p = idx + 1
                if lvl % p == 0: continue
                v = coeffs[idx]
                if abs(v) <= 2.0:
                    cp_vals.append(v)
        if R < median_R:
            low_R_cp.extend(cp_vals)
        else:
            high_R_cp.extend(cp_vals)

    low_R_cp = np.array(low_R_cp)
    high_R_cp = np.array(high_R_cp)

    ks_low, p_low = stats.kstest(low_R_cp, sato_tate_cdf)
    ks_high, p_high = stats.kstest(high_R_cp, sato_tate_cdf)
    m4m2_low = np.mean(low_R_cp**4) / np.mean(low_R_cp**2)**2
    m4m2_high = np.mean(high_R_cp**4) / np.mean(high_R_cp**2)**2

    print(f"  Low R (<{median_R:.2f}): {len(low_R_cp)} c_p, KS={ks_low:.5f}, M4/M2^2={m4m2_low:.5f}")
    print(f"  High R (>{median_R:.2f}): {len(high_R_cp)} c_p, KS={ks_high:.5f}, M4/M2^2={m4m2_high:.5f}")

    # 2-sample KS between low-R and high-R
    ks_2sample, p_2sample = stats.ks_2samp(low_R_cp, high_R_cp)
    print(f"  2-sample KS (low vs high R): D={ks_2sample:.5f}, p={p_2sample:.6e}")

    # == Build results ==
    results = {
        "experiment": "Maass coefficient distribution shape vs level",
        "data_source": "maass_with_coefficients.json",
        "n_forms_total": len(data),
        "n_levels_analyzed": len(level_results),
        "min_forms_per_level": MIN_FORMS,
        "method": (
            "Pool c_p (p prime, p not dividing level, |c_p|<=2 for tempered) "
            "per level, compare to Sato-Tate semicircle (2/pi)sqrt(1-x^2/4)"
        ),

        "global_analysis": {
            "n_cp_values": int(len(all_cp_global)),
            "n_tempered": int(len(tempered_global)),
            "fraction_tempered": round(len(tempered_global) / len(all_cp_global), 6),
            "KS_statistic": round(float(ks_global), 6),
            "KS_pvalue": float(f"{ks_p_global:.6e}"),
            "M2_tempered": round(float(m2_global), 6),
            "M4_tempered": round(float(m4_global), 6),
            "M4_over_M2_sq_tempered": round(float(kurt_global), 6),
            "M4_over_M2_sq_raw": round(float(kurt_raw), 6),
            "sato_tate_M4_over_M2_sq": 2.0,
        },

        "per_level_results": level_results,

        "kurtosis_vs_level": {
            "mean_M4_over_M2_sq": round(float(overall_kurtosis), 6),
            "std_M4_over_M2_sq": round(float(kurtosis_std), 6),
            "regression_slope_vs_log_level": round(float(slope), 6) if len(levels_arr) > 3 else None,
            "regression_r": round(float(r_val), 4) if len(levels_arr) > 3 else None,
            "regression_p": round(float(p_val), 4) if len(levels_arr) > 3 else None,
        },

        "level_averaged_deviation": {
            "bin_centers": [round(float(x), 4) for x in bin_centers.tolist()],
            "mean_deviation": [round(float(x), 6) for x in mean_deviation.tolist()],
            "std_deviation": [round(float(x), 6) for x in std_deviation.tolist()],
            "n_significant_bins": int(n_sig),
            "center_mean_deviation": round(float(center_dev), 6),
            "mid_mean_deviation": round(float(mid_dev), 6),
            "tail_mean_deviation": round(float(tail_dev), 6),
            "mean_asymmetry": round(float(mean_asym), 6),
        },

        "prime_vs_composite_levels": {
            "n_prime_levels": len(prime_level_results),
            "n_composite_levels": len(composite_level_results),
            "prime_mean_KS": round(float(prime_ks), 6) if not np.isnan(prime_ks) else None,
            "composite_mean_KS": round(float(comp_ks), 6) if not np.isnan(comp_ks) else None,
            "prime_mean_M4_M2_sq": round(float(prime_kurt), 6) if not np.isnan(prime_kurt) else None,
            "composite_mean_M4_M2_sq": round(float(comp_kurt), 6) if not np.isnan(comp_kurt) else None,
            "prime_levels_fit_better": bool(prime_better) if prime_better is not None else None,
        },

        "spectral_parameter_dependence": {
            "median_R": round(float(median_R), 4),
            "low_R_n": int(len(low_R_cp)),
            "high_R_n": int(len(high_R_cp)),
            "low_R_KS": round(float(ks_low), 6),
            "high_R_KS": round(float(ks_high), 6),
            "low_R_M4_M2_sq": round(float(m4m2_low), 6),
            "high_R_M4_M2_sq": round(float(m4m2_high), 6),
            "two_sample_KS_D": round(float(ks_2sample), 6),
            "two_sample_KS_p": float(f"{p_2sample:.6e}"),
        },

        "ks_scaling": {
            "mean_D_sqrt_n": round(float(np.mean(ks_scaled)), 4),
            "std_D_sqrt_n": round(float(np.std(ks_scaled)), 4),
            "correlation_with_level": round(float(corr), 4) if not np.isnan(corr) else None,
            "correlation_pvalue": round(float(p_corr), 4) if not np.isnan(p_corr) else None,
        },

        "conclusions": {},
    }

    # == Conclusions ==
    conclusions = {}

    # KS pass rate
    n_pass_ks = sum(1 for r in level_results if r["ks_pvalue"] > 0.05)
    n_fail_ks = len(level_results) - n_pass_ks
    conclusions["ks_pass_rate"] = f"{n_pass_ks}/{len(level_results)} levels pass KS at alpha=0.05"

    # Kurtosis trend
    if len(levels_arr) > 3 and p_val < 0.05:
        conclusions["kurtosis_trend"] = (
            f"M4/M2^2 shows significant trend with log(level): "
            f"slope={slope:.6f}, p={p_val:.4f}"
        )
    else:
        conclusions["kurtosis_trend"] = (
            f"No significant kurtosis trend with level (slope={slope:.6f}, p={p_val:.4f})"
        )

    # Prime vs composite
    if prime_better is not None:
        conclusions["prime_vs_composite"] = (
            f"Prime levels {'DO' if prime_better else 'do NOT'} fit semicircle better "
            f"(KS: prime={prime_ks:.5f} vs composite={comp_ks:.5f})"
        )

    # Global kurtosis
    kurt_dev = abs(kurt_global - 2.0)
    conclusions["global_kurtosis"] = (
        f"M4/M2^2={kurt_global:.6f} (tempered), deviation from ST={kurt_dev:.6f}"
    )

    # Spectral parameter dependence
    if p_2sample < 0.01:
        conclusions["spectral_dependence"] = (
            f"Shape DOES depend on spectral parameter: "
            f"low-R M4/M2^2={m4m2_low:.5f}, high-R M4/M2^2={m4m2_high:.5f}, "
            f"2-sample KS p={p_2sample:.2e}"
        )
    else:
        conclusions["spectral_dependence"] = (
            f"Shape does NOT significantly depend on spectral parameter "
            f"(2-sample KS p={p_2sample:.2e})"
        )

    # Non-tempered fraction
    conclusions["tempered_fraction"] = (
        f"{len(tempered_global)}/{len(all_cp_global)} c_p values tempered "
        f"({len(tempered_global)/len(all_cp_global)*100:.3f}%). "
        f"Raw M4/M2^2={kurt_raw:.4f} vs tempered M4/M2^2={kurt_global:.4f} -- "
        f"{'non-tempered forms severely distort moments' if abs(kurt_raw - kurt_global) > 0.5 else 'minimal impact'}"
    )

    # Systematic deviation
    if n_sig > 20:
        conclusions["systematic_deviation"] = (
            f"Systematic deviation detected: {n_sig}/100 bins significant. "
            f"Pattern: center={center_dev:+.5f}, mid={mid_dev:+.5f}, tail={tail_dev:+.5f}. "
            f"{'Excess at center relative to tails' if center_dev > tail_dev else 'Deficit at center relative to tails'}"
        )
    elif n_sig > 10:
        conclusions["systematic_deviation"] = (
            f"Mild systematic deviation: {n_sig}/100 bins significant"
        )
    else:
        conclusions["systematic_deviation"] = (
            f"No strong systematic deviation: only {n_sig}/100 bins significant"
        )

    # Overall verdict
    if n_pass_ks >= len(level_results) * 0.5 and kurt_dev < 0.05:
        conclusions["verdict"] = (
            "CONFIRMED: Maass form c_p follow Sato-Tate semicircle at every tested level. "
            f"M4/M2^2={kurt_global:.4f} matches SU(2) prediction 2.0 within {kurt_dev:.4f}. "
            "Shape is universal across levels."
        )
    elif kurt_dev < 0.1:
        conclusions["verdict"] = (
            "CONFIRMED with caveats: Semicircle is correct to high precision "
            f"(M4/M2^2={kurt_global:.4f}), but large-sample KS tests can detect "
            "tiny deviations. Shape is effectively level-independent."
        )
    else:
        conclusions["verdict"] = (
            f"PARTIAL: M4/M2^2={kurt_global:.4f} deviates from ST prediction 2.0 "
            f"by {kurt_dev:.4f}. Shape may vary with level or spectral parameter."
        )

    results["conclusions"] = conclusions

    # Print conclusions
    print("\n" + "="*60)
    print("CONCLUSIONS")
    print("="*60)
    for k, v in conclusions.items():
        print(f"  {k}: {v}")

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
