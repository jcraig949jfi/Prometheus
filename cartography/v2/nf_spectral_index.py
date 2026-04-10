#!/usr/bin/env python3
"""
F8: Number Field Discriminant Spectral Index

Load 9,116 number fields, group by degree (2-6), compute FFT on
discriminant sequences (zero-mean, unit-variance normalized), extract
power spectra, fit spectral index alpha where P(f) ~ f^(-alpha).

Also compare to OEIS spectral signatures from representative families.
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import gzip

ROOT = Path(__file__).resolve().parent.parent
NF_PATH = ROOT / "number_fields" / "data" / "number_fields.json"
OEIS_PATH = ROOT / "oeis" / "data" / "stripped_new.txt"
OUT_PATH = Path(__file__).resolve().parent / "nf_spectral_index_results.json"


def load_number_fields():
    with open(NF_PATH) as f:
        data = json.load(f)
    by_degree = defaultdict(list)
    for nf in data:
        deg = nf["degree"]
        if deg in (2, 3, 4, 5, 6):
            by_degree[deg].append(int(nf["disc_abs"]))
    # Sort each group by discriminant value
    for deg in by_degree:
        by_degree[deg].sort()
    return dict(by_degree)


def compute_spectral_index(seq):
    """
    Compute power spectrum and spectral index for a sequence.
    Returns (alpha, r_squared, freqs, power, dominant_freq_idx).
    """
    arr = np.array(seq, dtype=np.float64)
    # Zero-mean, unit-variance normalization
    mu, sigma = arr.mean(), arr.std()
    if sigma < 1e-15:
        return None
    arr = (arr - mu) / sigma

    # FFT
    N = len(arr)
    fft_vals = np.fft.rfft(arr)
    power = np.abs(fft_vals) ** 2 / N
    freqs = np.fft.rfftfreq(N)

    # Skip DC component (index 0)
    freqs_pos = freqs[1:]
    power_pos = power[1:]

    if len(freqs_pos) < 5:
        return None

    # Dominant frequency (highest power)
    dominant_idx = np.argmax(power_pos)
    dominant_freq = freqs_pos[dominant_idx]

    # Fit spectral index: log P = -alpha * log f + c
    # Use only positive power values
    mask = power_pos > 0
    if mask.sum() < 5:
        return None

    log_f = np.log10(freqs_pos[mask])
    log_p = np.log10(power_pos[mask])

    # Linear regression
    A = np.vstack([log_f, np.ones_like(log_f)]).T
    result = np.linalg.lstsq(A, log_p, rcond=None)
    slope, intercept = result[0]
    alpha = -slope  # P(f) ~ f^(-alpha)

    # R-squared
    predicted = slope * log_f + intercept
    ss_res = np.sum((log_p - predicted) ** 2)
    ss_tot = np.sum((log_p - log_p.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return {
        "alpha": float(alpha),
        "r_squared": float(r_squared),
        "dominant_freq": float(dominant_freq),
        "dominant_freq_idx": int(dominant_idx),
        "n_points": int(N),
        "n_spectral_bins": int(len(freqs_pos)),
        "power_mean": float(power_pos.mean()),
        "power_max": float(power_pos.max()),
        "top5_freqs": [float(freqs_pos[i]) for i in np.argsort(power_pos)[-5:][::-1]],
        "top5_powers": [float(power_pos[i]) for i in np.argsort(power_pos)[-5:][::-1]],
    }


def load_oeis_families(n_seqs=50, min_len=100):
    """
    Load representative OEIS sequences for spectral comparison.
    Pick sequences from diverse families based on A-number ranges.
    """
    families = {}
    # Target some well-known families
    targets = {
        "primes": "A000040",
        "fibonacci": "A000045",
        "partition": "A000041",
        "catalan": "A000108",
        "triangular": "A000217",
        "squares": "A000290",
        "cubes": "A000578",
        "factorials": "A000142",
        "sigma": "A000203",       # sum of divisors
        "euler_totient": "A000010",
        "moebius": "A008683",
        "prime_gaps": "A001223",
        "twin_primes": "A001359",
        "mersenne_exp": "A000043",
        "bernoulli_num": "A027642",  # denominators
        "collatz_steps": "A006577",
        "abundant": "A005101",
        "semiprime": "A001358",
        "squarefree": "A005117",
        "highly_composite": "A002182",
    }

    if not OEIS_PATH.exists():
        print(f"OEIS data not found at {OEIS_PATH}, skipping comparison")
        return {}

    target_ids = set(targets.values())
    collected = {}

    with open(OEIS_PATH, "r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 2:
                continue
            seq_id = parts[0].strip()
            if seq_id in target_ids:
                vals = []
                for v in parts[1:]:
                    v = v.strip()
                    if v:
                        try:
                            vals.append(int(v))
                        except ValueError:
                            pass
                if len(vals) >= 30:
                    name = [k for k, v in targets.items() if v == seq_id][0]
                    collected[name] = vals

    return collected


def compare_spectra(nf_results, oeis_results):
    """Compare NF spectral indices to OEIS families."""
    comparisons = {}
    for deg, nf_spec in nf_results.items():
        if nf_spec is None:
            continue
        nf_alpha = nf_spec["alpha"]
        closest = None
        closest_dist = float("inf")
        for name, oeis_spec in oeis_results.items():
            if oeis_spec is None:
                continue
            dist = abs(nf_alpha - oeis_spec["alpha"])
            if dist < closest_dist:
                closest_dist = dist
                closest = name
        comparisons[str(deg)] = {
            "nf_alpha": nf_alpha,
            "closest_oeis": closest,
            "closest_oeis_alpha": oeis_results[closest]["alpha"] if closest and oeis_results.get(closest) else None,
            "alpha_distance": float(closest_dist) if closest else None,
        }
    return comparisons


def main():
    print("Loading number fields...")
    by_degree = load_number_fields()
    for deg in sorted(by_degree):
        print(f"  degree {deg}: {len(by_degree[deg])} fields, "
              f"disc range [{by_degree[deg][0]}, {by_degree[deg][-1]}]")

    # Compute spectral index for each degree
    print("\nComputing spectral indices...")
    nf_results = {}
    for deg in sorted(by_degree):
        seq = by_degree[deg]
        if len(seq) < 20:
            print(f"  degree {deg}: too few fields ({len(seq)}), skipping")
            nf_results[deg] = None
            continue
        result = compute_spectral_index(seq)
        if result:
            print(f"  degree {deg}: alpha={result['alpha']:.4f}, "
                  f"R²={result['r_squared']:.4f}, "
                  f"dominant_freq={result['dominant_freq']:.6f}, "
                  f"N={result['n_points']}")
            nf_results[deg] = result
        else:
            print(f"  degree {deg}: computation failed")
            nf_results[deg] = None

    # Check scaling of dominant frequency with degree
    print("\n--- Dominant frequency vs degree ---")
    dom_freqs = {}
    for deg in sorted(nf_results):
        if nf_results[deg]:
            dom_freqs[deg] = nf_results[deg]["dominant_freq"]
            print(f"  deg {deg}: dominant_freq = {dom_freqs[deg]:.6f}")

    freq_scaling = None
    if len(dom_freqs) >= 3:
        degs = np.array(list(dom_freqs.keys()), dtype=float)
        freqs = np.array(list(dom_freqs.values()))
        # Fit log-log: freq ~ degree^beta
        mask = freqs > 0
        if mask.sum() >= 2:
            log_d = np.log10(degs[mask])
            log_f = np.log10(freqs[mask])
            A = np.vstack([log_d, np.ones_like(log_d)]).T
            res = np.linalg.lstsq(A, log_f, rcond=None)
            beta = res[0][0]
            predicted = res[0][0] * log_d + res[0][1]
            ss_res = np.sum((log_f - predicted) ** 2)
            ss_tot = np.sum((log_f - log_f.mean()) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            freq_scaling = {"beta": float(beta), "r_squared": float(r2)}
            print(f"  freq ~ degree^{beta:.3f} (R²={r2:.4f})")

    # Check alpha vs degree
    print("\n--- Spectral index alpha vs degree ---")
    alpha_trend = {}
    for deg in sorted(nf_results):
        if nf_results[deg]:
            alpha_trend[deg] = nf_results[deg]["alpha"]
            print(f"  deg {deg}: alpha = {alpha_trend[deg]:.4f}")

    alpha_scaling = None
    if len(alpha_trend) >= 3:
        degs = np.array(list(alpha_trend.keys()), dtype=float)
        alphas = np.array(list(alpha_trend.values()))
        # Linear fit: alpha = m * degree + b
        A = np.vstack([degs, np.ones_like(degs)]).T
        res = np.linalg.lstsq(A, alphas, rcond=None)
        slope, intercept = res[0]
        predicted = slope * degs + intercept
        ss_res = np.sum((alphas - predicted) ** 2)
        ss_tot = np.sum((alphas - alphas.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        alpha_scaling = {
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r2),
        }
        print(f"  alpha = {slope:.4f} * degree + {intercept:.4f} (R²={r2:.4f})")

    # Load OEIS families for comparison
    print("\nLoading OEIS families for spectral comparison...")
    oeis_seqs = load_oeis_families()
    print(f"  Loaded {len(oeis_seqs)} OEIS families")

    oeis_results = {}
    for name, seq in oeis_seqs.items():
        result = compute_spectral_index(seq)
        if result:
            oeis_results[name] = result
            print(f"  {name}: alpha={result['alpha']:.4f}, N={result['n_points']}")

    # Compare
    print("\n--- Cross-domain spectral comparison ---")
    comparisons = compare_spectra(nf_results, oeis_results)
    for deg_str, comp in comparisons.items():
        print(f"  degree {deg_str}: alpha={comp['nf_alpha']:.4f} "
              f"closest OEIS={comp['closest_oeis']} "
              f"(alpha={comp['closest_oeis_alpha']:.4f}, "
              f"dist={comp['alpha_distance']:.4f})" if comp['closest_oeis'] else
              f"  degree {deg_str}: no OEIS comparison available")

    # Null test: shuffle discriminants, recompute alpha
    print("\n--- Null test: shuffled discriminants ---")
    rng = np.random.RandomState(42)
    null_alphas = {}
    for deg in sorted(by_degree):
        seq = by_degree[deg]
        if len(seq) < 20:
            continue
        shuffled = list(seq)
        rng.shuffle(shuffled)
        result = compute_spectral_index(shuffled)
        if result:
            null_alphas[deg] = result["alpha"]
            real_alpha = nf_results[deg]["alpha"] if nf_results[deg] else None
            print(f"  deg {deg}: null alpha={result['alpha']:.4f}, "
                  f"real alpha={real_alpha:.4f}" if real_alpha else
                  f"  deg {deg}: null alpha={result['alpha']:.4f}")

    # Build output
    output = {
        "problem": "F8: Number Field Discriminant Spectral Index",
        "description": (
            "FFT spectral analysis of discriminant sequences grouped by degree. "
            "Tests whether spectral index alpha (P(f)~f^-alpha) varies with degree, "
            "and compares to OEIS spectral signatures."
        ),
        "data": {
            "total_fields": sum(len(v) for v in by_degree.values()),
            "fields_per_degree": {str(d): len(v) for d, v in sorted(by_degree.items())},
        },
        "spectral_indices": {
            str(deg): nf_results[deg] for deg in sorted(nf_results)
        },
        "dominant_frequency_scaling": freq_scaling,
        "alpha_vs_degree": alpha_scaling,
        "null_test_shuffled_alphas": {str(d): v for d, v in null_alphas.items()},
        "oeis_comparison": {
            "n_oeis_families": len(oeis_results),
            "oeis_spectral_indices": {
                name: {"alpha": r["alpha"], "r_squared": r["r_squared"], "n_points": r["n_points"]}
                for name, r in sorted(oeis_results.items())
            },
            "closest_matches": comparisons,
        },
        "findings": [],
    }

    # Summarize findings
    findings = []

    # 1. Does alpha change with degree?
    if alpha_scaling:
        if abs(alpha_scaling["r_squared"]) > 0.7:
            findings.append(
                f"Alpha shows strong linear trend with degree: "
                f"slope={alpha_scaling['slope']:.4f}, R²={alpha_scaling['r_squared']:.4f}"
            )
        elif abs(alpha_scaling["r_squared"]) > 0.3:
            findings.append(
                f"Alpha shows moderate trend with degree: "
                f"slope={alpha_scaling['slope']:.4f}, R²={alpha_scaling['r_squared']:.4f}"
            )
        else:
            findings.append(
                f"Alpha shows no clear trend with degree: "
                f"slope={alpha_scaling['slope']:.4f}, R²={alpha_scaling['r_squared']:.4f}"
            )

    # 2. Dominant frequency scaling
    if freq_scaling:
        findings.append(
            f"Dominant frequency scales as degree^{freq_scaling['beta']:.3f} "
            f"(R²={freq_scaling['r_squared']:.4f})"
        )

    # 3. Null test
    for deg in sorted(null_alphas):
        if nf_results.get(deg):
            real = nf_results[deg]["alpha"]
            null = null_alphas[deg]
            if abs(real - null) > 0.3:
                findings.append(
                    f"Degree {deg}: real alpha ({real:.3f}) differs from null ({null:.3f}) "
                    f"by {abs(real-null):.3f} — sorted order carries spectral structure"
                )

    # 4. OEIS matches
    for deg_str, comp in comparisons.items():
        if comp.get("alpha_distance") is not None and comp["alpha_distance"] < 0.2:
            findings.append(
                f"Degree {deg_str} discriminants spectrally similar to OEIS {comp['closest_oeis']} "
                f"(alpha distance={comp['alpha_distance']:.4f})"
            )

    output["findings"] = findings
    print("\n=== FINDINGS ===")
    for f in findings:
        print(f"  • {f}")

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
