#!/usr/bin/env python3
"""
F22: Autocorrelation Phase Transition Index

For 5000 OEIS sequences with 50+ terms, compute autocorrelation at lags 1-15.
Define autocorrelation strength S = max(|AC(lag)|).
Classify: structured (S>0.5), random (S<0.1).
Measure distribution, threshold sharpness, correlations with growth rate and BM recurrence order.
"""

import json
import os
import numpy as np
from pathlib import Path
from collections import Counter

DATA_FILE = Path(__file__).parent.parent / "oeis" / "data" / "stripped_new.txt"
OUT_FILE = Path(__file__).parent / "ac_phase_transition_results.json"
PLOT_FILE = Path(__file__).parent / "ac_phase_transition.png"

MAX_SEQS = 5000
MIN_TERMS = 50
MAX_LAGS = 15


def parse_sequences(path, max_seqs=MAX_SEQS, min_terms=MIN_TERMS):
    """Parse OEIS stripped file, return dict of {A-number: [int list]}."""
    seqs = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) != 2:
                continue
            a_num = parts[0]
            vals_str = parts[1].strip().rstrip(",").lstrip(",")
            if not vals_str:
                continue
            try:
                vals = [int(x) for x in vals_str.split(",") if x.strip() != ""]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                seqs[a_num] = vals
            if len(seqs) >= max_seqs:
                break
    return seqs


def autocorrelation(x, max_lag=MAX_LAGS):
    """Compute normalized autocorrelation at lags 1..max_lag."""
    x = np.array(x, dtype=np.float64)
    n = len(x)
    mu = np.mean(x)
    var = np.var(x)
    if var == 0:
        return np.zeros(max_lag)
    x_centered = x - mu
    ac = np.zeros(max_lag)
    for lag in range(1, max_lag + 1):
        if lag >= n:
            break
        ac[lag - 1] = np.sum(x_centered[:n - lag] * x_centered[lag:]) / (n * var)
    return ac


def estimate_bm_recurrence_order(x, max_order=10):
    """
    Estimate Berlekamp-Massey style linear recurrence order.
    Try fitting x[n] = sum(c_i * x[n-i]) for orders 1..max_order.
    Return the smallest order where residual is < 1e-6 of variance,
    or max_order+1 if none fits.
    """
    x = np.array(x, dtype=np.float64)
    n = len(x)
    var = np.var(x)
    if var == 0:
        return 0  # constant sequence

    for order in range(1, max_order + 1):
        if order + order >= n:
            return max_order + 1
        # Build Toeplitz system
        rows = n - order
        A = np.zeros((rows, order))
        b = x[order:order + rows]
        for i in range(rows):
            for j in range(order):
                A[i, j] = x[order + i - j - 1]
        try:
            coeffs, residuals, rank, sv = np.linalg.lstsq(A, b, rcond=None)
            pred = A @ coeffs
            resid_var = np.var(b - pred)
            if resid_var / var < 1e-6:
                return order
        except np.linalg.LinAlgError:
            continue
    return max_order + 1


def estimate_growth_rate(x):
    """
    Estimate growth rate as log-ratio of last quartile mean to first quartile mean.
    Returns log growth rate (0 = constant, positive = growing, negative = shrinking).
    """
    x = np.array(x, dtype=np.float64)
    n = len(x)
    q = n // 4
    if q < 2:
        return 0.0
    first_q = np.abs(x[:q])
    last_q = np.abs(x[-q:])
    m1 = np.mean(first_q) + 1e-15
    m2 = np.mean(last_q) + 1e-15
    return float(np.log(m2 / m1))


def main():
    print(f"Loading sequences from {DATA_FILE} ...")
    seqs = parse_sequences(DATA_FILE)
    print(f"Loaded {len(seqs)} sequences with >= {MIN_TERMS} terms")

    results_per_seq = {}
    S_values = []
    bm_orders = []
    growth_rates = []
    ac_matrices = []

    for i, (a_num, vals) in enumerate(seqs.items()):
        if i % 500 == 0:
            print(f"  Processing {i}/{len(seqs)} ...")

        ac = autocorrelation(vals)
        S = float(np.max(np.abs(ac)))
        bm = estimate_bm_recurrence_order(vals)
        gr = estimate_growth_rate(vals)

        S_values.append(S)
        bm_orders.append(bm)
        growth_rates.append(gr)
        ac_matrices.append(ac.tolist())

        results_per_seq[a_num] = {
            "S": round(S, 6),
            "bm_order": bm,
            "growth_rate": round(gr, 4),
            "ac_lags": [round(v, 6) for v in ac],
            "n_terms": len(vals),
        }

    S_arr = np.array(S_values)
    bm_arr = np.array(bm_orders)
    gr_arr = np.array(growth_rates)

    # Classification
    n_structured = int(np.sum(S_arr > 0.5))
    n_random = int(np.sum(S_arr < 0.1))
    n_intermediate = int(np.sum((S_arr >= 0.1) & (S_arr <= 0.5)))

    frac_structured = n_structured / len(S_arr)
    frac_random = n_random / len(S_arr)
    frac_intermediate = n_intermediate / len(S_arr)

    # Distribution shape analysis
    hist_counts, hist_edges = np.histogram(S_arr, bins=50, range=(0, 1))
    hist_centers = 0.5 * (hist_edges[:-1] + hist_edges[1:])

    # Check for bimodality: is there a valley between two peaks?
    peak_indices = []
    for i in range(1, len(hist_counts) - 1):
        if hist_counts[i] > hist_counts[i - 1] and hist_counts[i] > hist_counts[i + 1]:
            peak_indices.append(i)

    is_bimodal = len(peak_indices) >= 2

    # Entropy of distribution (normalized)
    p = hist_counts / hist_counts.sum()
    p_nonzero = p[p > 0]
    entropy = float(-np.sum(p_nonzero * np.log2(p_nonzero)))
    max_entropy = np.log2(len(hist_counts))
    normalized_entropy = entropy / max_entropy

    # Correlations: S vs BM order, S vs growth rate
    # Filter out BM order = max+1 (no fit) for correlation
    finite_bm = bm_arr <= 10
    if np.sum(finite_bm) > 10:
        corr_s_bm = float(np.corrcoef(S_arr[finite_bm], bm_arr[finite_bm])[0, 1])
    else:
        corr_s_bm = None

    finite_gr = np.isfinite(gr_arr)
    if np.sum(finite_gr) > 10:
        corr_s_gr = float(np.corrcoef(S_arr[finite_gr], gr_arr[finite_gr])[0, 1])
    else:
        corr_s_gr = None

    # Mean S by BM order bucket
    s_by_bm = {}
    for order in range(0, 12):
        mask = bm_arr == order
        if np.sum(mask) > 0:
            s_by_bm[str(order)] = {
                "count": int(np.sum(mask)),
                "mean_S": round(float(np.mean(S_arr[mask])), 4),
                "std_S": round(float(np.std(S_arr[mask])), 4),
            }

    # Growth rate quartiles vs S
    gr_finite = gr_arr[finite_gr]
    s_finite = S_arr[finite_gr]
    if len(gr_finite) > 40:
        quartiles = np.percentile(gr_finite, [25, 50, 75])
        gr_q_labels = ["Q1_slow", "Q2", "Q3", "Q4_fast"]
        gr_bins = [-np.inf] + list(quartiles) + [np.inf]
        s_by_growth = {}
        for qi in range(4):
            mask = (gr_finite >= gr_bins[qi]) & (gr_finite < gr_bins[qi + 1])
            if np.sum(mask) > 0:
                s_by_growth[gr_q_labels[qi]] = {
                    "count": int(np.sum(mask)),
                    "mean_S": round(float(np.mean(s_finite[mask])), 4),
                }
    else:
        s_by_growth = {}

    # Dominant lag analysis
    dominant_lags = []
    for ac in ac_matrices:
        ac_abs = np.abs(ac)
        dominant_lags.append(int(np.argmax(ac_abs)) + 1)  # 1-indexed
    lag_counter = Counter(dominant_lags)

    # Summary
    summary = {
        "n_sequences": len(S_arr),
        "min_terms_required": MIN_TERMS,
        "max_lags": MAX_LAGS,
        "classification": {
            "structured_gt05": n_structured,
            "random_lt01": n_random,
            "intermediate": n_intermediate,
            "frac_structured": round(frac_structured, 4),
            "frac_random": round(frac_random, 4),
            "frac_intermediate": round(frac_intermediate, 4),
        },
        "distribution_shape": {
            "mean_S": round(float(np.mean(S_arr)), 4),
            "median_S": round(float(np.median(S_arr)), 4),
            "std_S": round(float(np.std(S_arr)), 4),
            "skewness": round(float(((S_arr - np.mean(S_arr)) ** 3).mean() / (np.std(S_arr) ** 3 + 1e-15)), 4),
            "is_bimodal": is_bimodal,
            "n_histogram_peaks": len(peak_indices),
            "peak_S_values": [round(float(hist_centers[i]), 3) for i in peak_indices],
            "normalized_entropy": round(normalized_entropy, 4),
        },
        "correlations": {
            "S_vs_bm_order": round(corr_s_bm, 4) if corr_s_bm is not None else None,
            "S_vs_growth_rate": round(corr_s_gr, 4) if corr_s_gr is not None else None,
        },
        "S_by_bm_order": s_by_bm,
        "S_by_growth_quartile": s_by_growth,
        "dominant_lag_distribution": {str(k): v for k, v in sorted(lag_counter.items())},
        "histogram": {
            "bin_centers": [round(float(c), 3) for c in hist_centers],
            "counts": [int(c) for c in hist_counts],
        },
        "percentiles": {
            "p5": round(float(np.percentile(S_arr, 5)), 4),
            "p25": round(float(np.percentile(S_arr, 25)), 4),
            "p50": round(float(np.percentile(S_arr, 50)), 4),
            "p75": round(float(np.percentile(S_arr, 75)), 4),
            "p95": round(float(np.percentile(S_arr, 95)), 4),
        },
        "top_10_most_structured": [],
        "top_10_most_random": [],
    }

    # Top/bottom examples
    sorted_by_s = sorted(results_per_seq.items(), key=lambda x: x[1]["S"], reverse=True)
    summary["top_10_most_structured"] = [
        {"id": a, "S": d["S"], "bm_order": d["bm_order"], "growth_rate": d["growth_rate"]}
        for a, d in sorted_by_s[:10]
    ]
    summary["top_10_most_random"] = [
        {"id": a, "S": d["S"], "bm_order": d["bm_order"], "growth_rate": d["growth_rate"]}
        for a, d in sorted_by_s[-10:]
    ]

    # Save results
    with open(OUT_FILE, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("F22: Autocorrelation Phase Transition Index (OEIS)", fontsize=14, fontweight="bold")

        # 1. Histogram of S
        ax = axes[0, 0]
        ax.bar(hist_centers, hist_counts, width=0.02, color="steelblue", edgecolor="navy", alpha=0.8)
        ax.axvline(0.5, color="red", ls="--", lw=1.5, label="Structured threshold (0.5)")
        ax.axvline(0.1, color="green", ls="--", lw=1.5, label="Random threshold (0.1)")
        ax.set_xlabel("Autocorrelation Strength S = max|AC(lag)|")
        ax.set_ylabel("Count")
        ax.set_title(f"Distribution of S (n={len(S_arr)})")
        ax.legend(fontsize=8)

        # 2. CDF of S
        ax = axes[0, 1]
        s_sorted = np.sort(S_arr)
        cdf = np.arange(1, len(s_sorted) + 1) / len(s_sorted)
        ax.plot(s_sorted, cdf, color="steelblue", lw=2)
        ax.axvline(0.5, color="red", ls="--", lw=1, alpha=0.7)
        ax.axvline(0.1, color="green", ls="--", lw=1, alpha=0.7)
        ax.set_xlabel("S")
        ax.set_ylabel("CDF")
        ax.set_title("Cumulative Distribution of S")
        ax.grid(True, alpha=0.3)

        # 3. S vs BM order (box plot style)
        ax = axes[1, 0]
        bm_unique = sorted(set(bm_arr))
        bp_data = []
        bp_labels = []
        for o in bm_unique:
            mask = bm_arr == o
            if np.sum(mask) >= 3:
                bp_data.append(S_arr[mask])
                label = str(o) if o <= 10 else ">10"
                bp_labels.append(label)
        if bp_data:
            bp = ax.boxplot(bp_data, tick_labels=bp_labels, patch_artist=True)
            for patch in bp["boxes"]:
                patch.set_facecolor("lightskyblue")
        ax.set_xlabel("BM Recurrence Order")
        ax.set_ylabel("S")
        ax.set_title("S vs BM Recurrence Order")

        # 4. S vs growth rate (scatter)
        ax = axes[1, 1]
        gr_clipped = np.clip(gr_arr, -10, 20)
        ax.scatter(gr_clipped, S_arr, alpha=0.15, s=5, c="steelblue")
        ax.set_xlabel("Growth Rate (log-ratio, clipped)")
        ax.set_ylabel("S")
        ax.set_title(f"S vs Growth Rate (r={corr_s_gr:.3f})" if corr_s_gr else "S vs Growth Rate")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(PLOT_FILE, dpi=150, bbox_inches="tight")
        print(f"Plot saved to {PLOT_FILE}")
    except Exception as e:
        print(f"Plotting failed: {e}")

    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Sequences analyzed: {len(S_arr)}")
    print(f"Structured (S > 0.5): {n_structured} ({frac_structured:.1%})")
    print(f"Random (S < 0.1):     {n_random} ({frac_random:.1%})")
    print(f"Intermediate:         {n_intermediate} ({frac_intermediate:.1%})")
    print(f"Mean S: {np.mean(S_arr):.4f}, Median S: {np.median(S_arr):.4f}")
    print(f"Bimodal: {is_bimodal} ({len(peak_indices)} peaks)")
    print(f"Correlation S vs BM order: {corr_s_bm}")
    print(f"Correlation S vs growth:   {corr_s_gr}")
    print(f"Dominant lag distribution: {dict(sorted(lag_counter.items()))}")


if __name__ == "__main__":
    main()
