"""
Geometric Probes — Cross-dataset structural analysis beyond correlation.
=========================================================================
A library of geometric, spectral, and information-theoretic tests that
can be applied to any pair of numerical arrays from different datasets.

Each probe returns a signature dict that feeds the shadow tensor.
All probes are zero-cost (no LLM, no API).

Probe categories:
  1. SHAPE: curvature, convexity, inflection points
  2. SPECTRAL: FFT peaks, spectral gaps, harmonic structure
  3. DISTRIBUTION: Benford's law, Zipf exponents, moment profiles
  4. INFORMATION: entropy, mutual information, transfer entropy
  5. TOPOLOGY: persistence (gap structure), lacunarity, fractal dimension
  6. TRANSPORT: Wasserstein distance, optimal alignment cost
  7. GRAPH: degree spectra, clustering coefficients (for graph datasets)

Usage:
    from geometric_probes import run_all_probes
    signatures = run_all_probes(array_a, array_b, name_a="KnotInfo_det", name_b="NF_class")
"""

import numpy as np
from scipy import stats as sp_stats
from scipy.fft import fft
from collections import Counter
from typing import Optional


# =====================================================================
# 1. SHAPE PROBES — curvature, convexity, growth geometry
# =====================================================================

def probe_curvature(a):
    """Second derivative of sorted values — how the distribution bends."""
    if len(a) < 10:
        return None
    s = np.sort(a)
    d1 = np.diff(s)
    d2 = np.diff(d1)
    return {
        "probe": "curvature",
        "mean_curvature": float(np.mean(d2)),
        "std_curvature": float(np.std(d2)),
        "max_curvature": float(np.max(np.abs(d2))),
        "sign_changes": int(np.sum(np.diff(np.sign(d2)) != 0)),
        "convex_fraction": float(np.mean(d2 > 0)),
    }


def probe_growth_shape(a):
    """Classify growth: linear, polynomial, exponential, sub-linear."""
    if len(a) < 10:
        return None
    s = np.sort(a[a > 0])
    if len(s) < 10:
        return None
    idx = np.arange(1, len(s) + 1, dtype=float)

    # Fit log(a) vs log(n) — slope gives polynomial degree
    with np.errstate(divide='ignore', invalid='ignore'):
        log_s = np.log(s[s > 0])
        log_idx = np.log(idx[:len(log_s)])
    if len(log_s) < 5:
        return None

    slope, intercept, r_poly, _, _ = sp_stats.linregress(log_idx, log_s)

    # Fit a vs n — r^2 for linear
    _, _, r_linear, _, _ = sp_stats.linregress(idx[:len(s)], s)

    # Fit log(a) vs n — r^2 for exponential
    _, _, r_exp, _, _ = sp_stats.linregress(idx[:len(log_s)], log_s)

    return {
        "probe": "growth_shape",
        "poly_degree": round(float(slope), 3),
        "r2_linear": round(float(r_linear**2), 4),
        "r2_polynomial": round(float(r_poly**2), 4),
        "r2_exponential": round(float(r_exp**2), 4),
        "best_fit": "exponential" if r_exp**2 > max(r_linear**2, r_poly**2)
                    else ("polynomial" if r_poly**2 > r_linear**2 else "linear"),
    }


# =====================================================================
# 2. SPECTRAL PROBES — frequency domain analysis
# =====================================================================

def probe_fft_signature(a, n_peaks=5):
    """FFT of sequence — dominant frequencies and spectral gaps."""
    if len(a) < 20:
        return None
    # Detrend
    detrended = a - np.linspace(a[0], a[-1], len(a))
    spectrum = np.abs(fft(detrended))[:len(a)//2]

    if len(spectrum) < 5:
        return None

    # Normalize
    total_power = np.sum(spectrum**2)
    if total_power == 0:
        return None

    # Top peaks
    peak_indices = np.argsort(spectrum)[-n_peaks:][::-1]
    peaks = [(int(i), float(spectrum[i])) for i in peak_indices]

    # Spectral entropy
    power_dist = spectrum**2 / total_power
    power_dist = power_dist[power_dist > 0]
    spectral_entropy = float(-np.sum(power_dist * np.log2(power_dist)))

    # Spectral centroid
    freqs = np.arange(len(spectrum))
    centroid = float(np.sum(freqs * spectrum**2) / total_power)

    return {
        "probe": "fft_signature",
        "top_peaks": peaks,
        "spectral_entropy": round(spectral_entropy, 4),
        "spectral_centroid": round(centroid, 4),
        "total_power": round(float(total_power), 4),
        "peak_concentration": round(float(sum(s**2 for _, s in peaks) / total_power), 4),
    }


def probe_spectral_cross(a, b):
    """Cross-spectral coherence between two arrays."""
    n = min(len(a), len(b))
    if n < 20:
        return None
    a, b = a[:n], b[:n]

    # Detrend both
    a_d = a - np.linspace(a[0], a[-1], n)
    b_d = b - np.linspace(b[0], b[-1], n)

    fa = fft(a_d)[:n//2]
    fb = fft(b_d)[:n//2]

    # Cross-spectral density
    cross = fa * np.conj(fb)
    power_a = np.abs(fa)**2
    power_b = np.abs(fb)**2

    # Coherence
    denom = np.sqrt(power_a * power_b)
    denom[denom == 0] = 1
    coherence = np.abs(cross) / denom

    return {
        "probe": "spectral_cross",
        "mean_coherence": round(float(np.mean(coherence)), 4),
        "max_coherence": round(float(np.max(coherence)), 4),
        "peak_coherence_freq": int(np.argmax(coherence)),
        "n_high_coherence": int(np.sum(coherence > 0.8)),
    }


# =====================================================================
# 3. DISTRIBUTION PROBES — statistical fingerprints
# =====================================================================

def probe_benford(a):
    """Benford's law test — leading digit distribution."""
    positive = a[a > 0]
    if len(positive) < 30:
        return None

    leading = [int(str(int(abs(x)))[0]) for x in positive if x != 0]
    if not leading:
        return None

    counts = Counter(leading)
    total = len(leading)
    observed = np.array([counts.get(d, 0) / total for d in range(1, 10)])

    # Benford expected
    expected = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

    # Chi-squared
    chi2 = float(np.sum((observed - expected)**2 / expected) * total)
    p_value = float(1 - sp_stats.chi2.cdf(chi2, 8))

    return {
        "probe": "benford",
        "observed": [round(x, 4) for x in observed],
        "expected_benford": [round(x, 4) for x in expected],
        "chi2": round(chi2, 2),
        "p_value": round(p_value, 4),
        "follows_benford": p_value > 0.05,
    }


def probe_moments(a):
    """Higher moment profile — skewness, kurtosis, coefficient of variation."""
    if len(a) < 10:
        return None
    return {
        "probe": "moments",
        "mean": round(float(np.mean(a)), 6),
        "std": round(float(np.std(a)), 6),
        "cv": round(float(np.std(a) / abs(np.mean(a))) if np.mean(a) != 0 else 0, 4),
        "skewness": round(float(sp_stats.skew(a)), 4),
        "kurtosis": round(float(sp_stats.kurtosis(a)), 4),
        "median_mean_ratio": round(float(np.median(a) / np.mean(a)) if np.mean(a) != 0 else 0, 4),
    }


def probe_zipf(a):
    """Zipf/power-law exponent of value frequency distribution."""
    positive = a[a > 0].astype(int)
    if len(positive) < 30:
        return None

    counts = Counter(positive)
    if len(counts) < 5:
        return None

    # Rank-frequency
    freqs = sorted(counts.values(), reverse=True)
    ranks = np.arange(1, len(freqs) + 1, dtype=float)
    log_ranks = np.log(ranks)
    log_freqs = np.log(np.array(freqs, dtype=float))

    slope, _, r, _, _ = sp_stats.linregress(log_ranks, log_freqs)

    return {
        "probe": "zipf",
        "zipf_exponent": round(float(-slope), 4),
        "r2": round(float(r**2), 4),
        "is_zipf": r**2 > 0.8 and slope < -0.5,
        "n_unique_values": len(counts),
    }


# =====================================================================
# 4. INFORMATION PROBES — entropy and mutual information
# =====================================================================

def probe_entropy(a, n_bins=20):
    """Shannon entropy of binned distribution."""
    if len(a) < 10:
        return None
    hist, _ = np.histogram(a, bins=n_bins, density=True)
    hist = hist[hist > 0]
    bin_width = (np.max(a) - np.min(a)) / n_bins if np.max(a) != np.min(a) else 1
    entropy = float(-np.sum(hist * bin_width * np.log2(hist * bin_width + 1e-15)))

    return {
        "probe": "entropy",
        "shannon_entropy": round(entropy, 4),
        "max_possible": round(float(np.log2(n_bins)), 4),
        "normalized_entropy": round(entropy / max(np.log2(n_bins), 1), 4),
    }


def probe_mutual_information(a, b, n_bins=15):
    """Mutual information between two arrays — non-linear correlation."""
    n = min(len(a), len(b))
    if n < 30:
        return None
    a, b = a[:n], b[:n]

    # 2D histogram
    hist2d, _, _ = np.histogram2d(a, b, bins=n_bins)
    pxy = hist2d / hist2d.sum()
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)

    # MI = sum p(x,y) * log(p(x,y) / (p(x)*p(y)))
    mi = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))

    # Normalized MI
    hx = float(-np.sum(px[px > 0] * np.log2(px[px > 0])))
    hy = float(-np.sum(py[py > 0] * np.log2(py[py > 0])))
    nmi = mi / max(min(hx, hy), 1e-10)

    return {
        "probe": "mutual_information",
        "mi_bits": round(float(mi), 6),
        "normalized_mi": round(float(nmi), 4),
        "entropy_a": round(hx, 4),
        "entropy_b": round(hy, 4),
    }


# =====================================================================
# 5. TOPOLOGY PROBES — gap structure, lacunarity
# =====================================================================

def probe_gap_structure(a):
    """Analyze the gap distribution of sorted values — lacunarity and persistence."""
    if len(a) < 10:
        return None
    s = np.sort(np.unique(a[a > 0]))
    if len(s) < 5:
        return None

    gaps = np.diff(s)
    if len(gaps) == 0 or np.mean(gaps) == 0:
        return None

    # Normalized gaps
    mean_gap = np.mean(gaps)
    norm_gaps = gaps / mean_gap

    # Lacunarity (coefficient of variation of gaps squared + 1)
    lacunarity = float((np.std(norm_gaps) / np.mean(norm_gaps))**2 + 1) if np.mean(norm_gaps) > 0 else 1

    # Gap ratio distribution (consecutive gap ratios)
    if len(gaps) >= 3:
        gap_ratios = gaps[1:] / np.maximum(gaps[:-1], 1e-10)
        gap_ratio_mean = float(np.mean(gap_ratios))
    else:
        gap_ratio_mean = 1.0

    return {
        "probe": "gap_structure",
        "mean_gap": round(float(mean_gap), 4),
        "std_gap": round(float(np.std(gaps)), 4),
        "lacunarity": round(lacunarity, 4),
        "gap_ratio_mean": round(gap_ratio_mean, 4),
        "max_gap": round(float(np.max(gaps)), 4),
        "n_unique": len(s),
    }


def probe_fractal_dimension(a, n_scales=10):
    """Box-counting dimension estimate of value distribution."""
    if len(a) < 20:
        return None
    s = np.sort(a[a > 0])
    if len(s) < 10:
        return None

    lo, hi = s[0], s[-1]
    if hi <= lo:
        return None

    scales = np.logspace(np.log10(max(hi - lo, 1) / 100),
                         np.log10(hi - lo), n_scales)
    counts = []
    for scale in scales:
        bins = int(np.ceil((hi - lo) / scale))
        if bins < 1:
            bins = 1
        hist, _ = np.histogram(s, bins=bins)
        counts.append(np.sum(hist > 0))

    log_scales = np.log(scales)
    log_counts = np.log(np.array(counts, dtype=float) + 1)

    slope, _, r, _, _ = sp_stats.linregress(log_scales, log_counts)

    return {
        "probe": "fractal_dimension",
        "box_counting_dim": round(float(-slope), 4),
        "r2": round(float(r**2), 4),
        "n_scales": n_scales,
    }


# =====================================================================
# 6. TRANSPORT PROBES — distribution distance
# =====================================================================

def probe_wasserstein(a, b):
    """Wasserstein (earth mover's) distance between two distributions.

    Includes uniformity check: if both inputs are near-uniform (R^2 > 0.95
    on sorted vs index), the match is flagged as a normalization artifact.
    Learned from NF-SmallGroups false positive (April 2026).
    """
    n = min(len(a), len(b))
    if n < 10:
        return None

    # Check if inputs are near-uniform (artifact detector)
    def _is_near_uniform(arr):
        s = np.sort(arr)
        idx = np.arange(len(s), dtype=float)
        if len(s) < 5:
            return False
        r = np.corrcoef(idx, s)[0, 1]
        return r ** 2 > 0.95

    a_uniform = _is_near_uniform(a[:n])
    b_uniform = _is_near_uniform(b[:n])

    # Normalize to same scale
    a_norm = (a[:n] - np.mean(a[:n])) / max(np.std(a[:n]), 1e-10)
    b_norm = (b[:n] - np.mean(b[:n])) / max(np.std(b[:n]), 1e-10)

    # 1D Wasserstein = integral of |F_a - F_b|
    w1 = float(sp_stats.wasserstein_distance(a_norm, b_norm))

    # KS distance
    ks_stat, ks_p = sp_stats.ks_2samp(a_norm, b_norm)

    is_artifact = a_uniform and b_uniform

    return {
        "probe": "wasserstein",
        "w1_distance": round(w1, 6),
        "ks_statistic": round(float(ks_stat), 4),
        "ks_p_value": round(float(ks_p), 4),
        "distributions_same": ks_p > 0.05 and not is_artifact,
        "uniformity_artifact": is_artifact,
    }


# =====================================================================
# 7. CROSS-DATASET GEOMETRIC PROBES
# =====================================================================

def probe_alignment_cost(a, b):
    """Dynamic time warping-inspired alignment cost between sorted sequences."""
    n = min(len(a), len(b), 500)  # cap for speed
    if n < 10:
        return None

    a_s = np.sort(a[:n])
    b_s = np.sort(b[:n])

    # Normalize
    a_n = (a_s - np.mean(a_s)) / max(np.std(a_s), 1e-10)
    b_n = (b_s - np.mean(b_s)) / max(np.std(b_s), 1e-10)

    # Direct alignment cost (same indices)
    direct_cost = float(np.mean(np.abs(a_n - b_n)))

    # Shifted alignment (find best shift)
    best_shift_cost = direct_cost
    best_shift = 0
    for shift in range(-min(n//4, 50), min(n//4, 50)):
        if shift > 0:
            cost = float(np.mean(np.abs(a_n[shift:] - b_n[:n-shift])))
        elif shift < 0:
            cost = float(np.mean(np.abs(a_n[:n+shift] - b_n[-shift:])))
        else:
            cost = direct_cost
        if cost < best_shift_cost:
            best_shift_cost = cost
            best_shift = shift

    return {
        "probe": "alignment",
        "direct_cost": round(direct_cost, 4),
        "best_shift": best_shift,
        "best_shift_cost": round(best_shift_cost, 4),
        "shift_improvement": round(1 - best_shift_cost / max(direct_cost, 1e-10), 4),
    }


# =====================================================================
# MASTER RUNNER
# =====================================================================

SINGLE_PROBES = [
    ("curvature", probe_curvature),
    ("growth_shape", probe_growth_shape),
    ("fft", probe_fft_signature),
    ("benford", probe_benford),
    ("moments", probe_moments),
    ("zipf", probe_zipf),
    ("entropy", probe_entropy),
    ("gaps", probe_gap_structure),
    ("fractal_dim", probe_fractal_dimension),
]

PAIR_PROBES = [
    ("spectral_cross", probe_spectral_cross),
    ("mutual_info", probe_mutual_information),
    ("wasserstein", probe_wasserstein),
    ("alignment", probe_alignment_cost),
]


def run_single_probes(a, name="array"):
    """Run all single-array probes."""
    results = {}
    a = np.array(a, dtype=float)
    a = a[np.isfinite(a)]
    for probe_name, probe_fn in SINGLE_PROBES:
        try:
            result = probe_fn(a)
            if result:
                results[probe_name] = result
        except Exception:
            pass
    return results


def run_pair_probes(a, b, name_a="a", name_b="b"):
    """Run all cross-dataset probes on a pair of arrays."""
    results = {}
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]

    for probe_name, probe_fn in PAIR_PROBES:
        try:
            result = probe_fn(a, b)
            if result:
                results[probe_name] = result
        except Exception:
            pass
    return results


def run_all_probes(a, b, name_a="a", name_b="b"):
    """Run all probes: single on each array, plus pair probes."""
    return {
        "single_a": run_single_probes(a, name_a),
        "single_b": run_single_probes(b, name_b),
        "pair": run_pair_probes(a, b, name_a, name_b),
    }


if __name__ == "__main__":
    # Self-test
    rng = np.random.RandomState(42)

    # Two correlated arrays
    a = np.sort(rng.exponential(100, 500))
    b = np.sort(rng.exponential(150, 500))

    print("=== Single probes on array A ===")
    for name, result in run_single_probes(a, "test_a").items():
        print(f"  {name}: {result}")

    print("\n=== Pair probes ===")
    for name, result in run_pair_probes(a, b).items():
        print(f"  {name}: {result}")
