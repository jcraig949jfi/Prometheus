#!/usr/bin/env python3
"""
Hecke eigenvalue entropy scaling with level.

For each of the 17,314 dim-1 weight-2 modular forms in DuckDB:
  - Extract a_p at the first 25 primes (p = 2..97)
  - Compute Shannon entropy H of the empirical distribution of a_p values
    binned into 20 equal-width bins spanning the Hasse range [-2*sqrt(p_max), 2*sqrt(p_max)]
  - Fit H = h * log(N) + c  where N = level
  - Stratify by CM vs non-CM (proxy for Galois image class: ST group 1.2.1.d1 = CM)

Outputs:
  - cartography/v2/hecke_entropy_rate_results.json
  - cartography/v2/hecke_entropy_rate.png
"""

import json
import math
import sys
import os
import numpy as np
from scipy import stats

# ── Configuration ──────────────────────────────────────────────────────────
NUM_PRIMES = 25
NUM_BINS = 20
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "charon", "data", "charon.duckdb")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# First 25 primes
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]
P_MAX = PRIMES_25[-1]  # 97
HASSE_BOUND = 2 * math.sqrt(P_MAX)  # ~19.7


def shannon_entropy(values, num_bins, bin_range):
    """Compute Shannon entropy (bits) of empirical distribution via histogram."""
    counts, _ = np.histogram(values, bins=num_bins, range=bin_range)
    # Normalize to probabilities
    total = counts.sum()
    if total == 0:
        return 0.0
    probs = counts / total
    # H = -sum p_i log2(p_i), ignoring zero bins
    mask = probs > 0
    return -np.sum(probs[mask] * np.log2(probs[mask]))


def main():
    import duckdb

    con = duckdb.connect(DB_PATH, read_only=True)

    # Pull all dim-1 weight-2 forms
    rows = con.execute("""
        SELECT level, ap_coeffs, is_cm, sato_tate_group
        FROM modular_forms
        WHERE dim = 1 AND weight = 2
        ORDER BY level
    """).fetchall()
    con.close()

    print(f"Loaded {len(rows)} forms")

    bin_range = (-HASSE_BOUND, HASSE_BOUND)
    levels = []
    entropies = []
    cm_flags = []
    st_groups = []
    skipped = 0

    for level, ap_json, is_cm, st_group in rows:
        if ap_json is None:
            skipped += 1
            continue
        ap_list = json.loads(ap_json)
        if len(ap_list) < NUM_PRIMES:
            skipped += 1
            continue

        # Extract a_p for first 25 primes (dim=1 so each entry is [val])
        a_p = np.array([ap_list[i][0] for i in range(NUM_PRIMES)], dtype=float)

        H = shannon_entropy(a_p, NUM_BINS, bin_range)

        levels.append(level)
        entropies.append(H)
        cm_flags.append(bool(is_cm))
        st_groups.append(st_group or "unknown")

    print(f"Computed entropy for {len(levels)} forms (skipped {skipped})")

    levels = np.array(levels, dtype=float)
    entropies = np.array(entropies)
    cm_flags = np.array(cm_flags)
    log_levels = np.log(levels)

    # ── Global fit: H = h * log(N) + c ───────────────────────────────────
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_levels, entropies)
    print(f"\nGlobal fit: H = {slope:.6f} * log(N) + {intercept:.4f}")
    print(f"  R^2 = {r_value**2:.6f}, p = {p_value:.2e}, SE(h) = {std_err:.6f}")

    results = {
        "description": "Shannon entropy of Hecke eigenvalue distributions vs level",
        "config": {
            "num_primes": NUM_PRIMES,
            "primes": PRIMES_25,
            "num_bins": NUM_BINS,
            "hasse_bound": round(HASSE_BOUND, 4),
            "bin_range": [round(-HASSE_BOUND, 4), round(HASSE_BOUND, 4)],
        },
        "n_forms": len(levels),
        "global_fit": {
            "h_entropy_growth_coeff": round(slope, 6),
            "intercept": round(intercept, 4),
            "R_squared": round(r_value ** 2, 6),
            "p_value": float(f"{p_value:.4e}"),
            "std_err_h": round(std_err, 6),
        },
        "stratified": {},
    }

    # ── Stratify by Galois image proxy (CM vs non-CM / Sato-Tate) ────────
    unique_st = sorted(set(st_groups))
    labels_map = {
        "1.2.3.c1": "non-CM (SU(2))",
        "1.2.1.d1": "CM",
    }

    for st in unique_st:
        mask = np.array([s == st for s in st_groups])
        n = mask.sum()
        if n < 10:
            continue
        sl, ic, rv, pv, se = stats.linregress(log_levels[mask], entropies[mask])
        label = labels_map.get(st, st)
        print(f"\n{label} (n={n}): H = {sl:.6f} * log(N) + {ic:.4f}, R^2 = {rv**2:.6f}")
        results["stratified"][label] = {
            "sato_tate_group": st,
            "n_forms": int(n),
            "h_entropy_growth_coeff": round(sl, 6),
            "intercept": round(ic, 4),
            "R_squared": round(rv ** 2, 6),
            "p_value": float(f"{pv:.4e}"),
            "std_err_h": round(se, 6),
            "mean_entropy": round(float(entropies[mask].mean()), 4),
            "std_entropy": round(float(entropies[mask].std()), 4),
        }

    # Also add CM vs non-CM summary
    for flag, label in [(True, "CM"), (False, "non-CM")]:
        mask = cm_flags == flag
        n = mask.sum()
        if n < 5:
            continue
        results["stratified"][label + "_summary"] = {
            "n_forms": int(n),
            "mean_entropy": round(float(entropies[mask].mean()), 4),
            "std_entropy": round(float(entropies[mask].std()), 4),
            "mean_level": round(float(levels[mask].mean()), 1),
        }

    # ── Binned means for cleaner visualization ───────────────────────────
    log_bin_edges = np.linspace(log_levels.min(), log_levels.max(), 30)
    bin_centers = []
    bin_means = []
    bin_stds = []
    bin_counts = []
    for i in range(len(log_bin_edges) - 1):
        mask = (log_levels >= log_bin_edges[i]) & (log_levels < log_bin_edges[i + 1])
        if mask.sum() > 0:
            bin_centers.append(float((log_bin_edges[i] + log_bin_edges[i + 1]) / 2))
            bin_means.append(float(entropies[mask].mean()))
            bin_stds.append(float(entropies[mask].std()))
            bin_counts.append(int(mask.sum()))

    results["binned_trend"] = {
        "log_level_centers": [round(x, 3) for x in bin_centers],
        "mean_entropy": [round(x, 4) for x in bin_means],
        "std_entropy": [round(x, 4) for x in bin_stds],
        "counts": bin_counts,
    }

    # ── Save results ─────────────────────────────────────────────────────
    out_json = os.path.join(OUT_DIR, "hecke_entropy_rate_results.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_json}")

    # ── Plot ──────────────────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Left panel: scatter + fit
        ax = axes[0]
        non_cm = ~cm_flags
        ax.scatter(log_levels[non_cm], entropies[non_cm], alpha=0.05, s=3,
                   color="steelblue", label=f"non-CM (n={non_cm.sum()})", rasterized=True)
        ax.scatter(log_levels[cm_flags], entropies[cm_flags], alpha=0.3, s=8,
                   color="crimson", label=f"CM (n={cm_flags.sum()})", rasterized=True)

        x_fit = np.linspace(log_levels.min(), log_levels.max(), 100)
        ax.plot(x_fit, slope * x_fit + intercept, "k-", lw=2,
                label=f"H = {slope:.4f} log(N) + {intercept:.2f}")
        ax.set_xlabel("log(level)")
        ax.set_ylabel("Shannon entropy H (bits)")
        ax.set_title("Hecke eigenvalue entropy vs level")
        ax.legend(fontsize=9)

        # Right panel: binned means with error bars
        ax2 = axes[1]
        ax2.errorbar(bin_centers, bin_means, yerr=bin_stds, fmt="o-",
                     color="steelblue", capsize=3, markersize=4)
        ax2.plot(x_fit, slope * x_fit + intercept, "k--", lw=1.5, alpha=0.7,
                 label=f"h = {slope:.4f}")
        ax2.set_xlabel("log(level)")
        ax2.set_ylabel("Mean Shannon entropy H (bits)")
        ax2.set_title("Binned entropy trend")
        ax2.legend()

        plt.tight_layout()
        out_png = os.path.join(OUT_DIR, "hecke_entropy_rate.png")
        plt.savefig(out_png, dpi=150)
        print(f"Plot saved to {out_png}")
        plt.close()
    except ImportError:
        print("matplotlib not available; skipping plot")

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"ENTROPY GROWTH COEFFICIENT h = {slope:.6f} +/- {std_err:.6f}")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    main()
