#!/usr/bin/env python3
"""
OEIS Local Spectral Dimension Under Random Masking (List1 #8)
=============================================================
Mask 10-40% of entries in OEIS sequences, recompute local spectral dimension,
and measure the dimension stability exponent.

Method:
  1. Load 1000 OEIS sequences with 50+ terms
  2. For each sequence: compute autocorrelation spectrum
     (FFT -> power spectral density -> slope in log-log = spectral dimension proxy)
  3. Repeat with 10%, 20%, 30%, 40% of entries randomly masked
     - Zero-fill method: masked entries set to 0
     - Interpolation method: masked entries linearly interpolated from neighbors
  4. Stability exponent sigma: fit |D_masked/D_original| vs mask_fraction
     |D| should degrade as (1-f)^sigma
  5. Distribution of sigma across sequences
  6. Expected: sigma ~ 0.72-0.88
"""

import json
import numpy as np
from pathlib import Path
import time

DATA_FILE = Path(__file__).parent.parent / "oeis" / "data" / "stripped_new.txt"
OUT_FILE = Path(__file__).parent / "oeis_masking_stability_results.json"

MIN_TERMS = 50
N_SEQUENCES = 1000
MASK_FRACTIONS = [0.10, 0.20, 0.30, 0.40]
N_TRIALS = 30  # trials per mask fraction for robust averaging
RNG_SEED = 42


def parse_oeis(path, min_terms=MIN_TERMS, max_seqs=N_SEQUENCES):
    """Parse OEIS stripped file, return sequences with 50+ terms."""
    sequences = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            seq_id = parts[0]
            vals_str = parts[1].strip().strip(",")
            if not vals_str:
                continue
            try:
                vals = [int(x) for x in vals_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                sequences[seq_id] = vals
                if len(sequences) >= max_seqs:
                    break
    return sequences


def compute_spectral_dimension(values):
    """
    Compute local spectral dimension proxy from PSD slope.

    FFT -> power spectral density -> slope in log-log space.
    Returns the negative slope (positive = decaying spectrum = correlated signal).
    """
    arr = np.array(values, dtype=np.float64)
    if len(arr) < 16:
        return None

    # Log-transform to handle wide dynamic range
    arr = np.sign(arr) * np.log1p(np.abs(arr))
    arr = arr - arr.mean()

    if np.max(np.abs(arr)) < 1e-15:
        return None

    # FFT -> PSD
    fft_vals = np.fft.rfft(arr)
    psd = np.abs(fft_vals) ** 2

    # Use frequencies 1..N/2 (skip DC)
    n_freq = len(psd) - 1
    if n_freq < 4:
        return None

    freqs = np.arange(1, n_freq + 1, dtype=np.float64)
    psd_nondc = psd[1:n_freq + 1]

    # Remove zero-power bins
    valid = psd_nondc > 0
    if np.sum(valid) < 4:
        return None

    log_freq = np.log(freqs[valid])
    log_psd = np.log(psd_nondc[valid])

    try:
        coeffs = np.polyfit(log_freq, log_psd, 1)
        d_s = -coeffs[0]  # negative slope = spectral dimension proxy
        return float(d_s)
    except Exception:
        return None


def mask_zero(values, fraction, rng):
    """Mask entries by setting them to 0."""
    arr = np.array(values, dtype=np.float64)
    n = len(arr)
    n_mask = max(1, int(round(fraction * n)))
    idx = rng.choice(n, size=n_mask, replace=False)
    arr[idx] = 0
    return arr.tolist()


def mask_interpolate(values, fraction, rng):
    """Mask entries by replacing with linear interpolation from neighbors."""
    arr = np.array(values, dtype=np.float64)
    n = len(arr)
    n_mask = max(1, int(round(fraction * n)))
    idx = sorted(rng.choice(n, size=n_mask, replace=False))
    mask = np.zeros(n, dtype=bool)
    mask[idx] = True
    unmasked = np.where(~mask)[0]
    masked = np.where(mask)[0]
    if len(unmasked) >= 2:
        arr[masked] = np.interp(masked, unmasked, arr[unmasked])
    return arr.tolist()


def fit_stability_exponent(mask_fractions, d_values, d_original):
    """
    Fit stability exponent sigma.

    Model: |D_masked| / |D_original| = (1-f)^sigma
    => log(|D_masked/D_original|) = sigma * log(1-f)

    Uses OLS through origin in log-log space.
    Returns sigma, r_squared.
    """
    ratios = np.abs(np.array(d_values)) / np.abs(d_original)
    log_1mf = np.log(1.0 - np.array(mask_fractions))

    # Only keep finite, positive ratios
    valid = np.isfinite(ratios) & (ratios > 0) & np.isfinite(log_1mf)
    if np.sum(valid) < 2:
        return None, None

    log_1mf = log_1mf[valid]
    log_ratio = np.log(ratios[valid])

    # OLS through origin: sigma = sum(xy) / sum(x^2)
    sigma = float(np.sum(log_1mf * log_ratio) / np.sum(log_1mf ** 2))

    # R^2 relative to origin model
    predicted = sigma * log_1mf
    ss_res = np.sum((log_ratio - predicted) ** 2)
    ss_tot = np.sum(log_ratio ** 2)  # relative to 0 (origin)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0

    return sigma, r_squared


def run_masking_experiment(sequences, original_dims, mask_func, method_name, rng):
    """Run the full masking experiment with a given masking function."""
    print(f"\n  --- Method: {method_name} ---")

    # Collect masked spectral dimensions
    masked_data = {sid: {f: [] for f in MASK_FRACTIONS} for sid in original_dims}

    for frac in MASK_FRACTIONS:
        for trial in range(N_TRIALS):
            for sid in original_dims:
                vals = sequences[sid]
                masked_vals = mask_func(vals, frac, rng)
                d = compute_spectral_dimension(masked_vals)
                if d is not None and np.isfinite(d):
                    masked_data[sid][frac].append(d)

    # Fit per-sequence stability exponents
    sigmas = []
    r2s = []
    per_seq = []

    for sid in original_dims:
        d_orig = original_dims[sid]
        fracs_used = []
        d_medians = []

        for frac in MASK_FRACTIONS:
            trials = masked_data[sid][frac]
            if len(trials) >= 5:
                fracs_used.append(frac)
                d_medians.append(float(np.median(trials)))

        if len(fracs_used) >= 3:
            sigma, r2 = fit_stability_exponent(fracs_used, d_medians, d_orig)
            if sigma is not None and np.isfinite(sigma) and abs(sigma) < 50:
                sigmas.append(sigma)
                r2s.append(r2 if r2 is not None else 0)
                per_seq.append({
                    "seq_id": sid,
                    "d_original": round(d_orig, 6),
                    "sigma": round(sigma, 6),
                    "r_squared": round(r2, 6) if r2 is not None else None,
                    "d_ratios": {f"{f:.2f}": round(abs(dm) / abs(d_orig), 6)
                                 for f, dm in zip(fracs_used, d_medians)}
                })

    sigmas = np.array(sigmas)
    r2s = np.array(r2s)

    print(f"    Valid sigma fits: {len(sigmas)}")
    print(f"    Sigma: mean={np.mean(sigmas):.4f}, median={np.median(sigmas):.4f}, std={np.std(sigmas):.4f}")
    print(f"    Sigma IQR: [{np.percentile(sigmas, 25):.4f}, {np.percentile(sigmas, 75):.4f}]")
    print(f"    Mean R^2: {np.mean(r2s):.4f}, Median R^2: {np.median(r2s):.4f}")

    # Fraction in expected range
    in_range = np.sum((sigmas >= 0.72) & (sigmas <= 0.88))
    frac_in_range = in_range / len(sigmas) if len(sigmas) > 0 else 0

    # Global degradation curve (median of medians)
    global_curve = {}
    for frac in MASK_FRACTIONS:
        all_ratios = []
        for sid in original_dims:
            trials = masked_data[sid][frac]
            if len(trials) >= 5:
                ratio = abs(np.median(trials)) / abs(original_dims[sid])
                if np.isfinite(ratio) and ratio > 0:
                    all_ratios.append(ratio)
        if all_ratios:
            global_curve[f"{frac:.2f}"] = {
                "median_ratio": round(float(np.median(all_ratios)), 6),
                "mean_ratio": round(float(np.mean(all_ratios)), 6),
                "std_ratio": round(float(np.std(all_ratios)), 6),
                "n": len(all_ratios)
            }
            print(f"    f={frac:.0%}: median(|D_m/D_o|) = {np.median(all_ratios):.4f}")

    # Fit global sigma from median ratios
    g_fracs = [f for f in MASK_FRACTIONS if f"{f:.2f}" in global_curve]
    g_ratios = [global_curve[f"{f:.2f}"]["median_ratio"] for f in g_fracs]
    global_sigma, global_r2 = fit_stability_exponent(g_fracs, g_ratios, 1.0)
    if global_sigma is not None:
        print(f"    Global sigma (from median ratios): {global_sigma:.4f} (R^2={global_r2:.4f})")

    # Percentiles
    percentiles = {}
    for p in [5, 10, 25, 50, 75, 90, 95]:
        percentiles[f"p{p}"] = round(float(np.percentile(sigmas, p)), 6)

    # Histogram
    s_min, s_max = np.percentile(sigmas, 1), np.percentile(sigmas, 99)
    hist_bins = np.linspace(s_min - 0.1, s_max + 0.1, 40)
    hist_counts, hist_edges = np.histogram(sigmas, bins=hist_bins)
    histogram = [{"bin_center": round(float((hist_edges[i] + hist_edges[i+1]) / 2), 4),
                  "count": int(hist_counts[i])}
                 for i in range(len(hist_counts)) if hist_counts[i] > 0]

    per_seq.sort(key=lambda x: x["sigma"])

    return {
        "method_name": method_name,
        "n_valid_sigma": len(sigmas),
        "sigma_stats": {
            "mean": round(float(np.mean(sigmas)), 6),
            "median": round(float(np.median(sigmas)), 6),
            "std": round(float(np.std(sigmas)), 6),
            "min": round(float(np.min(sigmas)), 6),
            "max": round(float(np.max(sigmas)), 6),
            "iqr": [round(float(np.percentile(sigmas, 25)), 6),
                    round(float(np.percentile(sigmas, 75)), 6)],
            "percentiles": percentiles
        },
        "expected_range": [0.72, 0.88],
        "fraction_in_expected_range": round(float(frac_in_range), 6),
        "global_sigma": round(float(global_sigma), 6) if global_sigma is not None else None,
        "global_r_squared": round(float(global_r2), 6) if global_r2 is not None else None,
        "degradation_curve": global_curve,
        "mean_fit_r_squared": round(float(np.mean(r2s)), 6),
        "median_fit_r_squared": round(float(np.median(r2s)), 6),
        "sigma_histogram": histogram,
        "per_sequence_sample": {
            "lowest_sigma_10": per_seq[:10],
            "median_sigma_10": per_seq[len(per_seq)//2 - 5 : len(per_seq)//2 + 5],
            "highest_sigma_10": per_seq[-10:]
        }
    }


def main():
    t0 = time.time()
    print("OEIS Local Spectral Dimension Under Random Masking")
    print("=" * 55)

    # 1. Load sequences
    print(f"\n[1] Loading OEIS sequences (min {MIN_TERMS} terms, max {N_SEQUENCES})...")
    sequences = parse_oeis(DATA_FILE, MIN_TERMS, N_SEQUENCES)
    print(f"  Loaded {len(sequences)} sequences")

    seq_ids = list(sequences.keys())
    seq_vals = [sequences[s] for s in seq_ids]
    term_counts = [len(v) for v in seq_vals]
    print(f"  Term counts: min={min(term_counts)}, median={int(np.median(term_counts))}, max={max(term_counts)}")

    rng = np.random.default_rng(RNG_SEED)

    # 2. Compute original spectral dimensions
    print(f"\n[2] Computing original spectral dimensions...")
    original_dims = {}
    for sid, vals in zip(seq_ids, seq_vals):
        d = compute_spectral_dimension(vals)
        if d is not None and np.isfinite(d) and abs(d) > 1e-6:
            original_dims[sid] = d

    d_orig_vals = np.array(list(original_dims.values()))
    print(f"  Valid: {len(original_dims)}/{len(seq_ids)}")
    print(f"  D_original: mean={np.mean(d_orig_vals):.4f}, median={np.median(d_orig_vals):.4f}, "
          f"std={np.std(d_orig_vals):.4f}")

    # 3. Run both masking methods
    print(f"\n[3] Running masking experiments ({N_TRIALS} trials x {len(MASK_FRACTIONS)} fractions)...")

    rng_zero = np.random.default_rng(RNG_SEED)
    zero_results = run_masking_experiment(sequences, original_dims, mask_zero, "zero_fill", rng_zero)

    rng_interp = np.random.default_rng(RNG_SEED + 1)
    interp_results = run_masking_experiment(sequences, original_dims, mask_interpolate, "interpolation", rng_interp)

    # 4. Combined analysis
    print(f"\n[4] Combined analysis...")
    # The "best" method is the one with higher median R^2
    best = zero_results if zero_results["median_fit_r_squared"] > interp_results["median_fit_r_squared"] else interp_results
    print(f"  Best method: {best['method_name']} (median R^2 = {best['median_fit_r_squared']:.4f})")
    print(f"  Best global sigma: {best['global_sigma']}")
    print(f"  Best median sigma: {best['sigma_stats']['median']}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Assemble results
    results = {
        "problem": "OEIS Local Spectral Dimension Under Random Masking (List1 #8)",
        "method": {
            "description": (
                "FFT-based PSD slope as spectral dimension proxy. "
                "Sequences masked at 10-40% with both zero-fill and interpolation. "
                "Stability exponent sigma fit via |D_masked/D_original| = (1-f)^sigma."
            ),
            "n_sequences_loaded": len(sequences),
            "n_sequences_valid_d": len(original_dims),
            "min_terms": MIN_TERMS,
            "mask_fractions": MASK_FRACTIONS,
            "n_trials_per_fraction": N_TRIALS,
            "rng_seed": RNG_SEED,
            "spectral_dimension_proxy": "negative slope of log(PSD) vs log(freq) after log1p transform",
            "stability_model": "|D_masked|/|D_original| = (1-f)^sigma, OLS through origin in log-log"
        },
        "original_spectral_dimension": {
            "mean": round(float(np.mean(d_orig_vals)), 6),
            "median": round(float(np.median(d_orig_vals)), 6),
            "std": round(float(np.std(d_orig_vals)), 6),
            "min": round(float(np.min(d_orig_vals)), 6),
            "max": round(float(np.max(d_orig_vals)), 6),
            "positive_fraction": round(float(np.mean(d_orig_vals > 0)), 4)
        },
        "zero_fill_masking": zero_results,
        "interpolation_masking": interp_results,
        "best_method": best["method_name"],
        "best_global_sigma": best["global_sigma"],
        "best_median_sigma": best["sigma_stats"]["median"],
        "expected_sigma_range": [0.72, 0.88],
        "assessment": (
            f"Zero-fill: global sigma = {zero_results['global_sigma']}, median per-seq = {zero_results['sigma_stats']['median']:.4f}. "
            f"Interpolation: global sigma = {interp_results['global_sigma']}, median per-seq = {interp_results['sigma_stats']['median']:.4f}. "
            f"Best method ({best['method_name']}): median sigma = {best['sigma_stats']['median']:.4f}, "
            f"{'WITHIN' if 0.72 <= abs(best['sigma_stats']['median']) <= 0.88 else 'OUTSIDE'} expected [0.72, 0.88]. "
            f"The spectral dimension {'is' if abs(best['sigma_stats']['median']) < 2 else 'is not'} "
            f"reasonably stable under random masking."
        ),
        "elapsed_seconds": round(elapsed, 1)
    }

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")

    return results


if __name__ == "__main__":
    main()
