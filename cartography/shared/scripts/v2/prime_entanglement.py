#!/usr/bin/env python3
"""
Prime Entanglement Score — Measuring Subtle Cross-Prime Correlations
=====================================================================
Measures the mutual information between mod-ell fingerprint vectors
across primes ell in {3, 5, 7, 11}.

KEY INSIGHT: At each prime position p, (a_p mod 3) and (a_p mod 5) are
deterministic functions of the same integer a_p — so pointwise MI is
trivially positive (arithmetic, not entanglement). The real question is
whether the FULL fingerprint vectors across forms carry cross-ell
structure beyond what individual-position arithmetic forces.

Approach:
- "Cluster membership" MI: whether being in a non-trivial cluster at
  ell_1 predicts cluster membership at ell_2 (binary MI, cleanest test)
- "Profile" MI: whether the vector of cluster sizes across ells carries
  mutual information (low-dimensional representation)
- Pointwise MI with CRT correction: subtract arithmetic MI baseline

Charon / Project Prometheus — 2026-04-09
"""

import json
import math
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import duckdb
import numpy as np

# ── Config ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]  # F:\Prometheus
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
GALOIS_PATH = Path(__file__).resolve().parent / "galois_image_results.json"
OUT_PATH = Path(__file__).resolve().parent / "prime_entanglement_results.json"

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

ELLS = [3, 5, 7, 11]
ELL_PAIRS = list(combinations(ELLS, 2))
N_PERM = 1000

# ── Helpers ──────────────────────────────────────────────────────────

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def compute_fingerprint(traces, level, ell):
    """Compute mod-ell fingerprint vector at 25 primes. Bad primes -> -1."""
    bad_primes = prime_factors(level)
    fp = []
    for p in PRIMES_25:
        if p in bad_primes:
            fp.append(-1)
        else:
            if p - 1 < len(traces):
                ap = int(round(traces[p - 1]))
                fp.append(ap % ell)
            else:
                fp.append(-1)
    return tuple(fp)


def discrete_mi(x_arr, y_arr):
    """Compute MI I(X;Y) for discrete arrays. Returns MI in nats."""
    n = len(x_arr)
    if n == 0:
        return 0.0
    joint = Counter(zip(x_arr, y_arr))
    cx = Counter(x_arr)
    cy = Counter(y_arr)
    mi = 0.0
    for (x, y), nxy in joint.items():
        pxy = nxy / n
        px = cx[x] / n
        py = cy[y] / n
        if pxy > 0 and px > 0 and py > 0:
            mi += pxy * math.log(pxy / (px * py))
    return mi


def hamming_distance(fp1, fp2):
    """Hamming distance ignoring bad primes (-1)."""
    dist = 0
    compared = 0
    for a, b in zip(fp1, fp2):
        if a == -1 or b == -1:
            continue
        compared += 1
        if a != b:
            dist += 1
    return dist, compared


# ── Data loading ─────────────────────────────────────────────────────

def load_forms():
    print(f"[load] Connecting to {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute('''
        SELECT lmfdb_label, level, traces, is_cm
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    con.close()
    print(f"[load] {len(rows)} forms loaded")
    forms = []
    for label, level, traces, is_cm in rows:
        forms.append({
            'label': label,
            'level': int(level),
            'traces': traces,
            'is_cm': bool(is_cm) if is_cm is not None else False,
        })
    return forms


def classify_galois_image(form, fingerprints):
    """Simplified Galois image classification from zero-frequency."""
    if form['is_cm']:
        return 'CM'
    for ell in ELLS:
        fp = fingerprints[ell]
        good = [v for v in fp if v >= 0]
        if len(good) == 0:
            continue
        zero_frac = sum(1 for v in good if v == 0) / len(good)
        if zero_frac > 1.5 / ell:
            return f'borel_mod{ell}'
    return 'full_image'


# ── Analysis 1: Cluster membership MI ────────────────────────────────

def compute_cluster_sizes(all_fps, ell):
    """For each form, compute its cluster size at ell (number of forms
    sharing its exact fingerprint)."""
    fp_counter = Counter(all_fps[ell])
    return [fp_counter[fp] for fp in all_fps[ell]]


def cluster_membership_mi(cluster_sizes_1, cluster_sizes_2, threshold=1, n_perm=N_PERM):
    """
    MI between binary variables: is form in a non-trivial cluster at ell_1
    vs at ell_2. This directly measures the R5-3 interference finding.
    """
    x = [1 if s > threshold else 0 for s in cluster_sizes_1]
    y = [1 if s > threshold else 0 for s in cluster_sizes_2]

    observed = discrete_mi(x, y)

    rng = np.random.default_rng(42)
    y_arr = np.array(y)
    null_mis = []
    for _ in range(n_perm):
        y_shuf = rng.permutation(y_arr).tolist()
        null_mis.append(discrete_mi(x, y_shuf))

    null_mis = np.array(null_mis)
    null_mean = float(np.mean(null_mis))
    null_std = float(np.std(null_mis))
    z = (observed - null_mean) / null_std if null_std > 0 else 0.0

    # Also compute contingency table
    n = len(x)
    n11 = sum(1 for a, b in zip(x, y) if a == 1 and b == 1)
    n10 = sum(1 for a, b in zip(x, y) if a == 1 and b == 0)
    n01 = sum(1 for a, b in zip(x, y) if a == 0 and b == 1)
    n00 = sum(1 for a, b in zip(x, y) if a == 0 and b == 0)
    p1 = sum(x) / n
    p2 = sum(y) / n
    expected_11 = p1 * p2 * n
    ratio = n11 / expected_11 if expected_11 > 0 else 0.0

    return {
        'observed_MI': round(observed, 10),
        'null_MI_mean': round(null_mean, 10),
        'null_MI_std': round(null_std, 10),
        'entanglement_score': round(z, 4),
        'excess_MI_bits': round((observed - null_mean) / math.log(2), 10) if observed > null_mean else 0.0,
        'contingency': {'n11': n11, 'n10': n10, 'n01': n01, 'n00': n00},
        'expected_n11': round(expected_11, 2),
        'overlap_ratio': round(ratio, 6),
    }


# ── Analysis 2: Cluster-size profile MI ──────────────────────────────

def cluster_profile_mi(cluster_sizes_1, cluster_sizes_2, n_perm=N_PERM):
    """
    MI between cluster-size categories at two ells.
    Bin sizes into: 1 (singleton), 2 (pair), 3-5 (small), 6+ (large).
    """
    def binned(s):
        if s == 1: return 0
        elif s == 2: return 1
        elif s <= 5: return 2
        else: return 3

    x = [binned(s) for s in cluster_sizes_1]
    y = [binned(s) for s in cluster_sizes_2]

    observed = discrete_mi(x, y)

    rng = np.random.default_rng(99)
    y_arr = np.array(y)
    null_mis = []
    for _ in range(n_perm):
        y_shuf = rng.permutation(y_arr).tolist()
        null_mis.append(discrete_mi(x, y_shuf))

    null_mis = np.array(null_mis)
    null_mean = float(np.mean(null_mis))
    null_std = float(np.std(null_mis))
    z = (observed - null_mean) / null_std if null_std > 0 else 0.0

    return {
        'observed_MI': round(observed, 10),
        'null_MI_mean': round(null_mean, 10),
        'null_MI_std': round(null_std, 10),
        'entanglement_score': round(z, 4),
        'excess_MI_bits': round((observed - null_mean) / math.log(2), 10) if observed > null_mean else 0.0,
    }


# ── Analysis 3: Pointwise MI (arithmetic CRT dependence) ────────────

def compute_pointwise_mi(all_fps, ell1, ell2):
    """
    For each prime position p, compute MI(a_p mod ell1; a_p mod ell2).

    NOTE: This MI is ENTIRELY arithmetic (CRT). Since (a_p mod 3) and
    (a_p mod 5) are deterministic functions of the same a_p, any MI here
    reflects the distribution of a_p values, not cross-ell entanglement.

    We measure it anyway to:
    1. Verify it's uniform across positions (no bad-prime spikes)
    2. Quantify how much arithmetic MI exists at each position
    3. Identify if any positions have LESS MI than expected (masking)

    The null is form-shuffled: for each position p, shuffle which form
    gets which (a_p mod ell1) value while keeping (a_p mod ell2) fixed.
    This breaks within-form CRT pairing.
    """
    n_forms = len(all_fps[ell1])
    rng = np.random.default_rng(777)
    results = {}

    for pidx, p in enumerate(PRIMES_25):
        x_vals = []
        y_vals = []
        for i in range(n_forms):
            v1 = all_fps[ell1][i][pidx]
            v2 = all_fps[ell2][i][pidx]
            if v1 >= 0 and v2 >= 0:
                x_vals.append(v1)
                y_vals.append(v2)

        n_good = len(x_vals)
        if n_good < 50:
            results[str(p)] = {'mi': 0.0, 'n_good': n_good, 'note': 'insufficient'}
            continue

        observed = discrete_mi(x_vals, y_vals)

        # Null: shuffle x to break CRT pairing with y
        null_mis = []
        x_arr = np.array(x_vals)
        y_arr = np.array(y_vals)
        for _ in range(200):
            x_shuf = rng.permutation(x_arr).tolist()
            null_mis.append(discrete_mi(x_shuf, y_vals))

        null_mean = float(np.mean(null_mis))
        null_std = float(np.std(null_mis))
        z = (observed - null_mean) / null_std if null_std > 0 else 0.0

        results[str(p)] = {
            'mi_nats': round(observed, 8),
            'mi_bits': round(observed / math.log(2), 8),
            'null_mean': round(null_mean, 8),
            'null_std': round(null_std, 8),
            'excess_mi': round(observed - null_mean, 8),
            'z_score': round(z, 4),
            'n_good': n_good,
            'note': 'CRT_arithmetic_dependence',
        }

    return results


# ── Analysis 4: Conditional MI given Galois image ────────────────────

def conditional_cluster_mi(cluster_sizes_1, cluster_sizes_2, galois_classes, threshold=1, n_perm=500):
    """
    Compute bias-corrected I(cluster_ell1; cluster_ell2 | Galois_class).

    Raw MI has upward bias in small groups. We correct by subtracting
    the permutation-null MI within each class (the bias floor).
    If corrected conditional MI drops to zero, Galois image explains it.
    """
    x = [1 if s > threshold else 0 for s in cluster_sizes_1]
    y = [1 if s > threshold else 0 for s in cluster_sizes_2]

    # Group by Galois class
    class_groups = defaultdict(list)
    for i, c in enumerate(galois_classes):
        class_groups[c].append(i)

    n_total = len(galois_classes)
    rng = np.random.default_rng(456)

    cond_mi_raw = 0.0
    cond_mi_corrected = 0.0
    class_details = {}

    for cls, indices in class_groups.items():
        if len(indices) < 20:
            continue
        weight = len(indices) / n_total
        x_cls = [x[i] for i in indices]
        y_cls = [y[i] for i in indices]

        mi_cls = discrete_mi(x_cls, y_cls)
        cond_mi_raw += weight * mi_cls

        # Permutation null within this class (measures bias)
        y_arr = np.array(y_cls)
        null_mis = []
        for _ in range(min(500, n_perm)):
            y_shuf = rng.permutation(y_arr).tolist()
            null_mis.append(discrete_mi(x_cls, y_shuf))
        null_mean = float(np.mean(null_mis))
        null_std = float(np.std(null_mis))
        z = (mi_cls - null_mean) / null_std if null_std > 0 else 0.0

        # Bias-corrected MI for this class
        mi_corrected = max(0.0, mi_cls - null_mean)
        cond_mi_corrected += weight * mi_corrected

        class_details[cls] = {
            'n_forms': len(indices),
            'weight': round(weight, 6),
            'mi_raw': round(mi_cls, 8),
            'mi_corrected': round(mi_corrected, 8),
            'null_mean': round(null_mean, 8),
            'z_score': round(z, 4),
            'p1': round(sum(x_cls) / len(x_cls), 4),
            'p2': round(sum(y_cls) / len(y_cls), 4),
        }

    return round(cond_mi_raw, 10), round(cond_mi_corrected, 10), class_details


# ── Main ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    forms = load_forms()
    n_forms = len(forms)

    # Compute fingerprints
    print("[fingerprint] Computing mod-ell fingerprints for ells =", ELLS)
    all_fps = {}
    for ell in ELLS:
        fps = [compute_fingerprint(f['traces'], f['level'], ell) for f in forms]
        all_fps[ell] = fps
    print(f"[fingerprint] Done: {n_forms} forms x {len(ELLS)} ells")

    # Cluster sizes
    print("[cluster] Computing cluster sizes...")
    cluster_sizes = {}
    for ell in ELLS:
        cluster_sizes[ell] = compute_cluster_sizes(all_fps, ell)
        non_sing = sum(1 for s in cluster_sizes[ell] if s > 1)
        print(f"  ell={ell}: {non_sing} forms in non-trivial clusters ({non_sing/n_forms:.1%})")

    # Galois classification
    print("[galois] Classifying Galois images...")
    galois_classes = []
    for i, form in enumerate(forms):
        fps_for_form = {ell: all_fps[ell][i] for ell in ELLS}
        galois_classes.append(classify_galois_image(form, fps_for_form))
    class_dist = Counter(galois_classes)
    print(f"[galois] Distribution: {dict(class_dist)}")

    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS 1: Cluster membership MI (binary: in cluster or not)
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ANALYSIS 1: Cluster Membership MI (binary)")
    print("=" * 70)
    membership_mi = {}
    for ell1, ell2 in ELL_PAIRS:
        key = f"{ell1}x{ell2}"
        print(f"  {key}...", end=" ", flush=True)
        result = cluster_membership_mi(cluster_sizes[ell1], cluster_sizes[ell2])
        membership_mi[key] = result
        print(f"MI={result['observed_MI']:.8f}, z={result['entanglement_score']:.2f}, "
              f"ratio={result['overlap_ratio']:.4f}")

    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS 2: Cluster-size profile MI (4-bin categorical)
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ANALYSIS 2: Cluster Size Profile MI")
    print("=" * 70)
    profile_mi = {}
    for ell1, ell2 in ELL_PAIRS:
        key = f"{ell1}x{ell2}"
        print(f"  {key}...", end=" ", flush=True)
        result = cluster_profile_mi(cluster_sizes[ell1], cluster_sizes[ell2])
        profile_mi[key] = result
        print(f"MI={result['observed_MI']:.8f}, z={result['entanglement_score']:.2f}")

    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS 3: CRT-corrected pointwise MI
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ANALYSIS 3: Pointwise MI (arithmetic CRT baseline)")
    print("=" * 70)
    pointwise_mi = {}
    for ell1, ell2 in ELL_PAIRS:
        key = f"{ell1}x{ell2}"
        print(f"  {key}...")
        pw = compute_pointwise_mi(all_fps, ell1, ell2)
        pointwise_mi[key] = pw

        # Summary
        z_vals = [v.get('z_score', 0) for v in pw.values() if isinstance(v, dict) and 'z_score' in v]
        sig = sum(1 for z in z_vals if z > 3.0)
        mean_z = np.mean(z_vals) if z_vals else 0
        print(f"    Mean z={mean_z:.2f}, significant (z>3): {sig}/{len(z_vals)}")

    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS 4: Conditional MI given Galois image
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ANALYSIS 4: Conditional MI given Galois Image")
    print("=" * 70)
    conditional_mi = {}
    for ell1, ell2 in ELL_PAIRS:
        key = f"{ell1}x{ell2}"
        print(f"  {key}...", end=" ", flush=True)

        cond_mi_raw, cond_mi_corrected, class_details = conditional_cluster_mi(
            cluster_sizes[ell1], cluster_sizes[ell2], galois_classes
        )
        # Use bias-corrected unconditional MI too
        uncond_mi = membership_mi[key]['observed_MI']
        uncond_excess = membership_mi[key]['excess_MI_bits'] * math.log(2)  # back to nats
        uncond_corrected = max(0.0, uncond_mi - membership_mi[key]['null_MI_mean'])

        reduction = 1.0 - (cond_mi_corrected / uncond_corrected) if uncond_corrected > 0 else 0.0

        conditional_mi[key] = {
            'ell_1': ell1,
            'ell_2': ell2,
            'unconditional_MI_corrected': round(uncond_corrected, 10),
            'conditional_MI_raw': cond_mi_raw,
            'conditional_MI_corrected': cond_mi_corrected,
            'MI_reduction_fraction': round(reduction, 6),
            'galois_explains': reduction > 0.5,
            'class_breakdown': class_details,
        }
        expl = "GALOIS EXPLAINS" if reduction > 0.5 else f"residual {1-reduction:.1%}"
        print(f"uncond_corr={uncond_corrected:.8f}, cond_corr={cond_mi_corrected:.8f}, "
              f"reduction={reduction:.1%} -> {expl}")

    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS 5: Cross-pair comparison & R5-3 concordance
    # ═══════════════════════════════════════════════════════════════════
    interference_ratios = {
        '3x5': 1.366801, '3x7': 1.464123, '3x11': 0.683605,
        '5x7': 2.555716, '5x11': 3.104722, '7x11': 15.835976,
    }

    comparison = {}
    for key in membership_mi:
        z = membership_mi[key]['entanglement_score']
        ratio = interference_ratios.get(key)
        comparison[key] = {
            'entanglement_z': z,
            'R5_3_interference_ratio': ratio,
            'both_constructive': z > 2.0 and (ratio is not None and ratio > 1.0),
            'overlap_ratio': membership_mi[key]['overlap_ratio'],
        }

    # Bad-prime analysis from pointwise
    bad_prime_analysis = {}
    for key in pointwise_mi:
        pw = pointwise_mi[key]
        small_z = {}
        large_z = []
        for p_str, v in pw.items():
            if not isinstance(v, dict) or 'z_score' not in v:
                continue
            p = int(p_str)
            z = v['z_score']
            if p <= 11:
                small_z[p_str] = round(z, 2)
            else:
                large_z.append(z)
        bad_prime_analysis[key] = {
            'small_primes': small_z,
            'large_primes_mean_z': round(np.mean(large_z), 4) if large_z else 0.0,
            'large_primes_max_z': round(max(large_z), 4) if large_z else 0.0,
            'large_primes_min_z': round(min(large_z), 4) if large_z else 0.0,
        }

    # ── Output ──
    elapsed = time.time() - t0

    # Entanglement ordering
    pairs_sorted = sorted(membership_mi.items(),
                          key=lambda x: x[1]['entanglement_score'], reverse=True)

    results = {
        'metadata': {
            'n_forms': n_forms,
            'ells': ELLS,
            'primes_25': PRIMES_25,
            'n_permutations': N_PERM,
            'galois_class_distribution': dict(class_dist),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed_seconds': round(elapsed, 1),
            'method_notes': (
                'Cluster membership MI measures binary dependence: '
                'is form in non-trivial cluster at ell_1 vs ell_2. '
                'Pointwise MI uses CRT-corrected null (independent marginal resampling). '
                'Conditional MI conditions on Galois image class.'
            ),
        },
        'cluster_membership_mi': {k: v for k, v in membership_mi.items()},
        'cluster_profile_mi': profile_mi,
        'entanglement_ordering': [
            {'pair': k, 'z': v['entanglement_score'],
             'MI_bits': v['excess_MI_bits'],
             'overlap_ratio': v['overlap_ratio']}
            for k, v in pairs_sorted
        ],
        'pointwise_mi_crt_corrected': pointwise_mi,
        'bad_prime_analysis': bad_prime_analysis,
        'conditional_mi': conditional_mi,
        'R5_3_comparison': comparison,
    }

    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n[done] Results saved to {OUT_PATH}")
    print(f"[done] Elapsed: {elapsed:.1f}s")

    # ── Summary tables ──
    print("\n" + "=" * 70)
    print("PRIME ENTANGLEMENT SCORE — FINAL SUMMARY")
    print("=" * 70)

    print(f"\nCluster Membership MI (binary entanglement):")
    print(f"{'Pair':<8} {'MI (nats)':>12} {'Null':>12} {'Z-score':>8} {'Bits':>12} {'Overlap':>8}")
    print("-" * 66)
    for key, val in pairs_sorted:
        print(f"{key:<8} {val['observed_MI']:>12.8f} {val['null_MI_mean']:>12.8f} "
              f"{val['entanglement_score']:>8.2f} {val['excess_MI_bits']:>12.8f} "
              f"{val['overlap_ratio']:>8.4f}")

    print(f"\nCluster Profile MI (4-bin categorical):")
    print(f"{'Pair':<8} {'MI (nats)':>12} {'Z-score':>8}")
    print("-" * 30)
    for key, _ in pairs_sorted:
        val = profile_mi[key]
        print(f"{key:<8} {val['observed_MI']:>12.8f} {val['entanglement_score']:>8.2f}")

    print(f"\nConditional MI (given Galois image, bias-corrected):")
    print(f"{'Pair':<8} {'Uncond':>12} {'Cond':>12} {'Reduction':>10} {'Explains?':>10}")
    print("-" * 56)
    for key, _ in pairs_sorted:
        c = conditional_mi[key]
        print(f"{key:<8} {c['unconditional_MI_corrected']:>12.8f} {c['conditional_MI_corrected']:>12.8f} "
              f"{c['MI_reduction_fraction']:>9.1%} "
              f"{'YES' if c['galois_explains'] else 'no':>10}")

    print(f"\nR5-3 Concordance:")
    print(f"{'Pair':<8} {'Entangle z':>12} {'R5-3 ratio':>12} {'Concordant':>12}")
    print("-" * 48)
    for key, c in sorted(comparison.items()):
        ratio_str = f"{c['R5_3_interference_ratio']:.4f}" if c['R5_3_interference_ratio'] else "N/A"
        print(f"{key:<8} {c['entanglement_z']:>12.2f} {ratio_str:>12} "
              f"{'YES' if c['both_constructive'] else 'no':>12}")

    print(f"\nPointwise MI (CRT-corrected, summary):")
    print(f"{'Pair':<8} {'Mean z':>8} {'Max z':>8} {'Min z':>8}")
    print("-" * 36)
    for key in [k for k, _ in pairs_sorted]:
        ba = bad_prime_analysis[key]
        print(f"{key:<8} {ba['large_primes_mean_z']:>8.2f} "
              f"{ba['large_primes_max_z']:>8.2f} {ba['large_primes_min_z']:>8.2f}")


if __name__ == '__main__':
    main()
