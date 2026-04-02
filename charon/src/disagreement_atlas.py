"""
Charon Disagreement Atlas — Cross-Layer Analysis

Compares zero-space neighborhoods with graph-space neighborhoods for every
object in the database. Classifies each object by agreement type and
surfaces the most interesting cases.

Types:
  A (Agreement):   zero neighbors ≈ graph neighbors — validated structure
  B (Zero-driven): tight zero cluster, no graph edges — candidate discoveries
  C (Graph-only):  graph edges exist, zeros don't see them — structural anomalies
  D (Noise/Isolated): no coherence in either layer

This is the cross-layer query that exploits the proven orthogonality
between zeros (rank-aware continuous geometry) and the relationship graph
(discrete algebraic structure).
"""

import duckdb
import numpy as np
import networkx as nx
import json
import time
import logging
from collections import defaultdict
from sklearn.neighbors import NearestNeighbors
from pathlib import Path

from charon.src.config import DB_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("charon.atlas")

K_ZERO = 10       # zero-space neighbors
GRAPH_HOPS = 2    # graph neighborhood depth


def get_duck(readonly=True):
    return duckdb.connect(str(DB_PATH), read_only=readonly)


def load_zero_neighbors():
    """Compute k-NN in zero space for all objects with zeros."""
    log.info("Computing zero-space neighborhoods (k=%d)...", K_ZERO)
    t0 = time.time()

    duck = get_duck()
    rows = duck.execute("""
        SELECT oz.object_id, o.object_type, o.conductor, o.lmfdb_label,
               oz.zeros_vector, oz.n_zeros_stored
        FROM object_zeros oz
        JOIN objects o ON oz.object_id = o.id
        WHERE oz.zeros_vector IS NOT NULL
    """).fetchall()

    # Load EC metadata
    ec_meta = {}
    for oid, iso, rank, torsion, cm in duck.execute("""
        SELECT ec.object_id, ec.lmfdb_iso, ec.rank, ec.torsion, ec.cm
        FROM elliptic_curves ec
    """).fetchall():
        ec_meta[oid] = {'iso': iso, 'rank': int(rank or 0),
                        'torsion': int(torsion or 0), 'cm': int(cm or 0)}
    duck.close()

    # Build vectors
    obj_list = []
    for oid, otype, cond, label, zvec, nz in rows:
        n = min(nz or 0, 20)
        vec = [float(zvec[i]) if i < n and zvec[i] is not None else 0.0 for i in range(20)]
        meta = ec_meta.get(oid, {})
        obj_list.append({
            'id': oid, 'type': otype, 'conductor': int(cond), 'label': label,
            'vec': np.array(vec), **meta
        })

    X = np.array([o['vec'] for o in obj_list])
    means = X.mean(axis=0)
    stds = X.std(axis=0)
    stds[stds < 1e-10] = 1.0
    X_norm = (X - means) / stds

    nn = NearestNeighbors(n_neighbors=K_ZERO + 1, metric='euclidean', algorithm='brute')
    nn.fit(X_norm)
    distances, indices = nn.kneighbors(X_norm)

    # Build neighbor sets (exclude self)
    id_to_idx = {o['id']: i for i, o in enumerate(obj_list)}
    zero_neighbors = {}
    for i, obj in enumerate(obj_list):
        nns = set()
        for j_pos in range(indices.shape[1]):
            j = indices[i, j_pos]
            if j != i:
                nns.add(obj_list[j]['id'])
            if len(nns) >= K_ZERO:
                break
        zero_neighbors[obj['id']] = nns

    log.info("Zero neighbors computed for %d objects in %.1fs", len(zero_neighbors), time.time() - t0)
    return obj_list, zero_neighbors, id_to_idx


def load_graph_neighbors():
    """Build graph and compute 2-hop neighborhoods."""
    log.info("Building graph neighborhoods (hops=%d)...", GRAPH_HOPS)
    t0 = time.time()

    duck = get_duck()
    edges = duck.execute("SELECT source_id, target_id, edge_type FROM graph_edges").fetchall()
    duck.close()

    G = nx.Graph()
    for src, tgt, etype in edges:
        G.add_edge(src, tgt, type=etype)

    log.info("Graph: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())

    # Compute 2-hop neighborhoods for all nodes
    graph_neighbors = {}
    for node in G.nodes():
        # BFS to depth GRAPH_HOPS
        neighbors = set()
        try:
            lengths = nx.single_source_shortest_path_length(G, node, cutoff=GRAPH_HOPS)
            for n, d in lengths.items():
                if n != node and d <= GRAPH_HOPS:
                    neighbors.add(n)
        except Exception:
            pass
        graph_neighbors[node] = neighbors

    log.info("Graph neighbors computed for %d nodes in %.1fs", len(graph_neighbors), time.time() - t0)
    return G, graph_neighbors


def build_atlas(obj_list, zero_neighbors, graph_neighbors, G, id_to_idx):
    """
    For each object, compute disagreement metrics between zero and graph neighborhoods.
    Classify into types A/B/C/D.
    """
    log.info("Building disagreement atlas...")
    t0 = time.time()

    # Pre-compute component sizes
    comp_sizes = {}
    for cc in nx.connected_components(G):
        sz = len(cc)
        for node in cc:
            comp_sizes[node] = sz

    atlas = []
    for idx, obj in enumerate(obj_list):
        if idx % 20000 == 0 and idx > 0:
            log.info(f"  Atlas progress: {idx}/{len(obj_list)}")
        oid = obj['id']
        z_nn = zero_neighbors.get(oid, set())
        g_nn = graph_neighbors.get(oid, set())

        # Jaccard
        union = z_nn | g_nn
        intersection = z_nn & g_nn
        jaccard = len(intersection) / len(union) if union else 0.0

        # Precision: fraction of zero-neighbors that are graph-connected
        precision = len(intersection) / len(z_nn) if z_nn else 0.0

        # Recall: fraction of graph-neighbors found by zeros
        recall = len(intersection) / len(g_nn) if g_nn else 0.0

        # Graph degree and component size (pre-computed)
        graph_degree = G.degree(oid) if G.has_node(oid) else 0
        component_size = comp_sizes.get(oid, 0)

        # Zero cluster coherence: mean distance to zero neighbors
        # (lower = tighter cluster)
        zero_coherence = 0.0
        if z_nn:
            dists = []
            for nid in z_nn:
                nidx = id_to_idx.get(nid)
                if nidx is not None:
                    dists.append(np.linalg.norm(obj['vec'] - obj_list[nidx]['vec']))
            zero_coherence = np.mean(dists) if dists else 0.0

        # Classification
        has_graph = len(g_nn) > 0
        has_zero_cluster = len(z_nn) > 0 and zero_coherence < 2.0  # tight cluster threshold

        if jaccard > 0.1 and has_graph:
            dtype = 'A'  # Agreement
        elif has_zero_cluster and not has_graph:
            dtype = 'B'  # Zero-driven (candidate discoveries)
        elif has_graph and jaccard < 0.05:
            dtype = 'C'  # Graph-only (structural anomalies)
        else:
            dtype = 'D'  # Noise/isolated

        atlas.append({
            'object_id': oid,
            'label': obj['label'],
            'object_type': obj['type'],
            'conductor': obj['conductor'],
            'rank': obj.get('rank', None),
            'torsion': obj.get('torsion', None),
            'cm': obj.get('cm', None),
            'jaccard': jaccard,
            'precision': precision,
            'recall': recall,
            'zero_coherence': zero_coherence,
            'graph_degree': graph_degree,
            'component_size': component_size,
            'n_zero_nn': len(z_nn),
            'n_graph_nn': len(g_nn),
            'n_overlap': len(intersection),
            'disagreement_type': dtype,
        })

    log.info("Atlas built for %d objects in %.1fs", len(atlas), time.time() - t0)
    return atlas


def store_atlas(atlas):
    """Store atlas in DuckDB."""
    log.info("Storing atlas in DuckDB...")
    duck = get_duck(readonly=False)

    duck.execute("DROP TABLE IF EXISTS disagreement_atlas")
    duck.execute("""
        CREATE TABLE disagreement_atlas (
            object_id INTEGER PRIMARY KEY,
            label TEXT,
            object_type TEXT,
            conductor INTEGER,
            rank INTEGER,
            torsion INTEGER,
            cm INTEGER,
            jaccard DOUBLE,
            precision_score DOUBLE,
            recall_score DOUBLE,
            zero_coherence DOUBLE,
            graph_degree INTEGER,
            component_size INTEGER,
            n_zero_nn INTEGER,
            n_graph_nn INTEGER,
            n_overlap INTEGER,
            disagreement_type TEXT
        )
    """)

    import pandas as pd
    df = pd.DataFrame(atlas)
    df = df.rename(columns={'precision': 'precision_score', 'recall': 'recall_score'})
    duck.execute("INSERT INTO disagreement_atlas SELECT * FROM df")

    duck.close()
    log.info("Atlas stored: %d rows", len(atlas))


def report_atlas(atlas):
    """Print summary report of the atlas."""
    log.info("=" * 60)
    log.info("DISAGREEMENT ATLAS REPORT")
    log.info("=" * 60)

    # Type distribution
    type_counts = defaultdict(int)
    for entry in atlas:
        type_counts[entry['disagreement_type']] += 1

    log.info("\nType Distribution:")
    for dtype in ['A', 'B', 'C', 'D']:
        count = type_counts[dtype]
        pct = count / len(atlas) * 100
        log.info(f"  Type {dtype}: {count:>7,} ({pct:.1f}%)")

    # Type descriptions
    descs = {
        'A': 'Agreement — zeros and graph agree',
        'B': 'Zero-driven — candidate discoveries (tight zero cluster, no graph edges)',
        'C': 'Graph-only — structural anomalies (graph edges, zeros dont see them)',
        'D': 'Noise/Isolated — no coherence in either layer',
    }
    for dtype, desc in descs.items():
        log.info(f"    {dtype}: {desc}")

    # Top Type B candidates (zero-driven, no graph edges — these are the discoveries)
    log.info("\n--- TOP TYPE B: Candidate Discoveries ---")
    log.info("Objects with tight zero clusters but no graph edges:")
    type_b = [e for e in atlas if e['disagreement_type'] == 'B']
    type_b.sort(key=lambda x: x['zero_coherence'])
    for entry in type_b[:20]:
        log.info(f"  {entry['label']:20s} (cond={entry['conductor']}, rank={entry['rank']}, "
                 f"coherence={entry['zero_coherence']:.4f}, zero_nn={entry['n_zero_nn']})")

    # Top Type C anomalies (graph edges but zeros diverge)
    log.info("\n--- TOP TYPE C: Structural Anomalies ---")
    log.info("Objects with graph edges but zero-space neighbors don't match:")
    type_c = [e for e in atlas if e['disagreement_type'] == 'C']
    type_c.sort(key=lambda x: -x['graph_degree'])
    for entry in type_c[:20]:
        log.info(f"  {entry['label']:20s} (cond={entry['conductor']}, graph_deg={entry['graph_degree']}, "
                 f"comp_size={entry['component_size']}, jaccard={entry['jaccard']:.4f})")

    # Agreement statistics
    type_a = [e for e in atlas if e['disagreement_type'] == 'A']
    if type_a:
        mean_j = np.mean([e['jaccard'] for e in type_a])
        mean_p = np.mean([e['precision'] for e in type_a])
        mean_r = np.mean([e['recall'] for e in type_a])
        log.info(f"\n--- TYPE A Statistics ---")
        log.info(f"  Count: {len(type_a)}")
        log.info(f"  Mean Jaccard: {mean_j:.4f}")
        log.info(f"  Mean Precision: {mean_p:.4f}")
        log.info(f"  Mean Recall: {mean_r:.4f}")

    # Property breakdown by type
    log.info("\n--- Rank Distribution by Type ---")
    for dtype in ['A', 'B', 'C', 'D']:
        entries = [e for e in atlas if e['disagreement_type'] == dtype and e['rank'] is not None]
        if entries:
            ranks = [e['rank'] for e in entries]
            rank_counts = defaultdict(int)
            for r in ranks:
                rank_counts[r] += 1
            rank_str = ', '.join(f"r{r}:{c}" for r, c in sorted(rank_counts.items()))
            log.info(f"  Type {dtype}: {rank_str}")

    log.info("\n" + "=" * 60)


def run_atlas():
    """Build the full disagreement atlas."""
    t0 = time.time()
    log.info("=" * 60)
    log.info("CHARON DISAGREEMENT ATLAS")
    log.info("=" * 60)

    obj_list, zero_neighbors, id_to_idx = load_zero_neighbors()
    G, graph_neighbors = load_graph_neighbors()
    atlas = build_atlas(obj_list, zero_neighbors, graph_neighbors, G, id_to_idx)
    store_atlas(atlas)
    report_atlas(atlas)

    elapsed = time.time() - t0
    log.info(f"\nAtlas complete in {elapsed:.1f}s ({elapsed/60:.1f}m)")
    return atlas


if __name__ == "__main__":
    run_atlas()
