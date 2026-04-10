#!/usr/bin/env python3
"""
Charon — Quadratic Enrichment Analysis (Q1)
============================================
Analyze prime density of quadratic polynomials f(n) = an^2 + bn + c,
grouped by discriminant Delta = b^2 - 4ac.

Questions:
1. Does enrichment (prime density above PNT baseline ~1/ln(N)) correlate
   with discriminant?
2. Does the algebraic DNA enrichment law (8x after detrending) apply to
   prime-generating polynomial families grouped by Delta?
3. How do high-density polynomials compare to low-density ones in
   mod-p fingerprint and BM recurrence structure?

Method:
  - Generate 100 quadratic polynomials with |a|<=10, |b|<=20, |c|<=100.
  - For each polynomial, evaluate f(1)..f(1000) and compute:
    (a) prime fraction,
    (b) mod-p fingerprint of the prime-index subsequence at p=2,3,5,7,11,
    (c) Berlekamp-Massey recurrence order of the prime-index subsequence.
  - Group by discriminant Delta and measure within-group fingerprint
    enrichment vs random baseline.
  - Compare high-density vs low-density families.

Writes:
  - cartography/v2/quadratic_enrichment_results.json
"""

import json
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np

# ── paths ────────────────────────────────────────────────────────────────
OUT = Path(__file__).resolve().parent / "quadratic_enrichment_results.json"

PRIMES_FP = [2, 3, 5, 7, 11]   # fingerprint moduli
N_RANGE = range(1, 1001)        # evaluate f(1)..f(1000)
N_POLYS = 100                   # number of polynomials to analyse
FP_LEN = 50                     # fingerprint window length
MAX_BM = 200                    # max BM recurrence order attempted

random.seed(42)
np.random.seed(42)


# ── primality ────────────────────────────────────────────────────────────
def _small_primes_set(limit=1_100_000):
    """Sieve of Eratosthenes up to limit."""
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return frozenset(i for i in range(2, limit + 1) if sieve[i])

PRIME_SET = _small_primes_set()

def is_prime(n):
    if n < 2:
        return False
    if n < 1_100_001:
        return n in PRIME_SET
    # Miller-Rabin for larger values (shouldn't happen for n<=1000 polys)
    if n % 2 == 0:
        return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


# ── mod-p fingerprint ────────────────────────────────────────────────────
def mod_p_fingerprint(seq, p, length=FP_LEN):
    """Return tuple of (val % p) for the first `length` elements."""
    usable = seq[:length]
    if len(usable) < length:
        return None
    return tuple(v % p for v in usable)


# ── Berlekamp-Massey over integers (mod large prime) ─────────────────────
def berlekamp_massey_order(seq, mod=1_000_000_007):
    """
    Berlekamp-Massey algorithm over GF(mod) to find minimal
    linear recurrence length of `seq`.
    Returns the order (length of the LFSR).
    """
    if not seq:
        return 0
    n = len(seq)
    s = [x % mod for x in seq]

    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1

    for i in range(n):
        d = s[i]
        for j in range(1, L + 1):
            if j < len(C):
                d = (d + C[j] * s[i - j]) % mod
        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = C[:]
            coef = (d * pow(b, mod - 2, mod)) % mod
            # Extend C if needed
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coef * B[j]) % mod
            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            coef = (d * pow(b, mod - 2, mod)) % mod
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coef * B[j]) % mod
            m += 1

    return min(L, MAX_BM)


# ── Polynomial selection ─────────────────────────────────────────────────
def generate_polynomials(n_total=N_POLYS):
    """
    Generate polynomials: include famous ones, then fill with random.
    Ensure a != 0 (must be genuinely quadratic).
    """
    polys = []

    # Famous high-density quadratics
    famous = [
        (1, 1, 41,   "Euler n^2+n+41"),
        (1, -1, 41,  "Euler variant n^2-n+41"),
        (6, 0, -1,   "6n^2-1"),
        (4, 4, 59,   "4n^2+4n+59"),
        (1, 1, 17,   "n^2+n+17"),
        (2, -1, 41,  "2n^2-n+41"),
        (2, 1, 29,   "2n^2+n+29"),
        (1, 1, 11,   "n^2+n+11"),
        (3, 3, 23,   "3n^2+3n+23"),
        (1, -1, 17,  "n^2-n+17"),
    ]
    for a, b, c, name in famous:
        disc = b * b - 4 * a * c
        polys.append({"a": a, "b": b, "c": c, "disc": disc, "name": name})

    # Random polynomials to fill to n_total
    seen = {(p["a"], p["b"], p["c"]) for p in polys}
    attempts = 0
    while len(polys) < n_total and attempts < 100000:
        a = random.choice([x for x in range(-10, 11) if x != 0])
        b = random.randint(-20, 20)
        c = random.randint(-100, 100)
        attempts += 1
        if (a, b, c) in seen:
            continue
        # Ensure at least some values are positive (so primality makes sense)
        vals = [a * n * n + b * n + c for n in [1, 5, 10, 50, 100]]
        if sum(1 for v in vals if v > 1) < 3:
            continue
        seen.add((a, b, c))
        disc = b * b - 4 * a * c
        polys.append({"a": a, "b": b, "c": c, "disc": disc, "name": None})

    return polys[:n_total]


# ── Main analysis ────────────────────────────────────────────────────────
def analyse_polynomial(poly):
    """Compute prime density, fingerprints, BM order for one polynomial."""
    a, b, c = poly["a"], poly["b"], poly["c"]

    values = []
    prime_indices = []     # 1-based indices n where f(n) is prime
    prime_values = []      # the actual f(n) values that are prime

    for n in N_RANGE:
        v = a * n * n + b * n + c
        values.append(v)
        if v > 1 and is_prime(abs(v)):
            prime_indices.append(n)
            prime_values.append(v)

    n_prime = len(prime_indices)
    n_total = len(values)
    prime_fraction = n_prime / n_total

    # PNT baseline: average 1/ln(|f(n)|) for the values evaluated
    pnt_sum = 0
    pnt_count = 0
    for v in values:
        av = abs(v)
        if av > 1:
            pnt_sum += 1.0 / math.log(av)
            pnt_count += 1
    pnt_baseline = pnt_sum / pnt_count if pnt_count > 0 else 0
    enrichment_vs_pnt = prime_fraction / pnt_baseline if pnt_baseline > 0 else 0

    # Mod-p fingerprints of the prime-index subsequence
    fingerprints = {}
    for p in PRIMES_FP:
        fp = mod_p_fingerprint(prime_indices, p, FP_LEN)
        if fp is not None:
            fingerprints[str(p)] = list(fp)
        else:
            fingerprints[str(p)] = None

    # BM recurrence order of the prime-index subsequence
    bm_seq = prime_indices[:min(len(prime_indices), 200)]
    bm_order = berlekamp_massey_order(bm_seq) if len(bm_seq) >= 4 else None

    return {
        "a": a, "b": b, "c": c,
        "discriminant": poly["disc"],
        "name": poly["name"],
        "n_prime": n_prime,
        "n_total": n_total,
        "prime_fraction": round(prime_fraction, 6),
        "pnt_baseline": round(pnt_baseline, 6),
        "enrichment_vs_pnt": round(enrichment_vs_pnt, 4),
        "mod_p_fingerprints": fingerprints,
        "bm_recurrence_order": bm_order,
    }


# ── Within-group fingerprint enrichment ──────────────────────────────────
def compute_enrichment_by_discriminant(results):
    """
    Group polynomials by discriminant. Within each group, measure
    fingerprint match rate vs random baseline.
    """
    # Group by discriminant
    disc_groups = defaultdict(list)
    for r in results:
        disc_groups[r["discriminant"]].append(r)

    # Only consider groups with >= 2 members
    group_stats = []
    for disc, members in sorted(disc_groups.items()):
        if len(members) < 2:
            continue

        match_rates = {}
        for p in PRIMES_FP:
            fps = []
            for m in members:
                fp = m["mod_p_fingerprints"].get(str(p))
                if fp is not None:
                    fps.append(tuple(fp))
            if len(fps) < 2:
                continue

            # Within-group match rate
            n_pairs = 0
            n_match = 0
            for i in range(len(fps)):
                for j in range(i + 1, len(fps)):
                    n_pairs += 1
                    if fps[i] == fps[j]:
                        n_match += 1

            match_rate = n_match / n_pairs if n_pairs > 0 else 0

            # Random baseline: probability two random fingerprints match
            # is 1/p^FP_LEN (vanishingly small for p>=2, FP_LEN=50)
            # So enrichment = match_rate / (1/p^FP_LEN)
            # But this is astronomical. Instead use empirical: cross-group rate.
            match_rates[str(p)] = {
                "n_pairs": n_pairs,
                "n_match": n_match,
                "match_rate": round(match_rate, 6),
            }

        avg_density = np.mean([m["prime_fraction"] for m in members])
        avg_enrichment = np.mean([m["enrichment_vs_pnt"] for m in members])
        avg_bm = np.mean([m["bm_recurrence_order"] for m in members
                          if m["bm_recurrence_order"] is not None]) if any(
            m["bm_recurrence_order"] is not None for m in members) else None

        group_stats.append({
            "discriminant": disc,
            "n_members": len(members),
            "avg_prime_fraction": round(float(avg_density), 6),
            "avg_enrichment_vs_pnt": round(float(avg_enrichment), 4),
            "avg_bm_order": round(float(avg_bm), 1) if avg_bm is not None else None,
            "fingerprint_match_rates": match_rates,
        })

    return group_stats, disc_groups


def compute_cross_group_enrichment(results):
    """
    Compare within-discriminant-group fingerprint similarity to
    cross-group (random) baseline. This is the core enrichment test.
    """
    # For each prime p, compute:
    # - within-group: fraction of same-disc pairs sharing a fingerprint
    # - cross-group:  fraction of diff-disc pairs sharing a fingerprint

    disc_groups = defaultdict(list)
    for r in results:
        disc_groups[r["discriminant"]].append(r)

    enrichment_by_p = {}

    for p in PRIMES_FP:
        # Collect (discriminant, fingerprint) pairs
        disc_fp_pairs = []
        for r in results:
            fp = r["mod_p_fingerprints"].get(str(p))
            if fp is not None:
                disc_fp_pairs.append((r["discriminant"], tuple(fp)))

        if len(disc_fp_pairs) < 4:
            continue

        # Sample pairs for efficiency
        n_sample = min(50000, len(disc_fp_pairs) * (len(disc_fp_pairs) - 1) // 2)
        within_match = 0
        within_total = 0
        cross_match = 0
        cross_total = 0

        indices = list(range(len(disc_fp_pairs)))
        for _ in range(n_sample):
            i, j = random.sample(indices, 2)
            d1, fp1 = disc_fp_pairs[i]
            d2, fp2 = disc_fp_pairs[j]
            match = (fp1 == fp2)
            if d1 == d2:
                within_total += 1
                if match:
                    within_match += 1
            else:
                cross_total += 1
                if match:
                    cross_match += 1

        within_rate = within_match / within_total if within_total > 0 else 0
        cross_rate = cross_match / cross_total if cross_total > 0 else 0
        enrichment = (within_rate / cross_rate) if cross_rate > 0 else (
            float('inf') if within_rate > 0 else 1.0)

        enrichment_by_p[str(p)] = {
            "within_match_rate": round(within_rate, 6),
            "cross_match_rate": round(cross_rate, 6),
            "enrichment_ratio": round(enrichment, 2) if enrichment != float('inf') else "inf",
            "within_pairs": within_total,
            "cross_pairs": cross_total,
        }

    return enrichment_by_p


def density_split_analysis(results):
    """
    Split polynomials into high-density and low-density groups.
    Compare their BM orders, fingerprint diversity, and enrichment.
    """
    sorted_by_density = sorted(results, key=lambda r: r["prime_fraction"], reverse=True)
    n = len(sorted_by_density)
    top_quartile = sorted_by_density[:n // 4]
    bottom_quartile = sorted_by_density[3 * n // 4:]

    def group_summary(group, label):
        densities = [r["prime_fraction"] for r in group]
        enrichments = [r["enrichment_vs_pnt"] for r in group]
        bm_orders = [r["bm_recurrence_order"] for r in group
                     if r["bm_recurrence_order"] is not None]

        # Fingerprint diversity: number of distinct fingerprints per prime
        fp_diversity = {}
        for p in PRIMES_FP:
            fps = set()
            for r in group:
                fp = r["mod_p_fingerprints"].get(str(p))
                if fp is not None:
                    fps.add(tuple(fp))
            fp_diversity[str(p)] = len(fps)

        return {
            "label": label,
            "n": len(group),
            "mean_prime_fraction": round(float(np.mean(densities)), 6),
            "mean_enrichment_vs_pnt": round(float(np.mean(enrichments)), 4),
            "mean_bm_order": round(float(np.mean(bm_orders)), 1) if bm_orders else None,
            "median_bm_order": round(float(np.median(bm_orders)), 1) if bm_orders else None,
            "fingerprint_diversity": fp_diversity,
        }

    return {
        "top_quartile": group_summary(top_quartile, "top_25%_density"),
        "bottom_quartile": group_summary(bottom_quartile, "bottom_25%_density"),
    }


def disc_enrichment_correlation(results):
    """
    Compute Spearman correlation between |discriminant| and prime density/enrichment.
    """
    discs = [abs(r["discriminant"]) for r in results]
    densities = [r["prime_fraction"] for r in results]
    enrichments = [r["enrichment_vs_pnt"] for r in results]

    from scipy import stats as sp_stats

    rho_density, p_density = sp_stats.spearmanr(discs, densities)
    rho_enrich, p_enrich = sp_stats.spearmanr(discs, enrichments)

    return {
        "abs_disc_vs_density": {
            "spearman_rho": round(float(rho_density), 4),
            "p_value": float(f"{p_density:.2e}"),
        },
        "abs_disc_vs_enrichment": {
            "spearman_rho": round(float(rho_enrich), 4),
            "p_value": float(f"{p_enrich:.2e}"),
        },
    }


def detrended_enrichment(results):
    """
    Test the 8x enrichment law: after removing the prime-density trend,
    do polynomials with the same discriminant still cluster in mod-p space?

    Detrending: subtract the expected fingerprint given only the polynomial's
    prime density. If discriminant grouping still shows enrichment above
    the detrended baseline, the algebraic DNA law applies.

    Concrete approach: within each discriminant group, compute the residual
    of prime_fraction vs overall mean. Then check if same-discriminant pairs
    have more similar residuals than cross-discriminant pairs (measured as
    |residual_i - residual_j|).
    """
    overall_mean = np.mean([r["prime_fraction"] for r in results])
    for r in results:
        r["_residual"] = r["prime_fraction"] - overall_mean

    disc_groups = defaultdict(list)
    for r in results:
        disc_groups[r["discriminant"]].append(r)

    # Within-group residual distance
    within_dists = []
    cross_dists = []

    disc_list = list(disc_groups.keys())

    for disc in disc_list:
        members = disc_groups[disc]
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                within_dists.append(abs(members[i]["_residual"] - members[j]["_residual"]))

    # Cross-group: sample
    all_results = list(results)
    n_cross_sample = min(50000, len(all_results) * (len(all_results) - 1) // 2)
    for _ in range(n_cross_sample):
        i, j = random.sample(range(len(all_results)), 2)
        if all_results[i]["discriminant"] != all_results[j]["discriminant"]:
            cross_dists.append(abs(all_results[i]["_residual"] - all_results[j]["_residual"]))

    within_mean = float(np.mean(within_dists)) if within_dists else None
    cross_mean = float(np.mean(cross_dists)) if cross_dists else None

    # Enrichment: cross/within (smaller within-dist = more clustered)
    if within_mean and cross_mean and within_mean > 0:
        detrended_ratio = cross_mean / within_mean
    else:
        detrended_ratio = None

    # Also do fingerprint-level detrending:
    # Bin polynomials by density decile, compute within-bin fingerprint
    # match rate, then see if same-discriminant pairs exceed that rate.
    sorted_by_density = sorted(results, key=lambda r: r["prime_fraction"])
    decile_size = max(1, len(sorted_by_density) // 10)
    density_bins = {}
    for idx, r in enumerate(sorted_by_density):
        bin_id = min(idx // decile_size, 9)
        density_bins.setdefault(bin_id, []).append(r)

    fp_detrended = {}
    for p in PRIMES_FP:
        # Within-density-bin match rate (baseline after detrending)
        bin_matches = 0
        bin_pairs = 0
        for bin_id, members in density_bins.items():
            fps = [tuple(m["mod_p_fingerprints"][str(p)])
                   for m in members if m["mod_p_fingerprints"].get(str(p)) is not None]
            for i in range(len(fps)):
                for j in range(i + 1, len(fps)):
                    bin_pairs += 1
                    if fps[i] == fps[j]:
                        bin_matches += 1

        bin_rate = bin_matches / bin_pairs if bin_pairs > 0 else 0

        # Within-discriminant match rate
        disc_matches = 0
        disc_pairs = 0
        for disc, members in disc_groups.items():
            fps = [tuple(m["mod_p_fingerprints"][str(p)])
                   for m in members if m["mod_p_fingerprints"].get(str(p)) is not None]
            for i in range(len(fps)):
                for j in range(i + 1, len(fps)):
                    disc_pairs += 1
                    if fps[i] == fps[j]:
                        disc_matches += 1

        disc_rate = disc_matches / disc_pairs if disc_pairs > 0 else 0

        ratio = (disc_rate / bin_rate) if bin_rate > 0 else (
            float('inf') if disc_rate > 0 else 1.0)

        fp_detrended[str(p)] = {
            "within_disc_rate": round(disc_rate, 6),
            "density_bin_rate": round(bin_rate, 6),
            "detrended_enrichment": round(ratio, 2) if ratio != float('inf') else "inf",
        }

    # Clean up temp field
    for r in results:
        r.pop("_residual", None)

    return {
        "residual_clustering": {
            "within_disc_mean_dist": round(within_mean, 6) if within_mean else None,
            "cross_disc_mean_dist": round(cross_mean, 6) if cross_mean else None,
            "detrended_ratio": round(detrended_ratio, 2) if detrended_ratio else None,
            "interpretation": "ratio > 1 means same-disc polys cluster even after detrending",
        },
        "fingerprint_detrended": fp_detrended,
    }


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print("Generating polynomials...")
    polys = generate_polynomials(N_POLYS)
    print(f"  {len(polys)} polynomials generated")

    print("Analysing each polynomial...")
    results = []
    for i, poly in enumerate(polys):
        r = analyse_polynomial(poly)
        results.append(r)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(polys)} done")

    print("Computing discriminant-group statistics...")
    group_stats, disc_groups = compute_enrichment_by_discriminant(results)

    print("Computing cross-group enrichment...")
    cross_enrichment = compute_cross_group_enrichment(results)

    print("Computing density split analysis...")
    density_split = density_split_analysis(results)

    print("Computing discriminant-enrichment correlation...")
    correlation = disc_enrichment_correlation(results)

    print("Computing detrended enrichment (8x law test)...")
    detrended = detrended_enrichment(results)

    # Summary statistics
    densities = [r["prime_fraction"] for r in results]
    enrichments = [r["enrichment_vs_pnt"] for r in results]
    bm_orders = [r["bm_recurrence_order"] for r in results
                 if r["bm_recurrence_order"] is not None]

    # Top 10 by density
    top10 = sorted(results, key=lambda r: r["prime_fraction"], reverse=True)[:10]
    top10_summary = [{
        "polynomial": f"{r['a']}n^2 + {r['b']}n + {r['c']}",
        "name": r["name"],
        "discriminant": r["discriminant"],
        "prime_fraction": r["prime_fraction"],
        "enrichment_vs_pnt": r["enrichment_vs_pnt"],
        "bm_order": r["bm_recurrence_order"],
    } for r in top10]

    output = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_polynomials": len(results),
            "n_range": "f(1)..f(1000)",
            "fingerprint_primes": PRIMES_FP,
            "fingerprint_length": FP_LEN,
        },
        "summary": {
            "mean_prime_fraction": round(float(np.mean(densities)), 6),
            "std_prime_fraction": round(float(np.std(densities)), 6),
            "median_prime_fraction": round(float(np.median(densities)), 6),
            "mean_enrichment_vs_pnt": round(float(np.mean(enrichments)), 4),
            "mean_bm_order": round(float(np.mean(bm_orders)), 1) if bm_orders else None,
            "median_bm_order": round(float(np.median(bm_orders)), 1) if bm_orders else None,
            "n_unique_discriminants": len(set(r["discriminant"] for r in results)),
        },
        "top_10_by_density": top10_summary,
        "discriminant_group_stats": group_stats,
        "cross_group_enrichment": cross_enrichment,
        "density_split_analysis": density_split,
        "disc_enrichment_correlation": correlation,
        "detrended_enrichment_8x_test": detrended,
        "per_polynomial_results": results,
    }

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults written to {OUT}")
    print(f"\n=== SUMMARY ===")
    print(f"Polynomials analysed: {len(results)}")
    print(f"Mean prime fraction:  {np.mean(densities):.4f}")
    print(f"Mean enrichment/PNT:  {np.mean(enrichments):.4f}")
    print(f"Unique discriminants: {len(set(r['discriminant'] for r in results))}")
    print(f"\nTop 5 by density:")
    for t in top10_summary[:5]:
        print(f"  {t['polynomial']:30s}  D={t['discriminant']:>8d}  "
              f"frac={t['prime_fraction']:.4f}  enrich={t['enrichment_vs_pnt']:.2f}  "
              f"BM={t['bm_order']}")

    print(f"\nCorrelation |D| vs density:    rho={correlation['abs_disc_vs_density']['spearman_rho']:.3f}  "
          f"p={correlation['abs_disc_vs_density']['p_value']:.2e}")
    print(f"Correlation |D| vs enrichment: rho={correlation['abs_disc_vs_enrichment']['spearman_rho']:.3f}  "
          f"p={correlation['abs_disc_vs_enrichment']['p_value']:.2e}")

    dt = detrended["residual_clustering"]
    print(f"\nDetrended clustering ratio: {dt['detrended_ratio']}")
    print(f"  (>1 = same-D polys cluster after removing density trend)")

    print(f"\nDetrended fingerprint enrichment by prime:")
    for p in PRIMES_FP:
        d = detrended["fingerprint_detrended"].get(str(p), {})
        print(f"  p={p:>2d}: disc_rate={d.get('within_disc_rate', 'N/A')}  "
              f"bin_rate={d.get('density_bin_rate', 'N/A')}  "
              f"enrichment={d.get('detrended_enrichment', 'N/A')}")


if __name__ == "__main__":
    main()
