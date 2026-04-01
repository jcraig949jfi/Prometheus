"""
Test 2.1 — Embedding Must Beat Raw k-NN

The zero representation passed Layer 1. Now test whether spectral embedding
adds value over raw k-NN search in zero space.

Method:
  1. Hold out 20% of known bridge pairs
  2. Build k-NN in raw zero space -> measure recovery rate (held-out MF in top-5 cross-type neighbors)
  3. Build PCA embedding -> measure recovery rate
  4. Embedding must beat raw by >= 8 percentage points

If raw k-NN already works well, embedding is unnecessary complexity.
That's a valid outcome — you have a search system without needing a landscape.

Threshold: embedding recovery >= raw recovery + 8%
Set before data: 2026-04-01
"""

import duckdb
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from collections import defaultdict
from charon.src.config import DB_PATH

np.random.seed(42)

THRESHOLD_IMPROVEMENT = 0.08  # 8 percentage points
TOP_K = 5


def load_data():
    """Load EC representatives and MFs with zero vectors, using masked zeros."""
    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # EC representatives (one per isogeny class)
    ec_rows = duck.execute("""
        SELECT ec.object_id, ec.lmfdb_iso, o.conductor, oz.zeros_vector, oz.n_zeros_stored
        FROM elliptic_curves ec
        JOIN objects o ON ec.object_id = o.id
        JOIN object_zeros oz ON ec.object_id = oz.object_id
        WHERE oz.zeros_vector IS NOT NULL
        ORDER BY ec.lmfdb_iso
    """).fetchall()

    seen = set()
    ecs = []
    for oid, iso, cond, zvec, nz in ec_rows:
        if iso in seen:
            continue
        seen.add(iso)
        ecs.append({'id': oid, 'iso': iso, 'conductor': int(cond),
                    'zvec': zvec, 'n_zeros': nz or 0, 'type': 'ec'})

    # MFs (dim-1, weight-2, trivial char)
    mf_rows = duck.execute("""
        SELECT o.id, o.lmfdb_label, o.conductor, oz.zeros_vector, oz.n_zeros_stored
        FROM objects o
        JOIN modular_forms mf ON o.id = mf.object_id
        JOIN object_zeros oz ON o.id = oz.object_id
        WHERE oz.zeros_vector IS NOT NULL
          AND mf.weight = 2 AND mf.dim = 1 AND mf.char_order = 1
    """).fetchall()

    mfs = []
    for oid, label, cond, zvec, nz in mf_rows:
        mfs.append({'id': oid, 'label': label, 'conductor': int(cond),
                    'zvec': zvec, 'n_zeros': nz or 0, 'type': 'mf'})

    # Bridges
    bridges = duck.execute("""
        SELECT source_id, target_id FROM known_bridges WHERE bridge_type = 'modularity'
    """).fetchall()
    bridge_map = {s: t for s, t in bridges}

    duck.close()
    return ecs, mfs, bridge_map


def build_vectors(objects, n_dims=20):
    """Build fixed-length vectors: first n_dims zeros (masked) + 4 metadata."""
    vectors = []
    for obj in objects:
        zvec = obj['zvec']
        n_actual = min(obj['n_zeros'], n_dims)
        # Use actual zeros, pad remainder with column mean (imputed later)
        vec = []
        for i in range(n_dims):
            if i < n_actual and zvec[i] is not None:
                vec.append(float(zvec[i]))
            else:
                vec.append(np.nan)  # mark for imputation
        # Metadata
        vec.append(float(zvec[20]) if zvec[20] is not None else 0.0)  # root_number
        vec.append(float(zvec[21]) if zvec[21] is not None else 0.0)  # analytic_rank
        vec.append(float(zvec[22]) if zvec[22] is not None else 2.0)  # degree
        vec.append(float(zvec[23]) if zvec[23] is not None else 0.0)  # log_conductor
        vectors.append(vec)

    X = np.array(vectors)
    # Impute NaN with column mean
    col_means = np.nanmean(X, axis=0)
    for j in range(X.shape[1]):
        mask = np.isnan(X[:, j])
        X[mask, j] = col_means[j]

    return X


def measure_recovery(all_objects, all_vectors, bridge_map, holdout_ec_ids, top_k=TOP_K):
    """
    For each held-out EC, find top-k cross-type nearest neighbors.
    Check if the true MF bridge partner is among them.
    """
    id_to_idx = {obj['id']: i for i, obj in enumerate(all_objects)}
    types = [obj['type'] for obj in all_objects]

    nn = NearestNeighbors(n_neighbors=min(top_k * 5, len(all_objects)), metric='euclidean', algorithm='brute')
    nn.fit(all_vectors)

    recovered = 0
    total = 0

    for ec_id in holdout_ec_ids:
        if ec_id not in id_to_idx or ec_id not in bridge_map:
            continue
        mf_id = bridge_map[ec_id]
        if mf_id not in id_to_idx:
            continue

        ec_idx = id_to_idx[ec_id]
        mf_idx = id_to_idx[mf_id]

        # Find cross-type neighbors
        dists, indices = nn.kneighbors(all_vectors[ec_idx:ec_idx+1])
        cross_type_nn = []
        for j_pos in range(indices.shape[1]):
            j = indices[0, j_pos]
            if j == ec_idx:
                continue
            if types[j] != types[ec_idx]:
                cross_type_nn.append(j)
                if len(cross_type_nn) >= top_k:
                    break

        total += 1
        if mf_idx in cross_type_nn:
            recovered += 1

    return recovered / total if total > 0 else 0.0, total


def run_test():
    print("=" * 60)
    print("TEST 2.1: EMBEDDING BEATS RAW k-NN")
    print(f"Threshold: embedding must beat raw by >= {THRESHOLD_IMPROVEMENT:.0%}")
    print("=" * 60)
    print()

    ecs, mfs, bridge_map = load_data()
    print(f"EC representatives: {len(ecs)}")
    print(f"MFs (dim-1, wt-2): {len(mfs)}")
    print(f"Known bridges: {len(bridge_map)}")

    # Hold out 20% of bridge ECs
    bridged_ec_ids = [ec['id'] for ec in ecs if ec['id'] in bridge_map]
    np.random.shuffle(bridged_ec_ids)
    n_holdout = len(bridged_ec_ids) // 5
    holdout_ids = set(bridged_ec_ids[:n_holdout])
    print(f"Holdout bridge pairs: {n_holdout}")
    print()

    # Combine all objects
    all_objects = ecs + mfs
    X_raw = build_vectors(all_objects, n_dims=20)
    print(f"Feature matrix: {X_raw.shape}")

    # Normalize columns
    means = X_raw.mean(axis=0)
    stds = X_raw.std(axis=0)
    stds[stds < 1e-10] = 1.0
    X_norm = (X_raw - means) / stds

    # ============================================================
    # RAW k-NN recovery
    # ============================================================
    print("\n--- Raw k-NN (normalized zero space) ---")
    raw_rate, raw_total = measure_recovery(all_objects, X_norm, bridge_map, holdout_ids)
    print(f"Raw recovery: {raw_rate:.1%} ({int(raw_rate * raw_total)}/{raw_total})")

    # ============================================================
    # PCA Embedding recovery (same method as before)
    # ============================================================
    for n_components in [5, 10, 16]:
        pca = PCA(n_components=n_components, random_state=42)
        X_pca = pca.fit_transform(X_norm)
        explained = pca.explained_variance_ratio_.sum()

        pca_rate, pca_total = measure_recovery(all_objects, X_pca, bridge_map, holdout_ids)
        improvement = pca_rate - raw_rate
        print(f"PCA-{n_components} recovery: {pca_rate:.1%} (var explained: {explained:.1%}, "
              f"improvement: {improvement:+.1%})")

    # ============================================================
    # Verdict
    # ============================================================
    print()
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)

    # Use best PCA result
    best_improvement = -1
    for n_components in [5, 10, 16]:
        pca = PCA(n_components=n_components, random_state=42)
        X_pca = pca.fit_transform(X_norm)
        rate, _ = measure_recovery(all_objects, X_pca, bridge_map, holdout_ids)
        imp = rate - raw_rate
        if imp > best_improvement:
            best_improvement = imp
            best_dims = n_components
            best_rate = rate

    print(f"Raw k-NN recovery:     {raw_rate:.1%}")
    print(f"Best embedding (PCA-{best_dims}): {best_rate:.1%}")
    print(f"Improvement: {best_improvement:+.1%} (threshold: >= +{THRESHOLD_IMPROVEMENT:.0%})")
    print()

    if best_improvement >= THRESHOLD_IMPROVEMENT:
        print(f"TEST 2.1: PASSED — Embedding adds {best_improvement:.1%} over raw k-NN")
    elif best_improvement >= 0:
        print(f"TEST 2.1: FAILED — Embedding improves only {best_improvement:.1%} (< {THRESHOLD_IMPROVEMENT:.0%})")
        print("Raw zero-space k-NN may be sufficient. Embedding is not adding enough value.")
        print("Consider: vector search database instead of spectral landscape.")
    else:
        print(f"TEST 2.1: FAILED — Embedding is WORSE than raw k-NN by {-best_improvement:.1%}")
        print("Embedding is destroying signal. Do not build a spectral landscape.")

    return best_improvement >= THRESHOLD_IMPROVEMENT


if __name__ == "__main__":
    run_test()
