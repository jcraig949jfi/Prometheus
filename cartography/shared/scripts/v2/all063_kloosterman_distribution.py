"""
ALL-063: Kloosterman Sum Distribution
=======================================
Compute Kloosterman sums S(1,1;p) for primes p ≤ 1000.
Compare the normalized distribution S(1,1;p)/2√p against
the Sato-Tate semicircle law.

Also: compute S(a,b;p) for a,b ∈ {1..5} and test universality.
"""
import json, time, math
import numpy as np
from scipy import stats
from pathlib import Path
from collections import Counter

V2 = Path(__file__).resolve().parent
OUT = V2 / "all063_kloosterman_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def mod_inverse(a, p):
    return pow(a, p - 2, p)

def kloosterman_sum(a, b, p):
    """Compute S(a,b;p) = sum_{x=1}^{p-1} e^{2πi(ax + bx^{-1})/p}."""
    total = 0.0
    for x in range(1, p):
        x_inv = mod_inverse(x, p)
        angle = 2 * math.pi * (a * x + b * x_inv) / p
        total += math.cos(angle)
    return total

def main():
    t0 = time.time()
    print("=== ALL-063: Kloosterman Sum Distribution ===\n")

    primes = sieve(500)
    print(f"  {len(primes)} primes up to 500")

    # Phase 1: S(1,1;p) for all primes
    print("\n[1] Computing S(1,1;p)...")
    results_11 = []
    normalized = []
    for p in primes:
        s = kloosterman_sum(1, 1, p)
        bound = 2 * math.sqrt(p)
        norm = s / bound
        results_11.append({"prime": p, "S": round(s, 4), "normalized": round(norm, 6)})
        normalized.append(norm)
        if p <= 47:
            print(f"    S(1,1;{p}) = {s:.2f}, normalized = {norm:.4f}")

    norm_arr = np.array(normalized)
    print(f"\n  Normalized stats: mean={norm_arr.mean():.4f}, std={norm_arr.std():.4f}")
    print(f"  Range: [{norm_arr.min():.4f}, {norm_arr.max():.4f}]")
    print(f"  Fraction |x| > 1: {np.mean(np.abs(norm_arr) > 1):.4f} (should be 0 by Weil bound)")

    # Sato-Tate semicircle test: density ∝ √(1-x²)
    print("\n[2] Sato-Tate semicircle test...")
    # KS test against semicircle CDF: F(x) = (1/π)(arcsin(x) + x√(1-x²)) + 1/2
    def st_cdf(x):
        x = np.clip(x, -1, 1)
        return (np.arcsin(x) + x * np.sqrt(1 - x**2)) / np.pi + 0.5

    ks_stat, ks_p = stats.kstest(norm_arr, st_cdf)
    print(f"  KS test vs Sato-Tate: D={ks_stat:.4f}, p={ks_p:.4e}")

    # Also test vs uniform
    ks_unif_stat, ks_unif_p = stats.kstest(norm_arr, 'uniform', args=(-1, 2))
    print(f"  KS test vs Uniform[-1,1]: D={ks_unif_stat:.4f}, p={ks_unif_p:.4e}")

    # Histogram comparison
    hist, edges = np.histogram(norm_arr, bins=20, range=(-1, 1), density=True)
    bin_centers = (edges[:-1] + edges[1:]) / 2
    st_density = 2 / np.pi * np.sqrt(np.maximum(1 - bin_centers**2, 0))

    # Chi-squared vs ST
    expected = st_density * (edges[1] - edges[0]) * len(norm_arr)
    expected[expected < 1] = 1
    observed = hist * (edges[1] - edges[0]) * len(norm_arr)

    # Phase 2: Universality across (a,b)
    print("\n[3] Universality: S(a,b;p) for a,b ∈ {1..5}...")
    ab_results = {}
    small_primes = [p for p in primes if p <= 100]
    for a in range(1, 6):
        for b in range(1, 6):
            vals = []
            for p in small_primes:
                s = kloosterman_sum(a, b, p)
                vals.append(s / (2 * math.sqrt(p)))
            arr = np.array(vals)
            ks, p_val = stats.kstest(arr, st_cdf)
            ab_results[f"({a},{b})"] = {
                "mean": round(float(arr.mean()), 4),
                "std": round(float(arr.std()), 4),
                "ks_stat": round(float(ks), 4),
                "ks_pvalue": round(float(p_val), 4),
            }
    # How many (a,b) pairs pass ST test at p>0.05?
    n_pass = sum(1 for v in ab_results.values() if v["ks_pvalue"] > 0.05)
    print(f"  {n_pass}/25 (a,b) pairs consistent with Sato-Tate (KS p>0.05)")

    # Phase 3: Moments
    print("\n[4] Moment comparison...")
    empirical_moments = [round(float(np.mean(norm_arr**k)), 6) for k in range(1, 7)]
    # ST moments: M1=0, M2=1/4, M3=0, M4=1/8, M5=0, M6=5/64
    st_moments = [0, 0.25, 0, 0.125, 0, 5/64]
    print(f"  Empirical moments: {empirical_moments}")
    print(f"  ST moments:        {[round(m, 6) for m in st_moments]}")

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-063", "title": "Kloosterman Sum Distribution",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_primes": len(primes),
        "normalized_stats": {
            "mean": round(float(norm_arr.mean()), 6),
            "std": round(float(norm_arr.std()), 6),
            "range": [round(float(norm_arr.min()), 4), round(float(norm_arr.max()), 4)],
        },
        "sato_tate_test": {
            "ks_stat": round(float(ks_stat), 4),
            "ks_pvalue": round(float(ks_p), 4),
        },
        "uniform_test": {
            "ks_stat": round(float(ks_unif_stat), 4),
            "ks_pvalue": round(float(ks_unif_p), 4),
        },
        "empirical_moments": empirical_moments,
        "st_moments": [round(m, 6) for m in st_moments],
        "universality": {
            "n_ab_pairs_tested": 25,
            "n_pass_st": n_pass,
            "ab_results": ab_results,
        },
        "assessment": None,
    }

    if ks_p > 0.05:
        output["assessment"] = f"SATO-TATE CONFIRMED: S(1,1;p)/2√p follows semicircle law (KS p={ks_p:.3f}). {n_pass}/25 (a,b) pairs universal"
    elif ks_p > 0.001:
        output["assessment"] = f"WEAK SATO-TATE: marginal fit (KS p={ks_p:.4f}). Finite-prime effects visible"
    else:
        output["assessment"] = f"SATO-TATE REJECTED at this range (KS p={ks_p:.1e}). Need larger primes"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
