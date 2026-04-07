"""
Tensor Bridge — Cross-domain bridge detection via sparse tensor search.
========================================================================
python tensor_bridge.py [--top K] [--min-shared N] [--out PATH]

Replaces LLM hypothesis generation with structural search over the
concept index.  Builds a sparse 3-axis tensor (dataset x object x concept),
multiplies slices to find shared-concept bridges between dataset pairs,
scores them by specificity, and decomposes via SVD.

Runtime: ~10 seconds for 359K links / 12K concepts.
Cost: $0.  Discoveries: all structural bridges, simultaneously.
"""

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy import sparse

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parents[2] / "convergence" / "data"
LINKS_PATH = DATA_DIR / "concept_links.jsonl"
OUTPUT_PATH = DATA_DIR / "tensor_bridges.json"


# ---------------------------------------------------------------------------
# 1. Load concept links and build index mappings
# ---------------------------------------------------------------------------

def load_links(path: Path):
    """
    Read concept_links.jsonl and return:
      - links: list of (dataset, object_id, concept) tuples
      - dataset_idx: {name: int}
      - object_idx:  {(dataset, object_id): int}
      - concept_idx: {concept_name: int}
    """
    links = []
    datasets = set()
    objects = set()
    concepts = set()

    with open(path) as f:
        for line in f:
            rec = json.loads(line)
            ds = rec["dataset"]
            obj = rec["object_id"]
            con = rec["concept"]
            links.append((ds, obj, con))
            datasets.add(ds)
            objects.add((ds, obj))
            concepts.add(con)

    dataset_idx = {d: i for i, d in enumerate(sorted(datasets))}
    object_idx = {o: i for i, o in enumerate(sorted(objects))}
    concept_idx = {c: i for i, c in enumerate(sorted(concepts))}

    print(f"Loaded {len(links):,} links")
    print(f"  datasets: {len(dataset_idx)} — {sorted(dataset_idx)}")
    print(f"  objects:  {len(object_idx):,}")
    print(f"  concepts: {len(concept_idx):,}")

    return links, dataset_idx, object_idx, concept_idx


# ---------------------------------------------------------------------------
# 2. Build per-dataset sparse matrices (object x concept)
# ---------------------------------------------------------------------------

def build_dataset_matrices(links, dataset_idx, object_idx, concept_idx):
    """
    Build one sparse CSR matrix per dataset: shape (n_objects_global, n_concepts).
    Only rows corresponding to objects in that dataset are populated.

    Returns:
      - matrices: {dataset_name: sparse.csr_matrix}  shape (n_objects, n_concepts)
      - ds_objects: {dataset_name: sorted list of global object indices in that dataset}
    """
    n_obj = len(object_idx)
    n_con = len(concept_idx)

    # Collect COO entries per dataset
    ds_rows = defaultdict(list)   # dataset -> list of row indices (object)
    ds_cols = defaultdict(list)   # dataset -> list of col indices (concept)

    for ds, obj, con in links:
        r = object_idx[(ds, obj)]
        c = concept_idx[con]
        ds_rows[ds].append(r)
        ds_cols[ds].append(c)

    matrices = {}
    ds_objects = {}
    for ds in sorted(dataset_idx):
        rows = np.array(ds_rows[ds], dtype=np.int32)
        cols = np.array(ds_cols[ds], dtype=np.int32)
        data = np.ones(len(rows), dtype=np.float32)
        mat = sparse.csr_matrix((data, (rows, cols)), shape=(n_obj, n_con))
        # Deduplicate: clip values to 1 (in case of repeated links)
        mat.data[:] = 1.0
        matrices[ds] = mat
        ds_objects[ds] = sorted(set(rows.tolist()))
        nnz = mat.nnz
        print(f"  {ds:12s}: {len(ds_objects[ds]):>6,} objects, {nnz:>8,} entries "
              f"(density {nnz / (len(ds_objects[ds]) * n_con) * 100:.3f}%)")

    return matrices, ds_objects


# ---------------------------------------------------------------------------
# 3. Compute concept frequency (for specificity scoring)
# ---------------------------------------------------------------------------

def compute_concept_freq(links, concept_idx):
    """
    concept_freq[i] = number of distinct objects that have concept i.
    """
    freq = np.zeros(len(concept_idx), dtype=np.float64)
    # Count distinct (dataset, object) per concept
    seen = defaultdict(set)
    for ds, obj, con in links:
        seen[con].add((ds, obj))
    for con, objs in seen.items():
        freq[concept_idx[con]] = len(objs)
    return freq


# ---------------------------------------------------------------------------
# 4. Find top bridges between dataset pairs
# ---------------------------------------------------------------------------

def find_bridges(matrices, ds_objects, dataset_idx, object_idx, concept_idx,
                 concept_freq, top_k=50, min_shared=2):
    """
    For each pair of datasets (d1, d2), compute the bridge matrix:
        B = M[d1] @ M[d2].T   (objects_d1 x objects_d2, values = shared concepts)

    Extract top-K object pairs across all dataset pairs, scored by
    n_shared * specificity.

    Returns list of bridge dicts sorted by score descending.
    """
    inv_obj = {v: k for k, v in object_idx.items()}
    inv_con = {v: k for k, v in concept_idx.items()}

    all_bridges = []
    ds_names = sorted(dataset_idx)

    for d1, d2 in combinations(ds_names, 2):
        M1 = matrices[d1]   # (n_obj_global, n_concepts)
        M2 = matrices[d2]

        # Restrict to rows that belong to each dataset for efficiency
        rows1 = ds_objects[d1]
        rows2 = ds_objects[d2]
        if not rows1 or not rows2:
            continue

        # Submatrix: only rows for objects in each dataset
        S1 = M1[rows1, :]   # (|d1|, n_concepts)
        S2 = M2[rows2, :]   # (|d2|, n_concepts)

        # Bridge matrix: shared concept counts
        B = S1 @ S2.T       # (|d1|, |d2|), sparse

        # Extract entries above threshold, keep only top candidates
        B_coo = B.tocoo()
        mask = B_coo.data >= min_shared
        if not mask.any():
            continue

        r_all = B_coo.row[mask]
        c_all = B_coo.col[mask]
        vals_all = B_coo.data[mask]

        print(f"  {d1}--{d2}: {len(r_all):,} pairs above threshold")

        # Pre-filter: keep only top candidates by raw shared count
        # (score can only be higher for higher n_shared given same specificity)
        n_keep = min(len(r_all), top_k * 10)  # generous margin
        if len(r_all) > n_keep:
            top_idx = np.argpartition(vals_all, -n_keep)[-n_keep:]
        else:
            top_idx = np.arange(len(r_all))

        r = r_all[top_idx]
        c = c_all[top_idx]
        vals = vals_all[top_idx]

        for idx in range(len(r)):
            gi = rows1[r[idx]]   # global object index for d1
            gj = rows2[c[idx]]   # global object index for d2
            n_shared = int(vals[idx])

            # Identify shared concepts
            v1 = M1[gi, :].toarray().ravel()
            v2 = M2[gj, :].toarray().ravel()
            shared_mask = (v1 > 0) & (v2 > 0)
            shared_concept_ids = np.where(shared_mask)[0]
            shared_concepts = [inv_con[ci] for ci in shared_concept_ids]

            # Specificity: 1 / mean(freq) for shared concepts
            freqs = concept_freq[shared_concept_ids]
            specificity = 1.0 / freqs.mean() if freqs.mean() > 0 else 0.0

            # Uniqueness: fraction of shared concepts with freq <= 10
            uniqueness = float((freqs <= 10).sum()) / len(freqs) if len(freqs) > 0 else 0.0

            score = n_shared * specificity

            ds1_name, obj1_id = inv_obj[gi]
            ds2_name, obj2_id = inv_obj[gj]

            all_bridges.append({
                "dataset1": ds1_name,
                "object1": obj1_id,
                "dataset2": ds2_name,
                "object2": obj2_id,
                "n_shared_concepts": n_shared,
                "shared_concepts": shared_concepts,
                "specificity": round(specificity, 6),
                "uniqueness": round(uniqueness, 4),
                "score": round(score, 6),
            })

    # Sort by score descending, take top K
    all_bridges.sort(key=lambda b: b["score"], reverse=True)
    return all_bridges[:top_k]


# ---------------------------------------------------------------------------
# 5. Generate hypothesis dicts (compatible with research_cycle.py)
# ---------------------------------------------------------------------------

def bridges_to_hypotheses(bridges):
    """
    Convert scored bridges into hypothesis dicts for the research cycle.
    """
    hypotheses = []
    for b in bridges:
        top_concepts = b["shared_concepts"][:5]
        concept_str = ", ".join(top_concepts)
        n = b["n_shared_concepts"]

        hyp = {
            "hypothesis": (
                f"Objects {b['object1']} ({b['dataset1']}) and "
                f"{b['object2']} ({b['dataset2']}) share {n} concepts "
                f"including {concept_str}. "
                f"Their deeper invariants may correlate."
            ),
            "searches": [
                {"dataset": b["dataset1"], "query": b["object1"]},
                {"dataset": b["dataset2"], "query": b["object2"]},
            ],
            "falsification": "No correlation beyond shared concepts",
            "source": "tensor_bridge",
            "score": b["score"],
        }
        hypotheses.append(hyp)
    return hypotheses


# ---------------------------------------------------------------------------
# 6. SVD decomposition of bridge matrices — bond dimension analysis
# ---------------------------------------------------------------------------

def svd_bridge_analysis(matrices, ds_objects, dataset_idx,
                        energy_threshold=0.95, max_rank=50):
    """
    For each dataset pair, SVD the (dense, subsampled if needed) bridge matrix.
    Bond dimension = number of singular values capturing `energy_threshold`
    of the total energy (sum of squared singular values).

    Low bond dimension  -> simple, direct bridge (few shared concept axes).
    High bond dimension -> complex, multi-step bridge.

    Returns dict: {(d1, d2): {"bond_dim": int, "top_sv": list, "shape": (m, n)}}
    """
    ds_names = sorted(dataset_idx)
    results = {}

    for d1, d2 in combinations(ds_names, 2):
        rows1 = ds_objects[d1]
        rows2 = ds_objects[d2]
        if not rows1 or not rows2:
            continue

        S1 = matrices[d1][rows1, :]
        S2 = matrices[d2][rows2, :]

        # For very large pairs, subsample to keep SVD tractable
        max_dim = 2000
        if len(rows1) > max_dim:
            idx1 = np.random.choice(len(rows1), max_dim, replace=False)
            S1 = S1[idx1, :]
        if len(rows2) > max_dim:
            idx2 = np.random.choice(len(rows2), max_dim, replace=False)
            S2 = S2[idx2, :]

        B = (S1 @ S2.T).toarray().astype(np.float64)
        m, n = B.shape

        # Truncated SVD: only compute up to max_rank singular values
        k = min(max_rank, m, n)
        if k == 0:
            continue

        try:
            from scipy.sparse.linalg import svds
            # svds requires k < min(m, n)
            if k >= min(m, n):
                U, s, Vt = np.linalg.svd(B, full_matrices=False)
                s = s[:max_rank]
            else:
                U, s, Vt = svds(sparse.csr_matrix(B), k=k)
                s = np.sort(s)[::-1]  # svds returns ascending
        except Exception:
            U, s, Vt = np.linalg.svd(B, full_matrices=False)
            s = s[:max_rank]

        # Bond dimension: how many SVs to capture threshold of energy
        energy = np.cumsum(s ** 2)
        total_energy = energy[-1] if len(energy) > 0 else 0
        if total_energy > 0:
            bond_dim = int(np.searchsorted(energy / total_energy, energy_threshold)) + 1
        else:
            bond_dim = 0

        pair_key = f"{d1}--{d2}"
        results[pair_key] = {
            "bond_dim": bond_dim,
            "shape": [int(m), int(n)],
            "top_singular_values": [round(float(v), 4) for v in s[:10]],
            "energy_95pct_rank": bond_dim,
        }
        print(f"  {pair_key:30s}: bond_dim={bond_dim:3d}  "
              f"shape=({m:>5d} x {n:>5d})  "
              f"top_sv={s[0]:.2f}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Tensor Bridge: structural cross-domain search")
    parser.add_argument("--top", type=int, default=50, help="Number of top bridges to report")
    parser.add_argument("--min-shared", type=int, default=2, help="Minimum shared concepts for a bridge")
    parser.add_argument("--out", type=str, default=str(OUTPUT_PATH), help="Output JSON path")
    args = parser.parse_args()

    t0 = time.time()

    # Step 1: Load
    print("=" * 60)
    print("TENSOR BRIDGE — Cross-domain structural search")
    print("=" * 60)
    links, dataset_idx, object_idx, concept_idx = load_links(LINKS_PATH)

    # Step 2: Build sparse matrices
    print(f"\nBuilding per-dataset sparse matrices...")
    matrices, ds_objects = build_dataset_matrices(links, dataset_idx, object_idx, concept_idx)

    # Step 3: Concept frequencies
    print(f"\nComputing concept frequencies...")
    concept_freq = compute_concept_freq(links, concept_idx)
    print(f"  median freq: {np.median(concept_freq):.0f}, "
          f"max freq: {concept_freq.max():.0f}, "
          f"concepts with freq=1: {(concept_freq == 1).sum():,}")

    # Step 4: Find bridges
    print(f"\nFinding top {args.top} bridges (min_shared={args.min_shared})...")
    bridges = find_bridges(
        matrices, ds_objects, dataset_idx, object_idx, concept_idx,
        concept_freq, top_k=args.top, min_shared=args.min_shared,
    )
    print(f"  Found {len(bridges)} bridges")

    # Step 5: Print top bridges
    print(f"\n{'='*60}")
    print(f"TOP BRIDGES")
    print(f"{'='*60}")
    for i, b in enumerate(bridges[:20]):
        concepts_preview = ", ".join(b["shared_concepts"][:4])
        if len(b["shared_concepts"]) > 4:
            concepts_preview += f" +{len(b['shared_concepts'])-4} more"
        print(f"  {i+1:3d}. [{b['score']:8.4f}] "
              f"{b['object1']:20s} ({b['dataset1']:10s}) <-> "
              f"{b['object2']:20s} ({b['dataset2']:10s}) "
              f"| {b['n_shared_concepts']} shared: {concepts_preview}")

    # Step 6: SVD analysis
    print(f"\n{'='*60}")
    print(f"SVD BOND DIMENSION ANALYSIS")
    print(f"{'='*60}")
    svd_results = svd_bridge_analysis(matrices, ds_objects, dataset_idx)

    # Step 7: Generate hypotheses
    hypotheses = bridges_to_hypotheses(bridges)

    # Step 8: Save
    elapsed = time.time() - t0
    output = {
        "meta": {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_links": len(links),
            "n_datasets": len(dataset_idx),
            "n_objects": len(object_idx),
            "n_concepts": len(concept_idx),
            "top_k": args.top,
            "min_shared": args.min_shared,
            "elapsed_seconds": round(elapsed, 2),
        },
        "bridges": bridges,
        "hypotheses": hypotheses,
        "svd_bond_dimensions": svd_results,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Done in {elapsed:.1f}s — saved {len(bridges)} bridges to {out_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
