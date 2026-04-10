"""
M2: Enrichment-Position Curve E(n)
===================================
Measures how mod-p fingerprint enrichment varies with term position
in OEIS sequences. The K5 kill test showed non-monotonic behavior:
12.5x at [0:20], 10.6x at [20:40], 32.2x at [40:60]. This script
maps the full curve with sliding windows.

Key questions:
- Is the dip at 20-40 reproducible?
- Does enrichment keep rising after 40-60?
- Is there a peak? Where?
- What determines the characteristic position?

Usage:
    python enrichment_position_curve.py
"""

import gzip
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
OEIS_STRIPPED_GZ = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_TXT = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
C08_RESULTS = V2_DIR / "recurrence_euler_factor_results.json"
OUT_FILE = V2_DIR / "enrichment_position_results.json"

# Configuration
PRIMES = [2, 5, 11]
FP_LEN = 20          # fingerprint window length
WINDOW_STEP = 10     # step size for sliding window
MAX_START = 80       # maximum start position (need start + FP_LEN = 100 terms)
N_RANDOM_PAIRS = 50000  # more pairs to avoid 0-rate problem
BM_SAMPLE_SIZE = 40000  # sequences to scan with BM
MIN_FAMILY_SIZE = 3     # minimum sequences per family

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# Berlekamp-Massey (from scaling_law_battery.py)
# ---------------------------------------------------------------------------
def berlekamp_massey(seq):
    """Minimal LFSR. Returns (coefficients, degree) or None."""
    n = len(seq)
    if n == 0:
        return None
    b, c = [1], [1]
    l, m, d_b = 0, 1, 1
    for i in range(n):
        d = seq[i]
        for j in range(1, l + 1):
            if j < len(c) and i - j >= 0:
                d += c[j] * seq[i - j]
        if d == 0:
            m += 1
        elif 2 * l <= i:
            t = list(c)
            ratio = -d / d_b if d_b != 0 else 0
            while len(c) < len(b) + m:
                c.append(0)
            for j in range(len(b)):
                c[j + m] += ratio * b[j]
            l = i + 1 - l
            b, d_b, m = t, d, 1
        else:
            ratio = -d / d_b if d_b != 0 else 0
            while len(c) < len(b) + m:
                c.append(0)
            for j in range(len(b)):
                c[j + m] += ratio * b[j]
            m += 1
    if l == 0 or l > n // 3:
        return None
    return c[:l + 1], l


# ---------------------------------------------------------------------------
# Load OEIS
# ---------------------------------------------------------------------------
def load_oeis(min_terms=100):
    """Load OEIS sequences with at least min_terms terms."""
    cache = {}
    src = OEIS_STRIPPED_TXT if OEIS_STRIPPED_TXT.exists() else OEIS_STRIPPED_GZ
    if not src.exists():
        print(f"  ERROR: {src} not found")
        return cache
    opener = gzip.open if str(src).endswith('.gz') else open
    mode = "rt" if str(src).endswith('.gz') else "r"
    print(f"  Loading OEIS from {src.name} (min {min_terms} terms)...")
    with opener(src, mode, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < min_terms + 1:
                continue
            sid = parts[0].strip()
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try:
                        terms.append(int(t))
                    except ValueError:
                        pass
            if len(terms) >= min_terms:
                cache[sid] = terms
    print(f"  Loaded {len(cache):,} sequences with {min_terms}+ terms")
    return cache


# ---------------------------------------------------------------------------
# Build families via Berlekamp-Massey
# ---------------------------------------------------------------------------
def build_families(oeis_data, sample_size=BM_SAMPLE_SIZE):
    """Build polynomial families from BM on a sample of sequences."""
    print(f"\n  Building families via Berlekamp-Massey on {sample_size} sequences...")
    all_ids = list(oeis_data.keys())
    sample_ids = random.sample(all_ids, min(sample_size, len(all_ids)))

    poly_clusters = defaultdict(list)
    degree_counts = Counter()

    for i, sid in enumerate(sample_ids):
        terms = oeis_data[sid]
        # Use first 60 terms for BM detection
        result = berlekamp_massey([float(t) for t in terms[:60]])
        if result is not None:
            coeffs, degree = result
            if 2 <= degree <= 8:
                key = tuple(round(c, 6) for c in coeffs)
                poly_clusters[str(key)].append(sid)
                degree_counts[degree] += 1
        if (i + 1) % 10000 == 0:
            print(f"    Scanned {i+1}/{sample_size}...")

    # Filter to families with MIN_FAMILY_SIZE+ members
    families = {k: v for k, v in poly_clusters.items() if len(v) >= MIN_FAMILY_SIZE}

    total_seqs = sum(len(v) for v in families.values())
    sizes = sorted([len(v) for v in families.values()], reverse=True)
    print(f"  Built {len(families)} families ({total_seqs} sequences)")
    print(f"  Largest families: {sizes[:10]}")
    print(f"  Degree distribution of all BM hits: {degree_counts.most_common()}")

    # Also extract degree per family for characteristic-length analysis
    family_degrees = {}
    for k, v in families.items():
        # Re-extract degree from the first sequence
        sid = v[0]
        result = berlekamp_massey([float(t) for t in oeis_data[sid][:60]])
        if result is not None:
            family_degrees[k] = result[1]

    return families, family_degrees


# ---------------------------------------------------------------------------
# Fingerprint and enrichment computation
# ---------------------------------------------------------------------------
def fingerprint(terms, p, start=0, fp_len=FP_LEN):
    """Compute mod-p fingerprint of terms[start:start+fp_len]."""
    window = terms[start:start + fp_len]
    if len(window) < fp_len:
        return None
    return tuple(t % p for t in window)


def compute_family_match_rate(families, oeis_data, p, start=0):
    """Compute fraction of within-family pairs sharing exact mod-p fingerprint.
    Only considers families where enough sequences have sufficient terms."""
    matches = 0
    total = 0
    for poly, seq_ids in families.items():
        # Filter to sequences with enough terms for this window
        valid = [s for s in seq_ids if len(oeis_data[s]) >= start + FP_LEN]
        if len(valid) < 2:
            continue
        fps = {}
        for sid in valid:
            fp = fingerprint(oeis_data[sid], p, start)
            if fp is not None:
                fps[sid] = fp
        sids = list(fps.keys())
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                total += 1
                if fps[sids[i]] == fps[sids[j]]:
                    matches += 1
    rate = matches / total if total > 0 else 0
    return rate, total, matches


def compute_random_match_rate(oeis_data, p, start=0, n_pairs=N_RANDOM_PAIRS):
    """Compute exact match rate for random pairs at given position."""
    all_ids = [s for s in oeis_data if len(oeis_data[s]) >= start + FP_LEN]
    if len(all_ids) < 100:
        return 0, 0, 0
    matches = 0
    tested = 0
    for _ in range(n_pairs):
        a, b = random.sample(all_ids, 2)
        fp_a = fingerprint(oeis_data[a], p, start)
        fp_b = fingerprint(oeis_data[b], p, start)
        if fp_a is not None and fp_b is not None:
            tested += 1
            if fp_a == fp_b:
                matches += 1
    rate = matches / tested if tested > 0 else 0
    return rate, tested, matches


def enrichment_ratio(family_rate, random_rate):
    """Compute enrichment, with proper handling when random_rate is 0."""
    if random_rate == 0:
        # Use Laplace smoothing: assume 1 match in N+1 pairs
        return None  # Signal that we can't compute
    return family_rate / random_rate


# ---------------------------------------------------------------------------
# Model fitting
# ---------------------------------------------------------------------------
def fit_models(positions, enrichments):
    """Fit linear, quadratic, logarithmic, and periodic models to E(n)."""
    x = np.array(positions, dtype=float)
    y = np.array(enrichments, dtype=float)

    # Filter out None/inf values
    valid = np.isfinite(y)
    x = x[valid]
    y = y[valid]

    if len(x) < 3:
        return {"error": "insufficient data points"}

    results = {}

    # Linear: E(n) = a + b*n
    try:
        coeffs = np.polyfit(x, y, 1)
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        results["linear"] = {
            "params": {"a": float(coeffs[1]), "b": float(coeffs[0])},
            "r_squared": float(r2),
            "formula": f"E(n) = {coeffs[1]:.2f} + {coeffs[0]:.4f}*n"
        }
    except Exception as e:
        results["linear"] = {"error": str(e)}

    # Quadratic: E(n) = a + b*n + c*n^2
    try:
        coeffs = np.polyfit(x, y, 2)
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        # Find vertex
        if coeffs[0] != 0:
            vertex_x = -coeffs[1] / (2 * coeffs[0])
            vertex_y = np.polyval(coeffs, vertex_x)
        else:
            vertex_x, vertex_y = None, None
        results["quadratic"] = {
            "params": {"a": float(coeffs[2]), "b": float(coeffs[1]), "c": float(coeffs[0])},
            "r_squared": float(r2),
            "vertex_position": float(vertex_x) if vertex_x is not None else None,
            "vertex_enrichment": float(vertex_y) if vertex_y is not None else None,
            "formula": f"E(n) = {coeffs[2]:.2f} + {coeffs[1]:.4f}*n + {coeffs[0]:.6f}*n^2"
        }
    except Exception as e:
        results["quadratic"] = {"error": str(e)}

    # Logarithmic: E(n) = a + b*log(n+1) (shift to avoid log(0))
    try:
        log_x = np.log(x + 1)
        coeffs = np.polyfit(log_x, y, 1)
        y_pred = coeffs[0] * log_x + coeffs[1]
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        results["logarithmic"] = {
            "params": {"a": float(coeffs[1]), "b": float(coeffs[0])},
            "r_squared": float(r2),
            "formula": f"E(n) = {coeffs[1]:.2f} + {coeffs[0]:.4f}*log(n+1)"
        }
    except Exception as e:
        results["logarithmic"] = {"error": str(e)}

    # Periodic: E(n) = a + b*sin(c*n + d)
    try:
        def periodic(n, a, b, c, d):
            return a + b * np.sin(c * n + d)

        # Initial guess: mean as offset, amplitude from range, period ~40
        a0 = np.mean(y)
        b0 = (np.max(y) - np.min(y)) / 2
        c0 = 2 * np.pi / 40  # guess period = 40
        d0 = 0
        popt, pcov = curve_fit(periodic, x, y, p0=[a0, b0, c0, d0],
                               maxfev=10000)
        y_pred = periodic(x, *popt)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        period = 2 * np.pi / abs(popt[2]) if popt[2] != 0 else float('inf')
        results["periodic"] = {
            "params": {"a": float(popt[0]), "b": float(popt[1]),
                       "c": float(popt[2]), "d": float(popt[3])},
            "r_squared": float(r2),
            "implied_period": float(period),
            "formula": f"E(n) = {popt[0]:.2f} + {popt[1]:.2f}*sin({popt[2]:.4f}*n + {popt[3]:.2f})"
        }
    except Exception as e:
        results["periodic"] = {"error": str(e)}

    # Best model
    r2_scores = {}
    for model_name, model_data in results.items():
        if "r_squared" in model_data:
            r2_scores[model_name] = model_data["r_squared"]
    if r2_scores:
        best = max(r2_scores, key=r2_scores.get)
        results["best_model"] = best
        results["best_r_squared"] = r2_scores[best]

    return results


# ---------------------------------------------------------------------------
# Characteristic length analysis
# ---------------------------------------------------------------------------
def analyze_characteristic_length(enrichment_by_prime, family_degrees, positions):
    """Analyze whether peak position relates to recurrence order."""
    analysis = {}

    # Find peak position per prime
    for p_str, curve in enrichment_by_prime.items():
        valid = [(pos, e) for pos, e in zip(positions, curve) if e is not None]
        if not valid:
            continue
        peak_pos, peak_e = max(valid, key=lambda x: x[1])
        min_pos, min_e = min(valid, key=lambda x: x[1])
        analysis[p_str] = {
            "peak_position": peak_pos,
            "peak_enrichment": peak_e,
            "min_position": min_pos,
            "min_enrichment": min_e,
            "ratio_peak_to_min": peak_e / min_e if min_e > 0 else float('inf'),
        }

    # Degree distribution of families
    degree_dist = Counter(family_degrees.values())
    analysis["family_degree_distribution"] = dict(degree_dist.most_common())

    # Median recurrence order
    degrees = list(family_degrees.values())
    if degrees:
        analysis["median_recurrence_order"] = float(np.median(degrees))
        analysis["mean_recurrence_order"] = float(np.mean(degrees))

    return analysis


# ---------------------------------------------------------------------------
# Stratified analysis: enrichment curve by recurrence degree
# ---------------------------------------------------------------------------
def compute_enrichment_by_degree(families, family_degrees, oeis_data, positions, p=2):
    """Compute enrichment curve separately for each recurrence degree."""
    # Group families by degree
    degree_groups = defaultdict(dict)
    for fam_key, seq_ids in families.items():
        deg = family_degrees.get(fam_key)
        if deg is not None:
            degree_groups[deg][fam_key] = seq_ids

    results = {}
    for deg in sorted(degree_groups.keys()):
        deg_families = degree_groups[deg]
        n_fam = len(deg_families)
        n_seq = sum(len(v) for v in deg_families.values())
        if n_fam < 2 or n_seq < 6:
            continue

        curve = []
        for start in positions:
            fam_rate, fam_n, fam_matches = compute_family_match_rate(
                deg_families, oeis_data, p, start=start)
            if fam_n < 5:
                curve.append(None)
                continue
            rand_rate, _, _ = compute_random_match_rate(oeis_data, p, start=start, n_pairs=20000)
            e = enrichment_ratio(fam_rate, rand_rate)
            curve.append(e)
        results[str(deg)] = {
            "n_families": n_fam,
            "n_sequences": n_seq,
            "curve": curve,
        }
        print(f"    Degree {deg}: {n_fam} families, {n_seq} seqs, "
              f"curve = {[f'{x:.1f}' if x is not None else 'None' for x in curve]}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("M2: Enrichment-Position Curve E(n)")
    print("=" * 70)

    # 1. Load data
    oeis_data = load_oeis(min_terms=100)
    if len(oeis_data) < 1000:
        print("ERROR: insufficient OEIS data")
        return

    # 2. Build families
    families, family_degrees = build_families(oeis_data)
    if len(families) < 5:
        print("ERROR: insufficient families built")
        return

    # 3. Define sliding windows
    positions = list(range(0, MAX_START + 1, WINDOW_STEP))
    print(f"\n  Window positions: {positions}")
    print(f"  Window size: {FP_LEN}, step: {WINDOW_STEP}")
    print(f"  Windows: {[f'[{s}:{s+FP_LEN}]' for s in positions]}")

    # 4. Compute enrichment at each position for each prime
    print("\n" + "=" * 70)
    print("  Computing enrichment curve...")
    print("=" * 70)

    enrichment_curves = {}  # {prime_str: [enrichment at each position]}
    detailed_data = {}      # {prime_str: [{family_rate, random_rate, enrichment, ...}]}

    for p in PRIMES:
        print(f"\n  --- Prime p={p} ---")
        curve = []
        details = []

        # Compute random rates for all positions first (for consistency)
        print(f"  Computing random baselines...")
        random_rates = {}
        for start in positions:
            rand_rate, rand_n, rand_matches = compute_random_match_rate(
                oeis_data, p, start=start)
            random_rates[start] = {
                "rate": rand_rate, "pairs": rand_n, "matches": rand_matches
            }
            print(f"    Position {start}: random_rate={rand_rate:.6f} ({rand_matches}/{rand_n})")

        # Compute family rates
        print(f"  Computing family rates...")
        for start in positions:
            fam_rate, fam_n, fam_matches = compute_family_match_rate(
                families, oeis_data, p, start=start)
            rand_rate = random_rates[start]["rate"]
            e = enrichment_ratio(fam_rate, rand_rate)

            detail = {
                "position": start,
                "window": f"[{start}:{start+FP_LEN}]",
                "family_rate": fam_rate,
                "family_pairs": fam_n,
                "family_matches": fam_matches,
                "random_rate": rand_rate,
                "random_pairs": random_rates[start]["pairs"],
                "random_matches": random_rates[start]["matches"],
                "enrichment": e,
            }
            details.append(detail)
            curve.append(e)

            e_str = f"{e:.1f}x" if e is not None else "N/A"
            print(f"    [{start}:{start+FP_LEN}]: family={fam_rate:.4f} "
                  f"random={rand_rate:.6f} enrichment={e_str} "
                  f"({fam_matches}/{fam_n} fam, {random_rates[start]['matches']}/{random_rates[start]['pairs']} rand)")

        enrichment_curves[str(p)] = curve
        detailed_data[str(p)] = details

    # 5. Curve characterization
    print("\n" + "=" * 70)
    print("  Curve characterization")
    print("=" * 70)

    characterization = {}
    for p in PRIMES:
        p_str = str(p)
        curve = enrichment_curves[p_str]
        valid = [(pos, e) for pos, e in zip(positions, curve) if e is not None]

        if not valid:
            characterization[p_str] = {"error": "no valid data points"}
            continue

        valid_pos = [v[0] for v in valid]
        valid_e = [v[1] for v in valid]

        # Basic stats
        peak_idx = np.argmax(valid_e)
        trough_idx = np.argmin(valid_e)

        char = {
            "peak_position": valid_pos[peak_idx],
            "peak_enrichment": valid_e[peak_idx],
            "trough_position": valid_pos[trough_idx],
            "trough_enrichment": valid_e[trough_idx],
            "mean_enrichment": float(np.mean(valid_e)),
            "std_enrichment": float(np.std(valid_e)),
            "cv": float(np.std(valid_e) / np.mean(valid_e)) if np.mean(valid_e) > 0 else None,
            "n_data_points": len(valid),
        }

        # Is the [20:40] dip reproducible?
        # Find enrichment at position 0, 20, 40
        e_at = {}
        for pos, e in valid:
            e_at[pos] = e

        if 0 in e_at and 20 in e_at and 40 in e_at:
            dip_exists = e_at[20] < e_at[0] and e_at[20] < e_at[40]
            char["dip_at_20_40"] = {
                "E_0": e_at[0],
                "E_20": e_at[20],
                "E_40": e_at[40],
                "dip_exists": dip_exists,
                "dip_depth": (e_at[0] - e_at[20]) / e_at[0] if dip_exists and e_at[0] > 0 else None,
            }

        # Monotonicity check
        diffs = [valid_e[i+1] - valid_e[i] for i in range(len(valid_e) - 1)]
        char["monotonically_increasing"] = all(d > 0 for d in diffs)
        char["monotonically_decreasing"] = all(d < 0 for d in diffs)
        char["trend"] = "increasing" if sum(1 for d in diffs if d > 0) > len(diffs) / 2 else "decreasing"

        # Does it plateau? (last 3 values within 20% of each other)
        if len(valid_e) >= 3:
            last3 = valid_e[-3:]
            plateau_range = (max(last3) - min(last3)) / np.mean(last3) if np.mean(last3) > 0 else float('inf')
            char["plateau_at_end"] = plateau_range < 0.2
            char["plateau_range_pct"] = float(plateau_range * 100)

        characterization[p_str] = char
        print(f"\n  p={p}:")
        print(f"    Peak: position {char['peak_position']}, enrichment {char['peak_enrichment']:.1f}x")
        print(f"    Trough: position {char['trough_position']}, enrichment {char['trough_enrichment']:.1f}x")
        print(f"    Mean: {char['mean_enrichment']:.1f}x, StdDev: {char['std_enrichment']:.1f}")
        if "dip_at_20_40" in char:
            dip = char["dip_at_20_40"]
            print(f"    Dip at [20:40]: {'YES' if dip['dip_exists'] else 'NO'} "
                  f"(E0={dip['E_0']:.1f}, E20={dip['E_20']:.1f}, E40={dip['E_40']:.1f})")

    # 6. Fit models
    print("\n" + "=" * 70)
    print("  Model fitting")
    print("=" * 70)

    model_fits = {}
    for p in PRIMES:
        p_str = str(p)
        curve = enrichment_curves[p_str]
        valid_e = [e if e is not None else np.nan for e in curve]
        model_fits[p_str] = fit_models(positions, valid_e)

        print(f"\n  p={p}:")
        for model_name in ["linear", "quadratic", "logarithmic", "periodic"]:
            if model_name in model_fits[p_str]:
                m = model_fits[p_str][model_name]
                if "r_squared" in m:
                    print(f"    {model_name}: R²={m['r_squared']:.4f}  {m.get('formula','')}")
                else:
                    print(f"    {model_name}: {m.get('error', 'failed')}")
        if "best_model" in model_fits[p_str]:
            print(f"    Best: {model_fits[p_str]['best_model']} "
                  f"(R²={model_fits[p_str]['best_r_squared']:.4f})")

    # 7. Characteristic length analysis
    print("\n" + "=" * 70)
    print("  Characteristic length analysis")
    print("=" * 70)

    char_length = analyze_characteristic_length(enrichment_curves, family_degrees, positions)
    print(f"\n  Family degree distribution: {char_length.get('family_degree_distribution', {})}")
    if "median_recurrence_order" in char_length:
        print(f"  Median recurrence order: {char_length['median_recurrence_order']}")
        print(f"  Mean recurrence order: {char_length['mean_recurrence_order']:.1f}")

    for p_str in [str(p) for p in PRIMES]:
        if p_str in char_length:
            info = char_length[p_str]
            print(f"\n  p={p_str}:")
            print(f"    Peak at position {info['peak_position']} (enrichment {info['peak_enrichment']:.1f}x)")
            print(f"    Min at position {info['min_position']} (enrichment {info['min_enrichment']:.1f}x)")
            print(f"    Peak/Min ratio: {info['ratio_peak_to_min']:.1f}")

    # 8. Stratified by degree (for p=2 only, for speed)
    print("\n" + "=" * 70)
    print("  Stratified enrichment by recurrence degree (p=2)")
    print("=" * 70)

    degree_curves = compute_enrichment_by_degree(families, family_degrees, oeis_data, positions, p=2)

    # Check if peak position correlates with degree
    if degree_curves:
        degree_peaks = {}
        for deg_str, data in degree_curves.items():
            curve = data["curve"]
            valid = [(pos, e) for pos, e in zip(positions, curve) if e is not None]
            if valid:
                peak_pos, peak_e = max(valid, key=lambda x: x[1])
                degree_peaks[int(deg_str)] = {"peak_position": peak_pos, "peak_enrichment": peak_e}

        if len(degree_peaks) >= 2:
            degs = sorted(degree_peaks.keys())
            peaks = [degree_peaks[d]["peak_position"] for d in degs]
            print(f"\n  Degree -> Peak position: {dict(zip(degs, peaks))}")

            # Correlation
            if len(degs) >= 3:
                corr = np.corrcoef(degs, peaks)[0, 1]
                char_length["degree_peak_correlation"] = float(corr)
                print(f"  Correlation(degree, peak_position) = {corr:.3f}")
        char_length["degree_stratified_peaks"] = {
            str(d): v for d, v in degree_peaks.items()
        }

    # 9. Assemble results
    elapsed = time.time() - t0

    results = {
        "challenge": "M2",
        "title": "Enrichment-Position Curve E(n)",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config": {
            "primes": PRIMES,
            "fp_len": FP_LEN,
            "window_step": WINDOW_STEP,
            "max_start": MAX_START,
            "n_random_pairs": N_RANDOM_PAIRS,
            "bm_sample_size": BM_SAMPLE_SIZE,
            "min_family_size": MIN_FAMILY_SIZE,
        },
        "data": {
            "n_sequences": len(oeis_data),
            "n_families": len(families),
            "n_family_sequences": sum(len(v) for v in families.values()),
            "positions": positions,
            "windows": [f"[{s}:{s+FP_LEN}]" for s in positions],
        },
        "enrichment_curves": enrichment_curves,
        "detailed_data": detailed_data,
        "characterization": characterization,
        "model_fits": model_fits,
        "characteristic_length": char_length,
        "degree_stratified_curves": degree_curves,
        "elapsed_seconds": elapsed,
    }

    # 10. Verdict
    print("\n" + "=" * 70)
    print("  VERDICT")
    print("=" * 70)

    verdict = {
        "dip_reproducible": None,
        "rising_after_40": None,
        "has_peak": None,
        "peak_position": None,
        "plateaus": None,
        "best_model": None,
        "characteristic_length_explanation": None,
    }

    # Check dip across primes
    dip_count = 0
    for p in PRIMES:
        p_str = str(p)
        if p_str in characterization and "dip_at_20_40" in characterization[p_str]:
            if characterization[p_str]["dip_at_20_40"]["dip_exists"]:
                dip_count += 1
    verdict["dip_reproducible"] = dip_count >= 2
    print(f"  Dip at [20:40] reproducible: {verdict['dip_reproducible']} ({dip_count}/{len(PRIMES)} primes)")

    # Check rising after 40
    rising_count = 0
    for p in PRIMES:
        p_str = str(p)
        curve = enrichment_curves.get(p_str, [])
        # Compare position 40 to later positions
        valid_after_40 = [(pos, e) for pos, e in zip(positions, curve)
                          if pos >= 40 and e is not None]
        if len(valid_after_40) >= 2:
            vals = [e for _, e in valid_after_40]
            if vals[-1] > vals[0]:
                rising_count += 1
    verdict["rising_after_40"] = rising_count >= 2
    print(f"  Rising after position 40: {verdict['rising_after_40']} ({rising_count}/{len(PRIMES)} primes)")

    # Peak detection
    peak_positions = []
    for p in PRIMES:
        p_str = str(p)
        if p_str in characterization:
            peak_positions.append(characterization[p_str].get("peak_position"))
    peak_positions = [pp for pp in peak_positions if pp is not None]
    if peak_positions:
        median_peak = float(np.median(peak_positions))
        verdict["has_peak"] = True
        verdict["peak_position"] = median_peak
        print(f"  Has peak: YES at median position {median_peak} (per-prime: {peak_positions})")

    # Plateau
    plateau_count = sum(1 for p in PRIMES
                        if characterization.get(str(p), {}).get("plateau_at_end", False))
    verdict["plateaus"] = plateau_count >= 2
    print(f"  Plateaus at end: {verdict['plateaus']} ({plateau_count}/{len(PRIMES)} primes)")

    # Best model consensus
    best_models = [model_fits.get(str(p), {}).get("best_model") for p in PRIMES]
    best_models = [m for m in best_models if m is not None]
    if best_models:
        consensus = Counter(best_models).most_common(1)[0]
        verdict["best_model"] = consensus[0]
        print(f"  Best model consensus: {consensus[0]} ({consensus[1]}/{len(best_models)} primes)")

    # Characteristic length
    if "degree_peak_correlation" in char_length:
        corr = char_length["degree_peak_correlation"]
        if abs(corr) > 0.5:
            verdict["characteristic_length_explanation"] = (
                f"Peak position correlates with recurrence order (r={corr:.2f})")
        else:
            verdict["characteristic_length_explanation"] = (
                f"Peak position does NOT correlate with recurrence order (r={corr:.2f})")
        print(f"  Characteristic length: {verdict['characteristic_length_explanation']}")

    # Diagnostic: decompose enrichment change into family vs random contributions
    diagnostic = {}
    for p in PRIMES:
        p_str = str(p)
        details = detailed_data.get(p_str, [])
        if len(details) < 2:
            continue
        fam_rates = [d["family_rate"] for d in details]
        rand_rates = [d["random_rate"] for d in details]
        # Family rate trend
        fam_slope = np.polyfit(positions, fam_rates, 1)[0] if len(fam_rates) == len(positions) else None
        rand_slope = np.polyfit(positions, rand_rates, 1)[0] if len(rand_rates) == len(positions) else None
        # Coefficient of variation
        fam_cv = float(np.std(fam_rates) / np.mean(fam_rates)) if np.mean(fam_rates) > 0 else None
        rand_cv = float(np.std(rand_rates) / np.mean(rand_rates)) if np.mean(rand_rates) > 0 else None
        diagnostic[p_str] = {
            "family_rate_range": [float(min(fam_rates)), float(max(fam_rates))],
            "random_rate_range": [float(min(rand_rates)), float(max(rand_rates))],
            "family_rate_slope": float(fam_slope) if fam_slope is not None else None,
            "random_rate_slope": float(rand_slope) if rand_slope is not None else None,
            "family_rate_cv": fam_cv,
            "random_rate_cv": rand_cv,
            "enrichment_driven_by": "random_baseline_rising" if (
                rand_cv is not None and fam_cv is not None and rand_cv > 2 * fam_cv
            ) else "family_rate_change" if (
                fam_cv is not None and rand_cv is not None and fam_cv > 2 * rand_cv
            ) else "both",
        }
        print(f"\n  Diagnostic p={p}:")
        print(f"    Family rate: {min(fam_rates):.4f} -> {max(fam_rates):.4f} (CV={fam_cv:.2f})")
        print(f"    Random rate: {min(rand_rates):.6f} -> {max(rand_rates):.6f} (CV={rand_cv:.2f})")
        print(f"    Enrichment decline driven by: {diagnostic[p_str]['enrichment_driven_by']}")

    verdict["diagnostic"] = diagnostic
    results["verdict"] = verdict

    # Save
    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUT_FILE}")
    print(f"Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
