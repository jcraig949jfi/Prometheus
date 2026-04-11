#!/usr/bin/env python3
"""
Maass Higher Moments — Catalan Moment Chain Verification

Theory (Sato-Tate / Marchenko-Pastur for GL(2)):
If a(p) are distributed as semicircle on [-2,2], the even moments of a(p)/2
follow the Catalan numbers:
    M_{2k} / M_2^k = C_k  where C_k = (2k)! / ((k+1)! * k!)
    C1=1, C2=2, C3=5, C4=14

For the un-rescaled a(p) in [-2,2]:
    M2 = <a(p)^2> ~ 1.0  (for semicircle on [-2,2], M2 = 1)
    M4/M2^2 ~ 2  (C2)
    M6/M2^3 ~ 5  (C3)
    M8/M2^4 ~ 14 (C4)

We compute these ratios for Maass forms and compare to:
  - Sato-Tate theory (Catalan numbers)
  - Elliptic curve results (M6/M2^3=6.04, M8/M2^4=18.8)
"""

import json
import os
import numpy as np
from collections import defaultdict

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    is_p = np.ones(n + 1, dtype=bool)
    is_p[0] = is_p[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = False
    return np.where(is_p)[0]


def compute_moments(ap_values, max_moment=8):
    """Compute raw moments M2, M4, M6, M8 from array of a(p)."""
    ap = np.array(ap_values, dtype=np.float64)
    moments = {}
    for k in range(2, max_moment + 1, 2):
        moments[f"M{k}"] = float(np.mean(ap ** k))
    return moments


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data_path = os.path.join(
        os.path.dirname(__file__), "..",
        "maass", "data", "maass_with_coefficients.json"
    )
    with open(data_path) as f:
        data = json.load(f)

    print(f"Loaded {len(data)} Maass forms")

    # Build prime sieve up to max coefficient index
    max_n = max(d["n_coefficients"] for d in data)
    primes = sieve_primes(max_n)
    print(f"Primes up to {max_n}: {len(primes)}")

    # Require at least 30 prime-indexed coefficients for stable moments
    MIN_PRIMES = 30

    # Catalan numbers for reference
    catalan = {2: 1, 3: 5, 4: 14}

    # Per-form results
    form_results = []
    all_M2 = []
    all_M4 = []
    all_M6 = []
    all_M8 = []
    all_r42 = []
    all_r63 = []
    all_r84 = []

    for d in data:
        coeffs = d["coefficients"]
        n_coeffs = d["n_coefficients"]
        level = d["level"]

        # Extract a(p) at prime indices, excluding bad primes (p | level)
        prime_mask = primes[primes <= n_coeffs]
        # Exclude primes dividing the level
        good_primes = prime_mask[prime_mask % level != 0] if level > 1 else prime_mask

        if len(good_primes) < MIN_PRIMES:
            continue

        # coefficients are 1-indexed: coeffs[0]=a(1), coeffs[p-1]=a(p)
        ap = np.array([coeffs[p - 1] for p in good_primes], dtype=np.float64)

        m = compute_moments(ap, max_moment=8)
        M2 = m["M2"]
        M4 = m["M4"]
        M6 = m["M6"]
        M8 = m["M8"]

        if M2 < 1e-10:
            continue

        r42 = M4 / M2**2
        r63 = M6 / M2**3
        r84 = M8 / M2**4

        all_M2.append(M2)
        all_M4.append(M4)
        all_M6.append(M6)
        all_M8.append(M8)
        all_r42.append(r42)
        all_r63.append(r63)
        all_r84.append(r84)

        form_results.append({
            "maass_id": d["maass_id"],
            "level": level,
            "spectral_parameter": d["spectral_parameter"],
            "n_good_primes": int(len(good_primes)),
            "M2": round(M2, 6),
            "M4": round(M4, 6),
            "M6": round(M6, 6),
            "M8": round(M8, 6),
            "M4_over_M2_sq": round(r42, 6),
            "M6_over_M2_cu": round(r63, 6),
            "M8_over_M2_qu": round(r84, 6),
        })

    n_forms = len(form_results)
    print(f"\nAnalyzed {n_forms} forms (>= {MIN_PRIMES} good primes)")

    # ---------------------------------------------------------------------------
    # Aggregate statistics
    # ---------------------------------------------------------------------------
    all_M2 = np.array(all_M2)
    all_M4 = np.array(all_M4)
    all_M6 = np.array(all_M6)
    all_M8 = np.array(all_M8)
    all_r42 = np.array(all_r42)
    all_r63 = np.array(all_r63)
    all_r84 = np.array(all_r84)

    def stats(arr, name):
        return {
            "mean": round(float(np.mean(arr)), 6),
            "median": round(float(np.median(arr)), 6),
            "std": round(float(np.std(arr)), 6),
            "min": round(float(np.min(arr)), 6),
            "max": round(float(np.max(arr)), 6),
            "q25": round(float(np.percentile(arr, 25)), 6),
            "q75": round(float(np.percentile(arr, 75)), 6),
        }

    ratio_stats = {
        "M4_over_M2_sq": stats(all_r42, "M4/M2^2"),
        "M6_over_M2_cu": stats(all_r63, "M6/M2^3"),
        "M8_over_M2_qu": stats(all_r84, "M8/M2^4"),
    }

    moment_stats = {
        "M2": stats(all_M2, "M2"),
        "M4": stats(all_M4, "M4"),
        "M6": stats(all_M6, "M6"),
        "M8": stats(all_M8, "M8"),
    }

    # ---------------------------------------------------------------------------
    # Binned by number of primes (stability check)
    # ---------------------------------------------------------------------------
    bins = [(30, 100), (100, 200), (200, 400), (400, 800)]
    stability = {}
    for lo, hi in bins:
        mask = [(lo <= fr["n_good_primes"] < hi) for fr in form_results]
        idx = np.where(mask)[0]
        if len(idx) < 10:
            continue
        r42_bin = all_r42[idx]
        r63_bin = all_r63[idx]
        r84_bin = all_r84[idx]
        stability[f"{lo}-{hi}"] = {
            "n_forms": int(len(idx)),
            "M4_over_M2_sq_median": round(float(np.median(r42_bin)), 6),
            "M6_over_M2_cu_median": round(float(np.median(r63_bin)), 6),
            "M8_over_M2_qu_median": round(float(np.median(r84_bin)), 6),
        }

    # ---------------------------------------------------------------------------
    # Binned by level (physics check)
    # ---------------------------------------------------------------------------
    level_bins = [(1, 10), (10, 100), (100, 500), (500, 1000)]
    level_stability = {}
    for lo, hi in level_bins:
        mask = [(lo <= fr["level"] < hi) for fr in form_results]
        idx = np.where(mask)[0]
        if len(idx) < 10:
            continue
        level_stability[f"level_{lo}-{hi}"] = {
            "n_forms": int(len(idx)),
            "M4_over_M2_sq_median": round(float(np.median(all_r42[idx])), 6),
            "M6_over_M2_cu_median": round(float(np.median(all_r63[idx])), 6),
            "M8_over_M2_qu_median": round(float(np.median(all_r84[idx])), 6),
        }

    # ---------------------------------------------------------------------------
    # Robust per-form aggregation (median of per-form ratios — outlier-proof)
    # ---------------------------------------------------------------------------
    # The pooled approach is dominated by outlier forms; use median of per-form ratios
    pooled_ratios = {
        "n_forms": n_forms,
        "n_total_eigenvalues": int(np.sum([fr["n_good_primes"] for fr in form_results])),
        "M2_median": round(float(np.median(all_M2)), 6),
        "M4_over_M2_sq_median": round(float(np.median(all_r42)), 6),
        "M6_over_M2_cu_median": round(float(np.median(all_r63)), 6),
        "M8_over_M2_qu_median": round(float(np.median(all_r84)), 6),
    }

    # Also compute trimmed mean (drop top/bottom 5%) for robustness
    def trimmed_mean(arr, pct=5):
        lo = np.percentile(arr, pct)
        hi = np.percentile(arr, 100 - pct)
        mask = (arr >= lo) & (arr <= hi)
        return float(np.mean(arr[mask]))

    pooled_ratios["M4_over_M2_sq_trimmed_mean"] = round(trimmed_mean(all_r42), 6)
    pooled_ratios["M6_over_M2_cu_trimmed_mean"] = round(trimmed_mean(all_r63), 6)
    pooled_ratios["M8_over_M2_qu_trimmed_mean"] = round(trimmed_mean(all_r84), 6)

    # ---------------------------------------------------------------------------
    # Print summary
    # ---------------------------------------------------------------------------
    print("\n" + "="*70)
    print("CATALAN MOMENT CHAIN -- MAASS FORMS")
    print("="*70)

    print(f"\nMedian of per-form ratios ({n_forms} forms, {pooled_ratios['n_total_eigenvalues']:,} eigenvalues):")
    print(f"  M2 median    = {pooled_ratios['M2_median']:.4f}  (theory: 1.0)")
    print(f"  M4/M2^2      = {pooled_ratios['M4_over_M2_sq_median']:.4f}  (theory: C2 = 2)")
    print(f"  M6/M2^3      = {pooled_ratios['M6_over_M2_cu_median']:.4f}  (theory: C3 = 5)")
    print(f"  M8/M2^4      = {pooled_ratios['M8_over_M2_qu_median']:.4f}  (theory: C4 = 14)")

    print(f"\nTrimmed mean (5% tails dropped):")
    print(f"  M4/M2^2      = {pooled_ratios['M4_over_M2_sq_trimmed_mean']:.4f}")
    print(f"  M6/M2^3      = {pooled_ratios['M6_over_M2_cu_trimmed_mean']:.4f}")
    print(f"  M8/M2^4      = {pooled_ratios['M8_over_M2_qu_trimmed_mean']:.4f}")

    print(f"\nPer-form stats ({n_forms} forms):")
    print(f"  M4/M2^2  mean={ratio_stats['M4_over_M2_sq']['mean']:.4f}  median={ratio_stats['M4_over_M2_sq']['median']:.4f}  std={ratio_stats['M4_over_M2_sq']['std']:.4f}")
    print(f"  M6/M2^3  mean={ratio_stats['M6_over_M2_cu']['mean']:.4f}  median={ratio_stats['M6_over_M2_cu']['median']:.4f}  std={ratio_stats['M6_over_M2_cu']['std']:.4f}")
    print(f"  M8/M2^4  mean={ratio_stats['M8_over_M2_qu']['mean']:.4f}  median={ratio_stats['M8_over_M2_qu']['median']:.4f}  std={ratio_stats['M8_over_M2_qu']['std']:.4f}")

    r42_med = pooled_ratios["M4_over_M2_sq_median"]
    r63_med = pooled_ratios["M6_over_M2_cu_median"]
    r84_med = pooled_ratios["M8_over_M2_qu_median"]

    print(f"\nEC comparison (median):")
    print(f"  EC M4/M2^2   = 2.32   (Maass: {r42_med:.4f})")
    print(f"  EC M6/M2^3   = 6.04   (Maass: {r63_med:.4f})")
    print(f"  EC M8/M2^4   = 18.8   (Maass: {r84_med:.4f})")

    print(f"\nDeviation from Catalan (median):")
    for label, theory, obs in [
        ("M4/M2^2", 2, r42_med),
        ("M6/M2^3", 5, r63_med),
        ("M8/M2^4", 14, r84_med),
    ]:
        pct = 100 * (obs - theory) / theory
        print(f"  {label}: {obs:.4f} vs {theory}  ({pct:+.2f}%)")

    print(f"\nStability by prime count (median):")
    for k, v in stability.items():
        print(f"  {k} primes ({v['n_forms']} forms): "
              f"r42={v['M4_over_M2_sq_median']:.3f}, "
              f"r63={v['M6_over_M2_cu_median']:.3f}, "
              f"r84={v['M8_over_M2_qu_median']:.3f}")

    print(f"\nStability by level (median):")
    for k, v in level_stability.items():
        print(f"  {k} ({v['n_forms']} forms): "
              f"r42={v['M4_over_M2_sq_median']:.3f}, "
              f"r63={v['M6_over_M2_cu_median']:.3f}, "
              f"r84={v['M8_over_M2_qu_median']:.3f}")

    # ---------------------------------------------------------------------------
    # Save results
    # ---------------------------------------------------------------------------
    results = {
        "analysis": "maass_higher_moments_catalan_chain",
        "description": "Even moment ratios M_{2k}/M_2^k for Maass Hecke eigenvalues at good primes",
        "theory": {
            "distribution": "Sato-Tate (semicircle on [-2,2])",
            "catalan_numbers": {"C2": 2, "C3": 5, "C4": 14},
            "M2_expected": 1.0,
        },
        "data_summary": {
            "total_forms": len(data),
            "forms_analyzed": n_forms,
            "min_primes_required": MIN_PRIMES,
        },
        "pooled_results": pooled_ratios,
        "per_form_ratio_stats": ratio_stats,
        "per_form_moment_stats": moment_stats,
        "stability_by_prime_count": stability,
        "stability_by_level": level_stability,
        "comparison_to_ec": {
            "ec_M4_over_M2_sq": 2.32,
            "ec_M6_over_M2_cu": 6.04,
            "ec_M8_over_M2_qu": 18.8,
            "note": "EC ratios exceed Catalan due to rank/torsion effects shifting the distribution",
        },
        "verdict": {},
        "top_50_forms": sorted(form_results, key=lambda x: x["n_good_primes"], reverse=True)[:50],
    }

    # Build verdict using median (robust to outliers)
    for label, theory_val, med_key, trim_key in [
        ("M4/M2^2", 2, "M4_over_M2_sq_median", "M4_over_M2_sq_trimmed_mean"),
        ("M6/M2^3", 5, "M6_over_M2_cu_median", "M6_over_M2_cu_trimmed_mean"),
        ("M8/M2^4", 14, "M8_over_M2_qu_median", "M8_over_M2_qu_trimmed_mean"),
    ]:
        obs_med = pooled_ratios[med_key]
        obs_trim = pooled_ratios[trim_key]
        pct_med = 100 * (obs_med - theory_val) / theory_val
        pct_trim = 100 * (obs_trim - theory_val) / theory_val
        results["verdict"][label] = {
            "observed_median": obs_med,
            "observed_trimmed_mean": obs_trim,
            "theory_catalan": theory_val,
            "deviation_pct_median": round(pct_med, 4),
            "deviation_pct_trimmed": round(pct_trim, 4),
            "consistent": abs(pct_med) < 5,
        }

    out_path = os.path.join(os.path.dirname(__file__), "maass_higher_moments_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
