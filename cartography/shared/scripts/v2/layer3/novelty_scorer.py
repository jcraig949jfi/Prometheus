"""Layer 3: Novelty scoring and frontier target identification."""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import entropy as kl_divergence

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

DATA = Path(__file__).resolve().parents[4] / "convergence" / "data"
CONCEPTS_FILE = DATA / "concepts.jsonl"
BRIDGES_FILE = DATA / "bridges.jsonl"
SHADOW_FILE = DATA / "shadow_tensor.json"
VECTORS_FILE = DATA / "concept_vectors.npy"
METADATA_FILE = DATA / "concept_metadata.jsonl"


def load_inputs():
    """Load embedding vectors, metadata, concepts, bridges, shadow tensor."""
    vectors = np.load(VECTORS_FILE)

    metadata = []
    with open(METADATA_FILE) as f:
        for line in f:
            metadata.append(json.loads(line))

    # Concept -> source mapping + bridge info
    concept_source = {}
    with open(CONCEPTS_FILE) as f:
        for line in f:
            r = json.loads(line)
            concept_source[r["id"]] = r["source"]

    bridge_info = {}
    if BRIDGES_FILE.exists():
        with open(BRIDGES_FILE) as f:
            for line in f:
                r = json.loads(line)
                bridge_info[r["concept"]] = {
                    "n_datasets": r["n_datasets"],
                    "datasets": list(r["datasets"].keys()),
                }

    shadow = None
    if SHADOW_FILE.exists():
        try:
            shadow = json.load(open(SHADOW_FILE))
        except Exception as e:
            print(f"  Warning: shadow tensor load failed: {e}")

    return vectors, metadata, concept_source, bridge_info, shadow


def compute_edge_entropy(metadata, concept_source):
    """Shannon entropy of source distribution for each concept's neighbors.
    Approximated: concepts from same source have entropy=0, bridge concepts
    get entropy from their dataset distribution."""
    from collections import Counter

    entropies = []
    for m in metadata:
        # Use source as proxy — single-source concepts have 0 entropy
        src = concept_source.get(m["id"], "")
        n_edges = m["edge_count"]
        if n_edges == 0:
            entropies.append(0.0)
            continue
        # Approximate: edge_count neighbors mostly from same source
        # Real entropy would need neighbor list; use source count as proxy
        entropies.append(0.0)  # placeholder, overridden below for bridges

    return np.array(entropies)


def compute_shadow_cold(metadata, bridge_info, shadow):
    """Map concepts to dataset pairs and compute cold score from shadow tensor."""
    cold_scores = np.zeros(len(metadata))
    if shadow is None:
        return cold_scores

    cells = shadow.get("cells", {})
    # Build dataset-pair -> test count map
    pair_tests = {}
    for key, cell in cells.items():
        pair_tests[key] = cell.get("n_tested", 0)

    # For each concept, average test count across its dataset pairs
    max_tests = max(pair_tests.values()) if pair_tests else 1

    for i, m in enumerate(metadata):
        cid = m["id"]
        bi = bridge_info.get(cid)
        if bi is None or bi["n_datasets"] < 2:
            # Single-dataset concept: cold = 1 (never cross-tested)
            cold_scores[i] = 1.0
            continue

        datasets = bi["datasets"]
        test_counts = []
        for di in range(len(datasets)):
            for dj in range(di + 1, len(datasets)):
                key1 = f"{datasets[di]}--{datasets[dj]}"
                key2 = f"{datasets[dj]}--{datasets[di]}"
                tc = pair_tests.get(key1, pair_tests.get(key2, 0))
                test_counts.append(tc)

        if test_counts:
            mean_tests = np.mean(test_counts)
            cold_scores[i] = 1.0 - (mean_tests / max_tests)
        else:
            cold_scores[i] = 1.0

    return cold_scores


def _build_battery_profile(cell):
    """Build a probability distribution from a shadow tensor cell's test outcomes.

    Returns a 4-element array: [frac_killed, frac_passed, frac_open, frac_other].
    """
    n = cell.get("n_tested", 0)
    if n == 0:
        return np.array([0.25, 0.25, 0.25, 0.25])
    killed = cell.get("n_killed", 0)
    passed = cell.get("n_passed", 0)
    opened = cell.get("n_open", 0)
    other = max(0, n - killed - passed - opened)
    profile = np.array([killed, passed, opened, other], dtype=float) / n
    return profile


def _compute_surprise_scores(shadow, metadata, bridge_info):
    """Compute Bayesian surprise for each concept via shadow tensor prediction error.

    For each dataset pair, builds a battery profile (kill/pass/open distribution),
    predicts it from neighbor pairs (those sharing a dataset), and measures KL
    divergence between actual and predicted.  Maps per-pair surprise back to
    per-concept scores via dataset membership.
    """
    n = len(metadata)
    surprise_per_concept = np.zeros(n)

    if shadow is None:
        return surprise_per_concept, {}

    cells = shadow.get("cells", {})
    if not cells:
        return surprise_per_concept, {}

    # Step 1: build battery profiles per pair
    profiles = {}
    for key, cell in cells.items():
        if cell.get("n_tested", 0) < 5:
            continue
        profiles[key] = _build_battery_profile(cell)

    if not profiles:
        return surprise_per_concept, {}

    # Step 2: build adjacency — pairs sharing a dataset are neighbors
    dataset_to_pairs = defaultdict(list)
    for key in profiles:
        parts = key.split("--")
        if len(parts) == 2:
            dataset_to_pairs[parts[0]].append(key)
            dataset_to_pairs[parts[1]].append(key)

    # Step 3: compute predicted profile from neighbors and KL divergence
    EPS = 1e-10
    pair_surprise = {}
    for key, actual in profiles.items():
        parts = key.split("--")
        if len(parts) != 2:
            continue
        # Neighbors: all pairs sharing dataset A or dataset B, excluding self
        neighbor_keys = set()
        for ds in parts:
            for nk in dataset_to_pairs.get(ds, []):
                if nk != key:
                    neighbor_keys.add(nk)

        if not neighbor_keys:
            pair_surprise[key] = 0.0
            continue

        # Predicted profile = mean of neighbor profiles
        neighbor_profiles = np.array([profiles[nk] for nk in neighbor_keys if nk in profiles])
        if len(neighbor_profiles) == 0:
            pair_surprise[key] = 0.0
            continue

        predicted = neighbor_profiles.mean(axis=0)
        # Add epsilon to avoid log(0) in KL
        actual_safe = actual + EPS
        predicted_safe = predicted + EPS
        # Normalize after epsilon addition
        actual_safe /= actual_safe.sum()
        predicted_safe /= predicted_safe.sum()

        kl = float(kl_divergence(actual_safe, predicted_safe))
        pair_surprise[key] = kl

    if not pair_surprise:
        return surprise_per_concept, pair_surprise

    # Step 4: map pair surprise to per-concept scores
    id2idx = {m["id"]: i for i, m in enumerate(metadata)}

    for cid, bi in bridge_info.items():
        if cid not in id2idx:
            continue
        if bi["n_datasets"] < 2:
            continue
        datasets = bi["datasets"]
        pair_kls = []
        for di in range(len(datasets)):
            for dj in range(di + 1, len(datasets)):
                key1 = f"{datasets[di]}--{datasets[dj]}"
                key2 = f"{datasets[dj]}--{datasets[di]}"
                kl = pair_surprise.get(key1, pair_surprise.get(key2, None))
                if kl is not None:
                    pair_kls.append(kl)
        if pair_kls:
            surprise_per_concept[id2idx[cid]] = float(np.mean(pair_kls))

    return surprise_per_concept, pair_surprise


def score_novelty(vectors, metadata, concept_source, bridge_info, shadow, weights):
    """Compute novelty score for each concept."""
    t0 = time.time()
    n = len(metadata)
    w1, w2, w3, w4, w5 = weights

    # Component 1: distance to global centroid (already in metadata)
    centroid_dists = np.array([m["centroid_distance"] for m in metadata])
    if centroid_dists.max() > 0:
        c1 = centroid_dists / centroid_dists.max()
    else:
        c1 = np.zeros(n)

    # Component 2: inverse local density
    densities = np.array([m["local_density"] for m in metadata])
    # Higher density = closer neighbors = less novel. Invert.
    # density is mean NN distance: high value = sparse = novel
    if densities.max() > 0:
        c2 = densities / densities.max()
    else:
        c2 = np.zeros(n)

    # Component 3: edge entropy
    # Compute actual entropy from bridge dataset distribution
    entropies = np.zeros(n)
    for i, m in enumerate(metadata):
        bi = bridge_info.get(m["id"])
        if bi and bi["n_datasets"] >= 2:
            # Entropy of uniform over n_datasets
            nd = bi["n_datasets"]
            entropies[i] = np.log2(nd)
        else:
            entropies[i] = 0.0
    if entropies.max() > 0:
        c3 = entropies / entropies.max()
    else:
        c3 = np.zeros(n)

    # Component 4: shadow cold score
    c4 = compute_shadow_cold(metadata, bridge_info, shadow)

    # Component 5: Bayesian surprise from shadow tensor prediction error
    raw_surprise, pair_surprise = _compute_surprise_scores(shadow, metadata, bridge_info)
    if raw_surprise.max() > 0:
        c5 = raw_surprise / raw_surprise.max()
    else:
        c5 = np.zeros(n)

    novelty = w1 * c1 + w2 * c2 + w3 * c3 + w4 * c4 + w5 * c5

    print(f"  Novelty computed for {n} concepts, {time.time()-t0:.1f}s")
    print(f"  Component stats (mean/std):")
    print(f"    centroid_dist: {c1.mean():.3f}/{c1.std():.3f}")
    print(f"    inv_density:   {c2.mean():.3f}/{c2.std():.3f}")
    print(f"    edge_entropy:  {c3.mean():.3f}/{c3.std():.3f}")
    print(f"    shadow_cold:   {c4.mean():.3f}/{c4.std():.3f}")
    print(f"    surprise:      {c5.mean():.3f}/{c5.std():.3f}")

    # Print top 10 most surprising dataset pairs
    if pair_surprise:
        sorted_pairs = sorted(pair_surprise.items(), key=lambda x: -x[1])[:10]
        print(f"\n  Top 10 most surprising dataset pairs:")
        for pair, kl in sorted_pairs:
            print(f"    {pair:40s} KL={kl:.4f}")

    return novelty, c1, c2, c3, c4, c5


def build_heatmap(metadata, bridge_info, novelty):
    """NxN dataset matrix: mean novelty of shared concepts."""
    # Collect all datasets
    all_datasets = set()
    for bi in bridge_info.values():
        all_datasets.update(bi["datasets"])
    all_datasets = sorted(all_datasets)

    id2idx = {m["id"]: i for i, m in enumerate(metadata)}
    ds_idx = {d: i for i, d in enumerate(all_datasets)}
    n_ds = len(all_datasets)

    heatmap = np.zeros((n_ds, n_ds))
    counts = np.zeros((n_ds, n_ds))

    for cid, bi in bridge_info.items():
        if cid not in id2idx:
            continue
        nov = novelty[id2idx[cid]]
        datasets = bi["datasets"]
        for di in range(len(datasets)):
            for dj in range(di + 1, len(datasets)):
                a, b = ds_idx[datasets[di]], ds_idx[datasets[dj]]
                heatmap[a, b] += nov
                heatmap[b, a] += nov
                counts[a, b] += 1
                counts[b, a] += 1

    mask = counts > 0
    heatmap[mask] /= counts[mask]

    return {
        "datasets": all_datasets,
        "matrix": heatmap.tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description="Novelty scoring for concept graph")
    parser.add_argument("--top", type=int, default=50, help="Number of frontier targets")
    parser.add_argument("--weights", type=str, default="0.25,0.25,0.15,0.15,0.20",
                        help="Weights: centroid,density,entropy,shadow,surprise")
    args = parser.parse_args()

    weights = [float(w) for w in args.weights.split(",")]
    assert len(weights) == 5, "Need exactly 5 weights (centroid,density,entropy,shadow,surprise)"

    t_total = time.time()

    print("Loading inputs...")
    vectors, metadata, concept_source, bridge_info, shadow = load_inputs()
    print(f"  {len(metadata)} concepts, {len(bridge_info)} bridges, shadow={'yes' if shadow else 'no'}")

    print("Computing novelty scores...")
    novelty, c1, c2, c3, c4, c5 = score_novelty(
        vectors, metadata, concept_source, bridge_info, shadow, weights
    )

    # Rank
    order = np.argsort(-novelty)
    median_nov = np.median(novelty)

    # Save rankings
    out_rankings = DATA / "novelty_rankings.jsonl"
    with open(out_rankings, "w") as f:
        for idx in order:
            m = metadata[idx]
            bi = bridge_info.get(m["id"], {})
            f.write(json.dumps({
                "concept_id": m["id"],
                "novelty_score": round(float(novelty[idx]), 6),
                "centroid_dist": round(float(c1[idx]), 6),
                "inv_density": round(float(c2[idx]), 6),
                "edge_entropy": round(float(c3[idx]), 6),
                "shadow_cold": round(float(c4[idx]), 6),
                "surprise": round(float(c5[idx]), 6),
                "type": m["type"],
                "source": m["source"],
                "datasets": bi.get("datasets", [m["source"]]),
            }) + "\n")
    print(f"  Saved {out_rankings}")

    # Frontier targets: top N bridge concepts above median
    frontier = []
    for idx in order:
        m = metadata[idx]
        bi = bridge_info.get(m["id"])
        if bi is None or bi["n_datasets"] < 2:
            continue
        if novelty[idx] <= median_nov:
            continue
        frontier.append({
            "concept_id": m["id"],
            "novelty_score": round(float(novelty[idx]), 6),
            "n_datasets": bi["n_datasets"],
            "datasets": bi["datasets"],
            "type": m["type"],
            "centroid_distance": m["centroid_distance"],
            "local_density": m["local_density"],
            "suggested_direction": _suggest_direction(m, bi, c1[idx], c2[idx], c3[idx], c4[idx], c5[idx]),
        })
        if len(frontier) >= args.top:
            break

    out_frontier = DATA / "frontier_targets.jsonl"
    with open(out_frontier, "w") as f:
        for ft in frontier:
            f.write(json.dumps(ft) + "\n")
    print(f"  Saved {out_frontier} ({len(frontier)} targets)")

    # Heatmap
    print("Building exploration heatmap...")
    heatmap = build_heatmap(metadata, bridge_info, novelty)
    out_heatmap = DATA / "exploration_heatmap.json"
    with open(out_heatmap, "w") as f:
        json.dump(heatmap, f, indent=2)
    print(f"  Saved {out_heatmap}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Novelty distribution:")
    pcts = np.percentile(novelty, [10, 25, 50, 75, 90])
    print(f"  p10={pcts[0]:.4f} p25={pcts[1]:.4f} median={pcts[2]:.4f} p75={pcts[3]:.4f} p90={pcts[4]:.4f}")
    print(f"  mean={novelty.mean():.4f} std={novelty.std():.4f}")

    print(f"\nTop 20 highest-novelty concepts:")
    for i, idx in enumerate(order[:20]):
        m = metadata[idx]
        bi = bridge_info.get(m["id"], {})
        ds = bi.get("datasets", [m["source"]])
        print(f"  {i+1:2d}. {m['id']:40s} nov={novelty[idx]:.4f}  [{','.join(ds[:3])}{'...' if len(ds)>3 else ''}]")

    # Coldest dataset pairs
    cells = {}
    if shadow:
        cells = shadow.get("cells", {})
    if cells:
        cold_pairs = sorted(cells.items(), key=lambda x: x[1].get("n_tested", 0))[:10]
        print(f"\nColdest dataset pairs (fewest tests):")
        for pair, cell in cold_pairs:
            print(f"  {pair:40s} tests={cell.get('n_tested',0)}")

    print(f"\nTotal time: {time.time()-t_total:.1f}s")


def _suggest_direction(m, bi, c1, c2, c3, c4, c5):
    """Generate a short exploration suggestion based on dominant novelty component."""
    dominant = max([(c1, "centroid"), (c2, "density"), (c3, "entropy"), (c4, "shadow"), (c5, "surprise")])
    tag = dominant[1]
    if tag == "centroid":
        return f"Outlier in embedding space — check if genuinely novel or extraction artifact"
    elif tag == "density":
        return f"Isolated concept spanning {bi['n_datasets']} datasets — potential undiscovered bridge"
    elif tag == "entropy":
        return f"High cross-dataset diversity — test pairwise correlations"
    elif tag == "surprise":
        return f"Anomalous battery behavior vs neighbors — investigate what makes this region different"
    else:
        return f"Undertested in shadow tensor — prioritize for hypothesis generation"


if __name__ == "__main__":
    main()
