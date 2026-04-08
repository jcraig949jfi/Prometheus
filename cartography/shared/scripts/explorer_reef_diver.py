"""
Explorer: Reef Diver — deep characterize non-trivial sleeper clusters from DBSCAN.
====================================================================================
For each cluster with 10+ members, identifies:
  - All member sequences (re-runs clustering on the same parameters)
  - Common keywords from sequence names
  - Average entropy, growth rate, prime fraction
  - Mathematical family classification
  - Nearest hub sequence by term overlap

Usage:  python explorer_reef_diver.py
Output: cartography/convergence/data/reef_characterization.json
"""

import json
import math
import random
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths and imports
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

DATA_DIR = REPO / "cartography" / "convergence" / "data"
CLUSTERS_PATH = DATA_DIR / "sleeper_clusters.json"
OUTPUT_PATH = DATA_DIR / "reef_characterization.json"

# Reuse parameters from sleeper_clustering.py
ENTROPY_THRESHOLD = 3.91
MAX_XREF_DEGREE = 2
MAX_SLEEPERS = 20_000
MIN_TERMS = 8
DBSCAN_EPS = 1.5
DBSCAN_MIN_SAMPLES = 5
SEED = 42

# Stop words for keyword extraction
STOP_WORDS = {
    "a", "an", "the", "of", "for", "in", "is", "to", "and", "or", "by",
    "with", "from", "that", "this", "such", "each", "where", "which",
    "are", "on", "at", "as", "it", "if", "all", "its", "than", "not",
    "n", "k", "m", "x", "i", "j", "0", "1", "2", "3", "4", "5",
    "number", "numbers", "integer", "integers", "sequence",
}

# Mathematical family keywords
FAMILY_KEYWORDS = {
    "partition": ["partition", "partitions", "parts"],
    "prime_hunting": ["prime", "primes", "primality", "sieve", "composite"],
    "combinatorial": ["permutation", "permutations", "combination", "combinations",
                      "arrangements", "derangement", "paths", "walks", "lattice"],
    "recursive": ["recurrence", "recursive", "recursion", "iteration", "fibonacci"],
    "polynomial": ["polynomial", "coefficients", "roots", "chebyshev"],
    "modular": ["modular", "mod", "residue", "congruence", "modulo"],
    "divisor": ["divisor", "divisors", "sigma", "tau", "aliquot", "abundant"],
    "digit": ["digits", "digit", "decimal", "binary", "ternary", "palindrome"],
    "triangular": ["triangle", "triangular", "pascal", "row", "rows"],
    "graph_theoretic": ["graph", "graphs", "tree", "trees", "vertex", "edge", "edges"],
    "geometric": ["geometric", "square", "cube", "triangular", "pentagonal", "polygonal"],
    "exponential": ["exponential", "factorial", "subfactorial", "bell"],
    "arithmetic": ["arithmetic", "sum", "sums", "product", "products", "average"],
    "algebraic": ["algebraic", "group", "ring", "field", "galois"],
    "analytic": ["zeta", "gamma", "bernoulli", "euler", "harmonic", "series"],
    "cellular_automaton": ["automaton", "automata", "cellular", "rule"],
    "array": ["array", "arrays", "matrix", "table"],
    "continued_fraction": ["continued fraction", "convergent", "convergents"],
}


# ---------------------------------------------------------------------------
# Feature computation (replicated from sleeper_clustering.py)
# ---------------------------------------------------------------------------

def _shannon_entropy(values):
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)


def _is_prime(n):
    if n < 2:
        return False
    if n > 10_000_000:
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
    """Compute the 10D feature vector (same as sleeper_clustering.py)."""
    t = terms[:50]
    n = len(t)
    if n < 3:
        return None

    diffs = [t[i + 1] - t[i] for i in range(n - 1)]
    feat_0 = _shannon_entropy(diffs)

    ratios = []
    for i in range(n - 1):
        if t[i] != 0:
            ratios.append(t[i + 1] / t[i])
    feat_1 = min(float(np.std(ratios)), 1e6) if len(ratios) >= 2 else 0.0

    feat_2 = min(float(np.mean([abs(d) for d in diffs])), 1e12)
    feat_3 = sum(1 for x in t if _is_prime(abs(x))) / n
    feat_4 = sum(1 for x in t if x % 2 == 0) / n
    feat_5 = sum(1 for x in t if _is_perfect_square(abs(x))) / n

    abs_terms = [abs(x) for x in t if x != 0]
    if abs_terms:
        max_t, min_t = max(abs_terms), min(abs_terms)
        feat_6 = min(math.log10(max_t / min_t + 1), 30.0) if min_t > 0 else 0.0
    else:
        feat_6 = 0.0

    sign_changes = sum(1 for i in range(len(diffs) - 1) if diffs[i] * diffs[i + 1] < 0)
    feat_7 = float(sign_changes)

    n_even = sum(1 for x in t if x % 2 == 0)
    feat_8 = abs(n_even - (n - n_even)) / n

    feat_9 = _shannon_entropy([x % 3 for x in t])

    return [feat_0, feat_1, feat_2, feat_3, feat_4, feat_5, feat_6, feat_7, feat_8, feat_9]


# ---------------------------------------------------------------------------
# Sleeper identification (replicated)
# ---------------------------------------------------------------------------

def identify_sleepers():
    """Find all sleeping beauties matching the original parameters."""
    sleepers = []
    for seq_id, terms in _oeis_cache.items():
        if len(terms) < MIN_TERMS:
            continue

        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        total_deg = out_deg + in_deg
        if total_deg > MAX_XREF_DEGREE:
            continue

        diffs = [terms[i + 1] - terms[i] for i in range(min(len(terms) - 1, 30))]
        if not diffs:
            continue
        entropy = _shannon_entropy(diffs)
        if entropy < ENTROPY_THRESHOLD:
            continue

        sleepers.append((seq_id, terms, entropy, total_deg))

    return sleepers


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

def extract_keywords(names: list[str], min_fraction: float = 0.5) -> list[dict]:
    """Extract words appearing in >min_fraction of names.
    Returns list of {word, fraction, count}."""
    if not names:
        return []

    word_counts = Counter()
    for name in names:
        # Tokenize: lowercase, split on non-alpha
        words = set(re.findall(r'[a-zA-Z]+', name.lower()))
        # Filter stop words and short words
        words = {w for w in words if w not in STOP_WORDS and len(w) > 2}
        word_counts.update(words)

    n = len(names)
    common = []
    for word, count in word_counts.most_common():
        frac = count / n
        if frac >= min_fraction:
            common.append({"word": word, "fraction": round(frac, 3), "count": count})
        else:
            break  # sorted by count, so we can stop

    return common


def classify_family(names: list[str], keywords: list[dict]) -> str:
    """Classify mathematical family based on sequence names and common keywords."""
    # Combine all names into one search corpus
    corpus = " ".join(names).lower()
    keyword_words = {kw["word"] for kw in keywords}

    # Score each family
    family_scores = {}
    for family, kw_list in FAMILY_KEYWORDS.items():
        score = 0
        for kw in kw_list:
            if kw in corpus:
                # Higher score if the keyword is in the common keywords list
                if kw in keyword_words:
                    score += 3
                else:
                    score += 1
        if score > 0:
            family_scores[family] = score

    if not family_scores:
        return "unclassified"

    # Return the top family (or top-2 if close)
    sorted_families = sorted(family_scores.items(), key=lambda x: -x[1])
    top = sorted_families[0]
    if len(sorted_families) > 1 and sorted_families[1][1] >= top[1] * 0.7:
        return f"{top[0]} / {sorted_families[1][0]}"
    return top[0]


# ---------------------------------------------------------------------------
# Hub finding
# ---------------------------------------------------------------------------

def find_nearest_hub(member_terms: list[list[int]], hub_cache: dict) -> dict | None:
    """Find the nearest hub sequence by term overlap.

    hub_cache: {seq_id: terms_list} for high-degree sequences.
    member_terms: list of first-10 terms for each cluster member.
    """
    if not hub_cache or not member_terms:
        return None

    # Build a composite term set from cluster members (union of first 10 terms)
    cluster_terms = set()
    for terms in member_terms:
        cluster_terms.update(terms[:10])

    # Remove trivially common values
    cluster_terms -= {0, 1, -1, 2, -2}

    if len(cluster_terms) < 3:
        return None

    best_hub = None
    best_overlap = 0

    for hub_id, hub_terms in hub_cache.items():
        hub_set = set(hub_terms[:30]) - {0, 1, -1, 2, -2}
        overlap = len(cluster_terms & hub_set)
        if overlap > best_overlap:
            best_overlap = overlap
            best_hub = hub_id

    if best_hub and best_overlap >= 2:
        return {
            "hub_id": best_hub,
            "hub_name": _oeis_names_cache.get(best_hub, ""),
            "term_overlap": best_overlap,
            "hub_degree": (len(_oeis_xref_cache.get(best_hub, set())) +
                           len(_oeis_xref_reverse.get(best_hub, set()))),
        }
    return None


# ---------------------------------------------------------------------------
# Reef naming
# ---------------------------------------------------------------------------

REEF_NAME_MAP = {
    "partition": "Partition Reef",
    "prime_hunting": "Prime Shoals",
    "combinatorial": "Combinatorial Reef",
    "recursive": "Recursive Depths",
    "polynomial": "Polynomial Reef",
    "modular": "Modular Reef",
    "divisor": "Divisor Reef",
    "digit": "Digital Reef",
    "triangular": "Triangle Reef",
    "graph_theoretic": "Graph Reef",
    "geometric": "Geometric Reef",
    "exponential": "Exponential Abyss",
    "arithmetic": "Arithmetic Shallows",
    "algebraic": "Algebraic Reef",
    "analytic": "Analytic Depths",
    "cellular_automaton": "Automaton Reef",
    "array": "Array Reef",
    "continued_fraction": "Fraction Reef",
    "unclassified": "Uncharted Reef",
}


def name_reef(family: str, cluster_id: int) -> str:
    """Generate a reef name from family classification."""
    primary = family.split(" / ")[0] if " / " in family else family
    base_name = REEF_NAME_MAP.get(primary, "Uncharted Reef")
    return f"{base_name} #{cluster_id}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print("=" * 70)
    print("  REEF DIVER — Deep characterization of sleeper clusters")
    print("=" * 70)

    # 1. Load cluster results
    if not CLUSTERS_PATH.exists():
        print(f"  ERROR: {CLUSTERS_PATH} not found. Run sleeper_clustering.py first.")
        return
    clusters_data = json.loads(CLUSTERS_PATH.read_text(encoding="utf-8"))

    # Identify non-trivial clusters (10+ members)
    nontrivial = [c for c in clusters_data["dbscan_clusters"] if c["size"] >= 10]
    print(f"\n  Found {len(nontrivial)} non-trivial DBSCAN clusters (size >= 10)")
    for c in nontrivial:
        print(f"    Cluster {c['cluster_id']}: {c['size']} members")

    # 2. Re-run clustering to get member IDs
    print(f"\n  Re-running sleeper identification to recover member IDs...")
    _load_oeis()
    _load_oeis_names()
    _load_oeis_crossrefs()

    sleepers = identify_sleepers()
    if not sleepers:
        print("  ERROR: No sleeping beauties found.")
        return
    print(f"  Found {len(sleepers):,} sleeping beauties")

    # Sample to match original run
    random.seed(SEED)
    np.random.seed(SEED)
    if len(sleepers) > MAX_SLEEPERS:
        sleepers = random.sample(sleepers, MAX_SLEEPERS)

    # Compute features
    print(f"  Computing feature vectors...")
    seq_ids = []
    features = []
    meta = {}

    for seq_id, terms, entropy, degree in sleepers:
        fv = compute_feature_vector(terms)
        if fv is None:
            continue
        if any(math.isnan(v) or math.isinf(v) for v in fv):
            continue
        seq_ids.append(seq_id)
        features.append(fv)
        meta[seq_id] = {
            "entropy": round(entropy, 4),
            "degree": degree,
            "name": _oeis_names_cache.get(seq_id, ""),
            "first_terms": (_oeis_cache.get(seq_id, []))[:10],
        }

    X = np.array(features, dtype=np.float64)
    print(f"  Feature matrix: {X.shape[0]:,} x {X.shape[1]}")

    # Scale and cluster
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"  Running DBSCAN (eps={DBSCAN_EPS}, min_samples={DBSCAN_MIN_SAMPLES})...")
    db = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES, n_jobs=-1)
    db_labels = db.fit_predict(X_scaled)
    n_clusters = len(set(db_labels) - {-1})
    print(f"  Re-clustered: {n_clusters} clusters")

    # 3. Build hub cache (high-degree sequences for nearest-hub search)
    print(f"\n  Building hub cache (high-degree sequences)...")
    hub_cache = {}
    for seq_id in _oeis_cache:
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        total = out_deg + in_deg
        if total >= 50:
            hub_cache[seq_id] = _oeis_cache[seq_id]
    print(f"  Hub cache: {len(hub_cache):,} hub sequences (degree >= 50)")

    # 4. Characterize each non-trivial cluster
    print(f"\n{'='*70}")
    print("  REEF CHARACTERIZATION")
    print(f"{'='*70}")

    FEATURE_NAMES = clusters_data["parameters"]["feature_names"]
    reefs = []

    for cluster_info in nontrivial:
        cid = cluster_info["cluster_id"]
        expected_size = cluster_info["size"]

        # Get all members of this cluster
        mask = db_labels == cid
        cluster_member_ids = [seq_ids[i] for i in range(len(seq_ids)) if mask[i]]
        actual_size = len(cluster_member_ids)

        print(f"\n  --- Cluster {cid} ({actual_size} members) ---")

        # Get names and first terms
        member_names = [meta[sid]["name"] for sid in cluster_member_ids if sid in meta]
        member_terms = [meta[sid]["first_terms"] for sid in cluster_member_ids if sid in meta]

        # Common keywords
        keywords = extract_keywords(member_names, min_fraction=0.5)
        if not keywords:
            keywords = extract_keywords(member_names, min_fraction=0.3)

        print(f"    Common keywords (>50%): {[kw['word'] for kw in keywords[:10]]}")

        # Average features from raw centroid
        cluster_features = X[mask]
        avg_features = {}
        if cluster_features.shape[0] > 0:
            means = cluster_features.mean(axis=0)
            for i, fname in enumerate(FEATURE_NAMES):
                avg_features[fname] = round(float(means[i]), 4)

        avg_entropy = avg_features.get("diff_entropy", 0)
        avg_growth = avg_features.get("growth_complexity", 0)
        avg_prime_frac = avg_features.get("frac_prime", 0)
        print(f"    Avg entropy: {avg_entropy:.3f}, growth: {avg_growth:.1f}, "
              f"prime_frac: {avg_prime_frac:.3f}")

        # Mathematical family
        family = classify_family(member_names, keywords)
        reef_name = name_reef(family, cid)
        print(f"    Family: {family}")
        print(f"    Reef name: {reef_name}")

        # Nearest hub
        nearest_hub = find_nearest_hub(member_terms, hub_cache)
        if nearest_hub:
            print(f"    Nearest hub: {nearest_hub['hub_id']} — "
                  f"{nearest_hub['hub_name'][:60]} "
                  f"(overlap={nearest_hub['term_overlap']}, "
                  f"degree={nearest_hub['hub_degree']})")
        else:
            print(f"    Nearest hub: none found")

        # Sample members for report
        sample_size = min(20, actual_size)
        sample_ids = random.sample(cluster_member_ids, sample_size)
        sample_members = [
            {
                "id": sid,
                "name": meta[sid]["name"],
                "first_10_terms": meta[sid]["first_terms"],
            }
            for sid in sample_ids if sid in meta
        ]

        reef = {
            "cluster_id": cid,
            "size": actual_size,
            "expected_size": expected_size,
            "reef_name": reef_name,
            "mathematical_family": family,
            "common_keywords": keywords[:15],
            "nearest_hub": nearest_hub,
            "avg_features": avg_features,
            "summary": {
                "avg_entropy": avg_entropy,
                "avg_growth_rate": avg_growth,
                "avg_prime_fraction": avg_prime_frac,
                "avg_even_fraction": avg_features.get("frac_even", 0),
                "avg_square_fraction": avg_features.get("frac_square", 0),
                "avg_oscillation": avg_features.get("oscillation_count", 0),
                "avg_dynamic_range": avg_features.get("dynamic_range_log", 0),
            },
            "family_guess_original": cluster_info.get("family_guess", "unknown"),
            "sample_members": sample_members,
            "all_member_ids": cluster_member_ids,
        }
        reefs.append(reef)

    # 5. Summary
    elapsed = time.time() - t0

    print(f"\n{'='*70}")
    print(f"  REEF DIVER SUMMARY")
    print(f"{'='*70}")
    print(f"  Reefs characterized: {len(reefs)}")
    for reef in reefs:
        print(f"    {reef['reef_name']:30s}  {reef['size']:6d} members  "
              f"family={reef['mathematical_family']}")
    print(f"  Time elapsed: {elapsed:.1f}s")
    print(f"{'='*70}")

    # 6. Save
    output = {
        "meta": {
            "generated": datetime.now().isoformat(timespec="seconds"),
            "clusters_source": str(CLUSTERS_PATH.name),
            "n_reefs": len(reefs),
            "total_sleepers_reprocessed": len(seq_ids),
            "n_hub_sequences": len(hub_cache),
            "elapsed_seconds": round(elapsed, 2),
        },
        "reefs": reefs,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
