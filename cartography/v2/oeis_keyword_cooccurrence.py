"""
OEIS Keyword Co-occurrence Analysis
====================================
Build keyword co-occurrence matrix, compute PMI, cluster keywords into
natural domain groups, and compare to the cross-reference graph structure.

Data: 394K OEIS sequences with keyword lists.
"""

import json
import math
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "oeis" / "data"
KEYWORDS_FILE = DATA_DIR / "oeis_keywords.json"
GRAPH_RESULTS = Path(__file__).resolve().parent / "oeis_graph_structure_results.json"
OUT_JSON = Path(__file__).resolve().parent / "oeis_keyword_cooccurrence_results.json"


def load_keywords():
    with open(KEYWORDS_FILE) as f:
        return json.load(f)


def build_cooccurrence(kw_data):
    """Build keyword frequency and pairwise co-occurrence counts."""
    kw_freq = Counter()
    pair_freq = Counter()
    n_seqs = len(kw_data)

    for seq_id, keywords in kw_data.items():
        for kw in keywords:
            kw_freq[kw] += 1
        for a, b in combinations(sorted(set(keywords)), 2):
            pair_freq[(a, b)] += 1

    return kw_freq, pair_freq, n_seqs


def compute_pmi(kw_freq, pair_freq, n_seqs, min_pair_count=50):
    """Compute PMI for each keyword pair.

    PMI(a,b) = log2(P(a,b) / (P(a)*P(b)))
    where P(a,b) = count(a,b)/N, P(a) = count(a)/N
    """
    pmi_scores = {}
    for (a, b), count_ab in pair_freq.items():
        if count_ab < min_pair_count:
            continue
        p_a = kw_freq[a] / n_seqs
        p_b = kw_freq[b] / n_seqs
        p_ab = count_ab / n_seqs
        if p_a > 0 and p_b > 0 and p_ab > 0:
            pmi = math.log2(p_ab / (p_a * p_b))
            pmi_scores[(a, b)] = {
                "pmi": pmi,
                "count_ab": count_ab,
                "count_a": kw_freq[a],
                "count_b": kw_freq[b],
                "p_a": round(p_a, 6),
                "p_b": round(p_b, 6),
                "p_ab": round(p_ab, 6),
            }
    return pmi_scores


def npmi(pmi_val, p_ab):
    """Normalized PMI: PMI / -log2(P(a,b)), range [-1, 1]."""
    if p_ab <= 0:
        return 0.0
    denom = -math.log2(p_ab)
    if denom == 0:
        return 0.0
    return pmi_val / denom


def cluster_keywords_greedy(pmi_scores, kw_freq, min_kw_count=100, npmi_threshold=0.15):
    """Greedy agglomerative clustering by NPMI affinity.

    Start with each keyword as its own cluster. Merge the pair with
    highest average NPMI until no pair exceeds threshold.
    """
    # Filter to keywords with enough occurrences
    valid_kws = {kw for kw, c in kw_freq.items() if c >= min_kw_count}

    # Build NPMI adjacency
    adj = {}
    for (a, b), info in pmi_scores.items():
        if a not in valid_kws or b not in valid_kws:
            continue
        n = npmi(info["pmi"], info["p_ab"])
        if n > 0:
            adj.setdefault(a, {})[b] = n
            adj.setdefault(b, {})[a] = n

    # Initialize: each keyword is its own cluster
    kw_to_cluster = {kw: kw for kw in valid_kws if kw in adj}
    clusters = {kw: {kw} for kw in kw_to_cluster}

    def avg_npmi(c1, c2):
        total, count = 0.0, 0
        for x in c1:
            for y in c2:
                if x in adj and y in adj[x]:
                    total += adj[x][y]
                    count += 1
        return total / count if count > 0 else 0.0

    # Greedy merge
    changed = True
    while changed:
        changed = False
        cluster_ids = list(clusters.keys())
        best_score, best_pair = 0.0, None
        for i in range(len(cluster_ids)):
            for j in range(i + 1, len(cluster_ids)):
                ci, cj = cluster_ids[i], cluster_ids[j]
                score = avg_npmi(clusters[ci], clusters[cj])
                if score > best_score:
                    best_score = score
                    best_pair = (ci, cj)
        if best_pair and best_score >= npmi_threshold:
            ci, cj = best_pair
            clusters[ci] = clusters[ci] | clusters[cj]
            del clusters[cj]
            changed = True

    # Name clusters by most frequent keyword
    named = {}
    for cid, members in clusters.items():
        label = max(members, key=lambda k: kw_freq.get(k, 0))
        named[label] = sorted(members, key=lambda k: -kw_freq.get(k, 0))

    return named


def compare_to_graph(clusters, kw_freq, n_seqs):
    """Compare keyword clustering to cross-ref graph properties."""
    with open(GRAPH_RESULTS) as f:
        graph = json.load(f)

    graph_alpha = graph["power_law_fit"]["alpha_dmin5"]
    giant_frac = graph["connected_components"]["giant_component_fraction"]
    clustering_coeff = graph["clustering_coefficient"]["mean_sampled"]

    # Keyword-level stats
    n_keywords = len(kw_freq)
    n_with_100plus = sum(1 for c in kw_freq.values() if c >= 100)

    # How much of sequence space does each cluster cover?
    cluster_coverage = {}
    for label, members in clusters.items():
        # Union of sequences that have ANY keyword in this cluster
        coverage = sum(kw_freq[m] for m in members)
        cluster_coverage[label] = coverage

    return {
        "graph_alpha": graph_alpha,
        "graph_giant_fraction": giant_frac,
        "graph_clustering_coeff": clustering_coeff,
        "n_total_keywords": n_keywords,
        "n_keywords_100plus": n_with_100plus,
        "cluster_coverage_sums": {k: v for k, v in
            sorted(cluster_coverage.items(), key=lambda x: -x[1])},
        "interpretation": (
            f"The cross-ref graph has alpha={graph_alpha:.2f} (near-Lean hierarchical) "
            f"with giant component covering {giant_frac:.1%} of nodes. "
            f"Keyword clusters reveal the thematic domains that generate this connectivity."
        ),
    }


def keyword_degree_correlation(kw_data, kw_freq):
    """Do sequences with rare keywords have different connectivity patterns?

    Compute average number of keywords per sequence, binned by rarest keyword.
    """
    bins = {"common_only": [], "has_rare": [], "has_very_rare": []}
    for seq_id, keywords in kw_data.items():
        min_freq = min(kw_freq.get(k, 0) for k in keywords) if keywords else 0
        n_kw = len(keywords)
        if min_freq >= 10000:
            bins["common_only"].append(n_kw)
        elif min_freq >= 100:
            bins["has_rare"].append(n_kw)
        else:
            bins["has_very_rare"].append(n_kw)

    result = {}
    for label, vals in bins.items():
        if vals:
            result[label] = {
                "n_sequences": len(vals),
                "mean_keywords": round(np.mean(vals), 3),
                "median_keywords": float(np.median(vals)),
            }
    return result


def main():
    t0 = time.time()
    print("Loading OEIS keywords...")
    kw_data = load_keywords()
    n_seqs = len(kw_data)
    print(f"  {n_seqs:,} sequences loaded")

    print("Building co-occurrence matrix...")
    kw_freq, pair_freq, _ = build_cooccurrence(kw_data)
    print(f"  {len(kw_freq)} unique keywords")
    print(f"  {len(pair_freq):,} unique keyword pairs")

    # Top keywords by frequency
    top_kw = kw_freq.most_common(30)
    print(f"\n  Top 10 keywords: {[(k, c) for k, c in top_kw[:10]]}")

    print("Computing PMI scores...")
    pmi_scores = compute_pmi(kw_freq, pair_freq, n_seqs, min_pair_count=50)
    print(f"  {len(pmi_scores):,} pairs with count >= 50")

    # Add NPMI to scores
    for key, info in pmi_scores.items():
        info["npmi"] = round(npmi(info["pmi"], info["p_ab"]), 5)

    # Top 10 by PMI
    top_pmi = sorted(pmi_scores.items(), key=lambda x: -x[1]["pmi"])[:20]
    print("\n  Top 10 keyword pairs by PMI:")
    for (a, b), info in top_pmi[:10]:
        print(f"    {a} + {b}: PMI={info['pmi']:.3f}, NPMI={info['npmi']:.4f}, "
              f"count={info['count_ab']}")

    # Top 10 by NPMI
    top_npmi = sorted(pmi_scores.items(), key=lambda x: -x[1]["npmi"])[:20]
    print("\n  Top 10 keyword pairs by NPMI:")
    for (a, b), info in top_npmi[:10]:
        print(f"    {a} + {b}: NPMI={info['npmi']:.4f}, PMI={info['pmi']:.3f}, "
              f"count={info['count_ab']}")

    # Top 10 by raw co-occurrence count
    top_count = sorted(pmi_scores.items(), key=lambda x: -x[1]["count_ab"])[:20]
    print("\n  Top 10 keyword pairs by raw count:")
    for (a, b), info in top_count[:10]:
        print(f"    {a} + {b}: count={info['count_ab']:,}, "
              f"PMI={info['pmi']:.3f}, NPMI={info['npmi']:.4f}")

    print("\nClustering keywords by NPMI affinity...")
    clusters = cluster_keywords_greedy(pmi_scores, kw_freq,
                                        min_kw_count=100, npmi_threshold=0.15)
    print(f"  {len(clusters)} clusters found:")
    for label, members in sorted(clusters.items(),
                                  key=lambda x: -sum(kw_freq[m] for m in x[1])):
        total = sum(kw_freq[m] for m in members)
        print(f"    [{label}] ({len(members)} kw, ~{total:,} tag-uses): "
              f"{members[:6]}")

    print("\nComparing to cross-reference graph...")
    comparison = compare_to_graph(clusters, kw_freq, n_seqs)
    print(f"  Graph alpha: {comparison['graph_alpha']}")
    print(f"  Giant component: {comparison['graph_giant_fraction']:.1%}")

    print("\nKeyword-degree correlation...")
    kw_degree = keyword_degree_correlation(kw_data, kw_freq)
    for label, info in kw_degree.items():
        print(f"  {label}: n={info['n_sequences']:,}, "
              f"mean_kw={info['mean_keywords']:.2f}")

    elapsed = time.time() - t0

    # ── Assemble results ──
    results = {
        "metadata": {
            "dataset": "OEIS keyword co-occurrence",
            "source": str(KEYWORDS_FILE),
            "n_sequences": n_seqs,
            "n_unique_keywords": len(kw_freq),
            "n_unique_pairs": len(pair_freq),
            "n_pmi_pairs_min50": len(pmi_scores),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "computation_time_s": round(elapsed, 1),
        },
        "keyword_frequencies": {
            "top_30": [[k, c] for k, c in top_kw],
        },
        "top_10_by_pmi": [
            {"pair": f"{a}+{b}", **{k: round(v, 5) if isinstance(v, float) else v
             for k, v in info.items()}}
            for (a, b), info in top_pmi[:10]
        ],
        "top_10_by_npmi": [
            {"pair": f"{a}+{b}", **{k: round(v, 5) if isinstance(v, float) else v
             for k, v in info.items()}}
            for (a, b), info in top_npmi[:10]
        ],
        "top_10_by_count": [
            {"pair": f"{a}+{b}", **{k: round(v, 5) if isinstance(v, float) else v
             for k, v in info.items()}}
            for (a, b), info in top_count[:10]
        ],
        "keyword_clusters": {
            label: {
                "members": members,
                "n_members": len(members),
                "total_tag_uses": sum(kw_freq[m] for m in members),
            }
            for label, members in sorted(clusters.items(),
                key=lambda x: -sum(kw_freq[m] for m in x[1]))
        },
        "graph_comparison": comparison,
        "keyword_degree_correlation": kw_degree,
    }

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_JSON}")
    print(f"Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
