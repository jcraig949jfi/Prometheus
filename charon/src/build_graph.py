"""
Charon Direction 3 — Relationship Graph Construction

Builds a mathematical relationship graph from three edge sources:
  1. Isogeny edges (EC <-> EC): from ec_classdata.isogeny_matrix
  2. Modularity edges (EC <-> MF): from known_bridges table (already local)
  3. Twist edges (MF <-> MF): from mf_twists_nf

The graph is stored in DuckDB and exported to NetworkX for embedding.
"""

import json
import time
import logging
import duckdb
import psycopg2
import psycopg2.extras
import numpy as np
import networkx as nx
from collections import defaultdict
from pathlib import Path

from charon.src.config import DB_PATH, LMFDB_PG, BATCH_SIZE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("charon.graph")


def get_duck(readonly=True):
    return duckdb.connect(str(DB_PATH), read_only=readonly)


def init_graph_tables():
    """Create tables for storing graph edges."""
    duck = get_duck(readonly=False)
    duck.execute("""
        CREATE TABLE IF NOT EXISTS graph_edges (
            id INTEGER PRIMARY KEY,
            source_id INTEGER,
            target_id INTEGER,
            source_label TEXT,
            target_label TEXT,
            edge_type TEXT,        -- 'isogeny', 'modularity', 'twist'
            weight DOUBLE,         -- isogeny degree, or 1.0 for modularity/twist
            metadata JSON
        )
    """)
    duck.execute("CREATE SEQUENCE IF NOT EXISTS graph_edge_seq START 1")
    duck.execute("DELETE FROM graph_edges")  # fresh build
    duck.close()
    log.info("Graph tables initialized")


def build_isogeny_edges():
    """
    Build isogeny edges from ec_classdata.isogeny_matrix.
    Each off-diagonal entry [i,j] = degree of isogeny from curve i to curve j.
    Curves are ordered by lmfdb_number within the class.
    """
    log.info("Building isogeny edges...")
    t0 = time.time()

    pg = psycopg2.connect(**LMFDB_PG)
    cur = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get isogeny matrices for classes with >1 curve, conductor <= 5000
    cur.execute("""
        SELECT lmfdb_iso, isogeny_matrix, class_size
        FROM ec_classdata
        WHERE conductor <= 5000 AND class_size > 1
        ORDER BY lmfdb_iso
    """)

    duck = get_duck(readonly=False)

    # Build lookup: lmfdb_iso + curve_number -> object_id
    ec_lookup = {}
    ec_rows = duck.execute("""
        SELECT ec.object_id, ec.lmfdb_label, ec.lmfdb_iso
        FROM elliptic_curves ec
    """).fetchall()
    for oid, label, iso in ec_rows:
        ec_lookup[label] = oid

    edges_added = 0
    classes_processed = 0

    for row in cur:
        iso = row['lmfdb_iso']
        matrix = row['isogeny_matrix']
        class_size = row['class_size']

        if matrix is None or class_size <= 1:
            continue

        # Curves in this class are labeled iso + "1", iso + "2", etc.
        curve_labels = [f"{iso}{i+1}" for i in range(class_size)]
        curve_ids = [ec_lookup.get(label) for label in curve_labels]

        # Extract edges from upper triangle of isogeny matrix
        for i in range(class_size):
            for j in range(i + 1, class_size):
                if curve_ids[i] is None or curve_ids[j] is None:
                    continue
                try:
                    degree = int(matrix[i][j])
                except (IndexError, TypeError, ValueError):
                    continue

                edge_id = duck.execute("SELECT nextval('graph_edge_seq')").fetchone()[0]
                duck.execute("""
                    INSERT INTO graph_edges (id, source_id, target_id, source_label, target_label,
                                            edge_type, weight, metadata)
                    VALUES (?, ?, ?, ?, ?, 'isogeny', ?, ?)
                """, [edge_id, curve_ids[i], curve_ids[j],
                      curve_labels[i], curve_labels[j],
                      float(degree), json.dumps({"iso_class": iso, "degree": degree})])
                edges_added += 1

        classes_processed += 1
        if classes_processed % 1000 == 0:
            log.info(f"  Isogeny: {classes_processed} classes, {edges_added} edges")

    cur.close()
    pg.close()
    duck.close()

    log.info(f"Isogeny edges: {edges_added} from {classes_processed} classes ({time.time()-t0:.1f}s)")
    return edges_added


def build_modularity_edges():
    """Copy modularity bridges into graph_edges table."""
    log.info("Building modularity edges...")
    t0 = time.time()

    duck = get_duck(readonly=False)
    bridges = duck.execute("""
        SELECT source_id, target_id, source_label, target_label
        FROM known_bridges WHERE bridge_type = 'modularity'
    """).fetchall()

    for src_id, tgt_id, src_label, tgt_label in bridges:
        edge_id = duck.execute("SELECT nextval('graph_edge_seq')").fetchone()[0]
        duck.execute("""
            INSERT INTO graph_edges (id, source_id, target_id, source_label, target_label,
                                    edge_type, weight, metadata)
            VALUES (?, ?, ?, ?, ?, 'modularity', 1.0, NULL)
        """, [edge_id, src_id, tgt_id, src_label, tgt_label])

    duck.close()
    log.info(f"Modularity edges: {len(bridges)} ({time.time()-t0:.1f}s)")
    return len(bridges)


def build_twist_edges():
    """
    Build twist edges from mf_twists_nf.
    Only for forms already in our database (level <= 5000, weight 2).
    """
    log.info("Building twist edges...")
    t0 = time.time()

    duck = get_duck(readonly=False)

    # Build MF label -> object_id lookup
    mf_lookup = {}
    mf_rows = duck.execute("""
        SELECT o.id, o.lmfdb_label FROM objects o
        WHERE o.object_type = 'modular_form'
    """).fetchall()
    for oid, label in mf_rows:
        mf_lookup[label] = oid
    log.info(f"  MF lookup: {len(mf_lookup)} forms")

    # Query twist relationships from LMFDB
    pg = psycopg2.connect(**LMFDB_PG)
    cur = pg.cursor()

    # mf_twists_nf has source_label, target_label, twisting_char_label
    cur.execute("""
        SELECT source_label, target_label, twist_class_label
        FROM mf_twists_nf
        WHERE source_level <= 5000 AND target_level <= 5000
          AND source_label != target_label
    """)

    edges_added = 0
    rows_scanned = 0

    while True:
        rows = cur.fetchmany(5000)
        if not rows:
            break
        rows_scanned += len(rows)

        for source_label, target_label, twist_class in rows:
            src_id = mf_lookup.get(source_label)
            tgt_id = mf_lookup.get(target_label)
            if src_id is None or tgt_id is None:
                continue
            if src_id == tgt_id:
                continue

            edge_id = duck.execute("SELECT nextval('graph_edge_seq')").fetchone()[0]
            duck.execute("""
                INSERT INTO graph_edges (id, source_id, target_id, source_label, target_label,
                                        edge_type, weight, metadata)
                VALUES (?, ?, ?, ?, ?, 'twist', 1.0, ?)
            """, [edge_id, src_id, tgt_id, source_label, target_label,
                  json.dumps({"twist_class": twist_class})])
            edges_added += 1

        if rows_scanned % 50000 == 0:
            log.info(f"  Twist: scanned {rows_scanned}, added {edges_added}")

    cur.close()
    pg.close()
    duck.close()
    log.info(f"Twist edges: {edges_added} from {rows_scanned} rows ({time.time()-t0:.1f}s)")
    return edges_added


def build_networkx_graph():
    """Load graph_edges into a NetworkX graph with node attributes."""
    log.info("Building NetworkX graph...")
    t0 = time.time()

    duck = get_duck()

    G = nx.Graph()

    # Add nodes with attributes
    nodes = duck.execute("""
        SELECT o.id, o.lmfdb_label, o.object_type, o.conductor
        FROM objects o
    """).fetchall()
    for oid, label, otype, cond in nodes:
        G.add_node(oid, label=label, type=otype, conductor=int(cond))

    # Add edges
    edges = duck.execute("""
        SELECT source_id, target_id, edge_type, weight
        FROM graph_edges
    """).fetchall()
    for src, tgt, etype, weight in edges:
        if G.has_node(src) and G.has_node(tgt):
            if G.has_edge(src, tgt):
                # Keep the edge with higher priority: modularity > isogeny > twist
                existing = G[src][tgt].get('type', 'twist')
                priority = {'modularity': 3, 'isogeny': 2, 'twist': 1}
                if priority.get(etype, 0) > priority.get(existing, 0):
                    G[src][tgt]['type'] = etype
                    G[src][tgt]['weight'] = weight
            else:
                G.add_edge(src, tgt, type=etype, weight=weight)

    duck.close()

    log.info(f"NetworkX graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges ({time.time()-t0:.1f}s)")

    # Stats
    n_connected = nx.number_connected_components(G)
    largest_cc = max(nx.connected_components(G), key=len)
    log.info(f"  Connected components: {n_connected}")
    log.info(f"  Largest component: {len(largest_cc)} nodes")

    # Edge type counts
    type_counts = defaultdict(int)
    for _, _, data in G.edges(data=True):
        type_counts[data.get('type', 'unknown')] += 1
    for etype, count in sorted(type_counts.items()):
        log.info(f"  {etype} edges: {count}")

    return G


def test_zero_proximity_vs_graph_distance(G):
    """
    THE scientific test: does zero proximity predict graph distance?

    Method:
      1. For all pairs connected by an edge, compute zero-vector distance
      2. For random non-connected pairs at same conductor, compute zero distance
      3. Connected pairs should have smaller zero distances than non-connected

    Also: compute correlation between graph distance and zero distance
    for pairs within the largest connected component.
    """
    log.info("Testing: zero proximity vs graph distance...")
    t0 = time.time()

    duck = get_duck()

    # Load zero vectors for nodes in the graph
    zero_data = {}
    rows = duck.execute("""
        SELECT oz.object_id, oz.zeros_vector, oz.n_zeros_stored
        FROM object_zeros oz
    """).fetchall()
    for oid, zvec, nz in rows:
        if zvec is not None:
            n = min(nz or 0, 20)
            vec = [float(zvec[i]) if i < n and zvec[i] is not None else 0.0 for i in range(20)]
            zero_data[oid] = np.array(vec)
    duck.close()

    log.info(f"  Nodes with zero vectors: {len(zero_data)}")

    # Connected pair distances (excluding modularity — those are trivially 0)
    connected_dists = []
    for u, v, data in G.edges(data=True):
        if data.get('type') == 'modularity':
            continue  # skip — we know these are distance 0
        if u in zero_data and v in zero_data:
            d = np.linalg.norm(zero_data[u] - zero_data[v])
            connected_dists.append(d)

    # Random non-connected pairs (same conductor, for fair comparison)
    node_by_cond = defaultdict(list)
    for node in G.nodes():
        if node in zero_data:
            cond = G.nodes[node].get('conductor', 0)
            node_by_cond[cond].append(node)

    np.random.seed(42)
    random_dists = []
    attempts = 0
    while len(random_dists) < len(connected_dists) and attempts < len(connected_dists) * 10:
        cond = np.random.choice(list(node_by_cond.keys()))
        nodes_at_cond = node_by_cond[cond]
        if len(nodes_at_cond) < 2:
            attempts += 1
            continue
        i, j = np.random.choice(len(nodes_at_cond), 2, replace=False)
        u, v = nodes_at_cond[i], nodes_at_cond[j]
        if not G.has_edge(u, v):
            d = np.linalg.norm(zero_data[u] - zero_data[v])
            random_dists.append(d)
        attempts += 1

    connected_dists = np.array(connected_dists)
    random_dists = np.array(random_dists[:len(connected_dists)])

    log.info(f"  Connected pairs (non-modularity): {len(connected_dists)}")
    log.info(f"  Random non-connected pairs: {len(random_dists)}")

    if len(connected_dists) > 0 and len(random_dists) > 0:
        log.info(f"  Connected zero-dist: mean={connected_dists.mean():.4f}, median={np.median(connected_dists):.4f}")
        log.info(f"  Random zero-dist:    mean={random_dists.mean():.4f}, median={np.median(random_dists):.4f}")

        from scipy.stats import mannwhitneyu
        u_stat, p_val = mannwhitneyu(connected_dists, random_dists, alternative='less')
        log.info(f"  Mann-Whitney U: p={p_val:.2e} (connected < random?)")

        # Cohen's d
        pooled_std = np.sqrt((connected_dists.std()**2 + random_dists.std()**2) / 2)
        if pooled_std > 0:
            d = (random_dists.mean() - connected_dists.mean()) / pooled_std
        else:
            d = 0
        log.info(f"  Cohen's d: {d:.4f}")

        # Overlap
        connected_95 = np.percentile(connected_dists, 95)
        overlap = np.mean(random_dists <= connected_95)
        log.info(f"  Overlap (random <= connected 95th pctile): {overlap:.4f}")

        result = {
            "connected_mean": float(connected_dists.mean()),
            "random_mean": float(random_dists.mean()),
            "mann_whitney_p": float(p_val),
            "cohens_d": float(d),
            "overlap": float(overlap),
            "n_connected": len(connected_dists),
            "n_random": len(random_dists),
        }
    else:
        log.warning("  Insufficient data for graph-zero comparison")
        result = {}

    # Graph distance vs zero distance correlation (sample from largest CC)
    largest_cc = max(nx.connected_components(G), key=len)
    cc_nodes = [n for n in largest_cc if n in zero_data]

    if len(cc_nodes) > 100:
        log.info(f"  Computing graph-distance vs zero-distance correlation on {len(cc_nodes)} CC nodes...")
        sample = np.random.choice(cc_nodes, min(500, len(cc_nodes)), replace=False)

        graph_dists = []
        zero_dists_corr = []

        # Compute shortest paths for sample pairs
        sample_set = set(sample)
        for i, u in enumerate(sample[:50]):  # limit to 50 sources for speed
            try:
                sp = nx.single_source_shortest_path_length(G, u, cutoff=5)
                for v in sample:
                    if v != u and v in sp:
                        gd = sp[v]
                        zd = np.linalg.norm(zero_data[u] - zero_data[v])
                        graph_dists.append(gd)
                        zero_dists_corr.append(zd)
            except Exception:
                continue

        if graph_dists:
            from scipy.stats import spearmanr
            rho, p = spearmanr(graph_dists, zero_dists_corr)
            log.info(f"  Spearman rho(graph_dist, zero_dist): {rho:.4f}, p={p:.2e}")
            log.info(f"  Pairs sampled: {len(graph_dists)}")
            result["spearman_rho"] = float(rho)
            result["spearman_p"] = float(p)

    log.info(f"  Graph-zero test completed in {time.time()-t0:.1f}s")
    return result


def run_direction3():
    """Full Direction 3 pipeline."""
    log.info("=" * 60)
    log.info("DIRECTION 3: Relationship Graph Construction")
    log.info("=" * 60)
    t0 = time.time()

    init_graph_tables()

    n_isogeny = build_isogeny_edges()
    n_modularity = build_modularity_edges()
    n_twist = build_twist_edges()

    log.info(f"\nTotal edges: {n_isogeny + n_modularity + n_twist}")
    log.info(f"  Isogeny: {n_isogeny}")
    log.info(f"  Modularity: {n_modularity}")
    log.info(f"  Twist: {n_twist}")

    G = build_networkx_graph()
    results = test_zero_proximity_vs_graph_distance(G)

    elapsed = time.time() - t0
    log.info(f"\nDirection 3 complete in {elapsed:.1f}s ({elapsed/60:.1f}m)")
    log.info(f"Results: {json.dumps(results, indent=2)}")

    return G, results


if __name__ == "__main__":
    run_direction3()
