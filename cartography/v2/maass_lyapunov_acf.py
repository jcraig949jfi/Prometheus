#!/usr/bin/env python3
"""
Maass Hecke Lyapunov Exponent + Serial Autocorrelation

For each Maass form: extract c_p at prime indices, normalize x_p = c_p / sqrt(p).
Lyapunov: lambda = mean(log|x_{p_{i+1}} - x_{p_i}|) (difference method).
Autocorrelation: ACF at lags 1-20 of the normalized prime-indexed sequence.
Stratify by symmetry (even/odd) and spectral parameter R.

Comparison targets:
  EC Lyapunov lambda = -1.155 (contracting)
  EC ACF = zero autocorrelation after debiasing
"""

import json
import math
import numpy as np
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUT_FILE = Path(__file__).parent / "maass_lyapunov_acf_results.json"

MAX_LAGS = 20
MIN_PRIMES = 30  # need enough primes for meaningful ACF


def sieve_primes(n):
    """Return list of primes up to n."""
    if n < 2:
        return []
    is_prime = [False, False] + [True] * (n - 1)
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def compute_lyapunov(x_p):
    """Lyapunov exponent via difference method: mean(log|x_{i+1} - x_i|)."""
    diffs = np.diff(x_p)
    # Filter out exact zeros (shouldn't happen but be safe)
    abs_diffs = np.abs(diffs)
    mask = abs_diffs > 1e-15
    if mask.sum() < 5:
        return None
    return float(np.mean(np.log(abs_diffs[mask])))


def compute_acf(x, max_lag=MAX_LAGS):
    """Compute autocorrelation function at lags 1..max_lag."""
    n = len(x)
    if n < max_lag + 5:
        return None
    x_centered = x - np.mean(x)
    var = np.var(x)
    if var < 1e-15:
        return None
    acf = []
    for lag in range(1, max_lag + 1):
        if lag >= n:
            acf.append(0.0)
        else:
            c = np.mean(x_centered[:n - lag] * x_centered[lag:])
            acf.append(float(c / var))
    return acf


def analyze_form(form, primes_list):
    """Extract prime-indexed coefficients, normalize, compute Lyapunov + ACF."""
    coeffs = form["coefficients"]
    n_coeffs = len(coeffs)
    level = int(form["level"])

    # Extract c_p / sqrt(p) for primes p <= n_coeffs, skipping primes dividing the level
    x_p = []
    primes_used = []
    for p in primes_list:
        if p > n_coeffs:
            break
        # coefficients are 1-indexed: coeffs[0] = c_1, coeffs[p-1] = c_p
        if level % p == 0:
            continue  # skip bad primes
        c_p = coeffs[p - 1]
        x_p.append(c_p / math.sqrt(p))
        primes_used.append(p)

    if len(x_p) < MIN_PRIMES:
        return None

    x_p = np.array(x_p)

    lyap = compute_lyapunov(x_p)
    acf = compute_acf(x_p, MAX_LAGS)

    return {
        "n_primes": len(x_p),
        "lyapunov": lyap,
        "acf": acf,
        "x_p_mean": float(np.mean(x_p)),
        "x_p_std": float(np.std(x_p)),
    }


def main():
    print("Loading Maass data...")
    with open(DATA_FILE) as f:
        data = json.load(f)
    print(f"  {len(data)} forms loaded")

    # Build prime sieve up to max coefficient count
    max_n = max(len(d["coefficients"]) for d in data)
    primes = sieve_primes(max_n)
    print(f"  {len(primes)} primes up to {max_n}")

    # Analyze each form
    results_even = []  # symmetry = +1
    results_odd = []   # symmetry = -1
    skipped = 0

    for form in data:
        res = analyze_form(form, primes)
        if res is None:
            skipped += 1
            continue

        entry = {
            **res,
            "symmetry": form["symmetry"],
            "R": float(form["spectral_parameter"]),
            "level": int(form["level"]),
        }

        sym = form["symmetry"]
        if sym == 1:
            results_even.append(entry)
        else:
            results_odd.append(entry)

    all_results = results_even + results_odd
    print(f"  Analyzed {len(all_results)} forms ({skipped} skipped, < {MIN_PRIMES} primes)")
    print(f"  Even (sym=+1): {len(results_even)}, Odd (sym=-1): {len(results_odd)}")

    # --- Aggregate Lyapunov ---
    def lyap_stats(entries, label):
        lyaps = [e["lyapunov"] for e in entries if e["lyapunov"] is not None]
        if not lyaps:
            return {"label": label, "n": 0}
        lyaps = np.array(lyaps)
        return {
            "label": label,
            "n": len(lyaps),
            "mean": float(np.mean(lyaps)),
            "std": float(np.std(lyaps)),
            "median": float(np.median(lyaps)),
            "q25": float(np.percentile(lyaps, 25)),
            "q75": float(np.percentile(lyaps, 75)),
        }

    lyap_all = lyap_stats(all_results, "all")
    lyap_even = lyap_stats(results_even, "even (sym=+1)")
    lyap_odd = lyap_stats(results_odd, "odd (sym=-1)")

    print(f"\n=== Lyapunov Exponent (difference method) ===")
    print(f"  EC reference: lambda = -1.155 (contracting)")
    for s in [lyap_all, lyap_even, lyap_odd]:
        if s["n"] > 0:
            print(f"  {s['label']:20s}: lambda = {s['mean']:.4f} +/- {s['std']:.4f}  (n={s['n']})")

    # --- Aggregate ACF ---
    def acf_stats(entries, label):
        acfs = [np.array(e["acf"]) for e in entries if e["acf"] is not None]
        if not acfs:
            return {"label": label, "n": 0}
        acf_matrix = np.array(acfs)
        mean_acf = np.mean(acf_matrix, axis=0)
        std_acf = np.std(acf_matrix, axis=0)
        max_abs_mean = float(np.max(np.abs(mean_acf)))
        return {
            "label": label,
            "n": len(acfs),
            "mean_acf": [float(x) for x in mean_acf],
            "std_acf": [float(x) for x in std_acf],
            "max_abs_mean_acf": max_abs_mean,
        }

    acf_all = acf_stats(all_results, "all")
    acf_even = acf_stats(results_even, "even (sym=+1)")
    acf_odd = acf_stats(results_odd, "odd (sym=-1)")

    print(f"\n=== Autocorrelation (lags 1-{MAX_LAGS}) ===")
    print(f"  EC reference: zero autocorrelation after debiasing")
    for s in [acf_all, acf_even, acf_odd]:
        if s["n"] > 0:
            acf_str = ", ".join(f"{x:.4f}" for x in s["mean_acf"][:5])
            print(f"  {s['label']:20s}: ACF[1-5] = [{acf_str}]  max|ACF| = {s['max_abs_mean_acf']:.5f}  (n={s['n']})")

    # --- Lyapunov vs R (spectral parameter) ---
    # Bin into quintiles of R
    all_with_lyap = [e for e in all_results if e["lyapunov"] is not None]
    Rs = np.array([e["R"] for e in all_with_lyap])
    lyaps = np.array([e["lyapunov"] for e in all_with_lyap])

    n_bins = 5
    r_percentiles = np.percentile(Rs, np.linspace(0, 100, n_bins + 1))
    r_bins = []
    print(f"\n=== Lyapunov vs Spectral Parameter R (quintiles) ===")
    for i in range(n_bins):
        mask = (Rs >= r_percentiles[i]) & (Rs < r_percentiles[i + 1])
        if i == n_bins - 1:
            mask = (Rs >= r_percentiles[i]) & (Rs <= r_percentiles[i + 1])
        if mask.sum() == 0:
            continue
        bin_lyaps = lyaps[mask]
        bin_info = {
            "R_range": [float(r_percentiles[i]), float(r_percentiles[i + 1])],
            "n": int(mask.sum()),
            "lyapunov_mean": float(np.mean(bin_lyaps)),
            "lyapunov_std": float(np.std(bin_lyaps)),
        }
        r_bins.append(bin_info)
        print(f"  R in [{bin_info['R_range'][0]:.2f}, {bin_info['R_range'][1]:.2f}]: "
              f"lambda = {bin_info['lyapunov_mean']:.4f} +/- {bin_info['lyapunov_std']:.4f}  (n={bin_info['n']})")

    # --- Lyapunov-R correlation ---
    from scipy import stats as sp_stats
    r_corr, r_pval = sp_stats.pearsonr(Rs, lyaps)
    print(f"\n  Pearson(lambda, R) = {r_corr:.4f}, p = {r_pval:.2e}")

    # --- ACF vs R ---
    all_with_acf = [e for e in all_results if e["acf"] is not None]
    Rs_acf = np.array([e["R"] for e in all_with_acf])
    acf_lag1 = np.array([e["acf"][0] for e in all_with_acf])
    acf_r_corr, acf_r_pval = sp_stats.pearsonr(Rs_acf, acf_lag1)
    print(f"  Pearson(ACF[1], R) = {acf_r_corr:.4f}, p = {acf_r_pval:.2e}")

    # --- Summary ---
    summary = {
        "description": "Maass Hecke Lyapunov exponent + serial autocorrelation",
        "method": {
            "normalization": "x_p = c_p / sqrt(p) at good primes",
            "lyapunov": "mean(log|x_{p_{i+1}} - x_{p_i}|) (consecutive-prime differences)",
            "acf": "standard autocorrelation at lags 1-20",
            "bad_primes": "primes dividing level are excluded",
        },
        "ec_comparison": {
            "ec_lyapunov": -1.155,
            "ec_acf": "zero (no serial dependence)",
        },
        "n_forms_analyzed": len(all_results),
        "n_skipped": skipped,
        "lyapunov": {
            "all": lyap_all,
            "even": lyap_even,
            "odd": lyap_odd,
        },
        "acf": {
            "all": acf_all,
            "even": acf_even,
            "odd": acf_odd,
        },
        "lyapunov_vs_R": {
            "quintile_bins": r_bins,
            "pearson_r": float(r_corr),
            "pearson_p": float(r_pval),
        },
        "acf_lag1_vs_R": {
            "pearson_r": float(acf_r_corr),
            "pearson_p": float(acf_r_pval),
        },
    }

    # Verdict
    lyap_mean = lyap_all["mean"] if lyap_all["n"] > 0 else None
    max_acf = acf_all["max_abs_mean_acf"] if acf_all["n"] > 0 else None

    if lyap_mean is not None:
        if lyap_mean < -0.5:
            lyap_verdict = "contracting (like EC)"
        elif lyap_mean > 0.5:
            lyap_verdict = "expanding (unlike EC)"
        else:
            lyap_verdict = "near-neutral"
    else:
        lyap_verdict = "insufficient data"

    if max_acf is not None:
        if max_acf < 0.02:
            acf_verdict = "zero autocorrelation (like EC)"
        elif max_acf < 0.05:
            acf_verdict = "near-zero autocorrelation"
        else:
            acf_verdict = f"non-trivial autocorrelation (max|ACF|={max_acf:.4f})"
    else:
        acf_verdict = "insufficient data"

    sym_diff = None
    if lyap_even["n"] > 0 and lyap_odd["n"] > 0:
        diff = abs(lyap_even["mean"] - lyap_odd["mean"])
        pooled_std = math.sqrt(lyap_even["std"]**2 / lyap_even["n"] +
                               lyap_odd["std"]**2 / lyap_odd["n"])
        z = diff / pooled_std if pooled_std > 0 else 0
        sym_diff = {
            "even_mean": lyap_even["mean"],
            "odd_mean": lyap_odd["mean"],
            "difference": float(diff),
            "z_score": float(z),
            "significant": bool(z > 3.0),
        }

    summary["verdicts"] = {
        "lyapunov": lyap_verdict,
        "acf": acf_verdict,
        "symmetry_lyapunov_difference": sym_diff,
        "lyapunov_R_dependent": bool(abs(r_corr) > 0.1 and r_pval < 0.01),
    }

    print(f"\n=== Verdicts ===")
    print(f"  Lyapunov: {lyap_verdict} (mean={lyap_mean:.4f})")
    print(f"  ACF: {acf_verdict}")
    if sym_diff:
        print(f"  Symmetry split: even={sym_diff['even_mean']:.4f}, odd={sym_diff['odd_mean']:.4f}, "
              f"z={sym_diff['z_score']:.2f}, significant={sym_diff['significant']}")
    print(f"  Lambda depends on R: {summary['verdicts']['lyapunov_R_dependent']}")

    with open(OUT_FILE, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
