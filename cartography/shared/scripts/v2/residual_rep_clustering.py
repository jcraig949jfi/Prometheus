#!/usr/bin/env python3
"""
Residual Representation Clustering — Beyond Pairwise Congruence
================================================================
For each weight-2, dim-1 newform, extract the mod-ell fingerprint vector
  v_ell(f) = (a_2 mod ell, a_3 mod ell, a_5 mod ell, ..., a_97 mod ell)
at the first 25 primes, then:

1. Cluster forms by exact fingerprint match (shared residual representation)
2. Hamming distance analysis between fingerprints
3. Identify representation "hubs" (most popular fingerprints)
4. Cross-ell mutual information
5. Compare to C07 pairwise congruence results

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
C07_PATH = Path(__file__).resolve().parent / "congruence_graph.json"
OUT_PATH = Path(__file__).resolve().parent / "residual_rep_results.json"

# First 25 primes
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

ELLS = [3, 5, 7]

# Hamming distance sampling limit (all-pairs on 17K is ~150M pairs)
HAMMING_SAMPLE_SIZE = 500_000


def prime_factors(n):
    """Return set of prime factors of n."""
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
    """Load all dim-1 weight-2 newforms from DuckDB."""
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


def compute_fingerprint(traces, level, ell):
    """
    Compute mod-ell fingerprint vector for a form.
    traces[n-1] = a_n (float). We need a_p for prime p.
    Skip primes dividing the level (bad primes).
    Returns: tuple of (a_p mod ell) for good primes, with None for bad primes.
    For clustering, we use a canonical tuple representation.
    """
    bad_primes = prime_factors(level)
    fp = []
    for p in PRIMES_25:
        if p in bad_primes:
            fp.append(-1)  # sentinel for bad prime
        else:
            if p - 1 < len(traces):
                ap = int(round(traces[p - 1]))
                fp.append(ap % ell)
            else:
                fp.append(-1)  # no data
    return tuple(fp)


def cluster_by_fingerprint(forms, ell):
    """
    Group forms by exact fingerprint match.
    Returns: {fingerprint_tuple: [list of labels]}
    """
    clusters = defaultdict(list)
    for label, level, traces in forms:
        fp = compute_fingerprint(traces, level, ell)
        clusters[fp].append(label)
    return dict(clusters)


def cluster_size_distribution(clusters):
    """Compute distribution of cluster sizes."""
    sizes = [len(v) for v in clusters.values()]
    size_counts = Counter(sizes)
    return {
        "total_clusters": len(clusters),
        "size_distribution": dict(sorted(size_counts.items())),
        "singletons": size_counts.get(1, 0),
        "pairs": size_counts.get(2, 0),
        "triples": size_counts.get(3, 0),
        "larger_than_3": sum(c for s, c in size_counts.items() if s > 3),
        "max_cluster_size": max(sizes) if sizes else 0,
        "mean_cluster_size": np.mean(sizes) if sizes else 0,
    }


def find_hubs(clusters, ell, top_n=10):
    """Find the most popular fingerprint vectors."""
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
    hubs = []
    for fp, labels in sorted_clusters[:top_n]:
        # Analyze fingerprint: is it all zeros? all same?
        good_entries = [v for v in fp if v != -1]
        is_zero = all(v == 0 for v in good_entries) if good_entries else False
        unique_vals = set(good_entries)

        hubs.append({
            "fingerprint": list(fp),
            "size": len(labels),
            "labels_sample": labels[:10],
            "is_all_zero": is_zero,
            "unique_residues": len(unique_vals),
            "n_good_primes": len(good_entries),
        })
    return hubs


def hamming_distance(fp1, fp2):
    """
    Compute Hamming distance between two fingerprints.
    Only compare at positions where both have data (not -1).
    Returns (distance, positions_compared).
    """
    dist = 0
    compared = 0
    for a, b in zip(fp1, fp2):
        if a == -1 or b == -1:
            continue
        compared += 1
        if a != b:
            dist += 1
    return dist, compared


def hamming_analysis(forms, ell, n_samples=HAMMING_SAMPLE_SIZE):
    """
    Sample pairs and compute Hamming distance distribution.
    Also find near-matches (distance 1).
    """
    print(f"  [hamming] Computing fingerprints for ell={ell}...")
    fps = []
    labels = []
    for label, level, traces in forms:
        fp = compute_fingerprint(traces, level, ell)
        fps.append(fp)
        labels.append(label)

    n = len(fps)
    total_pairs = n * (n - 1) // 2

    print(f"  [hamming] Sampling {n_samples} of {total_pairs} pairs...")
    rng = np.random.default_rng(42)

    dist_counts = Counter()
    near_matches = []  # distance 1 pairs
    max_near_matches = 200  # cap collection

    for _ in range(n_samples):
        i, j = rng.choice(n, size=2, replace=False)
        d, c = hamming_distance(fps[i], fps[j])
        if c > 0:
            dist_counts[d] += 1
            if d == 1 and len(near_matches) < max_near_matches:
                near_matches.append({
                    "form_a": labels[i],
                    "form_b": labels[j],
                    "hamming_dist": 1,
                    "positions_compared": c,
                })

    return {
        "n_samples": n_samples,
        "total_possible_pairs": total_pairs,
        "distance_distribution": dict(sorted(dist_counts.items())),
        "near_matches_found": len(near_matches),
        "near_matches_sample": near_matches[:20],
        "mean_distance": sum(d * c for d, c in dist_counts.items()) / sum(dist_counts.values()) if dist_counts else 0,
    }


def cross_ell_mutual_information(forms, ell_a, ell_b, clusters_a=None, clusters_b=None):
    """
    Compute mutual information between clustering at ell_a and ell_b.
    Uses the cluster label (fingerprint) as the random variable.

    Also computes the more meaningful "pairwise overlap" metric:
    of all pairs sharing a cluster at ell_a, what fraction also share at ell_b?
    (NMI is inflated by singletons since unique forms trivially "agree".)
    """
    print(f"  [MI] Computing MI between ell={ell_a} and ell={ell_b}...")
    n = len(forms)

    # Assign cluster IDs
    cluster_a_map = {}  # fingerprint -> cluster_id
    cluster_b_map = {}
    labels_a = []
    labels_b = []
    fps_a = {}  # label -> fingerprint
    fps_b = {}

    for label, level, traces in forms:
        fp_a = compute_fingerprint(traces, level, ell_a)
        fp_b = compute_fingerprint(traces, level, ell_b)

        if fp_a not in cluster_a_map:
            cluster_a_map[fp_a] = len(cluster_a_map)
        if fp_b not in cluster_b_map:
            cluster_b_map[fp_b] = len(cluster_b_map)

        labels_a.append(cluster_a_map[fp_a])
        labels_b.append(cluster_b_map[fp_b])
        fps_a[label] = fp_a
        fps_b[label] = fp_b

    # Compute MI using contingency table approach
    joint = Counter()
    for a, b in zip(labels_a, labels_b):
        joint[(a, b)] += 1

    marginal_a = Counter(labels_a)
    marginal_b = Counter(labels_b)

    mi = 0.0
    for (a, b), n_ab in joint.items():
        p_ab = n_ab / n
        p_a = marginal_a[a] / n
        p_b = marginal_b[b] / n
        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * math.log2(p_ab / (p_a * p_b))

    # Normalized MI (divide by min of entropies)
    h_a = -sum((c / n) * math.log2(c / n) for c in marginal_a.values() if c > 0)
    h_b = -sum((c / n) * math.log2(c / n) for c in marginal_b.values() if c > 0)
    nmi = mi / min(h_a, h_b) if min(h_a, h_b) > 0 else 0.0

    # Pairwise overlap: for pairs in same cluster at ell_a, are they in same cluster at ell_b?
    # This is the meaningful cross-ell correlation measure.
    pairwise_agree = 0
    pairwise_total = 0
    if clusters_a is not None:
        for fp_key, lbls in clusters_a.items():
            if len(lbls) < 2:
                continue
            for i in range(len(lbls)):
                for j in range(i + 1, len(lbls)):
                    pairwise_total += 1
                    if fps_b.get(lbls[i]) == fps_b.get(lbls[j]):
                        pairwise_agree += 1

    return {
        "ell_a": ell_a,
        "ell_b": ell_b,
        "MI_bits": round(mi, 6),
        "H_a_bits": round(h_a, 6),
        "H_b_bits": round(h_b, 6),
        "NMI": round(nmi, 6),
        "NMI_note": "inflated by singletons — see pairwise_overlap for true cross-ell correlation",
        "n_clusters_a": len(cluster_a_map),
        "n_clusters_b": len(cluster_b_map),
        "pairwise_overlap": {
            "pairs_in_same_cluster_a": pairwise_total,
            "also_in_same_cluster_b": pairwise_agree,
            "overlap_rate": round(pairwise_agree / pairwise_total, 6) if pairwise_total > 0 else None,
        },
    }


def compare_to_c07(clusters_by_ell, c07_path):
    """
    Verify that every C07 pairwise congruence is captured by our clustering.
    Also find clusters of size > 2 that C07 missed.
    """
    if not c07_path.exists():
        return {"error": "C07 results not found"}

    with open(c07_path) as f:
        c07 = json.load(f)

    results = {}

    for ell_str, c07_data in c07.items():
        ell = int(ell_str)
        if ell not in [3, 5, 7]:
            continue

        clusters = clusters_by_ell.get(ell)
        if clusters is None:
            continue

        # Build reverse lookup: label -> fingerprint
        label_to_fp = {}
        for fp, labels_in_cluster in clusters.items():
            for lbl in labels_in_cluster:
                label_to_fp[lbl] = fp

        # Check each C07 congruence pair
        verified = 0
        missed = 0
        total = len(c07_data.get("congruences", []))

        for cong in c07_data.get("congruences", []):
            fa = cong["form_a"]
            fb = cong["form_b"]
            fp_a = label_to_fp.get(fa)
            fp_b = label_to_fp.get(fb)

            if fp_a is not None and fp_b is not None:
                # Check if same fingerprint (ignoring bad primes)
                same = True
                for va, vb in zip(fp_a, fp_b):
                    if va == -1 or vb == -1:
                        continue
                    if va != vb:
                        same = False
                        break
                if same:
                    verified += 1
                else:
                    missed += 1
            else:
                missed += 1

        # Find clusters > 2 that C07 could miss
        # C07 only checks same-level pairs
        multi_level_clusters = 0
        multi_level_examples = []
        for fp, labels_in_cluster in clusters.items():
            if len(labels_in_cluster) > 1:
                # Extract levels from labels (e.g., "116.2.a.a" -> 116)
                levels_in_cluster = set()
                for lbl in labels_in_cluster:
                    try:
                        levels_in_cluster.add(int(lbl.split(".")[0]))
                    except:
                        pass
                if len(levels_in_cluster) > 1:
                    multi_level_clusters += 1
                    if len(multi_level_examples) < 5:
                        multi_level_examples.append({
                            "fingerprint": list(fp),
                            "size": len(labels_in_cluster),
                            "levels": sorted(levels_in_cluster),
                            "labels": labels_in_cluster[:10],
                        })

        # Clusters of size > 2 (same level or cross-level)
        big_clusters = [(fp, labels_in_cluster) for fp, labels_in_cluster
                        in clusters.items() if len(labels_in_cluster) > 2]

        results[ell] = {
            "c07_total_pairs": total,
            "verified_in_clustering": verified,
            "missed": missed,
            "verification_rate": round(verified / total, 4) if total > 0 else None,
            "clusters_size_gt_2": len(big_clusters),
            "multi_level_clusters": multi_level_clusters,
            "multi_level_examples": multi_level_examples,
            "big_cluster_examples": [
                {"size": len(lbls), "labels_sample": lbls[:10], "fingerprint": list(fp)}
                for fp, lbls in sorted(big_clusters, key=lambda x: len(x[1]), reverse=True)[:5]
            ],
        }

    return results


def main():
    t0 = time.time()
    forms = load_forms()

    results = {
        "metadata": {
            "n_forms": len(forms),
            "primes_used": PRIMES_25,
            "n_primes": len(PRIMES_25),
            "ells_tested": ELLS,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "clustering": {},
        "hubs": {},
        "hamming": {},
        "cross_ell_mi": {},
        "c07_comparison": {},
    }

    clusters_by_ell = {}

    # Phase 1: Clustering per ell
    for ell in ELLS:
        print(f"\n{'='*60}")
        print(f"Phase 1: Clustering at ell={ell}")
        print(f"{'='*60}")
        t1 = time.time()

        clusters = cluster_by_fingerprint(forms, ell)
        clusters_by_ell[ell] = clusters

        dist = cluster_size_distribution(clusters)
        results["clustering"][str(ell)] = dist

        print(f"  Total clusters: {dist['total_clusters']}")
        print(f"  Singletons: {dist['singletons']}")
        print(f"  Pairs: {dist['pairs']}")
        print(f"  Triples: {dist['triples']}")
        print(f"  Larger: {dist['larger_than_3']}")
        print(f"  Max cluster size: {dist['max_cluster_size']}")
        print(f"  Time: {time.time() - t1:.1f}s")

    # Phase 2: Hub analysis
    for ell in ELLS:
        print(f"\n{'='*60}")
        print(f"Phase 2: Hub analysis at ell={ell}")
        print(f"{'='*60}")

        hubs = find_hubs(clusters_by_ell[ell], ell)
        results["hubs"][str(ell)] = hubs

        for i, hub in enumerate(hubs[:5]):
            print(f"  Hub #{i+1}: size={hub['size']}, "
                  f"all_zero={hub['is_all_zero']}, "
                  f"unique_residues={hub['unique_residues']}, "
                  f"good_primes={hub['n_good_primes']}")

    # Phase 3: Hamming distance analysis
    for ell in ELLS:
        print(f"\n{'='*60}")
        print(f"Phase 3: Hamming distance at ell={ell}")
        print(f"{'='*60}")
        t1 = time.time()

        hamming = hamming_analysis(forms, ell)
        results["hamming"][str(ell)] = hamming

        print(f"  Mean Hamming distance: {hamming['mean_distance']:.2f}")
        print(f"  Near-matches (d=1): {hamming['near_matches_found']}")
        # Print distribution summary
        dist = hamming["distance_distribution"]
        for d in sorted(dist.keys())[:15]:
            print(f"    d={d}: {dist[d]} ({100*dist[d]/hamming['n_samples']:.2f}%)")
        print(f"  Time: {time.time() - t1:.1f}s")

    # Phase 4: Cross-ell MI
    print(f"\n{'='*60}")
    print(f"Phase 4: Cross-ell mutual information")
    print(f"{'='*60}")

    for ell_a, ell_b in combinations(ELLS, 2):
        mi_result = cross_ell_mutual_information(
            forms, ell_a, ell_b,
            clusters_a=clusters_by_ell.get(ell_a),
            clusters_b=clusters_by_ell.get(ell_b),
        )
        key = f"{ell_a}_vs_{ell_b}"
        results["cross_ell_mi"][key] = mi_result
        print(f"  ell={ell_a} vs ell={ell_b}: MI={mi_result['MI_bits']:.4f} bits, "
              f"NMI={mi_result['NMI']:.4f}")

    # Phase 5: Compare to C07
    print(f"\n{'='*60}")
    print(f"Phase 5: Comparison to C07 pairwise congruences")
    print(f"{'='*60}")

    c07_comp = compare_to_c07(clusters_by_ell, C07_PATH)
    results["c07_comparison"] = c07_comp

    for ell, comp in c07_comp.items():
        if isinstance(comp, dict) and "c07_total_pairs" in comp:
            print(f"  ell={ell}: {comp['verified_in_clustering']}/{comp['c07_total_pairs']} "
                  f"verified ({comp['verification_rate']})")
            print(f"    Clusters size>2: {comp['clusters_size_gt_2']}")
            print(f"    Multi-level clusters: {comp['multi_level_clusters']}")

    # Save results
    # Convert any numpy types for JSON serialization
    def json_safe(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Not JSON serializable: {type(obj)}")

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2, default=json_safe)

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"Done in {elapsed:.1f}s. Results saved to {OUT_PATH}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
