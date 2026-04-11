"""
Hecke Eigenvector Spatial Localization — Inverse Participation Ratio (IPR)

Measures whether modular forms are "localized" or "delocalized" in the
basis of normalized Hecke eigenvalues x_p = a_p / (2*sqrt(p)).

IPR = sum(x_p^4) / (sum(x_p^2))^2
  - IPR = 1/N  =>  fully delocalized (uniform across all sites)
  - IPR = 1    =>  fully localized (concentrated at one site)

Data: weight-2, dim-1 newforms from charon DuckDB.
"""

import json
import os
import sys
import numpy as np
import duckdb
from pathlib import Path
from sympy import primerange

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO / "charon" / "data" / "charon.duckdb"
OUT_JSON = Path(__file__).resolve().parent / "hecke_ipr_results.json"
N_PRIMES = 25  # first 25 primes

PRIMES = list(primerange(2, 200))[:N_PRIMES]  # 2,3,5,...,97
assert len(PRIMES) == N_PRIMES

# Conductor bins for aggregation
COND_BINS = [(1, 100), (101, 500), (501, 1000), (1001, 5000), (5001, 20000)]


def compute_ipr(ap_values, primes):
    """Compute IPR from raw a_p values and corresponding primes."""
    x = np.array([ap / (2 * np.sqrt(p)) for ap, p in zip(ap_values, primes)])
    x2 = x ** 2
    x4 = x ** 4
    denom = np.sum(x2) ** 2
    if denom == 0:
        return np.nan, x
    return np.sum(x4) / denom, x


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Load weight-2, dim-1 forms with ap_coeffs
    rows = con.sql("""
        SELECT lmfdb_label, level, is_cm, ap_coeffs
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND ap_coeffs IS NOT NULL
        ORDER BY level
    """).fetchall()

    print(f"Loaded {len(rows)} weight-2 dim-1 newforms")

    results = []
    ipr_all = []
    ipr_cm = []
    ipr_noncm = []
    ipr_by_bin = {f"{lo}-{hi}": [] for lo, hi in COND_BINS}

    for label, level, is_cm, ap_raw in rows:
        ap_list = json.loads(ap_raw) if isinstance(ap_raw, str) else ap_raw
        if len(ap_list) < N_PRIMES:
            continue

        ap_values = [entry[0] for entry in ap_list[:N_PRIMES]]
        ipr_val, x_norm = compute_ipr(ap_values, PRIMES)

        if np.isnan(ipr_val):
            continue

        results.append({
            "label": label,
            "level": level,
            "is_cm": bool(is_cm) if is_cm is not None else None,
            "ipr": float(ipr_val),
        })

        ipr_all.append(ipr_val)
        if is_cm:
            ipr_cm.append(ipr_val)
        else:
            ipr_noncm.append(ipr_val)

        for lo, hi in COND_BINS:
            if lo <= level <= hi:
                ipr_by_bin[f"{lo}-{hi}"].append(ipr_val)
                break

    ipr_all = np.array(ipr_all)
    ipr_cm = np.array(ipr_cm)
    ipr_noncm = np.array(ipr_noncm)

    # ---------------------------------------------------------------------------
    # Summary statistics
    # ---------------------------------------------------------------------------
    uniform_ipr = 1.0 / N_PRIMES  # 0.04 for fully delocalized

    summary = {
        "n_primes": N_PRIMES,
        "primes_used": PRIMES,
        "uniform_ipr_1_over_N": round(uniform_ipr, 6),
        "total_forms": len(ipr_all),
        "overall": {
            "mean": round(float(np.mean(ipr_all)), 6),
            "median": round(float(np.median(ipr_all)), 6),
            "std": round(float(np.std(ipr_all)), 6),
            "min": round(float(np.min(ipr_all)), 6),
            "max": round(float(np.max(ipr_all)), 6),
            "p10": round(float(np.percentile(ipr_all, 10)), 6),
            "p25": round(float(np.percentile(ipr_all, 25)), 6),
            "p75": round(float(np.percentile(ipr_all, 75)), 6),
            "p90": round(float(np.percentile(ipr_all, 90)), 6),
        },
        "cm_forms": {
            "count": len(ipr_cm),
            "mean": round(float(np.mean(ipr_cm)), 6) if len(ipr_cm) > 0 else None,
            "median": round(float(np.median(ipr_cm)), 6) if len(ipr_cm) > 0 else None,
            "std": round(float(np.std(ipr_cm)), 6) if len(ipr_cm) > 0 else None,
        },
        "non_cm_forms": {
            "count": len(ipr_noncm),
            "mean": round(float(np.mean(ipr_noncm)), 6) if len(ipr_noncm) > 0 else None,
            "median": round(float(np.median(ipr_noncm)), 6) if len(ipr_noncm) > 0 else None,
            "std": round(float(np.std(ipr_noncm)), 6) if len(ipr_noncm) > 0 else None,
        },
        "cm_vs_noncm_ratio": None,
        "conductor_bins": {},
        "histogram_25_bins": None,
    }

    if len(ipr_cm) > 0 and len(ipr_noncm) > 0:
        summary["cm_vs_noncm_ratio"] = round(float(np.mean(ipr_cm) / np.mean(ipr_noncm)), 4)

    # Conductor bins
    for key, vals in ipr_by_bin.items():
        if vals:
            arr = np.array(vals)
            summary["conductor_bins"][key] = {
                "count": len(vals),
                "mean": round(float(np.mean(arr)), 6),
                "median": round(float(np.median(arr)), 6),
                "std": round(float(np.std(arr)), 6),
            }

    # Histogram
    counts, bin_edges = np.histogram(ipr_all, bins=25)
    summary["histogram_25_bins"] = {
        "counts": counts.tolist(),
        "bin_edges": [round(float(x), 6) for x in bin_edges],
    }

    # Top-10 most localized and delocalized
    sorted_results = sorted(results, key=lambda r: r["ipr"])
    summary["most_delocalized_10"] = sorted_results[:10]
    summary["most_localized_10"] = sorted_results[-10:][::-1]

    # ---------------------------------------------------------------------------
    # Theoretical IPR for Sato-Tate
    # ---------------------------------------------------------------------------
    # x_p = a_p/(2sqrt(p)) ~ Sato-Tate => density (2/pi)*sqrt(1-x^2)
    # E[x^2] = integral x^2 * (2/pi)*sqrt(1-x^2) dx over [-1,1] = 1/4
    # E[x^4] = integral x^4 * (2/pi)*sqrt(1-x^2) dx over [-1,1] = 1/8
    # IPR = N * E[x^4] / (N * E[x^2])^2 = E[x^4] / (N * E[x^2]^2)
    #      = (1/8) / (N * 1/16) = (1/8) * (16/N) = 2/N
    # For N=25: IPR_ST = 2/25 = 0.08
    # But this is for the ratio of sums, not sum of ratios. Let me be more careful.
    #
    # Actually IPR = sum(x_i^4) / (sum(x_i^2))^2
    # For iid x_i from Sato-Tate:
    #   E[sum(x^4)] = N * E[x^4] = N/8
    #   E[(sum(x^2))^2] = N*E[x^4] + N*(N-1)*(E[x^2])^2 = N/8 + N(N-1)/16
    # IPR ~ N*E[x^4] / (N*E[x^4] + N(N-1)*(E[x^2])^2)
    #      = (1/8) / (1/8 + (N-1)/16)
    #      = (1/8) / ((2 + N - 1)/16)
    #      = 2 / (N + 1)
    # For N=25: 2/26 = 0.0769
    # But E[IPR] != E[num]/E[denom], so this is approximate.
    # Let's compute via Monte Carlo.

    rng = np.random.default_rng(42)
    n_mc = 100000
    # Sample from Sato-Tate: x = cos(theta), theta ~ sin^2(theta) on [0,pi]
    # CDF inversion: use rejection or direct
    # Sato-Tate density for theta: (2/pi)*sin^2(theta), theta in [0,pi]
    # Sample theta, then x = cos(theta)
    # For sin^2 density: use inverse CDF
    # CDF = (1/pi)(theta - sin(theta)cos(theta))
    # Easier: rejection sampling
    mc_iprs = []
    for _ in range(n_mc):
        # rejection sample from Sato-Tate
        xs = []
        while len(xs) < N_PRIMES:
            theta = rng.uniform(0, np.pi)
            if rng.uniform() < np.sin(theta) ** 2:
                xs.append(np.cos(theta))
        xs = np.array(xs)
        s2 = np.sum(xs ** 2)
        if s2 > 0:
            mc_iprs.append(np.sum(xs ** 4) / s2 ** 2)

    mc_iprs = np.array(mc_iprs)
    summary["sato_tate_monte_carlo"] = {
        "n_samples": n_mc,
        "mean_ipr": round(float(np.mean(mc_iprs)), 6),
        "median_ipr": round(float(np.median(mc_iprs)), 6),
        "std_ipr": round(float(np.std(mc_iprs)), 6),
        "note": "Monte Carlo IPR from Sato-Tate distributed x_p (N=25 sites)"
    }

    # Interpretation (after MC so we can reference it)
    mean_ipr = float(np.mean(ipr_all))
    st_mean = float(np.mean(mc_iprs))
    if mean_ipr < 0.15:
        regime = "strongly delocalized"
    elif mean_ipr < 0.25:
        regime = "moderately delocalized"
    elif mean_ipr < 0.40:
        regime = "intermediate (Sato-Tate regime)"
    elif mean_ipr < 0.60:
        regime = "moderately localized"
    else:
        regime = "strongly localized"

    summary["interpretation"] = {
        "regime": regime,
        "note": (
            f"Mean IPR = {mean_ipr:.4f}. "
            f"Uniform (1/N) = {uniform_ipr:.4f}. "
            f"Sato-Tate MC baseline = {st_mean:.4f} for N={N_PRIMES}."
        ),
    }

    # ---------------------------------------------------------------------------
    # Print summary
    # ---------------------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"HECKE EIGENVECTOR IPR ANALYSIS")
    print(f"{'='*60}")
    print(f"Forms analyzed: {summary['total_forms']}")
    print(f"Primes used:    {N_PRIMES} (up to p={PRIMES[-1]})")
    print(f"Uniform IPR:    {uniform_ipr:.4f}")
    print(f"\nOverall IPR:")
    for k, v in summary["overall"].items():
        print(f"  {k:8s}: {v:.6f}")
    print(f"\nCM forms ({summary['cm_forms']['count']}):")
    if summary["cm_forms"]["mean"] is not None:
        print(f"  mean:   {summary['cm_forms']['mean']:.6f}")
        print(f"  median: {summary['cm_forms']['median']:.6f}")
    print(f"\nNon-CM forms ({summary['non_cm_forms']['count']}):")
    if summary["non_cm_forms"]["mean"] is not None:
        print(f"  mean:   {summary['non_cm_forms']['mean']:.6f}")
        print(f"  median: {summary['non_cm_forms']['median']:.6f}")
    if summary["cm_vs_noncm_ratio"]:
        print(f"\nCM/non-CM IPR ratio: {summary['cm_vs_noncm_ratio']:.4f}")

    print(f"\nConductor bins:")
    for key, vals in summary["conductor_bins"].items():
        print(f"  N={key:12s}: mean={vals['mean']:.6f}  n={vals['count']}")

    print(f"\nSato-Tate MC (theoretical baseline):")
    st = summary["sato_tate_monte_carlo"]
    print(f"  mean IPR:   {st['mean_ipr']:.6f}")
    print(f"  median IPR: {st['median_ipr']:.6f}")

    print(f"\nInterpretation: {summary['interpretation']['regime']}")
    print(summary['interpretation']['note'])

    # ---------------------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------------------
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {OUT_JSON}")

    con.close()


if __name__ == "__main__":
    main()
