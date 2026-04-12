"""
ALL-065: Complexity Entropy of Rosetta Stone
==============================================
The Rosetta Stone = the cross-domain concept graph (bridges.jsonl + concept_links.jsonl).
Compute:
1. Shannon entropy of the concept degree distribution
2. Effective dimensionality (SVD rank of concept-dataset matrix)
3. Concept specificity distribution (how many datasets per concept?)
4. Bridge redundancy: are cross-domain bridges concentrated or dispersed?
"""
import json, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
BRIDGES = V2.parents[3] / "cartography" / "convergence" / "data" / "bridges.jsonl"
LINKS = V2.parents[3] / "cartography" / "convergence" / "data" / "concept_links.jsonl"
OUT = V2 / "all065_rosetta_entropy_results.json"

def main():
    t0 = time.time()
    print("=== ALL-065: Complexity Entropy of Rosetta Stone ===\n")

    # Load bridges (compact: 1.1MB)
    print("[1] Loading bridges...")
    bridges = []
    with open(BRIDGES) as f:
        for line in f:
            if line.strip():
                try: bridges.append(json.loads(line))
                except: pass
    print(f"  {len(bridges)} bridge concepts")

    # Analyse bridge specificity
    specificities = [b.get("specificity", 0) for b in bridges]
    n_datasets = [b.get("n_datasets", 0) for b in bridges]
    total_objects = [b.get("total_objects", 0) for b in bridges]

    spec_arr = np.array(specificities)
    nd_arr = np.array(n_datasets)
    obj_arr = np.array(total_objects)

    print(f"\n  Specificity: mean={spec_arr.mean():.4f}, std={spec_arr.std():.4f}")
    print(f"  Datasets per concept: mean={nd_arr.mean():.1f}, max={nd_arr.max()}")
    print(f"  Objects per concept: mean={obj_arr.mean():.0f}, max={obj_arr.max()}")

    # Degree distribution (n_datasets = degree in bipartite graph)
    degree_dist = Counter(n_datasets)
    print(f"\n  Degree distribution:")
    for k in sorted(degree_dist.keys()):
        print(f"    degree {k}: {degree_dist[k]} concepts")

    # Shannon entropy of degree distribution
    total = sum(degree_dist.values())
    probs = np.array([v / total for v in degree_dist.values()])
    H_degree = float(-np.sum(probs * np.log2(probs + 1e-15)))
    H_max = np.log2(len(degree_dist))
    print(f"\n  H(degree) = {H_degree:.4f} bits (max = {H_max:.4f})")
    print(f"  Normalized entropy: {H_degree / H_max:.4f}")

    # Shannon entropy of specificity (binned)
    hist_spec, _ = np.histogram(specificities, bins=20)
    p_spec = hist_spec / hist_spec.sum()
    p_spec = p_spec[p_spec > 0]
    H_spec = float(-np.sum(p_spec * np.log2(p_spec)))
    print(f"  H(specificity) = {H_spec:.4f} bits")

    # Load concept_links (sample for speed — 323MB is large)
    print("\n[2] Sampling concept_links (first 500K lines)...")
    concept_datasets = defaultdict(set)
    dataset_concepts = defaultdict(set)
    n_links = 0
    with open(LINKS) as f:
        for line in f:
            if n_links >= 500000: break
            line = line.strip()
            if not line: continue
            try:
                r = json.loads(line)
                c = r.get("concept", "")
                d = r.get("dataset", "")
                if c and d:
                    concept_datasets[c].add(d)
                    dataset_concepts[d].add(c)
                n_links += 1
            except: pass
    print(f"  {n_links} links sampled")
    print(f"  {len(concept_datasets)} concepts, {len(dataset_concepts)} datasets")

    # Build concept-dataset binary matrix (top concepts)
    top_concepts = sorted(concept_datasets.keys(), key=lambda c: -len(concept_datasets[c]))[:500]
    all_datasets = sorted(dataset_concepts.keys())
    ds_idx = {d: i for i, d in enumerate(all_datasets)}

    n_c = len(top_concepts)
    n_d = len(all_datasets)
    M = np.zeros((n_c, n_d), dtype=np.float32)
    for i, c in enumerate(top_concepts):
        for d in concept_datasets[c]:
            if d in ds_idx:
                M[i, ds_idx[d]] = 1

    print(f"\n[3] SVD of concept-dataset matrix ({n_c} × {n_d})...")
    U, S, Vt = np.linalg.svd(M, full_matrices=False)
    total_var = np.sum(S**2)
    cum_var = np.cumsum(S**2) / total_var

    rank_90 = int(np.searchsorted(cum_var, 0.90) + 1)
    rank_95 = int(np.searchsorted(cum_var, 0.95) + 1)
    spectral_gap = float(S[0] / S[1]) if len(S) > 1 and S[1] > 0 else 0

    print(f"  Top singular values: {[round(float(s), 2) for s in S[:10]]}")
    print(f"  Rank for 90% variance: {rank_90}/{min(n_c, n_d)}")
    print(f"  Spectral gap: {spectral_gap:.2f}")

    # Concept overlap: how many concepts span ≥3 datasets?
    multi_ds = sum(1 for c in concept_datasets if len(concept_datasets[c]) >= 3)
    multi_frac = multi_ds / len(concept_datasets) if concept_datasets else 0
    print(f"\n  Concepts spanning ≥3 datasets: {multi_ds} ({multi_frac:.1%})")

    # Bridge concentration: Gini coefficient of specificity
    sorted_spec = np.sort(specificities)
    n = len(sorted_spec)
    gini = float(2 * np.sum((np.arange(1, n+1)) * sorted_spec) / (n * np.sum(sorted_spec)) - (n+1)/n) if np.sum(sorted_spec) > 0 else 0

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-065", "title": "Complexity Entropy of Rosetta Stone",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_bridges": len(bridges),
        "n_concepts": len(concept_datasets),
        "n_datasets": len(dataset_concepts),
        "n_links_sampled": n_links,
        "entropy": {
            "H_degree": round(H_degree, 4),
            "H_degree_max": round(H_max, 4),
            "H_normalized": round(H_degree / H_max, 4),
            "H_specificity": round(H_spec, 4),
        },
        "svd": {
            "rank_90": rank_90,
            "rank_95": rank_95,
            "spectral_gap": round(spectral_gap, 2),
            "top_10_sv": [round(float(s), 2) for s in S[:10]],
        },
        "bridge_stats": {
            "specificity_mean": round(float(spec_arr.mean()), 4),
            "specificity_std": round(float(spec_arr.std()), 4),
            "gini_coefficient": round(gini, 4),
            "multi_dataset_fraction": round(multi_frac, 4),
        },
        "assessment": None,
    }

    if rank_90 < 10:
        output["assessment"] = f"LOW COMPLEXITY: rank-{rank_90} explains 90%. Rosetta Stone is highly compressible — few latent factors govern cross-domain structure"
    elif rank_90 < 50:
        output["assessment"] = f"MODERATE COMPLEXITY: rank-{rank_90}. H={H_degree:.1f} bits. Gini={gini:.2f}. Multiple independent cross-domain channels"
    else:
        output["assessment"] = f"HIGH COMPLEXITY: rank-{rank_90}. H={H_degree:.1f} bits. Rosetta Stone is nearly full-rank — each concept carries independent information"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
