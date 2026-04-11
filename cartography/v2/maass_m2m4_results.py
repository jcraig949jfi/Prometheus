"""
Maass Form M2/M4 Verification — Confirm SU(2) Universality

For each Maass form, extract Hecke eigenvalues c_p at prime indices,
compute M2 = mean(c_p^2), M4 = mean(c_p^4), and the ratio M4/M2^2.

The LMFDB Maass coefficients are already normalized Hecke eigenvalues
satisfying c(p^2) = c(p)^2 - 1 and |c_p| <= 2 (Ramanujan bound).
No further sqrt(p) normalization is needed.

Theory predicts M4/M2^2 = 2.0 for SU(2) semicircle distribution on [-2,2].
Compare to EC result: M4/M2^2 = 1.991.
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import time

DATA_PATH = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUTPUT_PATH = Path(__file__).parent / "maass_m2m4_results.json"

def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return np.where(is_prime)[0]


def compute_moments(coefficients, primes_array, level=1):
    """Compute M2, M4, and ratio for a single form's coefficients.

    coefficients are already normalized Hecke eigenvalues in [-2,2].
    No sqrt(p) division needed. Excludes primes dividing the level (bad primes).
    """
    n_coeff = len(coefficients)
    mask = primes_array <= n_coeff
    usable_primes = primes_array[mask]
    # Exclude bad primes (p | level) — not governed by SU(2) Sato-Tate
    good_mask = np.array([level % p != 0 for p in usable_primes])
    usable_primes = usable_primes[good_mask]

    if len(usable_primes) < 10:
        return None

    coeff_arr = np.array(coefficients)
    c_p = coeff_arr[usable_primes - 1]  # p-1 because 0-indexed

    m2 = np.mean(c_p**2)
    m4 = np.mean(c_p**4)

    if m2 < 1e-15:
        return None

    ratio = m4 / (m2**2)
    return {
        "m2": float(m2),
        "m4": float(m4),
        "ratio": float(ratio),
        "n_primes_used": int(len(usable_primes)),
        "max_prime": int(usable_primes[-1]),
    }


def main():
    t0 = time.time()
    print(f"Loading data from {DATA_PATH}...")
    with open(DATA_PATH, "r") as f:
        forms = json.load(f)
    print(f"Loaded {len(forms)} forms in {time.time()-t0:.1f}s")

    # Precompute primes up to 6000
    MAX_N = 6000
    primes = sieve_primes(MAX_N)
    print(f"Using {len(primes)} primes up to {primes[-1]}")

    # Per-form results
    all_ratios = []
    all_m2 = []
    all_m4 = []
    per_form = []

    # Stratification buckets
    by_symmetry = defaultdict(list)  # sym -> list of ratios
    by_level = defaultdict(list)     # level -> list of ratios
    by_spectral_bin = defaultdict(list)  # bin -> list of ratios

    skipped = 0
    for i, form in enumerate(forms):
        coefficients = form.get("coefficients", [])
        level = int(form.get("level", 1))
        result = compute_moments(coefficients, primes, level=level)
        if result is None:
            skipped += 1
            continue

        ratio = result["ratio"]
        m2 = result["m2"]
        m4 = result["m4"]

        all_ratios.append(ratio)
        all_m2.append(m2)
        all_m4.append(m4)

        sym = form.get("symmetry", "unknown")
        R = float(form.get("spectral_parameter", 0))

        by_symmetry[str(sym)].append(ratio)
        by_level[int(level)].append(ratio)

        # Spectral parameter bins: [0,1), [1,2), [2,4), [4,7), [7,10), [10+)
        if R < 1:
            sbin = "R<1"
        elif R < 2:
            sbin = "1<=R<2"
        elif R < 4:
            sbin = "2<=R<4"
        elif R < 7:
            sbin = "4<=R<7"
        elif R < 10:
            sbin = "7<=R<10"
        else:
            sbin = "R>=10"
        by_spectral_bin[sbin].append(ratio)

        per_form.append({
            "maass_id": form.get("maass_id"),
            "level": int(level),
            "symmetry": int(sym) if isinstance(sym, (int, float)) else sym,
            "spectral_parameter": float(R),
            "m2": m2,
            "m4": m4,
            "ratio": ratio,
            "n_primes_used": result["n_primes_used"],
        })

    all_ratios = np.array(all_ratios)
    all_m2 = np.array(all_m2)
    all_m4 = np.array(all_m4)

    # Trimmed mean (1%-99%) for robustness against outliers
    lo, hi = np.percentile(all_ratios, [1, 99])
    trimmed = all_ratios[(all_ratios >= lo) & (all_ratios <= hi)]

    # Global statistics
    global_stats = {
        "n_forms_analyzed": len(all_ratios),
        "n_forms_skipped": skipped,
        "mean_ratio": float(np.mean(all_ratios)),
        "trimmed_mean_ratio_1_99": float(np.mean(trimmed)),
        "median_ratio": float(np.median(all_ratios)),
        "std_ratio": float(np.std(all_ratios)),
        "mean_m2": float(np.mean(all_m2)),
        "mean_m4": float(np.mean(all_m4)),
        "theory_prediction": 2.0,
        "ec_comparison": 1.991,
        "deviation_from_theory_pct": float(abs(np.mean(trimmed) - 2.0) / 2.0 * 100),
    }

    print(f"\n{'='*60}")
    print(f"GLOBAL RESULTS ({global_stats['n_forms_analyzed']} forms, {skipped} skipped)")
    print(f"{'='*60}")
    print(f"Mean M4/M2^2 ratio:      {global_stats['mean_ratio']:.6f}")
    print(f"Trimmed mean (1-99%):    {global_stats['trimmed_mean_ratio_1_99']:.6f}")
    print(f"Median M4/M2^2 ratio:    {global_stats['median_ratio']:.6f}")
    print(f"Std of ratio:            {global_stats['std_ratio']:.6f}")
    print(f"Theory (SU(2)):          2.000000")
    print(f"EC comparison:           1.991")
    print(f"Deviation from 2.0:      {global_stats['deviation_from_theory_pct']:.4f}%")

    # Stratification: symmetry
    sym_stats = {}
    print(f"\n{'='*60}")
    print("STRATIFIED BY SYMMETRY")
    print(f"{'='*60}")
    for sym, ratios in sorted(by_symmetry.items()):
        arr = np.array(ratios)
        label = "even" if sym == "1" else ("odd" if sym == "-1" else sym)
        stats = {
            "label": label,
            "n": len(arr),
            "mean_ratio": float(np.mean(arr)),
            "median_ratio": float(np.median(arr)),
            "std_ratio": float(np.std(arr)),
        }
        sym_stats[sym] = stats
        print(f"  Symmetry {label} (n={stats['n']}): mean={stats['mean_ratio']:.6f}, "
              f"median={stats['median_ratio']:.6f}, std={stats['std_ratio']:.6f}")

    # Stratification: spectral parameter
    spectral_stats = {}
    print(f"\n{'='*60}")
    print("STRATIFIED BY SPECTRAL PARAMETER")
    print(f"{'='*60}")
    for sbin in ["R<1", "1<=R<2", "2<=R<4", "4<=R<7", "7<=R<10", "R>=10"]:
        if sbin not in by_spectral_bin:
            continue
        arr = np.array(by_spectral_bin[sbin])
        stats = {
            "n": len(arr),
            "mean_ratio": float(np.mean(arr)),
            "median_ratio": float(np.median(arr)),
            "std_ratio": float(np.std(arr)),
        }
        spectral_stats[sbin] = stats
        print(f"  {sbin:12s} (n={stats['n']:5d}): mean={stats['mean_ratio']:.6f}, "
              f"median={stats['median_ratio']:.6f}, std={stats['std_ratio']:.6f}")

    # Stratification: level (top levels by count)
    level_stats = {}
    print(f"\n{'='*60}")
    print("STRATIFIED BY LEVEL (top 15 by count)")
    print(f"{'='*60}")
    level_counts = sorted(by_level.items(), key=lambda x: -len(x[1]))
    for level, ratios in level_counts[:15]:
        arr = np.array(ratios)
        stats = {
            "n": len(arr),
            "mean_ratio": float(np.mean(arr)),
            "median_ratio": float(np.median(arr)),
            "std_ratio": float(np.std(arr)),
        }
        level_stats[str(level)] = stats
        print(f"  Level {level:5d} (n={stats['n']:4d}): mean={stats['mean_ratio']:.6f}, "
              f"median={stats['median_ratio']:.6f}, std={stats['std_ratio']:.6f}")

    # All levels summary
    all_level_means = [float(np.mean(r)) for r in by_level.values() if len(r) >= 5]
    print(f"\n  All levels with n>=5: {len(all_level_means)} levels, "
          f"mean of means = {np.mean(all_level_means):.6f}, "
          f"std of means = {np.std(all_level_means):.6f}")

    # Percentile distribution of ratios
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    pct_values = {str(p): float(np.percentile(all_ratios, p)) for p in percentiles}
    print(f"\n{'='*60}")
    print("RATIO DISTRIBUTION PERCENTILES")
    print(f"{'='*60}")
    for p in percentiles:
        print(f"  {p:3d}th percentile: {pct_values[str(p)]:.6f}")

    # Save results
    output = {
        "description": "Maass form M2/M4 moment ratio analysis — SU(2) universality test",
        "theory": "M4/M2^2 = 2.0 for SU(2) semicircle (Sato-Tate)",
        "normalization": "c_p already normalized Hecke eigenvalues in [-2,2]; no sqrt(p) needed",
        "primes_used": f"all primes up to min(n_coefficients, {MAX_N})",
        "n_primes_available": int(len(primes)),
        "global": global_stats,
        "by_symmetry": sym_stats,
        "by_spectral_parameter": spectral_stats,
        "by_level_top15": level_stats,
        "all_level_means_summary": {
            "n_levels_with_5plus": len(all_level_means),
            "mean_of_means": float(np.mean(all_level_means)),
            "std_of_means": float(np.std(all_level_means)),
        },
        "ratio_percentiles": pct_values,
        "per_form_summary": per_form,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")
    print(f"Total time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
