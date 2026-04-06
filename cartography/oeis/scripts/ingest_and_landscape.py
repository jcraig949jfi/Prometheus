"""
OEIS Landscape: Ingest sequences, build cross-reference graph, detect communities.
==================================================================================
"""

import gzip
import re
import json
import numpy as np
import logging
import sys
from collections import defaultdict, Counter
from datetime import date
from pathlib import Path
from scipy import stats

DATA_DIR = Path(__file__).parent.parent / "data"
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(REPORT_DIR / f"oeis_landscape_{date.today()}.log",
                                  mode="w", encoding="utf-8")])
log = logging.getLogger("cart.oeis")


def parse_stripped(filepath):
    """Parse OEIS stripped format: A######  ,term1,term2,...,"""
    sequences = {}
    with gzip.open(filepath, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0].strip()
            if not seq_id.startswith("A"):
                continue
            terms_str = parts[1].strip().strip(",")
            try:
                terms = [int(t.strip()) for t in terms_str.split(",") if t.strip()]
                if len(terms) >= 5:
                    sequences[seq_id] = terms
            except ValueError:
                continue
    return sequences


def compute_features(terms, n_terms=20):
    """Compute feature vector from first n_terms of a sequence."""
    t = terms[:n_terms]
    if len(t) < 5:
        return None

    # Pad if short
    while len(t) < n_terms:
        t.append(0)

    arr = np.array(t, dtype=float)

    # Log-transform for scale invariance
    sign = np.sign(arr)
    log_abs = np.log1p(np.abs(arr))
    log_terms = sign * log_abs

    # Growth rate features
    diffs = np.diff(arr)
    if len(diffs) > 0 and np.std(arr) > 0:
        growth_rate = np.mean(np.abs(diffs)) / (np.std(arr) + 1e-10)
    else:
        growth_rate = 0.0

    # Ratio features (for detecting geometric sequences)
    ratios = []
    for i in range(1, min(len(t), 10)):
        if t[i-1] != 0:
            ratios.append(t[i] / t[i-1])
    ratio_std = np.std(ratios) if len(ratios) > 2 else 0.0

    # Is it monotonic?
    if len(diffs) > 0:
        mono_up = np.all(diffs >= 0)
        mono_down = np.all(diffs <= 0)
    else:
        mono_up = mono_down = False

    return {
        "log_terms": log_terms.tolist(),
        "growth_rate": growth_rate,
        "ratio_std": ratio_std,
        "monotonic": 1.0 if (mono_up or mono_down) else 0.0,
        "n_zeros": sum(1 for x in t if x == 0),
        "n_ones": sum(1 for x in t if x == 1),
        "max_val": float(max(abs(x) for x in t)),
    }


def find_term_matches(sequences, n_match=8):
    """Find sequences that share the same first n_match terms."""
    term_key = {}
    matches = defaultdict(list)

    for seq_id, terms in sequences.items():
        key = tuple(terms[:n_match])
        if key in term_key:
            matches[term_key[key]].append(seq_id)
        else:
            term_key[key] = seq_id

    # Return only groups with 2+ sequences
    return {k: [k] + v for k, v in matches.items() if v}


def main():
    log.info("=" * 70)
    log.info("OEIS LANDSCAPE: Ingest + Analyze")
    log.info(f"Date: {date.today()}")
    log.info("=" * 70)

    # ================================================================
    # 1. INGEST
    # ================================================================
    gz_path = DATA_DIR / "stripped_full.gz"
    log.info(f"Parsing {gz_path}...")
    sequences = parse_stripped(gz_path)
    log.info(f"Parsed {len(sequences)} sequences with 5+ terms")

    # Size distribution
    lengths = [len(v) for v in sequences.values()]
    log.info(f"Terms per sequence: min={min(lengths)}, median={np.median(lengths):.0f}, "
             f"max={max(lengths)}, mean={np.mean(lengths):.1f}")

    # ================================================================
    # 2. FEATURE VECTORS
    # ================================================================
    log.info(f"\nComputing feature vectors...")
    features = {}
    for seq_id, terms in sequences.items():
        f = compute_features(terms)
        if f:
            features[seq_id] = f
    log.info(f"Feature vectors computed for {len(features)} sequences")

    # ================================================================
    # 3. TERM-MATCH ANALYSIS (proto cross-references)
    # ================================================================
    log.info(f"\nFinding term-match groups (first 8 terms identical)...")
    match_groups = find_term_matches(sequences, n_match=8)
    log.info(f"Groups with shared first-8-terms: {len(match_groups)}")

    # Largest match groups
    sorted_groups = sorted(match_groups.items(), key=lambda x: -len(x[1]))
    log.info(f"Largest match groups:")
    for seq_id, group in sorted_groups[:15]:
        terms_preview = ",".join(str(t) for t in sequences[seq_id][:10])
        log.info(f"  {len(group)} sequences starting with [{terms_preview}...]")
        log.info(f"    IDs: {group[:5]}{'...' if len(group) > 5 else ''}")

    # ================================================================
    # 4. GROWTH CLASS DISTRIBUTION
    # ================================================================
    log.info(f"\nGrowth class analysis...")
    growth_rates = np.array([f["growth_rate"] for f in features.values()])
    max_vals = np.array([f["max_val"] for f in features.values()])
    monotonic = np.array([f["monotonic"] for f in features.values()])

    log.info(f"  Monotonic sequences: {np.sum(monotonic):.0f} ({100*np.mean(monotonic):.1f}%)")
    log.info(f"  Growth rate: median={np.median(growth_rates):.4f}, "
             f"mean={np.mean(growth_rates):.4f}")

    # Bin by max value (proxy for growth type)
    bins = [(0, 1, "binary/small"), (2, 100, "moderate"),
            (101, 10000, "polynomial"), (10001, 1e9, "exponential"),
            (1e9, float("inf"), "super-exponential")]

    log.info(f"\n  Growth type distribution:")
    for lo, hi, label in bins:
        n = np.sum((max_vals >= lo) & (max_vals < hi))
        log.info(f"    {label:>20}: {n:>6} ({100*n/len(max_vals):.1f}%)")

    # ================================================================
    # 5. CLUSTERING BY LOG-TRANSFORMED TERMS
    # ================================================================
    log.info(f"\nClustering sample by log-transformed first-20 terms...")

    # Take a random sample for clustering (full dataset is too large for K-means)
    rng = np.random.RandomState(42)
    all_ids = list(features.keys())
    sample_ids = rng.choice(all_ids, size=min(20000, len(all_ids)), replace=False)

    X = np.array([features[sid]["log_terms"] for sid in sample_ids])
    log.info(f"  Sample: {X.shape[0]} sequences, {X.shape[1]} features")

    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    for k in [10, 25, 50, 100]:
        km = KMeans(n_clusters=k, random_state=42, n_init=5, max_iter=100)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels, sample_size=min(5000, len(X)))
        log.info(f"  K={k:>3}: silhouette={sil:.4f}")

    # Best k = 50 (usually good for this size)
    km50 = KMeans(n_clusters=50, random_state=42, n_init=5)
    labels50 = km50.fit_predict(X)

    # What's in each cluster?
    log.info(f"\n  Cluster sizes (K=50):")
    cluster_sizes = Counter(labels50)
    for ci, size in cluster_sizes.most_common(10):
        # Sample a few IDs from this cluster
        cluster_ids = [sample_ids[i] for i in range(len(labels50)) if labels50[i] == ci]
        sample_seqs = cluster_ids[:3]
        previews = []
        for sid in sample_seqs:
            t = sequences[sid][:8]
            previews.append(f"{sid}:[{','.join(str(x) for x in t)}]")
        log.info(f"    Cluster {ci}: {size} seqs. Examples: {'; '.join(previews)}")

    # ================================================================
    # 6. KNOWN LANDMARK SEQUENCES
    # ================================================================
    log.info(f"\nLandmark sequence positions:")
    landmarks = {
        "A000040": "primes",
        "A000045": "Fibonacci",
        "A000079": "powers of 2",
        "A000108": "Catalan",
        "A000142": "factorials",
        "A000290": "squares",
        "A000396": "perfect numbers",
        "A000217": "triangular",
        "A001358": "semiprimes",
        "A005117": "squarefree",
    }

    for seq_id, name in landmarks.items():
        if seq_id in features:
            # Find which cluster it's in
            idx = list(sample_ids).index(seq_id) if seq_id in sample_ids else -1
            cluster = labels50[idx] if idx >= 0 else "N/A"
            terms = sequences[seq_id][:8]
            log.info(f"  {seq_id} ({name:>15}): cluster={cluster}, terms={terms}")

    log.info(f"\n{'='*70}")
    log.info("OEIS LANDSCAPE COMPLETE")
    log.info(f"{'='*70}")


if __name__ == "__main__":
    main()
