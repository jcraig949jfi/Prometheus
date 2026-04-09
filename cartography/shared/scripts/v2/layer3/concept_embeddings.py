"""Layer 3: Spectral embedding of the concept graph."""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

DATA = Path(__file__).resolve().parents[4] / "convergence" / "data"
CONCEPTS_FILE = DATA / "concepts.jsonl"
BRIDGES_FILE = DATA / "bridges.jsonl"


def load_concepts(bridges_only=False):
    """Load concepts. If bridges_only, keep only those in bridges.jsonl."""
    bridge_ids = None
    if bridges_only:
        bridge_ids = set()
        with open(BRIDGES_FILE) as f:
            for line in f:
                bridge_ids.add(json.loads(line)["concept"])

    concepts = []
    with open(CONCEPTS_FILE) as f:
        for line in f:
            rec = json.loads(line)
            if bridge_ids is None or rec["id"] in bridge_ids:
                concepts.append(rec)
    return concepts


def build_adjacency(concepts):
    """Build sparse adjacency: concepts sharing a source are connected.
    Weight = 1 for same-source, bridge concepts get bonus from bridges.jsonl."""
    t0 = time.time()
    id2idx = {c["id"]: i for i, c in enumerate(concepts)}
    n = len(concepts)

    # Group concepts by source
    source_groups = defaultdict(list)
    for i, c in enumerate(concepts):
        source_groups[c["source"]].append(i)

    print(f"  {len(source_groups)} source groups, building edges...")

    # Build edges via co-source membership
    rows, cols, vals = [], [], []
    for src, members in source_groups.items():
        if len(members) > 5000:
            # Very large groups: sample random pairs instead of O(n^2)
            print(f"  Source '{src}' has {len(members)} concepts, sampling edges...")
            rng = np.random.default_rng(42)
            n_edges = min(len(members) * 20, 200000)
            for _ in range(n_edges):
                i, j = rng.choice(len(members), 2, replace=False)
                a, b = members[i], members[j]
                rows.extend([a, b])
                cols.extend([b, a])
                vals.extend([1, 1])
        else:
            # Full pairwise for small groups
            for ki in range(len(members)):
                for kj in range(ki + 1, len(members)):
                    a, b = members[ki], members[kj]
                    rows.extend([a, b])
                    cols.extend([b, a])
                    vals.extend([1, 1])

    # Load bridge info for cross-dataset edges
    bridge_datasets = {}
    if BRIDGES_FILE.exists():
        with open(BRIDGES_FILE) as f:
            for line in f:
                rec = json.loads(line)
                cid = rec["concept"]
                if cid in id2idx:
                    bridge_datasets[id2idx[cid]] = list(rec["datasets"].keys())

    # Connect bridge concepts that share datasets
    bridge_indices = list(bridge_datasets.keys())
    bridge_by_ds = defaultdict(list)
    for idx in bridge_indices:
        for ds in bridge_datasets[idx]:
            bridge_by_ds[ds].append(idx)

    n_bridge_edges = 0
    for ds, members in bridge_by_ds.items():
        if len(members) > 2000:
            continue  # skip huge groups
        for ki in range(len(members)):
            for kj in range(ki + 1, len(members)):
                a, b = members[ki], members[kj]
                rows.extend([a, b])
                cols.extend([b, a])
                vals.extend([2, 2])  # higher weight for bridge edges
                n_bridge_edges += 1

    print(f"  {len(rows)//2} total edges ({n_bridge_edges} bridge), {time.time()-t0:.1f}s")

    A = sparse.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
    # Collapse duplicates by summing
    A.sum_duplicates()
    return A


def spectral_embed(A, k=64):
    """Compute spectral embedding from adjacency matrix."""
    t0 = time.time()
    n = A.shape[0]

    # Degree matrix
    degrees = np.array(A.sum(axis=1)).flatten().astype(float)
    degrees[degrees == 0] = 1.0  # avoid division by zero for isolated nodes

    # Normalized Laplacian: L = I - D^{-1/2} A D^{-1/2}
    d_inv_sqrt = 1.0 / np.sqrt(degrees)
    D_inv_sqrt = sparse.diags(d_inv_sqrt)
    L = sparse.eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

    # Bottom-k+1 eigenvectors (skip first trivial one)
    n_eigs = min(k + 1, n - 1)
    print(f"  Computing {n_eigs} eigenvectors of {n}x{n} Laplacian...")
    eigenvalues, eigenvectors = eigsh(L, k=n_eigs, which='SM', maxiter=5000, tol=1e-6)

    # Sort by eigenvalue
    order = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    # Skip trivial first eigenvector
    embedding = eigenvectors[:, 1:k+1]

    print(f"  Eigenvalue range: [{eigenvalues[1]:.6f}, {eigenvalues[min(k, len(eigenvalues)-1)]:.6f}]")
    print(f"  Spectral embedding: {embedding.shape}, {time.time()-t0:.1f}s")
    return embedding


def compute_metadata(concepts, embedding, A):
    """Compute per-concept metadata: centroid_distance, local_density, edge_count."""
    from sklearn.neighbors import NearestNeighbors

    t0 = time.time()
    centroid = embedding.mean(axis=0)
    dists_to_centroid = np.linalg.norm(embedding - centroid, axis=1)

    # Local density via k=10 NN
    k_nn = min(10, embedding.shape[0] - 1)
    nn = NearestNeighbors(n_neighbors=k_nn + 1, metric='euclidean')
    nn.fit(embedding)
    distances, _ = nn.kneighbors(embedding)
    # Skip self (index 0), mean of k neighbors
    local_density = distances[:, 1:].mean(axis=1)

    # Edge count per node
    edge_counts = np.array(A.getnnz(axis=1)).flatten()

    metadata = []
    for i, c in enumerate(concepts):
        metadata.append({
            "id": c["id"],
            "type": c["type"],
            "source": c["source"],
            "centroid_distance": round(float(dists_to_centroid[i]), 6),
            "local_density": round(float(local_density[i]), 6),
            "edge_count": int(edge_counts[i]),
        })

    print(f"  Metadata computed, {time.time()-t0:.1f}s")
    return metadata


def main():
    parser = argparse.ArgumentParser(description="Spectral embedding of concept graph")
    parser.add_argument("--k", type=int, default=64, help="Embedding dimension")
    parser.add_argument("--bridges-only", action="store_true", help="Only embed bridge concepts (fast mode)")
    args = parser.parse_args()

    t_total = time.time()

    print(f"Loading concepts (bridges_only={args.bridges_only})...")
    concepts = load_concepts(bridges_only=args.bridges_only)
    print(f"  {len(concepts)} concepts loaded")

    print("Building adjacency matrix...")
    A = build_adjacency(concepts)

    print("Computing spectral embedding...")
    embedding = spectral_embed(A, k=args.k)

    print("Computing metadata...")
    metadata = compute_metadata(concepts, embedding, A)

    # Save
    out_vectors = DATA / "concept_vectors.npy"
    out_ids = DATA / "concept_ids.json"
    out_meta = DATA / "concept_metadata.jsonl"

    np.save(out_vectors, embedding)
    print(f"  Saved {out_vectors} ({embedding.shape})")

    concept_ids = [c["id"] for c in concepts]
    with open(out_ids, "w") as f:
        json.dump(concept_ids, f)
    print(f"  Saved {out_ids} ({len(concept_ids)} ids)")

    with open(out_meta, "w") as f:
        for m in metadata:
            f.write(json.dumps(m) + "\n")
    print(f"  Saved {out_meta}")

    # Summary
    dists = [m["centroid_distance"] for m in metadata]
    densities = [m["local_density"] for m in metadata]
    edges = [m["edge_count"] for m in metadata]
    print(f"\nSummary:")
    print(f"  Centroid distance: mean={np.mean(dists):.4f}, std={np.std(dists):.4f}")
    print(f"  Local density:     mean={np.mean(densities):.4f}, std={np.std(densities):.4f}")
    print(f"  Edge count:        mean={np.mean(edges):.1f}, max={np.max(edges)}")
    print(f"  Total time: {time.time()-t_total:.1f}s")


if __name__ == "__main__":
    main()
