"""
Sleeper Clustering — Cluster OEIS Sleeping Beauty sequences in entropy-space.
===============================================================================
Identifies sleeping beauties (high entropy, low cross-reference degree) and
clusters them by a 10-dimensional feature vector capturing internal structure,
NOT connectivity.  Uses DBSCAN and k-means for comparison.

Usage:  python sleeper_clustering.py
Output: cartography/convergence/data/sleeper_clusters.json
"""

import json
import math
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Imports from search_engine
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from search_engine import (
    _load_oeis,
    _load_oeis_names,
    _load_oeis_crossrefs,
    _oeis_cache,
    _oeis_names_cache,
    _oeis_xref_cache,
    _oeis_xref_reverse,
    REPO,
)

# Output path
OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
OUTPUT_FILE = OUTPUT_DIR / "sleeper_clusters.json"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
ENTROPY_THRESHOLD = 3.91       # median; >= this qualifies
MAX_XREF_DEGREE = 2            # total degree <= 2
MAX_SLEEPERS = 20_000          # cap for initial run
MIN_TERMS = 8                  # need enough terms for features
DBSCAN_EPS = 1.5
DBSCAN_MIN_SAMPLES = 5
KMEANS_K = 20
SEED = 42


# ---------------------------------------------------------------------------
# Feature computation
# ---------------------------------------------------------------------------

def _shannon_entropy(values):
    """Shannon entropy (bits) of a discrete distribution."""
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)


def _is_prime(n):
    """Simple primality test for moderate integers. Skip huge numbers."""
    if n < 2:
        return False
    if n > 10_000_000:
        # Skip trial division for very large numbers — too slow at scale
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def _is_perfect_square(n):
    if n < 0:
        return False
    r = int(math.isqrt(n))
    return r * r == n


def compute_feature_vector(terms):
    """Compute the 10-dimensional feature vector for a sequence.

    Dimensions:
      0  Shannon entropy of first differences
      1  Growth complexity (std of consecutive ratios, positive seqs)
      2  Mean absolute first difference
      3  Fraction of terms that are prime
      4  Fraction of terms that are even
      5  Fraction of terms that are perfect squares
      6  Dynamic range (log10(max / min_nonzero))
      7  Number of sign changes in first differences (oscillation)
      8  mod-2 bias: |count_even - count_odd| / n
      9  mod-3 entropy: Shannon entropy of terms mod 3
    """
    t = terms[:50]  # cap at 50 terms for consistency
    n = len(t)
    if n < 3:
        return None

    diffs = [t[i + 1] - t[i] for i in range(n - 1)]

    # 0: Shannon entropy of first differences
    feat_0 = _shannon_entropy(diffs)

    # 1: Growth complexity — std of consecutive ratios (for positive sequences)
    ratios = []
    for i in range(n - 1):
        if t[i] != 0:
            ratios.append(t[i + 1] / t[i])
    if len(ratios) >= 2:
        feat_1 = float(np.std(ratios))
        # Clip extreme outliers
        feat_1 = min(feat_1, 1e6)
    else:
        feat_1 = 0.0

    # 2: Mean absolute first difference
    feat_2 = float(np.mean([abs(d) for d in diffs]))
    feat_2 = min(feat_2, 1e12)  # clip

    # 3: Fraction of terms that are prime
    feat_3 = sum(1 for x in t if _is_prime(abs(x))) / n

    # 4: Fraction of terms that are even
    feat_4 = sum(1 for x in t if x % 2 == 0) / n

    # 5: Fraction of terms that are perfect squares
    feat_5 = sum(1 for x in t if _is_perfect_square(abs(x))) / n

    # 6: Dynamic range (log-scaled)
    abs_terms = [abs(x) for x in t if x != 0]
    if abs_terms:
        max_t = max(abs_terms)
        min_t = min(abs_terms)
        if min_t > 0:
            feat_6 = math.log10(max_t / min_t + 1)
        else:
            feat_6 = 0.0
    else:
        feat_6 = 0.0
    feat_6 = min(feat_6, 30.0)  # clip extreme

    # 7: Number of sign changes in first differences (oscillation count)
    sign_changes = 0
    for i in range(len(diffs) - 1):
        if diffs[i] * diffs[i + 1] < 0:
            sign_changes += 1
    feat_7 = float(sign_changes)

    # 8: mod-2 bias: |count_even - count_odd| / n
    n_even = sum(1 for x in t if x % 2 == 0)
    n_odd = n - n_even
    feat_8 = abs(n_even - n_odd) / n

    # 9: mod-3 entropy
    mod3_vals = [x % 3 for x in t]
    feat_9 = _shannon_entropy(mod3_vals)

    return [feat_0, feat_1, feat_2, feat_3, feat_4, feat_5, feat_6, feat_7, feat_8, feat_9]


FEATURE_NAMES = [
    "diff_entropy",
    "growth_complexity",
    "mean_abs_diff",
    "frac_prime",
    "frac_even",
    "frac_square",
    "dynamic_range_log",
    "oscillation_count",
    "mod2_bias",
    "mod3_entropy",
]


# ---------------------------------------------------------------------------
# Sleeper identification
# ---------------------------------------------------------------------------

def identify_sleepers():
    """Find all sleeping beauties: entropy >= threshold, degree <= max."""
    _load_oeis()
    _load_oeis_names()
    _load_oeis_crossrefs()

    print(f"\n  [Sleeper] OEIS cache: {len(_oeis_cache):,} sequences")
    print(f"  [Sleeper] Xref cache: {len(_oeis_xref_cache):,} source nodes")

    sleepers = []
    skipped_short = 0
    skipped_degree = 0
    skipped_entropy = 0

    for seq_id, terms in _oeis_cache.items():
        if len(terms) < MIN_TERMS:
            skipped_short += 1
            continue

        # Total cross-reference degree
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        total_deg = out_deg + in_deg
        if total_deg > MAX_XREF_DEGREE:
            skipped_degree += 1
            continue

        # Shannon entropy of first differences
        diffs = [terms[i + 1] - terms[i] for i in range(min(len(terms) - 1, 30))]
        if not diffs:
            skipped_short += 1
            continue
        entropy = _shannon_entropy(diffs)
        if entropy < ENTROPY_THRESHOLD:
            skipped_entropy += 1
            continue

        sleepers.append((seq_id, terms, entropy, total_deg))

    print(f"  [Sleeper] Skipped: {skipped_short:,} short, {skipped_degree:,} high-degree, {skipped_entropy:,} low-entropy")
    print(f"  [Sleeper] Found {len(sleepers):,} sleeping beauties")

    return sleepers


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    random.seed(SEED)
    np.random.seed(SEED)

    # Step 1: Identify sleepers
    sleepers = identify_sleepers()
    if not sleepers:
        print("  [Sleeper] No sleeping beauties found. Exiting.")
        return

    # Step 2: Sample if too many
    if len(sleepers) > MAX_SLEEPERS:
        print(f"  [Sleeper] Sampling {MAX_SLEEPERS:,} from {len(sleepers):,} sleepers")
        sleepers = random.sample(sleepers, MAX_SLEEPERS)

    # Step 3: Compute feature vectors
    print(f"\n  [Features] Computing 10D feature vectors for {len(sleepers):,} sleepers...")
    seq_ids = []
    features = []
    meta = {}  # seq_id -> {entropy, degree, name, first_terms}

    for seq_id, terms, entropy, degree in sleepers:
        fv = compute_feature_vector(terms)
        if fv is None:
            continue
        # Skip rows with NaN/Inf
        if any(math.isnan(v) or math.isinf(v) for v in fv):
            continue
        seq_ids.append(seq_id)
        features.append(fv)
        meta[seq_id] = {
            "entropy": round(entropy, 4),
            "degree": degree,
            "name": _oeis_names_cache.get(seq_id, ""),
            "first_terms": terms[:10],
        }

    X = np.array(features, dtype=np.float64)
    print(f"  [Features] Valid feature vectors: {X.shape[0]:,} x {X.shape[1]}")

    # Step 4: Normalize (z-score)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Step 5: DBSCAN
    print(f"\n  [DBSCAN] Running with eps={DBSCAN_EPS}, min_samples={DBSCAN_MIN_SAMPLES}...")
    db = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES, n_jobs=-1)
    db_labels = db.fit_predict(X_scaled)
    n_db_clusters = len(set(db_labels) - {-1})
    n_noise = int(np.sum(db_labels == -1))
    print(f"  [DBSCAN] Clusters: {n_db_clusters}, Noise points: {n_noise:,}")

    # Step 6: KMeans
    print(f"\n  [KMeans] Running with k={KMEANS_K}...")
    km = KMeans(n_clusters=KMEANS_K, random_state=SEED, n_init=10)
    km_labels = km.fit_predict(X_scaled)

    # Step 7: Build report
    print("\n  [Report] Building cluster report...")
    report = {
        "parameters": {
            "entropy_threshold": ENTROPY_THRESHOLD,
            "max_xref_degree": MAX_XREF_DEGREE,
            "max_sleepers": MAX_SLEEPERS,
            "dbscan_eps": DBSCAN_EPS,
            "dbscan_min_samples": DBSCAN_MIN_SAMPLES,
            "kmeans_k": KMEANS_K,
            "n_features": len(FEATURE_NAMES),
            "feature_names": FEATURE_NAMES,
        },
        "summary": {
            "total_sleepers": len(seq_ids),
            "dbscan_clusters": n_db_clusters,
            "dbscan_noise": n_noise,
            "dbscan_noise_fraction": round(n_noise / len(seq_ids), 4) if seq_ids else 0,
            "kmeans_clusters": KMEANS_K,
        },
        "feature_stats": {},
        "dbscan_clusters": [],
        "kmeans_clusters": [],
    }

    # Feature stats (before scaling)
    for i, name in enumerate(FEATURE_NAMES):
        col = X[:, i]
        report["feature_stats"][name] = {
            "mean": round(float(np.mean(col)), 4),
            "std": round(float(np.std(col)), 4),
            "min": round(float(np.min(col)), 4),
            "max": round(float(np.max(col)), 4),
            "median": round(float(np.median(col)), 4),
        }

    # DBSCAN cluster details
    db_cluster_ids = sorted(set(db_labels) - {-1})
    size_dist = Counter(int(l) for l in db_labels if l != -1)

    for cid in db_cluster_ids:
        mask = db_labels == cid
        cluster_size = int(mask.sum())
        cluster_seqs = [seq_ids[i] for i in range(len(seq_ids)) if mask[i]]

        centroid = X_scaled[mask].mean(axis=0)
        centroid_raw = X[mask].mean(axis=0)

        cluster_info = {
            "cluster_id": int(cid),
            "size": cluster_size,
            "centroid_raw": {FEATURE_NAMES[j]: round(float(centroid_raw[j]), 4) for j in range(len(FEATURE_NAMES))},
            "centroid_scaled": {FEATURE_NAMES[j]: round(float(centroid[j]), 4) for j in range(len(FEATURE_NAMES))},
        }

        # For clusters with 10+ members, add examples and family guess
        if cluster_size >= 10:
            examples = random.sample(cluster_seqs, min(3, len(cluster_seqs)))
            cluster_info["examples"] = [
                {"id": sid, "name": meta[sid]["name"], "first_terms": meta[sid]["first_terms"]}
                for sid in examples
            ]
            # Heuristic family classification based on centroid features
            cluster_info["family_guess"] = _guess_family(centroid_raw)
        else:
            examples = cluster_seqs[:3]
            cluster_info["examples"] = [
                {"id": sid, "name": meta[sid]["name"], "first_terms": meta[sid]["first_terms"]}
                for sid in examples
            ]

        report["dbscan_clusters"].append(cluster_info)

    # Size distribution summary
    if size_dist:
        sizes = sorted(size_dist.values())
        report["summary"]["dbscan_size_distribution"] = {
            "min": min(sizes),
            "max": max(sizes),
            "mean": round(sum(sizes) / len(sizes), 1),
            "median": sizes[len(sizes) // 2],
            "sizes": dict(sorted(size_dist.items())),
        }

    # KMeans cluster details
    for cid in range(KMEANS_K):
        mask = km_labels == cid
        cluster_size = int(mask.sum())
        cluster_seqs = [seq_ids[i] for i in range(len(seq_ids)) if mask[i]]

        centroid_raw = X[mask].mean(axis=0)

        cluster_info = {
            "cluster_id": int(cid),
            "size": cluster_size,
            "centroid_raw": {FEATURE_NAMES[j]: round(float(centroid_raw[j]), 4) for j in range(len(FEATURE_NAMES))},
        }

        if cluster_size >= 10:
            examples = random.sample(cluster_seqs, min(3, len(cluster_seqs)))
            cluster_info["examples"] = [
                {"id": sid, "name": meta[sid]["name"], "first_terms": meta[sid]["first_terms"]}
                for sid in examples
            ]
            cluster_info["family_guess"] = _guess_family(centroid_raw)

        report["kmeans_clusters"].append(cluster_info)

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  [Output] Saved to {OUTPUT_FILE}")

    # Console summary
    elapsed = time.time() - t0
    print(f"\n{'='*70}")
    print(f"  SLEEPER CLUSTERING REPORT")
    print(f"{'='*70}")
    print(f"  Total sleepers analyzed:     {len(seq_ids):,}")
    print(f"  DBSCAN clusters:             {n_db_clusters}")
    print(f"  DBSCAN noise points:         {n_noise:,} ({100*n_noise/len(seq_ids):.1f}%)")
    print(f"  KMeans clusters:             {KMEANS_K}")
    print(f"  Time elapsed:                {elapsed:.1f}s")
    print(f"{'='*70}")

    if n_db_clusters > 0:
        print(f"\n  DBSCAN clusters with 10+ members:")
        for ci in report["dbscan_clusters"]:
            if ci["size"] >= 10:
                fg = ci.get("family_guess", "unknown")
                print(f"    Cluster {ci['cluster_id']:3d}: {ci['size']:5d} members — {fg}")
                for ex in ci.get("examples", []):
                    print(f"      {ex['id']}: {ex['name'][:60]}")

    print(f"\n  KMeans largest clusters:")
    km_sorted = sorted(report["kmeans_clusters"], key=lambda c: -c["size"])
    for ci in km_sorted[:10]:
        fg = ci.get("family_guess", "unknown")
        print(f"    Cluster {ci['cluster_id']:3d}: {ci['size']:5d} members — {fg}")


def _guess_family(centroid_raw):
    """Heuristic family classification based on centroid feature values.

    This is a rough classifier — it checks dominant features in the centroid
    to suggest what mathematical family the cluster might represent.
    """
    diff_ent, growth, mean_diff, frac_prime, frac_even, frac_sq, dyn_range, osc, mod2_bias, mod3_ent = centroid_raw

    tags = []

    # High prime fraction suggests prime-related
    if frac_prime > 0.4:
        tags.append("prime-rich")

    # High even fraction suggests parity-constrained
    if frac_even > 0.7:
        tags.append("even-dominated")
    elif frac_even < 0.3:
        tags.append("odd-dominated")

    # High square fraction suggests polynomial/square-related
    if frac_sq > 0.3:
        tags.append("square-rich")

    # Very high oscillation suggests alternating/oscillatory
    if osc > 15:
        tags.append("highly-oscillatory")
    elif osc > 8:
        tags.append("oscillatory")

    # Large dynamic range with high growth suggests exponential-type
    if dyn_range > 8 and growth > 5:
        tags.append("exponential-growth")
    elif dyn_range > 10:
        tags.append("wide-range")

    # Low mean diff and low dynamic range suggests slowly-growing
    if mean_diff < 5 and dyn_range < 3:
        tags.append("slowly-growing")

    # High mean diff suggests rapidly-growing
    if mean_diff > 1e6:
        tags.append("rapidly-growing")

    # High mod-3 entropy suggests uniformly distributed mod 3
    if mod3_ent > 1.5:
        tags.append("mod3-uniform")
    elif mod3_ent < 0.8:
        tags.append("mod3-biased")

    # High mod-2 bias suggests strong parity pattern
    if mod2_bias > 0.5:
        tags.append("strong-parity-pattern")

    # Low diff entropy suggests repetitive differences (arithmetic-progression-like)
    if diff_ent < 2.0:
        tags.append("low-diff-diversity")

    if not tags:
        tags.append("generic-structured")

    return "; ".join(tags)


if __name__ == "__main__":
    main()
