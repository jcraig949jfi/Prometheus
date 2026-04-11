#!/usr/bin/env python3
"""
Igusa Invariant Mod-p Equidistribution (List2 #12)
===================================================
Reduce absolute Igusa-Clebsch invariants [I2, I4, I6, I10] modulo primes p < 50.
Measure uniformity of joint and marginal distributions.

Data: LMFDB PostgreSQL dump of g2c_curves (66,158 curves).
"""

import json
import sys
import os
from collections import Counter
from math import sqrt, log
from pathlib import Path

DUMP_PATH = Path(__file__).resolve().parent.parent / "lmfdb_dump" / "g2c_curves.json"
OUT_PATH = Path(__file__).resolve().parent / "igusa_modp_equidist_results.json"

PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
INVARIANT_NAMES = ["I2", "I4", "I6", "I10"]


def parse_ic(raw):
    """Parse igusa_clebsch_inv string to list of ints."""
    if isinstance(raw, list):
        parts = raw
    elif isinstance(raw, str):
        s = raw.strip()
        if s.startswith('[') and s.endswith(']'):
            s = s[1:-1]
        parts = [p.strip().strip("'\"") for p in s.split(',')]
    else:
        return None
    if len(parts) != 4:
        return None
    try:
        return [int(x) for x in parts]
    except (ValueError, TypeError):
        return None


def load_curves():
    """Load igusa-clebsch invariants from the LMFDB dump."""
    print(f"Loading from {DUMP_PATH} ...")
    with open(DUMP_PATH, 'r') as f:
        data = json.load(f)

    records = data.get("records", [])
    print(f"  Total records: {len(records)}")

    invariants = []
    failures = 0
    for rec in records:
        ic = parse_ic(rec.get("igusa_clebsch_inv"))
        if ic is not None:
            invariants.append(ic)
        else:
            failures += 1

    print(f"  Parsed: {len(invariants)}, failures: {failures}")
    return invariants


def chi_squared_uniform(counts, expected_per_bin):
    """Chi-squared statistic against uniform distribution."""
    chi2 = 0.0
    for c in counts.values():
        chi2 += (c - expected_per_bin) ** 2 / expected_per_bin
    # Include zero-count bins
    n_observed_bins = len(counts)
    return chi2


def ks_statistic_discrete(counts, total, n_bins):
    """
    KS statistic for discrete uniform distribution on n_bins values.
    Compare empirical CDF to uniform CDF.
    """
    # Sort bins and compute empirical CDF
    sorted_bins = sorted(counts.keys())
    all_bins = list(range(n_bins))

    ecdf = 0.0
    max_diff = 0.0
    bin_idx = 0

    for b in all_bins:
        ecdf += counts.get(b, 0) / total
        ucdf = (b + 1) / n_bins
        diff = abs(ecdf - ucdf)
        if diff > max_diff:
            max_diff = diff

    return max_diff


def analyze_prime(invariants, p):
    """Analyze mod-p distribution for a single prime."""
    n = len(invariants)

    # --- Joint distribution (I2, I4, I6, I10) mod p ---
    joint_counts = Counter()
    for ic in invariants:
        tup = tuple(v % p for v in ic)
        joint_counts[tup] += 1

    n_joint_bins = p ** 4
    expected_joint = n / n_joint_bins

    # Chi-squared for joint (only meaningful if n >> p^4)
    # For large p, p^4 >> n so chi-squared is degenerate
    # We still compute it but flag when n < p^4
    joint_chi2 = 0.0
    for tup, c in joint_counts.items():
        joint_chi2 += (c - expected_joint) ** 2 / expected_joint
    # Add contribution from empty bins
    n_empty = n_joint_bins - len(joint_counts)
    joint_chi2 += n_empty * (expected_joint ** 2) / expected_joint  # = n_empty * expected_joint

    joint_chi2_normalized = joint_chi2 / n_joint_bins  # per-bin

    # --- Marginal distributions ---
    marginal_results = {}
    marginal_ks = {}
    for i, name in enumerate(INVARIANT_NAMES):
        counts = Counter()
        for ic in invariants:
            counts[ic[i] % p] += 1

        expected = n / p

        # Chi-squared
        chi2 = 0.0
        for v in range(p):
            c = counts.get(v, 0)
            chi2 += (c - expected) ** 2 / expected

        # Normalized chi-squared (divide by df = p-1)
        chi2_norm = chi2 / (p - 1)

        # KS statistic
        ks = ks_statistic_discrete(counts, n, p)

        # Entropy
        entropy = 0.0
        for v in range(p):
            c = counts.get(v, 0)
            if c > 0:
                prob = c / n
                entropy -= prob * log(prob)
        max_entropy = log(p)
        entropy_ratio = entropy / max_entropy if max_entropy > 0 else 0.0

        marginal_results[name] = {
            "chi2": round(chi2, 4),
            "chi2_normalized": round(chi2_norm, 4),
            "ks": round(ks, 6),
            "entropy_ratio": round(entropy_ratio, 6),
            "top3_bins": sorted(counts.items(), key=lambda x: -x[1])[:3],
            "bottom3_bins": sorted(counts.items(), key=lambda x: x[1])[:3],
        }
        marginal_ks[name] = ks

    # --- Pairwise joint distributions ---
    pairwise = {}
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    for i, j in pairs:
        pair_name = f"{INVARIANT_NAMES[i]}_{INVARIANT_NAMES[j]}"
        counts = Counter()
        for ic in invariants:
            counts[(ic[i] % p, ic[j] % p)] += 1

        n_bins = p * p
        expected = n / n_bins

        chi2 = 0.0
        for tup, c in counts.items():
            chi2 += (c - expected) ** 2 / expected
        n_empty = n_bins - len(counts)
        chi2 += n_empty * expected

        chi2_norm = chi2 / (n_bins - 1)

        pairwise[pair_name] = {
            "chi2": round(chi2, 2),
            "chi2_normalized": round(chi2_norm, 4),
            "n_occupied_bins": len(counts),
            "n_total_bins": n_bins,
            "occupancy_fraction": round(len(counts) / n_bins, 4),
        }

    # Average marginal KS
    avg_ks = sum(marginal_ks.values()) / len(marginal_ks)

    return {
        "p": p,
        "n_curves": n,
        "joint_p4": n_joint_bins,
        "joint_feasible": n >= n_joint_bins,
        "joint_chi2_per_bin": round(joint_chi2_normalized, 6) if n >= n_joint_bins else None,
        "n_joint_occupied": len(joint_counts),
        "joint_occupancy_fraction": round(len(joint_counts) / n_joint_bins, 6),
        "marginals": marginal_results,
        "pairwise": pairwise,
        "avg_marginal_ks": round(avg_ks, 6),
        "max_marginal_ks": round(max(marginal_ks.values()), 6),
        "least_uniform_invariant": max(marginal_ks, key=marginal_ks.get),
        "most_uniform_invariant": min(marginal_ks, key=marginal_ks.get),
    }


def main():
    invariants = load_curves()
    n = len(invariants)

    results_by_prime = {}
    all_avg_ks = []
    trend_data = []

    print(f"\nAnalyzing mod-p equidistribution for {len(PRIMES)} primes, {n} curves\n")
    print(f"{'p':>4} | {'avg KS':>10} | {'max KS':>10} | {'least uniform':>14} | {'joint occ%':>10}")
    print("-" * 65)

    for p in PRIMES:
        result = analyze_prime(invariants, p)
        results_by_prime[str(p)] = result
        all_avg_ks.append(result["avg_marginal_ks"])
        trend_data.append({"p": p, "avg_ks": result["avg_marginal_ks"], "max_ks": result["max_marginal_ks"]})

        print(f"{p:>4} | {result['avg_marginal_ks']:>10.6f} | {result['max_marginal_ks']:>10.6f} | "
              f"{result['least_uniform_invariant']:>14} | "
              f"{result['joint_occupancy_fraction']:>10.4f}")

    # --- Trend analysis ---
    # Does equidistribution improve with p?
    # Compute correlation between p and avg_ks
    ps = [d["p"] for d in trend_data]
    ks_vals = [d["avg_ks"] for d in trend_data]

    mean_p = sum(ps) / len(ps)
    mean_ks = sum(ks_vals) / len(ks_vals)

    cov = sum((ps[i] - mean_p) * (ks_vals[i] - mean_ks) for i in range(len(ps)))
    var_p = sum((x - mean_p) ** 2 for x in ps)
    var_ks = sum((x - mean_ks) ** 2 for x in ks_vals)

    if var_p > 0 and var_ks > 0:
        corr = cov / sqrt(var_p * var_ks)
    else:
        corr = 0.0

    # Which invariant is most/least uniform overall?
    invariant_avg_ks = {name: 0.0 for name in INVARIANT_NAMES}
    for p_str, result in results_by_prime.items():
        for name in INVARIANT_NAMES:
            invariant_avg_ks[name] += result["marginals"][name]["ks"]
    for name in INVARIANT_NAMES:
        invariant_avg_ks[name] /= len(PRIMES)

    overall_least_uniform = max(invariant_avg_ks, key=invariant_avg_ks.get)
    overall_most_uniform = min(invariant_avg_ks, key=invariant_avg_ks.get)

    # --- Summary ---
    overall_avg_ks = sum(all_avg_ks) / len(all_avg_ks)

    print(f"\n{'='*65}")
    print(f"Overall average KS: {overall_avg_ks:.6f}")
    print(f"Trend (corr p vs avg_ks): {corr:.4f}")
    if corr < -0.3:
        print("  => Equidistribution IMPROVES with p (negative correlation)")
    elif corr > 0.3:
        print("  => Equidistribution WORSENS with p")
    else:
        print("  => No strong trend with p")

    print(f"\nInvariant uniformity ranking (avg KS across all primes):")
    for name, ks in sorted(invariant_avg_ks.items(), key=lambda x: x[1]):
        print(f"  {name}: {ks:.6f}")
    print(f"\n  Most uniform:  {overall_most_uniform}")
    print(f"  Least uniform: {overall_least_uniform}")

    # --- Output ---
    output = {
        "experiment": "Igusa Invariant Mod-p Equidistribution (List2 #12)",
        "n_curves": n,
        "primes": PRIMES,
        "overall_avg_ks": round(overall_avg_ks, 6),
        "expected_avg_ks": 0.012,
        "trend_p_vs_ks_correlation": round(corr, 4),
        "equidist_improves_with_p": corr < -0.3,
        "invariant_avg_ks": {k: round(v, 6) for k, v in invariant_avg_ks.items()},
        "most_uniform_invariant": overall_most_uniform,
        "least_uniform_invariant": overall_least_uniform,
        "results_by_prime": results_by_prime,
        "trend_data": trend_data,
        "verdict": None,  # filled below
    }

    # Verdict
    if overall_avg_ks < 0.02:
        verdict = f"PASS: avg KS = {overall_avg_ks:.4f} < 0.02, consistent with equidistribution"
    elif overall_avg_ks < 0.05:
        verdict = f"MARGINAL: avg KS = {overall_avg_ks:.4f}, weak equidistribution"
    else:
        verdict = f"FAIL: avg KS = {overall_avg_ks:.4f}, significant departure from uniformity"
    output["verdict"] = verdict
    print(f"\nVerdict: {verdict}")

    with open(OUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
