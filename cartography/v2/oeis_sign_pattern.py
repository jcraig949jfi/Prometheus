#!/usr/bin/env python3
"""
OEIS Sign Pattern Structure
============================
For sequences with keyword 'sign', analyze the sign patterns:
- Fraction positive, negative, zero
- Autocorrelation of sign sequence at lags 1-10
- Periodicity detection via DFT on sign sequence
- Sign entropy (how predictable is the pattern?)

Data: OEIS stripped_new.txt + oeis_keywords.json
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
import time

DATA_FILE = Path(__file__).parent.parent / "oeis" / "data" / "stripped_new.txt"
KEYWORDS_FILE = Path(__file__).parent.parent / "oeis" / "data" / "oeis_keywords.json"
NAMES_FILE = Path(__file__).parent.parent / "oeis" / "data" / "oeis_names.json"
OUT_FILE = Path(__file__).parent / "oeis_sign_pattern_results.json"

MIN_TERMS = 10  # need at least 10 terms for meaningful analysis


def load_sign_sequence_ids():
    """Get all sequence IDs with 'sign' keyword."""
    with open(KEYWORDS_FILE) as f:
        kw = json.load(f)
    return {k for k, v in kw.items() if "sign" in v}


def load_sequences(sign_ids):
    """Load terms for sign sequences from stripped file."""
    seqs = {}
    with open(DATA_FILE) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            aid = parts[0]
            if aid not in sign_ids:
                continue
            raw = parts[1].strip().strip(",")
            if not raw:
                continue
            try:
                terms = [int(x) for x in raw.split(",") if x.strip()]
            except ValueError:
                continue
            if len(terms) >= MIN_TERMS:
                seqs[aid] = terms
    return seqs


def sign_of(x):
    """Return +1, -1, or 0."""
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0


def sign_entropy(signs):
    """Shannon entropy of sign distribution (bits). Max = log2(3) ~ 1.585."""
    c = Counter(signs)
    n = len(signs)
    if n == 0:
        return 0.0
    ent = 0.0
    for count in c.values():
        p = count / n
        if p > 0:
            ent -= p * np.log2(p)
    return ent


def autocorrelation(signs, max_lag=10):
    """Autocorrelation of sign sequence at lags 1..max_lag."""
    s = np.array(signs, dtype=float)
    n = len(s)
    if n < max_lag + 2:
        max_lag = n - 2
    if max_lag < 1:
        return []
    mean = s.mean()
    var = np.var(s)
    if var < 1e-15:
        return [0.0] * max_lag
    acf = []
    for lag in range(1, max_lag + 1):
        c = np.mean((s[:n - lag] - mean) * (s[lag:] - mean)) / var
        acf.append(float(c))
    return acf


def detect_periodicity(signs, max_period=50):
    """
    Use DFT on the sign sequence to find dominant period.
    Returns (dominant_period, spectral_peak_ratio).
    spectral_peak_ratio = peak power / mean power — high means periodic.
    """
    s = np.array(signs, dtype=float)
    n = len(s)
    if n < 6:
        return None, 0.0

    # Remove mean
    s = s - s.mean()
    if np.all(s == 0):
        return None, 0.0

    # DFT
    ft = np.fft.rfft(s)
    power = np.abs(ft) ** 2
    # Skip DC component (index 0)
    power = power[1:]
    if len(power) == 0:
        return None, 0.0

    mean_power = power.mean()
    if mean_power < 1e-15:
        return None, 0.0

    peak_idx = np.argmax(power)
    peak_ratio = float(power[peak_idx] / mean_power)

    # Convert frequency index to period
    # freq index k corresponds to frequency k/n, period = n/k
    freq_idx = peak_idx + 1  # +1 because we skipped DC
    period = n / freq_idx

    return float(period), peak_ratio


def classify_sign_pattern(signs):
    """Classify: all_positive, all_negative, alternating, periodic, mixed."""
    unique = set(signs)
    if unique <= {1}:
        return "all_positive"
    if unique <= {-1}:
        return "all_negative"
    if unique <= {0}:
        return "all_zero"
    if unique <= {0, 1}:
        return "nonneg_with_zeros"
    if unique <= {0, -1}:
        return "nonpos_with_zeros"

    # Check perfect alternation (+,-,+,-,... or -,+,-,+,...)
    n = len(signs)
    nonzero = [s for s in signs if s != 0]
    if len(nonzero) >= 4:
        alt = all(nonzero[i] * nonzero[i + 1] < 0 for i in range(len(nonzero) - 1))
        if alt:
            return "alternating"

    # Check periodicity
    for p in range(2, min(20, n // 3 + 1)):
        periodic = True
        for i in range(p, n):
            if signs[i] != signs[i % p]:
                periodic = False
                break
        if periodic:
            return f"periodic_p{p}"

    return "mixed"


def run_analysis():
    t0 = time.time()
    print("Loading sign sequence IDs...")
    sign_ids = load_sign_sequence_ids()
    print(f"  {len(sign_ids)} sequences with 'sign' keyword")

    print("Loading sequence data...")
    seqs = load_sequences(sign_ids)
    print(f"  {len(seqs)} sequences loaded with >= {MIN_TERMS} terms")

    # Try loading from full stripped too
    names = {}
    try:
        with open(NAMES_FILE) as f:
            names = json.load(f)
    except Exception:
        pass

    # Per-sequence analysis
    results_per_seq = {}
    all_fracs_pos = []
    all_fracs_neg = []
    all_fracs_zero = []
    all_entropies = []
    all_acf = []  # list of acf vectors
    all_peak_ratios = []
    all_periods = []
    pattern_counts = Counter()
    acf_by_pattern = defaultdict(list)

    for aid, terms in seqs.items():
        signs = [sign_of(x) for x in terms]
        n = len(signs)
        c = Counter(signs)
        frac_pos = c.get(1, 0) / n
        frac_neg = c.get(-1, 0) / n
        frac_zero = c.get(0, 0) / n

        ent = sign_entropy(signs)
        acf = autocorrelation(signs, max_lag=10)
        period, peak_ratio = detect_periodicity(signs)
        pattern = classify_sign_pattern(signs)

        all_fracs_pos.append(frac_pos)
        all_fracs_neg.append(frac_neg)
        all_fracs_zero.append(frac_zero)
        all_entropies.append(ent)
        if len(acf) == 10:
            all_acf.append(acf)
        all_peak_ratios.append(peak_ratio)
        if period is not None:
            all_periods.append(period)
        pattern_counts[pattern] += 1
        if len(acf) == 10:
            acf_by_pattern[pattern].append(acf)

        results_per_seq[aid] = {
            "n_terms": n,
            "frac_pos": round(frac_pos, 4),
            "frac_neg": round(frac_neg, 4),
            "frac_zero": round(frac_zero, 4),
            "entropy": round(ent, 4),
            "acf_lag1": round(acf[0], 4) if acf else None,
            "spectral_peak_ratio": round(peak_ratio, 2),
            "dominant_period": round(period, 2) if period else None,
            "pattern": pattern,
        }

    # Aggregate statistics
    all_fracs_pos = np.array(all_fracs_pos)
    all_fracs_neg = np.array(all_fracs_neg)
    all_fracs_zero = np.array(all_fracs_zero)
    all_entropies = np.array(all_entropies)
    all_acf = np.array(all_acf) if all_acf else np.zeros((0, 10))
    all_peak_ratios = np.array(all_peak_ratios)

    # Entropy histogram bins
    ent_bins = np.linspace(0, 1.6, 17)
    ent_hist, _ = np.histogram(all_entropies, bins=ent_bins)

    # ACF lag-1 histogram
    acf1_values = all_acf[:, 0] if len(all_acf) > 0 else np.array([])
    acf1_bins = np.linspace(-1, 1, 21)
    acf1_hist, _ = np.histogram(acf1_values, bins=acf1_bins)

    # Spectral peak ratio histogram
    pr_bins = [0, 2, 5, 10, 20, 50, 100, 500, 1e6]
    pr_hist, _ = np.histogram(all_peak_ratios, bins=pr_bins)

    # Mean ACF by lag
    mean_acf = all_acf.mean(axis=0).tolist() if len(all_acf) > 0 else []
    std_acf = all_acf.std(axis=0).tolist() if len(all_acf) > 0 else []

    # Mean ACF by pattern type
    mean_acf_by_pattern = {}
    for pat, acfs in acf_by_pattern.items():
        if len(acfs) >= 10:
            arr = np.array(acfs)
            mean_acf_by_pattern[pat] = {
                "mean_acf": [round(x, 4) for x in arr.mean(axis=0).tolist()],
                "count": len(acfs),
            }

    # Strongly periodic: peak ratio > 20
    n_strongly_periodic = int(np.sum(all_peak_ratios > 20))
    # Alternating (acf lag-1 < -0.5)
    n_strongly_alternating = int(np.sum(acf1_values < -0.5)) if len(acf1_values) > 0 else 0
    # Positively correlated (acf lag-1 > 0.5)
    n_positively_correlated = int(np.sum(acf1_values > 0.5)) if len(acf1_values) > 0 else 0

    # Top examples of each pattern
    examples = {}
    for pat in sorted(pattern_counts.keys(), key=lambda p: -pattern_counts[p]):
        exs = [(aid, r) for aid, r in results_per_seq.items() if r["pattern"] == pat]
        exs.sort(key=lambda x: -x[1]["n_terms"])
        top = []
        for aid, r in exs[:5]:
            top.append({
                "id": aid,
                "name": names.get(aid, ""),
                "n_terms": r["n_terms"],
                "entropy": r["entropy"],
                "acf_lag1": r["acf_lag1"],
            })
        examples[pat] = top

    # Highest entropy sequences (most unpredictable signs)
    sorted_by_ent = sorted(results_per_seq.items(), key=lambda x: -x[1]["entropy"])
    top_high_entropy = []
    for aid, r in sorted_by_ent[:20]:
        top_high_entropy.append({
            "id": aid,
            "name": names.get(aid, ""),
            "entropy": r["entropy"],
            "frac_pos": r["frac_pos"],
            "frac_neg": r["frac_neg"],
            "frac_zero": r["frac_zero"],
            "acf_lag1": r["acf_lag1"],
            "pattern": r["pattern"],
        })

    # Lowest entropy (most predictable)
    sorted_by_ent_asc = sorted(
        [(aid, r) for aid, r in results_per_seq.items() if r["pattern"] == "mixed"],
        key=lambda x: x[1]["entropy"]
    )
    top_low_entropy_mixed = []
    for aid, r in sorted_by_ent_asc[:20]:
        top_low_entropy_mixed.append({
            "id": aid,
            "name": names.get(aid, ""),
            "entropy": r["entropy"],
            "pattern": r["pattern"],
            "acf_lag1": r["acf_lag1"],
        })

    # Most strongly periodic (highest spectral peak)
    sorted_by_peak = sorted(results_per_seq.items(), key=lambda x: -x[1]["spectral_peak_ratio"])
    top_periodic = []
    for aid, r in sorted_by_peak[:20]:
        top_periodic.append({
            "id": aid,
            "name": names.get(aid, ""),
            "spectral_peak_ratio": r["spectral_peak_ratio"],
            "dominant_period": r["dominant_period"],
            "entropy": r["entropy"],
            "pattern": r["pattern"],
        })

    elapsed = time.time() - t0

    output = {
        "metadata": {
            "n_sign_sequences_total": len(sign_ids),
            "n_loaded": len(seqs),
            "min_terms": MIN_TERMS,
            "elapsed_sec": round(elapsed, 1),
        },
        "sign_fraction_stats": {
            "frac_positive": {
                "mean": round(float(all_fracs_pos.mean()), 4),
                "median": round(float(np.median(all_fracs_pos)), 4),
                "std": round(float(all_fracs_pos.std()), 4),
            },
            "frac_negative": {
                "mean": round(float(all_fracs_neg.mean()), 4),
                "median": round(float(np.median(all_fracs_neg)), 4),
                "std": round(float(all_fracs_neg.std()), 4),
            },
            "frac_zero": {
                "mean": round(float(all_fracs_zero.mean()), 4),
                "median": round(float(np.median(all_fracs_zero)), 4),
                "std": round(float(all_fracs_zero.std()), 4),
            },
        },
        "entropy_stats": {
            "mean": round(float(all_entropies.mean()), 4),
            "median": round(float(np.median(all_entropies)), 4),
            "std": round(float(all_entropies.std()), 4),
            "histogram_bins": [round(b, 2) for b in ent_bins.tolist()],
            "histogram_counts": ent_hist.tolist(),
        },
        "autocorrelation": {
            "mean_acf_by_lag": [round(x, 4) for x in mean_acf],
            "std_acf_by_lag": [round(x, 4) for x in std_acf],
            "n_strongly_alternating_acf1_lt_neg05": n_strongly_alternating,
            "n_positively_correlated_acf1_gt_05": n_positively_correlated,
            "acf1_histogram_bins": [round(b, 2) for b in acf1_bins.tolist()],
            "acf1_histogram_counts": acf1_hist.tolist(),
        },
        "periodicity": {
            "n_strongly_periodic_peak_gt_20": n_strongly_periodic,
            "spectral_peak_ratio_histogram_bins": [str(b) for b in pr_bins],
            "spectral_peak_ratio_histogram_counts": pr_hist.tolist(),
            "top_periodic_sequences": top_periodic,
        },
        "pattern_classification": {
            "counts": dict(sorted(pattern_counts.items(), key=lambda x: -x[1])),
            "examples": examples,
        },
        "mean_acf_by_pattern": mean_acf_by_pattern,
        "top_high_entropy_sequences": top_high_entropy,
        "top_low_entropy_mixed_sequences": top_low_entropy_mixed,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")
    print(f"Elapsed: {elapsed:.1f}s")

    # Print summary
    print(f"\n=== OEIS Sign Pattern Summary ===")
    print(f"Sequences analyzed: {len(seqs)}")
    print(f"\nSign fractions (mean): +{all_fracs_pos.mean():.3f}  -{all_fracs_neg.mean():.3f}  0:{all_fracs_zero.mean():.3f}")
    print(f"Sign entropy: mean={all_entropies.mean():.3f}, median={np.median(all_entropies):.3f}")
    print(f"\nMean ACF by lag: {' '.join(f'{x:.3f}' for x in mean_acf[:5])}")
    print(f"Strongly alternating (acf1 < -0.5): {n_strongly_alternating}")
    print(f"Positively correlated (acf1 > 0.5): {n_positively_correlated}")
    print(f"Strongly periodic (peak ratio > 20): {n_strongly_periodic}")
    print(f"\nPattern classification:")
    for pat, cnt in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"  {pat:30s} {cnt:6d} ({100*cnt/len(seqs):.1f}%)")


if __name__ == "__main__":
    run_analysis()
