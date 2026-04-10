#!/usr/bin/env python3
"""
C06: Lattice–NumberField Determinant Bridge Investigation

Tests whether the Lattice-NumberField tensor bridge (SV=5829) is genuine
structural or just shared prime factorization artifacts.

Tests:
  A. Determinant-Discriminant overlap
  B. Class number bridge (dim/degree × class_number)
  C. Prime detrending (factor, remove shared prime distribution, permutation null)
  D. Matched-object comparison (det vs |disc| at same dim/degree)
  E. Kissing number bridge

Philosophy: assume artifact until proven otherwise.
"""

import json
import math
import sys
import os
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

# ── reproducibility ──
np.random.seed(42)
N_PERM = 1000

# ── paths ──
BASE = Path("F:/Prometheus")
LAT_PATH = BASE / "cartography/lmfdb_dump/lat_lattices.json"
NF_PATH  = BASE / "cartography/number_fields/data/number_fields.json"
OUT_PATH = BASE / "cartography/shared/scripts/v2/lattice_nf_bridge_results.json"


# ══════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════

def load_lattices():
    with open(LAT_PATH) as f:
        raw = json.load(f)
    recs = raw["records"]
    out = []
    for r in recs:
        det = r.get("det")
        if det is None or det <= 0:
            continue
        out.append({
            "label": r["label"],
            "dim": r["dim"],
            "det": int(det),
            "class_number": int(r["class_number"]) if r.get("class_number") is not None else None,
            "kissing": int(r["kissing"]) if r.get("kissing") is not None else None,
            "minimum": r.get("minimum"),
            "level": r.get("level"),
            "aut": r.get("aut"),
        })
    return out


def load_number_fields():
    with open(NF_PATH) as f:
        recs = json.load(f)
    out = []
    for r in recs:
        disc = r.get("disc_abs")
        if disc is None or disc == "":
            continue
        out.append({
            "label": r["label"],
            "degree": int(r["degree"]),
            "disc_abs": int(disc),
            "disc_sign": int(r.get("disc_sign", 1)),
            "class_number": int(r["class_number"]) if r.get("class_number") not in (None, "") else None,
            "regulator": float(r["regulator"]) if r.get("regulator") not in (None, "") else None,
            "galois_label": r.get("galois_label", ""),
        })
    return out


# ══════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════

def small_factor(n):
    """Return prime factorization as dict {p: e} for moderate-size n."""
    if n <= 1:
        return {}
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def prime_signature(n):
    """Sorted tuple of exponents (ignoring which primes)."""
    f = small_factor(n)
    return tuple(sorted(f.values(), reverse=True)) if f else ()


def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


# ══════════════════════════════════════════════════════════════
# TEST A: Determinant-Discriminant overlap
# ══════════════════════════════════════════════════════════════

def test_det_disc_overlap(lat, nf):
    print("\n═══ TEST A: Determinant-Discriminant Overlap ═══")

    lat_dets = set(r["det"] for r in lat)
    nf_discs = set(r["disc_abs"] for r in nf)

    overlap = lat_dets & nf_discs
    raw_jaccard = jaccard(lat_dets, nf_discs)
    raw_overlap_frac = len(overlap) / min(len(lat_dets), len(nf_discs))

    print(f"  Unique lattice dets: {len(lat_dets)}")
    print(f"  Unique NF |disc|:    {len(nf_discs)}")
    print(f"  Overlap:             {len(overlap)}")
    print(f"  Jaccard:             {raw_jaccard:.6f}")
    print(f"  Overlap / min(|A|,|B|): {raw_overlap_frac:.6f}")

    # Random baseline: draw random integers from same range as lat_dets
    all_dets = sorted(lat_dets)
    lo, hi = min(all_dets), max(all_dets)
    null_jaccards = []
    null_overlaps = []
    for _ in range(N_PERM):
        rand_set = set(np.random.randint(lo, hi + 1, size=len(lat_dets)))
        null_jaccards.append(jaccard(rand_set, nf_discs))
        null_overlaps.append(len(rand_set & nf_discs) / min(len(rand_set), len(nf_discs)))

    pval_jaccard = (np.sum(np.array(null_jaccards) >= raw_jaccard) + 1) / (N_PERM + 1)
    pval_overlap = (np.sum(np.array(null_overlaps) >= raw_overlap_frac) + 1) / (N_PERM + 1)

    # Also try: restrict to NF disc range (1..9997) for fairer comparison
    lat_dets_small = set(d for d in lat_dets if d <= max(nf_discs))
    overlap_small = lat_dets_small & nf_discs
    frac_small = len(overlap_small) / min(len(lat_dets_small), len(nf_discs)) if lat_dets_small else 0

    null_small = []
    for _ in range(N_PERM):
        rand_set = set(np.random.randint(1, max(nf_discs) + 1, size=len(lat_dets_small)))
        null_small.append(len(rand_set & nf_discs) / min(len(rand_set), len(nf_discs)))
    pval_small = (np.sum(np.array(null_small) >= frac_small) + 1) / (N_PERM + 1)

    print(f"  Restricted to disc range: overlap={len(overlap_small)}/{len(lat_dets_small)} lat dets")
    print(f"  Restricted overlap frac: {frac_small:.6f}")
    print(f"  Null p-value (full):      {pval_overlap:.4f}")
    print(f"  Null p-value (restricted): {pval_small:.4f}")

    effect = (raw_overlap_frac - np.mean(null_overlaps)) / (np.std(null_overlaps) + 1e-12)
    effect_small = (frac_small - np.mean(null_small)) / (np.std(null_small) + 1e-12)

    verdict = "GENUINE" if pval_small < 0.01 and effect_small > 3 else \
              "PRIME ARTIFACT" if pval_small > 0.05 else "MARGINAL"

    print(f"  Effect size (full): {effect:.2f}σ")
    print(f"  Effect size (restricted): {effect_small:.2f}σ")
    print(f"  Verdict: {verdict}")

    return {
        "test": "A_det_disc_overlap",
        "unique_lat_dets": len(lat_dets),
        "unique_nf_discs": len(nf_discs),
        "overlap": len(overlap),
        "jaccard": round(raw_jaccard, 6),
        "overlap_frac": round(raw_overlap_frac, 6),
        "restricted_overlap": len(overlap_small),
        "restricted_frac": round(frac_small, 6),
        "pval_full": round(float(pval_overlap), 4),
        "pval_restricted": round(float(pval_small), 4),
        "effect_full": round(float(effect), 2),
        "effect_restricted": round(float(effect_small), 2),
        "verdict": verdict,
    }


# ══════════════════════════════════════════════════════════════
# TEST B: Class number bridge
# ══════════════════════════════════════════════════════════════

def test_class_number_bridge(lat, nf):
    print("\n═══ TEST B: Class Number Bridge ═══")

    # Joint distribution: (dim_or_degree, class_number) -> count
    lat_joint = Counter((r["dim"], r["class_number"]) for r in lat if r["class_number"] is not None)
    nf_joint = Counter((r["degree"], r["class_number"]) for r in nf if r["class_number"] is not None)

    # Marginal class number distributions
    lat_cn = Counter(r["class_number"] for r in lat if r["class_number"] is not None)
    nf_cn = Counter(r["class_number"] for r in nf if r["class_number"] is not None)

    # Overlap of class number sets
    lat_cn_set = set(lat_cn.keys())
    nf_cn_set = set(nf_cn.keys())
    cn_overlap = lat_cn_set & nf_cn_set
    print(f"  Lattice class numbers: {len(lat_cn_set)} unique values")
    print(f"  NF class numbers:      {len(nf_cn_set)} unique values")
    print(f"  Overlap:               {len(cn_overlap)} values")

    # Correlation of class number frequencies on shared values
    shared = sorted(cn_overlap)
    if len(shared) >= 3:
        lat_freq = np.array([lat_cn[c] for c in shared], dtype=float)
        nf_freq = np.array([nf_cn[c] for c in shared], dtype=float)
        # Normalize
        lat_freq /= lat_freq.sum()
        nf_freq /= nf_freq.sum()

        raw_corr = np.corrcoef(lat_freq, nf_freq)[0, 1]
        print(f"  Frequency correlation on shared CNs: {raw_corr:.4f}")

        # Permutation null: shuffle NF class numbers
        null_corrs = []
        nf_cn_list = [r["class_number"] for r in nf if r["class_number"] is not None]
        for _ in range(N_PERM):
            shuffled = np.random.permutation(nf_cn_list)
            shuf_cn = Counter(shuffled)
            shuf_freq = np.array([shuf_cn.get(c, 0) for c in shared], dtype=float)
            s = shuf_freq.sum()
            if s > 0:
                shuf_freq /= s
                null_corrs.append(np.corrcoef(lat_freq, shuf_freq)[0, 1])
        null_corrs = np.array(null_corrs)
        pval = (np.sum(null_corrs >= raw_corr) + 1) / (len(null_corrs) + 1)
        effect = (raw_corr - np.mean(null_corrs)) / (np.std(null_corrs) + 1e-12)
    else:
        raw_corr = 0.0
        pval = 1.0
        effect = 0.0

    # Joint key overlap: (N, cn) pairs that appear in both
    joint_overlap = set(lat_joint.keys()) & set(nf_joint.keys())
    print(f"  Joint (dim/deg, CN) overlap: {len(joint_overlap)} pairs")

    # Is joint overlap more than expected from marginals?
    # Null: random pairing of dims/degrees with class numbers
    lat_dims = [r["dim"] for r in lat if r["class_number"] is not None]
    lat_cns = [r["class_number"] for r in lat if r["class_number"] is not None]
    nf_degs = [r["degree"] for r in nf if r["class_number"] is not None]
    nf_cns_list = [r["class_number"] for r in nf if r["class_number"] is not None]

    null_joint_overlaps = []
    for _ in range(N_PERM):
        shuf_lat_cn = np.random.permutation(lat_cns)
        shuf_lat_joint = Counter(zip(lat_dims, shuf_lat_cn))
        null_joint_overlaps.append(len(set(shuf_lat_joint.keys()) & set(nf_joint.keys())))

    pval_joint = (np.sum(np.array(null_joint_overlaps) >= len(joint_overlap)) + 1) / (N_PERM + 1)
    effect_joint = (len(joint_overlap) - np.mean(null_joint_overlaps)) / (np.std(null_joint_overlaps) + 1e-12)

    print(f"  Frequency correlation p-value: {pval:.4f}")
    print(f"  Joint overlap p-value:         {pval_joint:.4f}")
    print(f"  Joint overlap effect:          {effect_joint:.2f}σ")

    # Class number is dominated by small integers — likely trivial overlap
    verdict = "GENUINE" if pval_joint < 0.01 and effect_joint > 3 else \
              "PRIME ARTIFACT" if pval_joint > 0.05 else "MARGINAL"
    print(f"  Verdict: {verdict}")

    return {
        "test": "B_class_number_bridge",
        "lat_cn_unique": len(lat_cn_set),
        "nf_cn_unique": len(nf_cn_set),
        "cn_overlap": len(cn_overlap),
        "freq_correlation": round(float(raw_corr), 4),
        "freq_pval": round(float(pval), 4),
        "freq_effect": round(float(effect), 2),
        "joint_overlap": len(joint_overlap),
        "joint_pval": round(float(pval_joint), 4),
        "joint_effect": round(float(effect_joint), 2),
        "verdict": verdict,
    }


# ══════════════════════════════════════════════════════════════
# TEST C: Prime detrending
# ══════════════════════════════════════════════════════════════

def test_prime_detrending(lat, nf):
    print("\n═══ TEST C: Prime Detrending ═══")

    # Factor all dets and discs
    lat_dets = [r["det"] for r in lat]
    nf_discs = [r["disc_abs"] for r in nf]

    # Prime frequency profiles
    lat_prime_freq = Counter()
    for d in lat_dets:
        for p in small_factor(d):
            lat_prime_freq[p] += 1

    nf_prime_freq = Counter()
    for d in nf_discs:
        for p in small_factor(d):
            nf_prime_freq[p] += 1

    shared_primes = set(lat_prime_freq.keys()) & set(nf_prime_freq.keys())
    print(f"  Primes in lattice dets: {len(lat_prime_freq)}")
    print(f"  Primes in NF discs:     {len(nf_prime_freq)}")
    print(f"  Shared primes:          {len(shared_primes)}")

    # Prime signature overlap (structural test beyond primes themselves)
    lat_sigs = Counter(prime_signature(d) for d in lat_dets)
    nf_sigs = Counter(prime_signature(d) for d in nf_discs)

    shared_sigs = set(lat_sigs.keys()) & set(nf_sigs.keys())
    print(f"  Lattice prime signatures: {len(lat_sigs)} types")
    print(f"  NF prime signatures:      {len(nf_sigs)} types")
    print(f"  Shared signatures:        {len(shared_sigs)} types")

    # Correlation of prime frequencies on shared primes
    sp_sorted = sorted(shared_primes)[:200]  # top 200 shared primes
    lat_pf = np.array([lat_prime_freq[p] for p in sp_sorted], dtype=float)
    nf_pf = np.array([nf_prime_freq[p] for p in sp_sorted], dtype=float)
    lat_pf /= lat_pf.sum()
    nf_pf /= nf_pf.sum()

    raw_corr = np.corrcoef(lat_pf, nf_pf)[0, 1]
    print(f"  Prime frequency correlation: {raw_corr:.4f}")

    # After removing prime distribution: use prime signatures as residual
    # Overlap of exact values AFTER controlling for prime signatures
    # Group dets/discs by prime signature, then test overlap within groups
    lat_by_sig = defaultdict(set)
    for d in lat_dets:
        lat_by_sig[prime_signature(d)].add(d)

    nf_by_sig = defaultdict(set)
    for d in nf_discs:
        nf_by_sig[prime_signature(d)].add(d)

    # Within shared signatures, compute overlap
    within_sig_overlap = 0
    within_sig_total_min = 0
    for sig in shared_sigs:
        ov = len(lat_by_sig[sig] & nf_by_sig[sig])
        mn = min(len(lat_by_sig[sig]), len(nf_by_sig[sig]))
        within_sig_overlap += ov
        within_sig_total_min += mn

    residual_frac = within_sig_overlap / within_sig_total_min if within_sig_total_min > 0 else 0
    print(f"  Within-signature exact overlap: {within_sig_overlap} / {within_sig_total_min}")
    print(f"  Residual overlap fraction:      {residual_frac:.6f}")

    # Permutation null: shuffle values within each signature class
    null_residuals = []
    for _ in range(N_PERM):
        total_ov = 0
        total_min = 0
        for sig in shared_sigs:
            lat_vals = list(lat_by_sig[sig])
            nf_vals = list(nf_by_sig[sig])
            # Shuffle lat values by drawing from same-signature random ints
            # Actually: the right null is to permute the NF values among same-sig slots
            np.random.shuffle(nf_vals)
            # Re-form set from shuffled (same values, same set — need different null)
            # Better null: for each signature, draw random integers with that signature
            # from the range of lat_dets
            # Simplest valid null: overlap of two random samples from integers with given signature
            # Since shuffling a set doesn't change the set, we need a different approach:
            # Null = the overlap expected if both sets were random subsets of all integers with that signature
            # Use hypergeometric: but we don't know the universe size
            # Instead: simply compare raw overlap fraction vs random-integer overlap
            total_ov += len(set(lat_vals) & set(nf_vals))
            total_min += min(len(lat_vals), len(nf_vals))
        null_residuals.append(total_ov / total_min if total_min > 0 else 0)

    # The shuffled null doesn't change the set — so we need a DIFFERENT null
    # Better approach: permute the det->label mapping across lattices
    # Then recompute which dets overlap with NF discs — this doesn't change either
    # The RIGHT null: compare overlap to random integers of same SIZE
    # Let's do that per signature

    print("  [Switching to random-integer-per-signature null]")
    null_residuals2 = []
    for trial in range(N_PERM):
        total_ov = 0
        total_min = 0
        for sig in shared_sigs:
            lat_vals = lat_by_sig[sig]
            nf_vals = nf_by_sig[sig]
            # Generate random set of same size as lat_vals
            # from all integers in the range that have this prime signature
            # This is expensive. Instead: draw random integers from lat det range
            # and keep those with matching signature — too slow.
            # Simpler: just compute expected overlap from two random subsets
            # of [1, max_val] of sizes |lat_vals| and |nf_vals|
            # Expected overlap ≈ |A|*|B|/max_val
            max_val = max(max(lat_vals), max(nf_vals))
            expected = len(lat_vals) * len(nf_vals) / max_val
            # Draw from Poisson
            total_ov += np.random.poisson(expected)
            total_min += min(len(lat_vals), len(nf_vals))
        null_residuals2.append(total_ov / total_min if total_min > 0 else 0)

    null_residuals2 = np.array(null_residuals2)
    pval = (np.sum(null_residuals2 >= residual_frac) + 1) / (N_PERM + 1)
    effect = (residual_frac - np.mean(null_residuals2)) / (np.std(null_residuals2) + 1e-12)

    print(f"  Null mean: {np.mean(null_residuals2):.6f}, std: {np.std(null_residuals2):.6f}")
    print(f"  p-value:   {pval:.4f}")
    print(f"  Effect:    {effect:.2f}σ")

    # Also test: omega (number of distinct prime factors) distribution
    lat_omegas = [len(small_factor(d)) for d in lat_dets]
    nf_omegas = [len(small_factor(d)) for d in nf_discs]

    from scipy.stats import ks_2samp
    ks_stat, ks_pval = ks_2samp(lat_omegas, nf_omegas)
    print(f"  Omega(det) vs Omega(disc) KS: stat={ks_stat:.4f}, p={ks_pval:.4e}")

    verdict = "GENUINE" if pval < 0.01 and effect > 3 else \
              "PRIME ARTIFACT" if pval > 0.05 else "MARGINAL"
    print(f"  Verdict: {verdict}")

    return {
        "test": "C_prime_detrending",
        "shared_primes": len(shared_primes),
        "prime_freq_correlation": round(float(raw_corr), 4),
        "shared_signatures": len(shared_sigs),
        "within_sig_overlap": within_sig_overlap,
        "residual_frac": round(float(residual_frac), 6),
        "null_mean": round(float(np.mean(null_residuals2)), 6),
        "pval": round(float(pval), 4),
        "effect": round(float(effect), 2),
        "omega_ks_stat": round(float(ks_stat), 4),
        "omega_ks_pval": float(f"{ks_pval:.4e}"),
        "verdict": verdict,
    }


# ══════════════════════════════════════════════════════════════
# TEST D: Matched-object comparison (dim=degree, det vs |disc|)
# ══════════════════════════════════════════════════════════════

def test_matched_dimension(lat, nf):
    print("\n═══ TEST D: Matched-Object Comparison (dim=degree) ═══")

    from scipy.stats import ks_2samp, mannwhitneyu

    target_dims = [2, 3, 4, 5, 6, 8]
    results_by_dim = {}

    for N in target_dims:
        lat_dets = [r["det"] for r in lat if r["dim"] == N]
        nf_discs = [r["disc_abs"] for r in nf if r["degree"] == N]

        if len(lat_dets) < 5 or len(nf_discs) < 5:
            print(f"  dim/deg={N}: INSUFFICIENT DATA (lat={len(lat_dets)}, nf={len(nf_discs)})")
            results_by_dim[N] = {"verdict": "INSUFFICIENT DATA",
                                 "n_lat": len(lat_dets), "n_nf": len(nf_discs)}
            continue

        lat_arr = np.array(lat_dets, dtype=float)
        nf_arr = np.array(nf_discs, dtype=float)

        # Log-scale distributions
        lat_log = np.log1p(lat_arr)
        nf_log = np.log1p(nf_arr)

        ks_stat, ks_pval = ks_2samp(lat_log, nf_log)

        # Exact value overlap
        overlap = len(set(lat_dets) & set(nf_discs))
        overlap_frac = overlap / min(len(set(lat_dets)), len(set(nf_discs)))

        # Permutation null for overlap: pool and split
        pooled = list(set(lat_dets)) + list(set(nf_discs))
        null_overlaps = []
        for _ in range(N_PERM):
            np.random.shuffle(pooled)
            split = len(set(lat_dets))
            a = set(pooled[:split])
            b = set(pooled[split:])
            null_overlaps.append(len(a & b) / min(len(a), len(b)) if min(len(a), len(b)) > 0 else 0)

        null_overlaps = np.array(null_overlaps)
        pval_ov = (np.sum(null_overlaps >= overlap_frac) + 1) / (N_PERM + 1)
        effect_ov = (overlap_frac - np.mean(null_overlaps)) / (np.std(null_overlaps) + 1e-12)

        # Mean-spacing normalized comparison
        lat_sorted = np.sort(lat_arr)
        nf_sorted = np.sort(nf_arr)
        lat_gaps = np.diff(lat_sorted)
        nf_gaps = np.diff(nf_sorted)
        lat_mean_gap = np.mean(lat_gaps) if len(lat_gaps) > 0 else 1
        nf_mean_gap = np.mean(nf_gaps) if len(nf_gaps) > 0 else 1

        lat_norm = lat_sorted / lat_mean_gap
        nf_norm = nf_sorted / nf_mean_gap

        # KS on normalized
        min_len = min(len(lat_norm), len(nf_norm))
        ks_norm, ks_norm_p = ks_2samp(lat_norm[:min_len], nf_norm[:min_len])

        print(f"  dim/deg={N}: lat={len(lat_dets)}, nf={len(nf_discs)}")
        print(f"    Log-KS: {ks_stat:.4f} (p={ks_pval:.4e})")
        print(f"    Overlap: {overlap} values, frac={overlap_frac:.4f}, p={pval_ov:.4f}")
        print(f"    Norm-KS: {ks_norm:.4f} (p={ks_norm_p:.4e})")

        verdict = "GENUINE" if pval_ov < 0.01 and effect_ov > 3 else \
                  "PRIME ARTIFACT" if ks_pval < 0.01 else "DIFFERENT DISTRIBUTIONS"

        results_by_dim[N] = {
            "n_lat": len(lat_dets),
            "n_nf": len(nf_discs),
            "log_ks_stat": round(float(ks_stat), 4),
            "log_ks_pval": float(f"{ks_pval:.4e}"),
            "overlap": overlap,
            "overlap_frac": round(float(overlap_frac), 4),
            "overlap_pval": round(float(pval_ov), 4),
            "overlap_effect": round(float(effect_ov), 2),
            "norm_ks_stat": round(float(ks_norm), 4),
            "norm_ks_pval": float(f"{ks_norm_p:.4e}"),
            "verdict": verdict,
        }

    # Overall verdict
    verdicts = [v.get("verdict", "INSUFFICIENT DATA") for v in results_by_dim.values()]
    genuine_count = sum(1 for v in verdicts if v == "GENUINE")
    overall = "GENUINE" if genuine_count >= 2 else \
              "PRIME ARTIFACT" if genuine_count == 0 else "MARGINAL"

    print(f"\n  Overall matched-object verdict: {overall}")
    return {
        "test": "D_matched_dimension",
        "by_dim": results_by_dim,
        "overall_verdict": overall,
    }


# ══════════════════════════════════════════════════════════════
# TEST E: Kissing number bridge
# ══════════════════════════════════════════════════════════════

def test_kissing_bridge(lat, nf):
    print("\n═══ TEST E: Kissing Number Bridge ═══")

    # Kissing numbers in lattices
    kissing_vals = [r["kissing"] for r in lat if r.get("kissing") is not None]
    kissing_counter = Counter(kissing_vals)
    print(f"  Lattices with kissing number: {len(kissing_vals)}")
    print(f"  Unique kissing values: {len(kissing_counter)}")
    print(f"  Top kissing values: {kissing_counter.most_common(10)}")

    # Is there ANY meaningful connection to NF?
    # Hypothesis: kissing numbers might appear as discriminants or class numbers
    kissing_set = set(kissing_vals)
    nf_disc_set = set(r["disc_abs"] for r in nf)
    nf_cn_set = set(r["class_number"] for r in nf if r["class_number"] is not None)

    kiss_disc_ov = kissing_set & nf_disc_set
    kiss_cn_ov = kissing_set & nf_cn_set

    print(f"  Kissing ∩ NF discs: {len(kiss_disc_ov)}")
    print(f"  Kissing ∩ NF class_numbers: {len(kiss_cn_ov)}")

    # Test: for lattices with same dim, is kissing number correlated with
    # anything in the matched NF?
    # Group lattices by (dim, det) and check if det overlap with NF disc
    # is higher for high-kissing lattices
    lat_dim3 = [r for r in lat if r["dim"] == 3 and r.get("kissing") is not None]
    if len(lat_dim3) > 100:
        median_kiss = np.median([r["kissing"] for r in lat_dim3])
        high_kiss = set(r["det"] for r in lat_dim3 if r["kissing"] > median_kiss)
        low_kiss = set(r["det"] for r in lat_dim3 if r["kissing"] <= median_kiss)
        nf_deg3 = set(r["disc_abs"] for r in nf if r["degree"] == 3)

        high_ov = len(high_kiss & nf_deg3)
        low_ov = len(low_kiss & nf_deg3)
        print(f"  Dim=3: high-kissing det overlap with deg-3 disc: {high_ov}/{len(high_kiss)}")
        print(f"  Dim=3: low-kissing det overlap with deg-3 disc:  {low_ov}/{len(low_kiss)}")

        # Fisher exact test
        from scipy.stats import fisher_exact
        table = [[high_ov, len(high_kiss) - high_ov],
                 [low_ov, len(low_kiss) - low_ov]]
        odds, fisher_p = fisher_exact(table)
        print(f"  Fisher exact: odds={odds:.3f}, p={fisher_p:.4f}")
        pval = fisher_p
        effect = abs(np.log(odds + 1e-12))
    else:
        pval = 1.0
        effect = 0.0
        odds = 1.0
        fisher_p = 1.0

    verdict = "GENUINE" if pval < 0.01 and effect > 1 else \
              "INSUFFICIENT DATA" if len(lat_dim3) < 100 else "NO BRIDGE"
    print(f"  Verdict: {verdict}")

    return {
        "test": "E_kissing_bridge",
        "n_with_kissing": len(kissing_vals),
        "unique_kissing": len(kissing_counter),
        "kissing_disc_overlap": len(kiss_disc_ov),
        "kissing_cn_overlap": len(kiss_cn_ov),
        "fisher_odds": round(float(odds), 3) if 'odds' in dir() else None,
        "fisher_pval": round(float(fisher_p), 4) if 'fisher_p' in dir() else None,
        "verdict": verdict,
    }


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print("C06: Lattice–NumberField Determinant Bridge Investigation")
    print("=" * 60)

    print("\nLoading data...")
    lat = load_lattices()
    nf = load_number_fields()
    print(f"  Lattices: {len(lat)} records")
    print(f"  Number fields: {len(nf)} records")

    results = {}

    results["A"] = test_det_disc_overlap(lat, nf)
    results["B"] = test_class_number_bridge(lat, nf)
    results["C"] = test_prime_detrending(lat, nf)
    results["D"] = test_matched_dimension(lat, nf)
    results["E"] = test_kissing_bridge(lat, nf)

    # ── Summary ──
    print("\n" + "=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(f"{'Test':<40} {'Verdict':<20}")
    print("-" * 60)
    for key in ["A", "B", "C", "D", "E"]:
        r = results[key]
        name = r["test"]
        v = r.get("verdict") or r.get("overall_verdict", "???")
        print(f"  {name:<38} {v:<20}")

    # Overall assessment
    verdicts = []
    for key in ["A", "B", "C", "D", "E"]:
        r = results[key]
        v = r.get("verdict") or r.get("overall_verdict", "???")
        verdicts.append(v)

    genuine = sum(1 for v in verdicts if v == "GENUINE")
    artifact = sum(1 for v in verdicts if "ARTIFACT" in v)

    if genuine >= 3:
        overall = "GENUINE BRIDGE — structure beyond primes"
    elif genuine >= 1:
        overall = "PARTIAL — some genuine signal, mostly artifact"
    else:
        overall = "ARTIFACT — bridge is dominated by shared primes and small integers"

    print(f"\n  OVERALL: {overall}")
    results["overall"] = overall

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
