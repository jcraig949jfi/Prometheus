"""
Type B Candidate Characterization
==================================
Analyze the 27,279 objects that form tight zero-space clusters
but have NO graph edges. What are they? What are they clustered with?
"""

import duckdb
import numpy as np
import json
import logging
from collections import defaultdict, Counter
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.typeb')


def run():
    log.info("=" * 60)
    log.info("TYPE B CANDIDATE CHARACTERIZATION")
    log.info("=" * 60)

    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # ============================================================
    # 1. Load Type B objects
    # ============================================================
    log.info("\n--- Loading Type B candidates ---")

    type_b = duck.execute("""
        SELECT da.object_id, da.label, da.object_type, da.conductor,
               da.rank, da.torsion, da.cm, da.zero_coherence,
               oz.zeros_vector, oz.n_zeros_stored
        FROM disagreement_atlas da
        JOIN object_zeros oz ON da.object_id = oz.object_id
        WHERE da.disagreement_type = 'B'
        ORDER BY da.zero_coherence
    """).fetchall()

    log.info(f"Type B candidates: {len(type_b)}")
    type_counts = Counter(r[2] for r in type_b)
    log.info(f"Object types: {dict(type_counts)}")

    conductors = [r[3] for r in type_b]
    log.info(f"Conductor range: {min(conductors)} - {max(conductors)}")
    log.info(f"Unique conductors: {len(set(conductors))}")

    ranks = [r[4] for r in type_b if r[4] is not None]
    if ranks:
        log.info(f"Rank distribution (ECs): {dict(Counter(ranks))}")
    else:
        log.info("No ECs in Type B (all MFs)")

    # ============================================================
    # 2. Load ALL objects for neighbor analysis
    # ============================================================
    log.info("\n--- Loading all objects ---")

    all_rows = duck.execute("""
        SELECT oz.object_id, o.object_type, o.conductor, o.lmfdb_label,
               oz.zeros_vector, oz.n_zeros_stored,
               da.disagreement_type
        FROM object_zeros oz
        JOIN objects o ON oz.object_id = o.id
        LEFT JOIN disagreement_atlas da ON oz.object_id = da.object_id
        WHERE oz.zeros_vector IS NOT NULL
    """).fetchall()

    mf_meta = {}
    for row in duck.execute("""
        SELECT mf.object_id, mf.lmfdb_label, mf.level, mf.weight, mf.dim,
               mf.char_order, mf.is_cm
        FROM modular_forms mf
    """).fetchall():
        mf_meta[row[0]] = {'label': row[1], 'level': row[2], 'weight': row[3],
                           'dim': row[4], 'char_order': row[5], 'is_cm': row[6]}

    ec_meta = {}
    for row in duck.execute("""
        SELECT ec.object_id, ec.lmfdb_label, ec.lmfdb_iso, ec.rank, ec.torsion, ec.cm
        FROM elliptic_curves ec
    """).fetchall():
        ec_meta[row[0]] = {'label': row[1], 'iso': row[2], 'rank': row[3],
                           'torsion': row[4], 'cm': row[5]}

    duck.close()

    obj_list = []
    for oid, otype, cond, label, zvec, nz, dtype in all_rows:
        n = min(nz or 0, 20)
        vec = [float(zvec[i]) if i < n and zvec[i] is not None else 0.0 for i in range(20)]
        obj_list.append({
            'id': oid, 'type': otype, 'conductor': int(cond), 'label': label,
            'vec': np.array(vec), 'atlas_type': dtype
        })

    id_to_idx = {o['id']: i for i, o in enumerate(obj_list)}
    X = np.array([o['vec'] for o in obj_list])
    means = X.mean(axis=0)
    stds = X.std(axis=0)
    stds[stds < 1e-10] = 1.0
    X_norm = (X - means) / stds

    log.info(f"Total objects: {len(obj_list)}")

    # ============================================================
    # 3. Analyze Type B neighborhoods
    # ============================================================
    log.info("\n--- Analyzing Type B neighborhoods ---")

    type_b_ids = set(r[0] for r in type_b)
    type_b_indices = [id_to_idx[oid] for oid in type_b_ids if oid in id_to_idx]

    nn = NearestNeighbors(n_neighbors=11, metric='euclidean', algorithm='brute')
    nn.fit(X_norm)
    _, nn_indices = nn.kneighbors(X_norm[type_b_indices])

    cross_conductor = 0
    same_conductor = 0
    neighbor_types = Counter()
    neighbor_atlas_types = Counter()
    has_ec_neighbor = 0
    cross_cond_examples = []

    for i, tb_idx in enumerate(type_b_indices):
        tb_obj = obj_list[tb_idx]
        tb_cond = tb_obj['conductor']

        neighbors = []
        for j_pos in range(1, nn_indices.shape[1]):
            n_idx = nn_indices[i, j_pos]
            n_obj = obj_list[n_idx]
            neighbors.append(n_obj)
            neighbor_types[n_obj['type']] += 1
            at = n_obj.get('atlas_type')
            if at:
                neighbor_atlas_types[at] += 1

        n_conds = set(n['conductor'] for n in neighbors)
        if len(n_conds) > 1 or tb_cond not in n_conds:
            cross_conductor += 1
            if len(cross_cond_examples) < 50:
                cross_cond_examples.append({
                    'source': tb_obj['label'], 'source_cond': tb_cond,
                    'neighbor_conds': sorted(n_conds),
                    'n_unique_conds': len(n_conds | {tb_cond}),
                })
        else:
            same_conductor += 1

        if any(n['type'] == 'elliptic_curve' for n in neighbors):
            has_ec_neighbor += 1

    n_tb = len(type_b_indices)
    log.info(f"Cross-conductor: {cross_conductor} ({cross_conductor/n_tb*100:.1f}%)")
    log.info(f"Same-conductor: {same_conductor} ({same_conductor/n_tb*100:.1f}%)")
    log.info(f"Has EC neighbor: {has_ec_neighbor}")
    log.info(f"Neighbor types: {dict(neighbor_types)}")
    log.info(f"Neighbor atlas types: {dict(neighbor_atlas_types)}")

    # ============================================================
    # 4. Cluster Type B objects
    # ============================================================
    log.info("\n--- Clustering Type B objects (DBSCAN) ---")

    X_tb = X_norm[type_b_indices]
    dbscan = DBSCAN(eps=0.5, min_samples=3)
    cluster_labels = dbscan.fit_predict(X_tb)

    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = (cluster_labels == -1).sum()
    cluster_sizes = Counter(cluster_labels)
    if -1 in cluster_sizes:
        del cluster_sizes[-1]

    log.info(f"Clusters: {n_clusters}")
    log.info(f"Noise: {n_noise} ({n_noise/n_tb*100:.1f}%)")
    if cluster_sizes:
        sizes = sorted(cluster_sizes.values(), reverse=True)
        log.info(f"Size range: {sizes[0]} - {sizes[-1]}")
        log.info(f"Top 10 sizes: {sizes[:10]}")

    # ============================================================
    # 5. Analyze top clusters
    # ============================================================
    log.info("\n--- Top clusters ---")

    top_clusters = sorted(cluster_sizes.items(), key=lambda x: -x[1])[:15]
    for cl_id, cl_size in top_clusters:
        members = [type_b_indices[i] for i in range(len(cluster_labels)) if cluster_labels[i] == cl_id]
        member_objs = [obj_list[idx] for idx in members]

        conds = [o['conductor'] for o in member_objs]
        unique_conds = len(set(conds))

        dims = [mf_meta.get(o['id'], {}).get('dim') for o in member_objs]
        dims = [d for d in dims if d is not None]
        char_orders = [mf_meta.get(o['id'], {}).get('char_order') for o in member_objs]
        char_orders = [c for c in char_orders if c is not None]

        log.info(f"\n  Cluster {cl_id} ({cl_size} members):")
        log.info(f"    Conductors: {unique_conds} unique, range {min(conds)}-{max(conds)}")
        log.info(f"    MF dims: {dict(Counter(dims))}")
        log.info(f"    Char orders: {dict(Counter(char_orders))}")
        log.info(f"    Samples: {[o['label'] for o in member_objs[:5]]}")

    # ============================================================
    # 6. Cross-conductor examples
    # ============================================================
    log.info("\n--- Cross-conductor examples ---")
    cross_cond_examples.sort(key=lambda x: -x['n_unique_conds'])
    spread_dist = Counter(c['n_unique_conds'] for c in cross_cond_examples)
    log.info(f"Conductor spread in sample: {dict(sorted(spread_dist.items()))}")
    for c in cross_cond_examples[:10]:
        log.info(f"  {c['source']:20s} (cond={c['source_cond']}): "
                 f"neighbors at {c['n_unique_conds']} conductors")

    # ============================================================
    # 7. MF dimension analysis — are Type B objects higher-dimensional?
    # ============================================================
    log.info("\n--- MF dimension analysis ---")
    tb_dims = []
    tb_chars = []
    for oid, _, otype, *_ in type_b:
        meta = mf_meta.get(oid, {})
        if meta.get('dim') is not None:
            tb_dims.append(meta['dim'])
        if meta.get('char_order') is not None:
            tb_chars.append(meta['char_order'])

    dim_dist = Counter(tb_dims)
    char_dist = Counter(tb_chars)
    log.info(f"MF dimension distribution:")
    for d in sorted(dim_dist.keys())[:10]:
        log.info(f"  dim {d}: {dim_dist[d]}")
    log.info(f"Character order distribution:")
    for c in sorted(char_dist.keys())[:10]:
        log.info(f"  char_order {c}: {char_dist[c]}")

    # What fraction are dim > 1?
    dim1 = dim_dist.get(1, 0)
    dim_gt1 = sum(v for k, v in dim_dist.items() if k > 1)
    log.info(f"\nDim-1 (rational): {dim1} ({dim1/len(tb_dims)*100:.1f}%)")
    log.info(f"Dim > 1 (higher): {dim_gt1} ({dim_gt1/len(tb_dims)*100:.1f}%)")

    # What fraction have non-trivial character?
    triv = char_dist.get(1, 0)
    nontriv = sum(v for k, v in char_dist.items() if k > 1)
    log.info(f"Trivial character: {triv} ({triv/len(tb_chars)*100:.1f}%)")
    log.info(f"Non-trivial character: {nontriv} ({nontriv/len(tb_chars)*100:.1f}%)")

    # ============================================================
    # Summary
    # ============================================================
    log.info("\n" + "=" * 60)
    log.info("SUMMARY")
    log.info("=" * 60)
    log.info(f"Type B candidates: {len(type_b)}")
    log.info(f"All modular forms: {'Yes' if type_counts.get('elliptic_curve', 0) == 0 else 'No'}")
    log.info(f"Cross-conductor neighborhoods: {cross_conductor/n_tb*100:.1f}%")
    log.info(f"Same-conductor neighborhoods: {same_conductor/n_tb*100:.1f}%")
    log.info(f"DBSCAN clusters: {n_clusters}, noise: {n_noise/n_tb*100:.1f}%")
    log.info(f"Higher-dimensional MFs: {dim_gt1/len(tb_dims)*100:.1f}%")
    log.info(f"Non-trivial character: {nontriv/len(tb_chars)*100:.1f}%")
    log.info(f"Has EC zero-neighbor: {has_ec_neighbor}/{n_tb}")

    # Save
    report = {
        'total': len(type_b),
        'all_mf': type_counts.get('elliptic_curve', 0) == 0,
        'cross_conductor_pct': cross_conductor / n_tb,
        'same_conductor_pct': same_conductor / n_tb,
        'n_clusters': n_clusters,
        'noise_pct': n_noise / n_tb,
        'dim1_pct': dim1 / len(tb_dims) if tb_dims else 0,
        'dim_gt1_pct': dim_gt1 / len(tb_dims) if tb_dims else 0,
        'trivial_char_pct': triv / len(tb_chars) if tb_chars else 0,
        'nontriv_char_pct': nontriv / len(tb_chars) if tb_chars else 0,
        'has_ec_neighbor': has_ec_neighbor,
    }
    out_path = Path(__file__).parent.parent / 'reports' / 'type_b_characterization.json'
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    log.info(f"Report: {out_path}")


if __name__ == "__main__":
    run()
