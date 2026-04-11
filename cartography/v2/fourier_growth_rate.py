#!/usr/bin/env python3
"""
Fourier Coefficient Growth Rate Classification

For weight-2 modular forms, the Ramanujan-Petersson conjecture bounds
|a_p| <= 2p^{(k-1)/2} = 2p^{0.5} for weight k=2.

This script measures the actual growth exponent alpha by fitting
log|a_p| ~ alpha * log(p) + c across primes, and compares to the
theoretical bound of 0.5.

Groups by CM vs non-CM, conductor range, and measures tightness
(fraction of forms with |a_p| > p^{0.45} for large p).
"""

import json
import numpy as np
import duckdb
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / ".." / "charon" / "data" / "charon.duckdb"
OUT_FILE = Path(__file__).parent / "fourier_growth_rate_results.json"


def primes_up_to(n):
    """Sieve of Eratosthenes."""
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = False
    return np.where(sieve)[0]


def load_data():
    """Load dim=1, weight=2 modular forms with ap_coeffs from DuckDB."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, is_cm, ap_coeffs, ap_maxp,
               sato_tate_group, self_twist_type
        FROM modular_forms
        WHERE dim = 1
          AND weight = 2
          AND ap_coeffs IS NOT NULL
    """).fetchall()
    con.close()

    forms = []
    for row in rows:
        label, level, is_cm, ap_coeffs_raw, ap_maxp, st_group, self_twist = row
        # ap_coeffs is list of [val] for dim=1
        coeffs_parsed = json.loads(ap_coeffs_raw) if isinstance(ap_coeffs_raw, str) else ap_coeffs_raw
        ap_values = [c[0] for c in coeffs_parsed]
        forms.append({
            'label': label,
            'level': level,
            'is_cm': bool(is_cm),
            'ap': np.array(ap_values, dtype=float),
            'ap_maxp': ap_maxp,
            'sato_tate': st_group,
            'self_twist': self_twist,
        })
    return forms


def fit_growth_exponent(ap_vals, primes):
    """Fit log|a_p| ~ alpha * log(p) + c using OLS on nonzero entries."""
    n = min(len(ap_vals), len(primes))
    ap = ap_vals[:n]
    p = primes[:n]

    mask = np.abs(ap) > 0
    if mask.sum() < 10:
        return None, None, None

    log_abs_ap = np.log(np.abs(ap[mask]))
    log_p = np.log(p[mask].astype(float))

    # OLS: log|a_p| = alpha * log(p) + c
    A = np.vstack([log_p, np.ones_like(log_p)]).T
    result = np.linalg.lstsq(A, log_abs_ap, rcond=None)
    alpha, intercept = result[0]
    residuals = log_abs_ap - (alpha * log_p + intercept)
    rmse = np.sqrt(np.mean(residuals**2))

    return alpha, intercept, rmse


def compute_tightness(ap_vals, primes, exponent_threshold=0.45, min_prime_idx=50):
    """Fraction of primes (beyond the 50th) where |a_p| > p^threshold."""
    n = min(len(ap_vals), len(primes))
    if n <= min_prime_idx:
        return None

    ap = ap_vals[min_prime_idx:n]
    p = primes[min_prime_idx:n].astype(float)
    bound = p ** exponent_threshold
    exceedances = np.abs(ap) > bound
    return float(np.mean(exceedances))


def compute_ramanujan_ratio(ap_vals, primes):
    """Mean of |a_p| / (2 * p^0.5) -- ratio to RP bound."""
    n = min(len(ap_vals), len(primes))
    ap = ap_vals[:n]
    p = primes[:n].astype(float)
    rp_bound = 2.0 * np.sqrt(p)
    ratios = np.abs(ap) / rp_bound
    return float(np.mean(ratios)), float(np.std(ratios))


def compute_serial_correlation(ap_vals, primes, max_lag=5):
    """Serial correlation of normalized |a_p|/sqrt(p) at lags 1..max_lag.

    Must normalize by sqrt(p) to remove growth trend; otherwise
    serial correlation is dominated by monotone increase in |a_p|.
    """
    n = min(len(ap_vals), len(primes))
    # Normalize: x_p = |a_p| / sqrt(p)  (Sato-Tate scale)
    x = np.abs(ap_vals[:n]) / np.sqrt(primes[:n].astype(float))
    x_centered = x - np.mean(x)
    var = np.var(x)
    if var < 1e-12:
        return [0.0] * max_lag

    corrs = []
    for lag in range(1, max_lag + 1):
        if n - lag < 2:
            corrs.append(0.0)
        else:
            c = np.mean(x_centered[:n-lag] * x_centered[lag:n]) / var
            corrs.append(float(c))
    return corrs


def conductor_bin(level):
    """Bin conductor into ranges."""
    if level <= 100:
        return "1-100"
    elif level <= 500:
        return "101-500"
    elif level <= 1000:
        return "501-1000"
    elif level <= 2500:
        return "1001-2500"
    else:
        return "2501+"


def main():
    print("Loading modular forms from DuckDB...")
    forms = load_data()
    print(f"Loaded {len(forms)} dim=1, weight=2 forms with ap_coeffs")

    # Build prime list up to max ap_maxp
    max_p = max(f['ap_maxp'] for f in forms)
    all_primes = primes_up_to(max_p)
    print(f"Generated {len(all_primes)} primes up to {max_p}")

    # For each form, ap_coeffs are indexed by sequential primes
    # ap[0] = a_{p_1=2}, ap[1] = a_{p_2=3}, etc.

    results_per_form = []
    for f in forms:
        primes = all_primes[:len(f['ap'])]
        # Exclude primes dividing the level (bad primes)
        good_mask = np.array([p for p in primes if f['level'] % p != 0])
        good_ap = np.array([a for a, p in zip(f['ap'], primes) if f['level'] % p != 0])

        if len(good_ap) < 20:
            continue

        alpha, intercept, rmse = fit_growth_exponent(good_ap, good_mask)
        if alpha is None:
            continue

        tightness = compute_tightness(good_ap, good_mask)
        rp_ratio_mean, rp_ratio_std = compute_ramanujan_ratio(good_ap, good_mask)
        serial_corr = compute_serial_correlation(good_ap, good_mask)

        results_per_form.append({
            'label': f['label'],
            'level': f['level'],
            'is_cm': f['is_cm'],
            'sato_tate': f['sato_tate'],
            'conductor_bin': conductor_bin(f['level']),
            'alpha': alpha,
            'rmse': rmse,
            'tightness_045': tightness,
            'rp_ratio_mean': rp_ratio_mean,
            'rp_ratio_std': rp_ratio_std,
            'serial_corr': serial_corr,
            'n_good_primes': len(good_ap),
        })

    print(f"Computed growth exponents for {len(results_per_form)} forms")

    # Aggregate statistics
    alphas = np.array([r['alpha'] for r in results_per_form])
    rp_ratios = np.array([r['rp_ratio_mean'] for r in results_per_form])
    tightnesses = np.array([r['tightness_045'] for r in results_per_form if r['tightness_045'] is not None])

    # CM vs non-CM split
    cm_alphas = np.array([r['alpha'] for r in results_per_form if r['is_cm']])
    noncm_alphas = np.array([r['alpha'] for r in results_per_form if not r['is_cm']])
    cm_rp = np.array([r['rp_ratio_mean'] for r in results_per_form if r['is_cm']])
    noncm_rp = np.array([r['rp_ratio_mean'] for r in results_per_form if not r['is_cm']])
    cm_tightness = np.array([r['tightness_045'] for r in results_per_form if r['is_cm'] and r['tightness_045'] is not None])
    noncm_tightness = np.array([r['tightness_045'] for r in results_per_form if not r['is_cm'] and r['tightness_045'] is not None])

    # By conductor bin
    bin_stats = {}
    for bname in ["1-100", "101-500", "501-1000", "1001-2500", "2501+"]:
        bin_alphas = np.array([r['alpha'] for r in results_per_form if r['conductor_bin'] == bname])
        if len(bin_alphas) > 0:
            bin_stats[bname] = {
                'count': len(bin_alphas),
                'alpha_mean': float(np.mean(bin_alphas)),
                'alpha_std': float(np.std(bin_alphas)),
                'alpha_median': float(np.median(bin_alphas)),
            }

    # Serial correlation aggregation
    all_serial = np.array([r['serial_corr'] for r in results_per_form])
    mean_serial = np.mean(all_serial, axis=0).tolist()
    cm_serial = np.array([r['serial_corr'] for r in results_per_form if r['is_cm']])
    noncm_serial = np.array([r['serial_corr'] for r in results_per_form if not r['is_cm']])

    # Ramanujan deficit = 0.5 - alpha
    deficits = 0.5 - alphas

    summary = {
        'description': 'Fourier coefficient growth rate classification for weight-2 modular forms',
        'theoretical_bound': 'Ramanujan-Petersson: |a_p| <= 2*p^0.5 for weight 2',
        'n_forms_analyzed': len(results_per_form),
        'n_cm': int(np.sum([r['is_cm'] for r in results_per_form])),
        'n_non_cm': int(np.sum([not r['is_cm'] for r in results_per_form])),
        'overall': {
            'alpha_mean': float(np.mean(alphas)),
            'alpha_std': float(np.std(alphas)),
            'alpha_median': float(np.median(alphas)),
            'alpha_q25': float(np.percentile(alphas, 25)),
            'alpha_q75': float(np.percentile(alphas, 75)),
            'ramanujan_deficit_mean': float(np.mean(deficits)),
            'ramanujan_deficit_std': float(np.std(deficits)),
            'rp_ratio_mean': float(np.mean(rp_ratios)),
            'rp_ratio_std': float(np.std(rp_ratios)),
            'tightness_045_mean': float(np.mean(tightnesses)),
            'tightness_045_std': float(np.std(tightnesses)),
            'mean_serial_correlation_lags_1_5': mean_serial,
        },
        'cm_forms': {
            'count': len(cm_alphas),
            'alpha_mean': float(np.mean(cm_alphas)) if len(cm_alphas) > 0 else None,
            'alpha_std': float(np.std(cm_alphas)) if len(cm_alphas) > 0 else None,
            'alpha_median': float(np.median(cm_alphas)) if len(cm_alphas) > 0 else None,
            'rp_ratio_mean': float(np.mean(cm_rp)) if len(cm_rp) > 0 else None,
            'tightness_045_mean': float(np.mean(cm_tightness)) if len(cm_tightness) > 0 else None,
            'serial_corr_lags_1_5': np.mean(cm_serial, axis=0).tolist() if len(cm_serial) > 0 else None,
        },
        'non_cm_forms': {
            'count': len(noncm_alphas),
            'alpha_mean': float(np.mean(noncm_alphas)),
            'alpha_std': float(np.std(noncm_alphas)),
            'alpha_median': float(np.median(noncm_alphas)),
            'rp_ratio_mean': float(np.mean(noncm_rp)),
            'tightness_045_mean': float(np.mean(noncm_tightness)),
            'serial_corr_lags_1_5': np.mean(noncm_serial, axis=0).tolist(),
        },
        'by_conductor_bin': bin_stats,
        'alpha_histogram': {
            'bin_edges': list(np.linspace(float(np.min(alphas)) - 0.01, float(np.max(alphas)) + 0.01, 31)),
            'counts': np.histogram(alphas, bins=30)[0].tolist(),
        },
        'interpretation': {},
    }

    # Top 20 highest-alpha forms (closest to bound)
    sorted_by_alpha = sorted(results_per_form, key=lambda r: r['alpha'], reverse=True)
    summary['top_20_highest_alpha'] = [
        {'label': r['label'], 'level': r['level'], 'is_cm': r['is_cm'],
         'alpha': round(r['alpha'], 6), 'rp_ratio': round(r['rp_ratio_mean'], 4)}
        for r in sorted_by_alpha[:20]
    ]

    # Bottom 20 lowest-alpha forms (furthest from bound)
    summary['bottom_20_lowest_alpha'] = [
        {'label': r['label'], 'level': r['level'], 'is_cm': r['is_cm'],
         'alpha': round(r['alpha'], 6), 'rp_ratio': round(r['rp_ratio_mean'], 4)}
        for r in sorted_by_alpha[-20:]
    ]

    # Interpretation
    summary['interpretation'] = {
        'ramanujan_deficit_explanation': (
            f"Mean alpha = {summary['overall']['alpha_mean']:.4f} vs theoretical max 0.5. "
            f"Ramanujan deficit = {summary['overall']['ramanujan_deficit_mean']:.4f}. "
            f"Typical forms sit well below the bound."
        ),
        'cm_vs_noncm': (
            f"CM forms: alpha = {summary['cm_forms']['alpha_mean']:.4f} "
            f"vs non-CM: alpha = {summary['non_cm_forms']['alpha_mean']:.4f}. "
            f"CM alpha is higher because OLS fits only nonzero |a_p|: "
            f"at split primes, CM a_p grows as p^0.5 (tight to bound), "
            f"while ~50% of primes are inert (a_p=0, excluded from fit). "
            f"Non-CM alpha of {summary['non_cm_forms']['alpha_mean']:.4f} reflects "
            f"the true typical deficit from the RP bound."
        ),
        'tightness': (
            f"Fraction with |a_p| > p^0.45 for large primes: "
            f"{summary['overall']['tightness_045_mean']:.4f}. "
            f"Most coefficients stay far from the bound."
        ),
        'serial_correlation': (
            f"Mean serial correlation at lag 1: {mean_serial[0]:.4f}. "
            f"{'Significant serial correlation detected.' if abs(mean_serial[0]) > 0.02 else 'Negligible serial correlation (consistent with pseudorandom).'}"
        ),
    }

    # Print summary
    print("\n" + "="*70)
    print("FOURIER COEFFICIENT GROWTH RATE RESULTS")
    print("="*70)
    print(f"Forms analyzed: {summary['n_forms_analyzed']}")
    print(f"  CM: {summary['n_cm']}, non-CM: {summary['n_non_cm']}")
    print(f"\nOverall growth exponent alpha:")
    print(f"  Mean:   {summary['overall']['alpha_mean']:.6f}")
    print(f"  Median: {summary['overall']['alpha_median']:.6f}")
    print(f"  Std:    {summary['overall']['alpha_std']:.6f}")
    print(f"  [Q25, Q75]: [{summary['overall']['alpha_q25']:.4f}, {summary['overall']['alpha_q75']:.4f}]")
    print(f"\nRamanujan deficit (0.5 - alpha):")
    print(f"  Mean:   {summary['overall']['ramanujan_deficit_mean']:.6f}")
    print(f"  Std:    {summary['overall']['ramanujan_deficit_std']:.6f}")
    print(f"\nRP ratio |a_p|/(2*sqrt(p)):")
    print(f"  Mean:   {summary['overall']['rp_ratio_mean']:.6f}")
    print(f"\nTightness (frac |a_p| > p^0.45 for large p):")
    print(f"  Mean:   {summary['overall']['tightness_045_mean']:.6f}")
    print(f"\nCM forms: alpha_mean = {summary['cm_forms']['alpha_mean']}")
    print(f"Non-CM:   alpha_mean = {summary['non_cm_forms']['alpha_mean']:.6f}")
    print(f"\nBy conductor bin:")
    for bname, bs in bin_stats.items():
        print(f"  {bname:>10}: n={bs['count']:>5}, alpha={bs['alpha_mean']:.4f} +/- {bs['alpha_std']:.4f}")
    print(f"\nSerial correlation (lags 1-5): {[round(x, 4) for x in mean_serial]}")

    # Save
    with open(OUT_FILE, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == '__main__':
    main()
