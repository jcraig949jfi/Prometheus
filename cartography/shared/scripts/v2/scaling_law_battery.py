"""
Scaling Law Battery — Attempt to Kill the C11 Algebraic DNA Signal
===================================================================
The C11 result: mod-p fingerprint enrichment in algebraic families scales
monotonically with prime (4.1x at mod 2 → 53.6x at mod 11).

This script runs 8 kill tests on that finding:

K1. PRIME DETRENDING: Is the signal just shared prime factors in sequence terms?
    Strip prime structure, recompute.
K2. FAMILY SIZE CONFOUND: Do larger families inflate enrichment mechanically?
    Stratify by family size, check if scaling persists per stratum.
K3. SYNTHETIC NULL FAMILIES: Create fake families (random polys, matched degree
    and coefficient range). Do they show the same scaling?
K4. TRIVIAL SEQUENCE FILTER: Remove constant, linear, and polynomial sequences.
    Does the signal survive with only "interesting" sequences?
K5. TERM POSITION SENSITIVITY: Shift the fingerprint window (terms 1-20 vs
    21-40 vs 41-60). If the signal depends on early terms only, it may be
    an initial-condition artifact.
K6. CROSS-VALIDATION: Split families 50/50. Does each half show the same scaling?
K7. BOOTSTRAPPED CONFIDENCE INTERVALS: How tight are the enrichment ratios?
K8. SCALING EXPONENT FIT: Fit enrichment(p) = A * p^alpha. Is alpha consistent
    across family types?

Usage:
    python scaling_law_battery.py
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

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
C11_RESULTS = V2_DIR / "algebraic_dna_fungrim_results.json"
C08_RESULTS = V2_DIR / "recurrence_euler_factor_results.json"
OEIS_STRIPPED_GZ = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_TXT = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUT_FILE = V2_DIR / "scaling_law_battery_results.json"

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]
FP_LEN = 20  # fingerprint window length

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# Berlekamp-Massey
# ---------------------------------------------------------------------------
def berlekamp_massey(seq):
    """Minimal LFSR. Returns list of coefficients or None."""
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
def load_oeis():
    """Load OEIS sequences into {id: terms_list}."""
    cache = {}
    src = OEIS_STRIPPED_TXT if OEIS_STRIPPED_TXT.exists() else OEIS_STRIPPED_GZ
    if not src.exists():
        print(f"  WARNING: {src} not found")
        return cache
    opener = gzip.open if str(src).endswith('.gz') else open
    mode = "rt" if str(src).endswith('.gz') else "r"
    print(f"  Loading OEIS from {src.name}...")
    with opener(src, mode, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 3:
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
            if terms:
                cache[sid] = terms
    print(f"  Loaded {len(cache):,} sequences")
    return cache


# ---------------------------------------------------------------------------
# Build families from C08 polynomial clusters
# ---------------------------------------------------------------------------
def load_families(oeis_data):
    """Load polynomial clusters and return {poly_str: [seq_ids]}."""
    if not C08_RESULTS.exists():
        print("  WARNING: C08 results not found, building families from scratch")
        return {}

    with open(C08_RESULTS, "r") as f:
        c08 = json.load(f)

    # C08 results have {total_clusters: N, top_clusters: [{char_poly_coeffs, degree, n_sequences, sequences: [ids]}, ...]}
    top_clusters = c08.get("top_clusters", [])
    if not top_clusters:
        # Try alternate structure
        clusters = c08.get("polynomial_clusters", {})
        if isinstance(clusters, dict):
            top_clusters = clusters.get("top_clusters", [])

    families = {}
    for cluster in top_clusters:
        if not isinstance(cluster, dict):
            continue
        coeffs = cluster.get("char_poly_coeffs", [])
        seq_ids = cluster.get("sequences", [])
        poly_str = str(coeffs)
        # Keep only sequences we have terms for
        seq_ids = [s for s in seq_ids if isinstance(s, str) and s in oeis_data and len(oeis_data[s]) >= FP_LEN]
        if len(seq_ids) >= 2:
            families[poly_str] = seq_ids

    print(f"  Loaded {len(families)} families with 2+ sequences (FP_LEN={FP_LEN})")
    return families


# ---------------------------------------------------------------------------
# Fingerprint computation
# ---------------------------------------------------------------------------
def fingerprint(terms, p, start=0):
    """Compute mod-p fingerprint of terms[start:start+FP_LEN]."""
    window = terms[start:start + FP_LEN]
    if len(window) < FP_LEN:
        return None
    return tuple(t % p for t in window)


def compute_exact_match_rate(families, oeis_data, p, start=0, term_filter=None):
    """Compute fraction of within-family pairs sharing exact mod-p fingerprint."""
    matches = 0
    total = 0
    for poly, seq_ids in families.items():
        if term_filter:
            seq_ids = [s for s in seq_ids if term_filter(oeis_data[s])]
        fps = {}
        for sid in seq_ids:
            fp = fingerprint(oeis_data[sid], p, start)
            if fp is not None:
                fps[sid] = fp
        sids = list(fps.keys())
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                total += 1
                if fps[sids[i]] == fps[sids[j]]:
                    matches += 1
    return matches / total if total > 0 else 0, total


def compute_random_match_rate(oeis_data, p, n_pairs=10000, start=0, term_filter=None):
    """Compute exact match rate for random pairs."""
    all_ids = list(oeis_data.keys())
    if term_filter:
        all_ids = [s for s in all_ids if len(oeis_data[s]) >= FP_LEN + start and term_filter(oeis_data[s])]
    else:
        all_ids = [s for s in all_ids if len(oeis_data[s]) >= FP_LEN + start]
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
    return matches / tested if tested > 0 else 0, tested


def enrichment_ratio(family_rate, random_rate):
    """Compute enrichment, avoiding division by zero."""
    if random_rate == 0:
        return float('inf') if family_rate > 0 else 1.0
    return family_rate / random_rate


# ---------------------------------------------------------------------------
# Kill tests
# ---------------------------------------------------------------------------
def run_battery(families, oeis_data):
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_families": len(families),
        "n_sequences": sum(len(v) for v in families.values()),
        "primes_tested": PRIMES,
        "tests": {},
    }

    # === K0: BASELINE (reproduce C11 result) ===
    print("\n=== K0: BASELINE ===")
    k0 = {}
    for p in PRIMES:
        fam_rate, fam_n = compute_exact_match_rate(families, oeis_data, p)
        rand_rate, rand_n = compute_random_match_rate(oeis_data, p)
        ratio = enrichment_ratio(fam_rate, rand_rate)
        k0[str(p)] = {"family_rate": fam_rate, "random_rate": rand_rate,
                       "enrichment": ratio, "family_pairs": fam_n, "random_pairs": rand_n}
        print(f"  mod {p:2d}: family={fam_rate:.4f} random={rand_rate:.4f} enrichment={ratio:.1f}x")
    results["tests"]["K0_baseline"] = k0

    # === K1: PRIME DETRENDING ===
    print("\n=== K1: PRIME DETRENDING ===")
    # Remove all factors of small primes from terms, then recompute
    def detrend_primes(terms):
        """Remove factors of 2,3,5,7,11 from each term."""
        out = []
        for t in terms:
            if t == 0:
                out.append(0)
                continue
            v = abs(t)
            for p in [2, 3, 5, 7, 11]:
                while v % p == 0 and v > 0:
                    v //= p
            out.append(v * (1 if t > 0 else -1))
        return out

    detrended = {sid: detrend_primes(terms) for sid, terms in oeis_data.items()}
    k1 = {}
    for p in PRIMES:
        fam_rate, fam_n = compute_exact_match_rate(families, detrended, p)
        rand_rate, rand_n = compute_random_match_rate(detrended, p)
        ratio = enrichment_ratio(fam_rate, rand_rate)
        k1[str(p)] = {"family_rate": fam_rate, "random_rate": rand_rate,
                       "enrichment": ratio, "family_pairs": fam_n}
        print(f"  mod {p:2d}: family={fam_rate:.4f} random={rand_rate:.4f} enrichment={ratio:.1f}x")
    results["tests"]["K1_prime_detrended"] = k1
    del detrended

    # === K2: FAMILY SIZE STRATIFICATION ===
    print("\n=== K2: FAMILY SIZE STRATIFICATION ===")
    small_fam = {k: v for k, v in families.items() if len(v) <= 5}
    med_fam = {k: v for k, v in families.items() if 6 <= len(v) <= 20}
    large_fam = {k: v for k, v in families.items() if len(v) > 20}
    k2 = {}
    for label, subset in [("small_2-5", small_fam), ("medium_6-20", med_fam), ("large_21+", large_fam)]:
        if not subset:
            k2[label] = {"note": "empty stratum"}
            continue
        k2[label] = {}
        print(f"  Stratum {label}: {len(subset)} families")
        for p in [2, 5, 11]:  # test at 3 primes for speed
            fam_rate, fam_n = compute_exact_match_rate(subset, oeis_data, p)
            rand_rate, _ = compute_random_match_rate(oeis_data, p, n_pairs=5000)
            ratio = enrichment_ratio(fam_rate, rand_rate)
            k2[label][str(p)] = {"family_rate": fam_rate, "enrichment": ratio, "pairs": fam_n}
            print(f"    mod {p:2d}: enrichment={ratio:.1f}x ({fam_n} pairs)")
    results["tests"]["K2_size_stratified"] = k2

    # === K3: SYNTHETIC NULL FAMILIES ===
    print("\n=== K3: SYNTHETIC NULL FAMILIES ===")
    # Create fake families: random groups of sequences (same size distribution as real families)
    all_ids = [s for s in oeis_data if len(oeis_data[s]) >= FP_LEN]
    size_dist = [len(v) for v in families.values()]
    fake_families = {}
    for i, sz in enumerate(size_dist[:200]):  # cap at 200 for speed
        sample = random.sample(all_ids, min(sz, len(all_ids)))
        fake_families[f"fake_{i}"] = sample
    k3 = {}
    for p in PRIMES:
        fake_rate, fake_n = compute_exact_match_rate(fake_families, oeis_data, p)
        real_rate = results["tests"]["K0_baseline"][str(p)]["family_rate"]
        rand_rate = results["tests"]["K0_baseline"][str(p)]["random_rate"]
        k3[str(p)] = {"fake_family_rate": fake_rate, "real_family_rate": real_rate,
                       "random_rate": rand_rate, "fake_enrichment": enrichment_ratio(fake_rate, rand_rate),
                       "real_enrichment": enrichment_ratio(real_rate, rand_rate)}
        print(f"  mod {p:2d}: fake={fake_rate:.4f} real={real_rate:.4f} random={rand_rate:.4f}")
    results["tests"]["K3_synthetic_null"] = k3

    # === K4: TRIVIAL SEQUENCE FILTER ===
    print("\n=== K4: TRIVIAL SEQUENCE FILTER ===")
    def is_nontrivial(terms):
        """Filter: not constant, not linear, not all zeros."""
        if len(set(terms[:FP_LEN])) <= 2:
            return False
        # Check if linear: constant differences
        diffs = [terms[i+1] - terms[i] for i in range(min(FP_LEN-1, len(terms)-1))]
        if len(set(diffs)) <= 1:
            return False
        return True

    k4 = {}
    for p in PRIMES:
        fam_rate, fam_n = compute_exact_match_rate(families, oeis_data, p, term_filter=is_nontrivial)
        rand_rate, rand_n = compute_random_match_rate(oeis_data, p, term_filter=is_nontrivial)
        ratio = enrichment_ratio(fam_rate, rand_rate)
        k4[str(p)] = {"family_rate": fam_rate, "random_rate": rand_rate,
                       "enrichment": ratio, "family_pairs": fam_n}
        print(f"  mod {p:2d}: family={fam_rate:.4f} random={rand_rate:.4f} enrichment={ratio:.1f}x")
    results["tests"]["K4_nontrivial_only"] = k4

    # === K5: TERM POSITION SENSITIVITY ===
    print("\n=== K5: TERM POSITION SENSITIVITY ===")
    k5 = {}
    for start in [0, 20, 40]:
        k5[f"start_{start}"] = {}
        n_avail = sum(1 for sid in oeis_data if len(oeis_data[sid]) >= start + FP_LEN)
        print(f"  Window [{start}:{start+FP_LEN}] — {n_avail} sequences available")
        if n_avail < 1000:
            k5[f"start_{start}"]["note"] = f"insufficient data ({n_avail} seqs)"
            continue
        for p in [2, 5, 11]:
            fam_rate, fam_n = compute_exact_match_rate(families, oeis_data, p, start=start)
            rand_rate, _ = compute_random_match_rate(oeis_data, p, n_pairs=5000, start=start)
            ratio = enrichment_ratio(fam_rate, rand_rate)
            k5[f"start_{start}"][str(p)] = {"family_rate": fam_rate, "enrichment": ratio}
            print(f"    mod {p:2d}: enrichment={ratio:.1f}x ({fam_n} pairs)")
    results["tests"]["K5_position_sensitivity"] = k5

    # === K6: CROSS-VALIDATION (50/50 split) ===
    print("\n=== K6: CROSS-VALIDATION ===")
    fam_keys = list(families.keys())
    random.shuffle(fam_keys)
    half = len(fam_keys) // 2
    split_a = {k: families[k] for k in fam_keys[:half]}
    split_b = {k: families[k] for k in fam_keys[half:]}
    k6 = {"split_a": {}, "split_b": {}}
    for label, subset in [("split_a", split_a), ("split_b", split_b)]:
        for p in PRIMES:
            fam_rate, fam_n = compute_exact_match_rate(subset, oeis_data, p)
            rand_rate, _ = compute_random_match_rate(oeis_data, p, n_pairs=5000)
            ratio = enrichment_ratio(fam_rate, rand_rate)
            k6[label][str(p)] = {"family_rate": fam_rate, "enrichment": ratio, "pairs": fam_n}
        ratios = [k6[label][str(p)]["enrichment"] for p in PRIMES]
        print(f"  {label}: enrichment at primes = {[f'{r:.1f}x' for r in ratios]}")
    # Check monotonicity in both halves
    for label in ["split_a", "split_b"]:
        ratios = [k6[label][str(p)]["enrichment"] for p in PRIMES]
        is_monotone = all(ratios[i] <= ratios[i+1] for i in range(len(ratios)-1))
        k6[label]["monotonically_increasing"] = is_monotone
        print(f"  {label} monotonically increasing: {is_monotone}")
    results["tests"]["K6_cross_validation"] = k6

    # === K7: BOOTSTRAP CONFIDENCE INTERVALS ===
    print("\n=== K7: BOOTSTRAP CONFIDENCE INTERVALS ===")
    k7 = {}
    n_boot = 200
    for p in [2, 5, 11]:  # 3 primes for speed
        boot_ratios = []
        fam_keys_list = list(families.keys())
        for b in range(n_boot):
            # Resample families with replacement
            boot_keys = [random.choice(fam_keys_list) for _ in range(len(fam_keys_list))]
            boot_fam = {f"b{i}_{k}": families[k] for i, k in enumerate(boot_keys)}
            fam_rate, _ = compute_exact_match_rate(boot_fam, oeis_data, p)
            rand_rate = results["tests"]["K0_baseline"][str(p)]["random_rate"]
            boot_ratios.append(enrichment_ratio(fam_rate, rand_rate))
        boot_ratios.sort()
        ci_lo = boot_ratios[int(0.025 * n_boot)]
        ci_hi = boot_ratios[int(0.975 * n_boot)]
        median = boot_ratios[n_boot // 2]
        k7[str(p)] = {"median": median, "ci_95_lo": ci_lo, "ci_95_hi": ci_hi,
                       "std": float(np.std(boot_ratios))}
        print(f"  mod {p:2d}: median={median:.1f}x  95% CI=[{ci_lo:.1f}x, {ci_hi:.1f}x]")
    results["tests"]["K7_bootstrap_ci"] = k7

    # === K8: SCALING EXPONENT FIT ===
    print("\n=== K8: SCALING EXPONENT FIT ===")
    baseline_enrichments = [results["tests"]["K0_baseline"][str(p)]["enrichment"]
                           for p in PRIMES if results["tests"]["K0_baseline"][str(p)]["enrichment"] < float('inf')]
    primes_used = [p for p in PRIMES if results["tests"]["K0_baseline"][str(p)]["enrichment"] < float('inf')]

    if len(primes_used) >= 3:
        log_p = np.log(primes_used)
        log_e = np.log(baseline_enrichments)
        # Fit log(enrichment) = alpha * log(p) + beta  =>  enrichment = exp(beta) * p^alpha
        coeffs = np.polyfit(log_p, log_e, 1)
        alpha = coeffs[0]
        A = np.exp(coeffs[1])
        # Residuals
        predicted = A * np.array(primes_used) ** alpha
        residuals = np.array(baseline_enrichments) - predicted
        rmse = float(np.sqrt(np.mean(residuals ** 2)))
        r_squared = 1.0 - np.sum(residuals**2) / np.sum((np.array(baseline_enrichments) - np.mean(baseline_enrichments))**2)

        k8 = {
            "model": "enrichment(p) = A * p^alpha",
            "alpha": float(alpha),
            "A": float(A),
            "r_squared": r_squared,
            "rmse": rmse,
            "primes": primes_used,
            "observed": baseline_enrichments,
            "predicted": [float(x) for x in predicted],
        }
        print(f"  Model: enrichment(p) = {A:.2f} * p^{alpha:.3f}")
        print(f"  R² = {r_squared:.4f}, RMSE = {rmse:.2f}")
        print(f"  Observed:  {[f'{x:.1f}' for x in baseline_enrichments]}")
        print(f"  Predicted: {[f'{x:.1f}' for x in predicted]}")
    else:
        k8 = {"note": "insufficient data points for fit"}
    results["tests"]["K8_scaling_exponent"] = k8

    # === VERDICT ===
    print("\n" + "=" * 60)
    print("  SCALING LAW BATTERY VERDICT")
    print("=" * 60)

    kills = []
    survives = []

    # K1: does detrending kill it?
    k1_ratios = [k1[str(p)]["enrichment"] for p in PRIMES if k1[str(p)]["enrichment"] < float('inf')]
    k0_ratios = [k0[str(p)]["enrichment"] for p in PRIMES if k0[str(p)]["enrichment"] < float('inf')]
    if k1_ratios and max(k1_ratios) < 1.5:
        kills.append("K1: signal destroyed by prime detrending")
    else:
        survives.append(f"K1: survives detrending (max enrichment {max(k1_ratios):.1f}x)")

    # K3: do synthetic families match?
    k3_fake_max = max(k3[str(p)]["fake_enrichment"] for p in PRIMES)
    k3_real_min = min(k3[str(p)]["real_enrichment"] for p in PRIMES)
    if k3_fake_max > k3_real_min * 0.5:
        kills.append(f"K3: synthetic null enrichment ({k3_fake_max:.1f}x) approaches real ({k3_real_min:.1f}x)")
    else:
        survives.append(f"K3: synthetic null ({k3_fake_max:.1f}x) << real ({k3_real_min:.1f}x)")

    # K4: does trivial filtering kill it?
    k4_ratios = [k4[str(p)]["enrichment"] for p in PRIMES if k4[str(p)]["enrichment"] < float('inf')]
    if k4_ratios and max(k4_ratios) < 2.0:
        kills.append("K4: signal vanishes after removing trivial sequences")
    else:
        survives.append(f"K4: survives trivial filter (max enrichment {max(k4_ratios):.1f}x)")

    # K6: cross-validation monotonicity
    cv_a_mono = k6["split_a"].get("monotonically_increasing", False)
    cv_b_mono = k6["split_b"].get("monotonically_increasing", False)
    if cv_a_mono and cv_b_mono:
        survives.append("K6: monotonic scaling replicates in both cross-validation halves")
    elif cv_a_mono or cv_b_mono:
        survives.append("K6: monotonic in one half, not both — moderate support")
    else:
        kills.append("K6: monotonicity fails in both cross-validation halves")

    # K8: scaling quality
    if "r_squared" in k8 and k8["r_squared"] > 0.95:
        survives.append(f"K8: power law fit R²={k8['r_squared']:.4f}, alpha={k8['alpha']:.3f}")
    elif "r_squared" in k8:
        survives.append(f"K8: power law fit R²={k8['r_squared']:.4f} (moderate)")

    results["verdict"] = {
        "kills": kills,
        "survives": survives,
        "signal_alive": len(kills) == 0,
        "summary": "SIGNAL SURVIVES ALL TESTS" if len(kills) == 0 else f"SIGNAL WEAKENED: {len(kills)} kills"
    }

    for item in kills:
        print(f"  KILLED: {item}")
    for item in survives:
        print(f"  SURVIVES: {item}")
    print(f"\n  VERDICT: {results['verdict']['summary']}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    t0 = time.time()
    print("Scaling Law Battery — C11 Kill Tests")
    print("=" * 60)

    oeis_data = load_oeis()
    families = load_families(oeis_data)

    if not families:
        print("No families loaded. Attempting direct BM extraction...")
        # Build families from scratch on a sample
        sample_ids = random.sample(list(oeis_data.keys()), min(30000, len(oeis_data)))
        poly_clusters = defaultdict(list)
        for sid in sample_ids:
            terms = oeis_data[sid]
            if len(terms) < 30:
                continue
            result = berlekamp_massey([float(t) for t in terms[:60]])
            if result is not None:
                coeffs, degree = result
                if 2 <= degree <= 6:
                    # Round coefficients for clustering
                    key = tuple(round(c, 6) for c in coeffs)
                    poly_clusters[str(key)].append(sid)
        families = {k: v for k, v in poly_clusters.items() if len(v) >= 2}
        print(f"  Built {len(families)} families from BM on {len(sample_ids)} sequences")

    results = run_battery(families, oeis_data)

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUT_FILE}")
    print(f"Total time: {time.time() - t0:.1f}s")
