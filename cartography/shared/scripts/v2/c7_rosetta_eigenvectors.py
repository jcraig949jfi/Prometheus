"""
Challenge 7: Deconstruct the Rosetta Rank-3 Tensor
=====================================================
Extract the 3 principal eigenvectors from the concept-dataset matrix.
Cross-reference against operadic verb structure. Define the semantic
meaning of the three fundamental modes of mathematical translation.
"""
import json, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
BRIDGES = V2.parents[3] / "cartography" / "convergence" / "data" / "bridges.jsonl"
LINKS = V2.parents[3] / "cartography" / "convergence" / "data" / "concept_links.jsonl"
OUT = V2 / "c7_rosetta_eigenvectors_results.json"

def main():
    t0 = time.time()
    print("=== C7: Deconstruct the Rosetta Rank-3 Tensor ===\n")

    # Load concept-dataset links (sample)
    print("[1] Loading concept-dataset links...")
    concept_datasets = defaultdict(set)
    dataset_concepts = defaultdict(set)
    concept_meta = {}
    n = 0
    with open(LINKS) as f:
        for line in f:
            if n >= 500000: break
            line = line.strip()
            if not line: continue
            try:
                r = json.loads(line)
                c = r.get("concept", "")
                d = r.get("dataset", "")
                if c and d:
                    concept_datasets[c].add(d)
                    dataset_concepts[d].add(c)
                    if c not in concept_meta:
                        concept_meta[c] = {k: v for k, v in r.items() if k not in ("concept", "dataset")}
                n += 1
            except: pass
    print(f"  {n} links, {len(concept_datasets)} concepts, {len(dataset_concepts)} datasets")

    # Build matrix
    top_concepts = sorted(concept_datasets.keys(), key=lambda c: -len(concept_datasets[c]))[:500]
    all_datasets = sorted(dataset_concepts.keys())
    ds_idx = {d: i for i, d in enumerate(all_datasets)}
    M = np.zeros((len(top_concepts), len(all_datasets)), dtype=np.float32)
    for i, c in enumerate(top_concepts):
        for d in concept_datasets[c]:
            if d in ds_idx:
                M[i, ds_idx[d]] = 1

    print(f"\n[2] SVD of {M.shape[0]}×{M.shape[1]} matrix...")
    U, S, Vt = np.linalg.svd(M, full_matrices=False)
    total_var = np.sum(S**2)
    cum_var = np.cumsum(S**2) / total_var
    print(f"  Singular values: {[round(float(s), 2) for s in S[:10]]}")
    print(f"  Cumulative: {[round(float(c), 4) for c in cum_var[:5]]}")

    # Extract the 3 eigenvectors
    modes = []
    for mode_idx in range(3):
        # Top concepts loading on this mode
        concept_loadings = [(top_concepts[i], float(U[i, mode_idx])) for i in range(len(top_concepts))]
        concept_loadings.sort(key=lambda x: -abs(x[1]))
        top_pos = [(c, l) for c, l in concept_loadings if l > 0][:15]
        top_neg = [(c, l) for c, l in concept_loadings if l < 0][:15]

        # Top datasets loading on this mode
        dataset_loadings = [(all_datasets[j], float(Vt[mode_idx, j])) for j in range(len(all_datasets))]
        dataset_loadings.sort(key=lambda x: -abs(x[1]))

        print(f"\n  === MODE {mode_idx+1} (σ={S[mode_idx]:.2f}, explains {S[mode_idx]**2/total_var:.1%}) ===")
        print(f"  Top positive concepts:")
        for c, l in top_pos[:8]:
            print(f"    {c}: {l:.4f}")
        print(f"  Top negative concepts:")
        for c, l in top_neg[:8]:
            print(f"    {c}: {l:.4f}")
        print(f"  Dataset loadings:")
        for d, l in dataset_loadings[:13]:
            print(f"    {d}: {l:.4f}")

        # Classify the mode by its concept content
        pos_concepts = set(c for c, _ in top_pos[:20])
        neg_concepts = set(c for c, _ in top_neg[:20])

        mode_info = {
            "mode": mode_idx + 1,
            "sigma": round(float(S[mode_idx]), 4),
            "variance_explained": round(float(S[mode_idx]**2/total_var), 4),
            "top_positive_concepts": [(c, round(l, 4)) for c, l in top_pos[:15]],
            "top_negative_concepts": [(c, round(l, 4)) for c, l in top_neg[:15]],
            "dataset_loadings": [(d, round(l, 4)) for d, l in dataset_loadings],
        }
        modes.append(mode_info)

    # Verb-like classification of concepts
    print("\n[3] Concept verb classification...")
    verb_by_mode = {1: Counter(), 2: Counter(), 3: Counter()}
    for mode_idx in range(3):
        top_all = [(top_concepts[i], float(U[i, mode_idx])) for i in range(len(top_concepts))]
        top_all.sort(key=lambda x: -abs(x[1]))
        for c, l in top_all[:50]:
            c_lower = c.lower()
            if any(w in c_lower for w in ['equal', 'identity', 'formula', 'relation', 'equation']):
                verb_by_mode[mode_idx+1]["Equal"] += 1
            elif any(w in c_lower for w in ['and', 'intersection', 'joint', 'both', 'mutual']):
                verb_by_mode[mode_idx+1]["And"] += 1
            elif any(w in c_lower for w in ['set', 'collection', 'class', 'family', 'group']):
                verb_by_mode[mode_idx+1]["Set"] += 1
            elif any(w in c_lower for w in ['map', 'transform', 'function', 'morphism', 'operation']):
                verb_by_mode[mode_idx+1]["Map"] += 1
            else:
                verb_by_mode[mode_idx+1]["Other"] += 1

    for m in [1, 2, 3]:
        print(f"  Mode {m} verb dist: {dict(verb_by_mode[m])}")

    # Mode interpretation
    interpretations = []
    for mode_info in modes:
        pos = [c for c, _ in mode_info["top_positive_concepts"][:10]]
        neg = [c for c, _ in mode_info["top_negative_concepts"][:10]]
        ds = [(d, l) for d, l in mode_info["dataset_loadings"][:5]]
        interpretations.append(f"Mode {mode_info['mode']}: {mode_info['variance_explained']:.0%} variance. "
                             f"Pos={pos[:3]}, Neg={neg[:3]}, Datasets={[d for d,_ in ds[:3]]}")

    elapsed = time.time() - t0
    output = {
        "challenge": "C7", "title": "Rosetta Rank-3 Eigenvectors",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_concepts": len(concept_datasets),
        "n_datasets": len(dataset_concepts),
        "matrix_shape": list(M.shape),
        "modes": modes,
        "verb_by_mode": {str(k): dict(v) for k, v in verb_by_mode.items()},
        "interpretations": interpretations,
        "assessment": None,
    }
    output["assessment"] = " | ".join(interpretations)

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
