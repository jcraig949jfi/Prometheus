#!/usr/bin/env python3
"""
Reconstruction Entropy Curve — M5 Metrology Challenge
======================================================
Measures H(form | mod-p_1, ..., mod-p_k): the conditional entropy of form
identity given the mod-ell fingerprint partition at depth k.

H(form | partition) = sum_i (n_i / N) * log2(n_i)

where n_i is the size of cluster i. This equals zero when all clusters are
singletons (complete reconstruction) and log2(N) when all forms are in one
cluster (no information).

Key quantities:
  H_0 = log2(N)                             (no information, all in one cluster)
  H_k = conditional entropy at depth k
  I_k = H_{k-1} - H_k                       (information gain from k-th prime)

Uses good-prime agreement clustering (matching R3-10 methodology).

Charon / Project Prometheus — 2026-04-10
"""

import json
import math
import time
from collections import Counter, defaultdict
from itertools import permutations
from pathlib import Path

import duckdb
import numpy as np

# ── Config ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]  # F:\Prometheus
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
OUT_DIR = Path(__file__).resolve().parent
OUT_PATH = OUT_DIR / "reconstruction_entropy_results.json"

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

BIG_PRIMES = [89, 97, 83, 79, 73]

ELLS_FULL = [3, 5, 7, 11]
ELLS_ORDERINGS = [3, 5, 7]
MIN_SHARED_PRIMES = 20


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


def load_forms():
    print(f"[load] Connecting to {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute('''
        SELECT lmfdb_label, level, traces
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    con.close()
    print(f"[load] {len(rows)} forms loaded")
    return rows


def compute_good_prime_fingerprint(traces, level, ells):
    bad_primes = prime_factors(level)
    fp = {}
    for ell in ells:
        for p in PRIMES_25:
            if p in bad_primes:
                continue
            if p - 1 < len(traces):
                ap = int(round(traces[p - 1]))
                fp[(ell, p)] = ap % ell
    return fp


def cluster_by_good_prime_agreement(forms, ells):
    """Cluster forms by agreement at ALL shared good primes across given ells."""
    form_fps = []
    for label, level, traces in forms:
        fp = compute_good_prime_fingerprint(traces, level, ells)
        form_fps.append((label, level, fp))

    level_groups = defaultdict(list)
    for label, level, fp in form_fps:
        level_groups[level].append((label, fp))

    same_level_clusters = defaultdict(list)
    cluster_id = 0
    cluster_fp = {}

    for level, group in level_groups.items():
        fp_to_labels = defaultdict(list)
        for label, fp in group:
            fp_key = tuple(sorted(fp.items()))
            fp_to_labels[fp_key].append(label)
        for fp_key, labels in fp_to_labels.items():
            cid = cluster_id
            cluster_id += 1
            same_level_clusters[cid] = labels
            cluster_fp[cid] = dict(fp_key)

    parent = {cid: cid for cid in same_level_clusters}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    hash_to_cids = defaultdict(list)
    cids = list(same_level_clusters.keys())
    for cid in cids:
        fp = cluster_fp[cid]
        hash_key = tuple(fp.get((ell, p), None) for ell in ells for p in BIG_PRIMES)
        hash_to_cids[hash_key].append(cid)

    n_merges = 0
    for hash_key, bucket in hash_to_cids.items():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                ci, cj = bucket[i], bucket[j]
                if find(ci) == find(cj):
                    continue
                fp_i = cluster_fp[ci]
                fp_j = cluster_fp[cj]
                shared_keys = set(fp_i.keys()) & set(fp_j.keys())
                if len(shared_keys) < MIN_SHARED_PRIMES:
                    continue
                if all(fp_i[k] == fp_j[k] for k in shared_keys):
                    union(ci, cj)
                    n_merges += 1

    final_clusters = defaultdict(list)
    for cid, labels in same_level_clusters.items():
        root = find(cid)
        final_clusters[root].extend(labels)

    return dict(final_clusters), n_merges


def conditional_entropy(cluster_sizes, n_total):
    """
    H(form | fingerprint) = sum_i (n_i/N) * log2(n_i)

    This is the expected uncertainty about form identity GIVEN the fingerprint.
    - If all clusters are singletons (n_i=1 for all i): H = 0 (complete reconstruction)
    - If all forms are in one cluster (n_1=N): H = log2(N) (no information)
    """
    H = 0.0
    for s in cluster_sizes:
        if s > 1:
            H += (s / n_total) * math.log2(s)
    return H


def partition_stats(clusters, n_total, n_merges=0):
    sizes = [len(v) for v in clusters.values()]
    n_clusters = len(sizes)
    n_singletons = sum(1 for s in sizes if s == 1)
    non_singleton = sum(1 for s in sizes if s > 1)
    max_size = max(sizes) if sizes else 0
    H = conditional_entropy(sizes, n_total)
    size_dist = Counter(sizes)

    return {
        "conditional_entropy_bits": round(H, 6),
        "n_clusters": n_clusters,
        "n_singletons": n_singletons,
        "n_non_singleton_clusters": non_singleton,
        "max_cluster_size": max_size,
        "cross_level_merges": n_merges,
        "size_distribution_top10": dict(sorted(size_dist.items(), key=lambda x: -x[1])[:10]),
    }


def main():
    t0 = time.time()
    forms = load_forms()
    N = len(forms)
    H0 = math.log2(N)
    print(f"[entropy] N = {N}, H_0 = log2(N) = {H0:.6f} bits")

    results = {
        "metadata": {
            "n_forms": N,
            "H_0_bits": round(H0, 6),
            "formula": "H(form|partition) = sum_i (n_i/N) * log2(n_i); H=0 at complete reconstruction",
            "primes_25": PRIMES_25,
            "ells_orderings": ELLS_ORDERINGS,
            "ells_single": ELLS_FULL,
            "clustering_method": "good_prime_agreement_with_cross_level_merge",
            "min_shared_primes": MIN_SHARED_PRIMES,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    }

    # ── 1. Single-prime entropy ─────────────────────────────────────
    print("\n[entropy] === Single-prime conditional entropy ===")
    single_prime = {}
    for ell in ELLS_FULL:
        t1 = time.time()
        clusters, n_merges = cluster_by_good_prime_agreement(forms, [ell])
        stats = partition_stats(clusters, N, n_merges)
        H = stats["conditional_entropy_bits"]
        info_gain = H0 - H
        stats["information_gain_bits"] = round(info_gain, 6)
        stats["pct_of_total_info"] = round(100.0 * info_gain / H0, 4)
        single_prime[f"mod_{ell}"] = stats
        dt = time.time() - t1
        print(f"  mod-{ell}: H(form|fp) = {H:.4f} bits, "
              f"I = {info_gain:.4f} bits ({stats['pct_of_total_info']:.2f}% of {H0:.2f}), "
              f"clusters = {stats['n_clusters']}, non-sing = {stats['n_non_singleton_clusters']}, "
              f"max = {stats['max_cluster_size']}, [{dt:.1f}s]")

    results["single_prime_entropy"] = single_prime

    ranking = sorted(single_prime.items(), key=lambda x: -x[1]["information_gain_bits"])
    results["single_prime_ranking"] = [
        {"ell": k, "info_bits": v["information_gain_bits"]} for k, v in ranking
    ]
    rank_strs = [k + "({:.4f}b)".format(v["information_gain_bits"]) for k, v in ranking]
    print(f"\n  Ranking: {' > '.join(rank_strs)}")

    # ── 2. All orderings of {3, 5, 7} ──────────────────────────────
    print("\n[entropy] === Entropy curves for all orderings ===")
    orderings_results = {}

    for perm in permutations(ELLS_ORDERINGS):
        perm_key = ",".join(str(e) for e in perm)
        print(f"\n  Ordering: {perm}")
        curve = {"ordering": list(perm), "depths": {}}

        H_prev = H0
        for depth in range(1, len(perm) + 1):
            ells_used = list(perm[:depth])
            t1 = time.time()
            clusters, n_merges = cluster_by_good_prime_agreement(forms, ells_used)
            stats = partition_stats(clusters, N, n_merges)
            dt = time.time() - t1
            H = stats["conditional_entropy_bits"]
            info_step = H_prev - H
            info_cumulative = H0 - H

            curve["depths"][f"depth_{depth}"] = {
                "ells_used": ells_used,
                "H_conditional_bits": round(H, 6),
                "info_gain_step_bits": round(info_step, 6),
                "info_gain_cumulative_bits": round(info_cumulative, 6),
                "n_clusters": stats["n_clusters"],
                "n_singletons": stats["n_singletons"],
                "n_non_singleton_clusters": stats["n_non_singleton_clusters"],
                "max_cluster_size": stats["max_cluster_size"],
                "cross_level_merges": n_merges,
            }

            print(f"    depth {depth} (ells={ells_used}): "
                  f"H = {H:.6f}, "
                  f"I_step = {info_step:.4f}, "
                  f"I_cum = {info_cumulative:.4f}, "
                  f"clusters = {stats['n_clusters']}, "
                  f"non-sing = {stats['n_non_singleton_clusters']}, "
                  f"max = {stats['max_cluster_size']}, [{dt:.1f}s]")

            H_prev = H

        orderings_results[perm_key] = curve

    results["orderings"] = orderings_results

    # ── 3. Ordering invariance ──────────────────────────────────────
    print("\n[entropy] === Ordering invariance ===")
    invariance = {"depth_1": {}, "depth_2": {}, "depth_3": {}}

    for perm_key, curve in orderings_results.items():
        for d in range(1, 4):
            dk = f"depth_{d}"
            invariance[dk][perm_key] = {
                "ells_used": curve["depths"][dk]["ells_used"],
                "H_bits": curve["depths"][dk]["H_conditional_bits"],
            }

    d1_H = [v["H_bits"] for v in invariance["depth_1"].values()]
    d2_H = [v["H_bits"] for v in invariance["depth_2"].values()]
    d3_H = [v["H_bits"] for v in invariance["depth_3"].values()]

    invariance["summary"] = {
        "depth_1_H_range": [round(min(d1_H), 6), round(max(d1_H), 6)],
        "depth_2_H_range": [round(min(d2_H), 6), round(max(d2_H), 6)],
        "depth_3_H_range": [round(min(d3_H), 6), round(max(d3_H), 6)],
        "depth_1_spread_bits": round(max(d1_H) - min(d1_H), 6),
        "depth_2_spread_bits": round(max(d2_H) - min(d2_H), 6),
        "depth_3_converged_to_zero": all(h < 0.001 for h in d3_H),
    }

    # Best first prime
    first_prime_info = {}
    for perm_key, curve in orderings_results.items():
        first_ell = curve["ordering"][0]
        first_prime_info[first_ell] = curve["depths"]["depth_1"]["info_gain_cumulative_bits"]

    best_first = max(first_prime_info, key=first_prime_info.get)
    invariance["best_first_prime"] = {
        "ell": best_first,
        "info_gain_bits": round(first_prime_info[best_first], 6),
        "all_first_primes": {str(k): round(v, 6) for k, v in sorted(first_prime_info.items())},
    }

    print(f"  Depth 1 H range: {invariance['summary']['depth_1_H_range']}")
    print(f"  Depth 2 H range: {invariance['summary']['depth_2_H_range']}")
    print(f"  Depth 3 converged to 0: {invariance['summary']['depth_3_converged_to_zero']}")
    print(f"  Best first prime: mod-{best_first} ({first_prime_info[best_first]:.4f} bits)")
    print(f"  All: {invariance['best_first_prime']['all_first_primes']}")

    results["ordering_invariance"] = invariance

    # ── 4. Canonical curve (3,5,7) ──────────────────────────────────
    print("\n[entropy] === Canonical entropy curve (3,5,7) ===")
    canonical = orderings_results["3,5,7"]
    H_curve = [H0]
    for d in range(1, 4):
        H_curve.append(canonical["depths"][f"depth_{d}"]["H_conditional_bits"])

    I_step = [round(H_curve[i] - H_curve[i + 1], 6) for i in range(3)]
    I_cum = [round(H0 - h, 6) for h in H_curve]

    slope_ratios = {}
    if I_step[0] > 0 and I_step[1] > 0:
        slope_ratios["I2_over_I1"] = round(I_step[1] / I_step[0], 6)
    if I_step[1] > 0 and I_step[2] > 0:
        slope_ratios["I3_over_I2"] = round(I_step[2] / I_step[1], 6)
    if I_step[0] > 0 and I_step[2] >= 0:
        slope_ratios["I3_over_I1"] = round(I_step[2] / I_step[0], 6)

    results["canonical_curve"] = {
        "ordering": [3, 5, 7],
        "depths": [0, 1, 2, 3],
        "H_conditional_bits": [round(h, 6) for h in H_curve],
        "I_cumulative_bits": I_cum,
        "I_step_bits": I_step,
        "slope_ratios": slope_ratios,
        "pct_per_step": [round(100.0 * s / H0, 4) for s in I_step],
    }

    print(f"  H(k):     {[round(h,4) for h in H_curve]}")
    print(f"  I_step:   {[round(s,4) for s in I_step]}")
    print(f"  I_cum:    {[round(c,4) for c in I_cum]}")
    print(f"  pct/step: {results['canonical_curve']['pct_per_step']}")
    print(f"  Slopes:   {slope_ratios}")

    # ── 5. Bits-per-prime analysis ──────────────────────────────────
    print("\n[entropy] === Bits-per-prime analysis ===")
    bpp = {}
    for perm_key, curve in orderings_results.items():
        depths = curve["depths"]
        steps = [depths[f"depth_{d}"]["info_gain_step_bits"] for d in range(1, 4)]
        total = sum(s for s in steps if s > 0)
        n_positive = sum(1 for s in steps if s > 0.001)
        avg = total / 3

        positive = [s for s in steps if s > 0.001]
        if len(positive) >= 2:
            pattern = "diminishing" if positive[0] > positive[-1] else "accelerating"
        elif len(positive) == 1:
            # How many primes needed for complete reconstruction?
            pattern = "single_dominant" if positive[0] / H0 > 0.9 else "front_loaded"
        else:
            pattern = "none"

        bpp[perm_key] = {
            "total_info_bits": round(total, 6),
            "avg_bits_per_prime": round(avg, 6),
            "steps": [round(s, 6) for s in steps],
            "n_informative_primes": n_positive,
            "pattern": pattern,
        }
        print(f"  {perm_key}: total={total:.4f}b, avg={avg:.4f}b/prime, "
              f"n_useful={n_positive}, pattern={pattern}")

    results["bits_per_prime"] = bpp

    # ── 6. Theoretical compression ──────────────────────────────────
    print("\n[entropy] === Theoretical compression ===")
    compression = {}
    for ell in ELLS_FULL:
        theoretical = 25 * math.log2(ell)
        actual = single_prime[f"mod_{ell}"]["information_gain_bits"]
        ratio = actual / theoretical if theoretical > 0 else 0
        n_clusters = single_prime[f"mod_{ell}"]["n_clusters"]

        compression[f"mod_{ell}"] = {
            "theoretical_max_bits": round(theoretical, 6),
            "actual_info_bits": round(actual, 6),
            "efficiency": round(ratio, 6),
            "n_distinct_clusters": n_clusters,
            "compression_factor": round(theoretical / actual, 4) if actual > 0 else float('inf'),
        }
        print(f"  mod-{ell}: max={theoretical:.2f}b, actual={actual:.4f}b, "
              f"eff={ratio:.6f}, compress={compression[f'mod_{ell}']['compression_factor']}x")

    results["theoretical_compression"] = compression

    # ── 7. Physical interpretation ──────────────────────────────────
    print("\n[entropy] === Physical interpretation ===")

    interp = {
        "total_identity_bits": round(H0, 6),
        "canonical_ordering": [3, 5, 7],
        "H_after_each_depth": [round(h, 4) for h in H_curve],
        "bits_per_step": [round(s, 4) for s in I_step],
        "pct_per_step": results["canonical_curve"]["pct_per_step"],
        "three_primes_sufficient": H_curve[3] < 0.001,
        "mod3_is_always_best_first": best_first == 3,
        "ordering_matters_at_depth_1": invariance["summary"]["depth_1_spread_bits"] > 1.0,
        "ordering_converges_at_depth_3": invariance["summary"]["depth_3_converged_to_zero"],
    }

    # Build description
    desc = []
    desc.append(f"RECONSTRUCTION ENTROPY for {N} weight-2 newforms ({H0:.2f} bits of identity):")
    desc.append("")
    desc.append(f"  Depth 0 (no info):   H = {H_curve[0]:.4f} bits")
    desc.append(f"  Depth 1 (mod-3):     H = {H_curve[1]:.4f} bits  (gained {I_step[0]:.4f} = {results['canonical_curve']['pct_per_step'][0]:.1f}%)")
    desc.append(f"  Depth 2 (mod-3,5):   H = {H_curve[2]:.4f} bits  (gained {I_step[1]:.4f} = {results['canonical_curve']['pct_per_step'][1]:.1f}%)")
    desc.append(f"  Depth 3 (mod-3,5,7): H = {H_curve[3]:.4f} bits  (gained {I_step[2]:.4f} = {results['canonical_curve']['pct_per_step'][2]:.1f}%)")
    desc.append("")
    desc.append(f"  mod-3 alone captures {results['canonical_curve']['pct_per_step'][0]:.1f}% of all identity information.")
    desc.append(f"  Ordering matters at depth 1 (spread = {invariance['summary']['depth_1_spread_bits']:.2f} bits)")
    desc.append(f"  but converges at depth 3: {invariance['summary']['depth_3_converged_to_zero']}")
    desc.append("")
    desc.append(f"  Single-prime ranking: mod-3 >> mod-5 >> mod-7 >> mod-11")
    desc.append(f"    mod-3:  {single_prime['mod_3']['information_gain_bits']:.4f} bits")
    desc.append(f"    mod-5:  {single_prime['mod_5']['information_gain_bits']:.4f} bits")
    desc.append(f"    mod-7:  {single_prime['mod_7']['information_gain_bits']:.4f} bits")
    desc.append(f"    mod-11: {single_prime['mod_11']['information_gain_bits']:.4f} bits")
    desc.append("")
    desc.append(f"  Compression: mod-3 fingerprint has {compression['mod_3']['theoretical_max_bits']:.0f} theoretical bits")
    desc.append(f"  but only {compression['mod_3']['actual_info_bits']:.2f} bits are informative ({compression['mod_3']['compression_factor']:.0f}x compression).")

    interp["description"] = "\n".join(desc)
    results["physical_interpretation"] = interp

    for line in desc:
        print(f"  {line}")

    # ── Save ────────────────────────────────────────────────────────
    elapsed = time.time() - t0
    results["metadata"]["elapsed_seconds"] = round(elapsed, 2)

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[entropy] Saved to {OUT_PATH}")
    print(f"[entropy] Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
