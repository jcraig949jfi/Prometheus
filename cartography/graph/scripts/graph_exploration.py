"""
Direction 1: LMFDB Relationship Graph Exploration
===================================================
396K edges already in DuckDB. What does the community structure look like?
Do clusters correspond to known mathematical structure or reveal gaps?
"""

import duckdb
import numpy as np
import json
import logging
import sys
from collections import defaultdict, Counter
from datetime import date
from pathlib import Path

DB = Path(__file__).parents[3] / "charon" / "data" / "charon.duckdb"
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(REPORT_DIR / f"graph_exploration_{date.today()}.log",
                                  mode="w", encoding="utf-8")])
log = logging.getLogger("cart.graph")


def main():
    log.info("=" * 70)
    log.info("DIRECTION 1: LMFDB RELATIONSHIP GRAPH EXPLORATION")
    log.info(f"Date: {date.today()}")
    log.info("=" * 70)

    duck = duckdb.connect(str(DB), read_only=True)

    # ================================================================
    # 1. Graph overview
    # ================================================================
    log.info("\n--- 1. GRAPH OVERVIEW ---")

    edge_count = duck.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0]
    log.info(f"Total edges: {edge_count}")

    edge_types = duck.execute("""
        SELECT edge_type, COUNT(*) as n
        FROM graph_edges
        GROUP BY edge_type
        ORDER BY n DESC
    """).fetchall()
    log.info("Edge types:")
    for (t, n) in edge_types:
        log.info(f"  {t}: {n}")

    # Node counts
    nodes = duck.execute("""
        SELECT COUNT(DISTINCT source_id) + COUNT(DISTINCT target_id) as approx_nodes
        FROM graph_edges
    """).fetchone()[0]
    log.info(f"Approximate node count: {nodes}")

    # ================================================================
    # 2. Degree distribution
    # ================================================================
    log.info("\n--- 2. DEGREE DISTRIBUTION ---")

    degrees = duck.execute("""
        WITH node_degrees AS (
            SELECT source_id as node_id, COUNT(*) as deg FROM graph_edges GROUP BY source_id
            UNION ALL
            SELECT target_id as node_id, COUNT(*) as deg FROM graph_edges GROUP BY target_id
        )
        SELECT node_id, SUM(deg) as total_deg
        FROM node_degrees
        GROUP BY node_id
        ORDER BY total_deg DESC
        LIMIT 20
    """).fetchall()

    log.info("Top 20 nodes by degree:")
    for (nid, deg) in degrees[:10]:
        # Get the object type and label
        info = duck.execute("""
            SELECT object_type, lmfdb_label FROM objects WHERE id = ?
        """, [nid]).fetchone()
        if info:
            log.info(f"  id={nid}, deg={deg}, type={info[0]}, label={info[1]}")
        else:
            log.info(f"  id={nid}, deg={deg}")

    # Degree distribution summary
    all_degrees = duck.execute("""
        WITH node_degrees AS (
            SELECT source_id as node_id, COUNT(*) as deg FROM graph_edges GROUP BY source_id
            UNION ALL
            SELECT target_id as node_id, COUNT(*) as deg FROM graph_edges GROUP BY target_id
        ),
        total_degrees AS (
            SELECT node_id, SUM(deg) as total_deg
            FROM node_degrees
            GROUP BY node_id
        )
        SELECT total_deg, COUNT(*) as n_nodes
        FROM total_degrees
        GROUP BY total_deg
        ORDER BY total_deg
    """).fetchall()

    deg_vals = {d: n for d, n in all_degrees}
    total_nodes = sum(deg_vals.values())
    log.info(f"\nDegree distribution: {total_nodes} nodes")
    log.info(f"  deg=1: {deg_vals.get(1, 0)} nodes ({100*deg_vals.get(1,0)/total_nodes:.1f}%)")
    log.info(f"  deg=2: {deg_vals.get(2, 0)} nodes")
    log.info(f"  deg=3-5: {sum(deg_vals.get(d,0) for d in range(3,6))} nodes")
    log.info(f"  deg=6-10: {sum(deg_vals.get(d,0) for d in range(6,11))} nodes")
    log.info(f"  deg>10: {sum(n for d,n in all_degrees if d > 10)} nodes")
    log.info(f"  max degree: {max(deg_vals.keys())}")

    # ================================================================
    # 3. Connected components
    # ================================================================
    log.info("\n--- 3. CONNECTED COMPONENTS ---")

    # Build adjacency list
    edges = duck.execute("SELECT source_id, target_id FROM graph_edges").fetchall()

    adj = defaultdict(set)
    for (s, t) in edges:
        adj[s].add(t)
        adj[t].add(s)

    # BFS for connected components
    visited = set()
    components = []
    for node in adj:
        if node in visited:
            continue
        # BFS
        queue = [node]
        component = set()
        while queue:
            n = queue.pop(0)
            if n in visited:
                continue
            visited.add(n)
            component.add(n)
            for neighbor in adj[n]:
                if neighbor not in visited:
                    queue.append(neighbor)
        components.append(component)

    components.sort(key=len, reverse=True)
    log.info(f"Connected components: {len(components)}")
    log.info(f"Largest component: {len(components[0])} nodes")
    log.info(f"Top 10 component sizes: {[len(c) for c in components[:10]]}")
    log.info(f"Singleton components: {sum(1 for c in components if len(c) == 1)}")
    log.info(f"Components with 2-5 nodes: {sum(1 for c in components if 2 <= len(c) <= 5)}")
    log.info(f"Components with 6-20 nodes: {sum(1 for c in components if 6 <= len(c) <= 20)}")
    log.info(f"Components with >20 nodes: {sum(1 for c in components if len(c) > 20)}")

    # ================================================================
    # 4. Edge type mixing
    # ================================================================
    log.info("\n--- 4. EDGE TYPE MIXING ---")
    log.info("For each edge type, what object types does it connect?")

    type_mixing = duck.execute("""
        SELECT ge.edge_type,
               o1.object_type as source_type,
               o2.object_type as target_type,
               COUNT(*) as n
        FROM graph_edges ge
        JOIN objects o1 ON ge.source_id = o1.id
        JOIN objects o2 ON ge.target_id = o2.id
        GROUP BY ge.edge_type, o1.object_type, o2.object_type
        ORDER BY ge.edge_type, n DESC
    """).fetchall()

    for (bt, st, tt, n) in type_mixing:
        log.info(f"  {bt}: {st} -> {tt}: {n}")

    # ================================================================
    # 5. Cross-type edges (the interesting ones)
    # ================================================================
    log.info("\n--- 5. CROSS-TYPE EDGES ---")

    cross_type = duck.execute("""
        SELECT ge.edge_type, COUNT(*) as n
        FROM graph_edges ge
        JOIN objects o1 ON ge.source_id = o1.id
        JOIN objects o2 ON ge.target_id = o2.id
        WHERE o1.object_type != o2.object_type
        GROUP BY ge.edge_type
        ORDER BY n DESC
    """).fetchall()

    log.info(f"Cross-type edges:")
    for (bt, n) in cross_type:
        log.info(f"  {bt}: {n}")

    total_cross = sum(n for _, n in cross_type)
    log.info(f"Total cross-type: {total_cross} / {edge_count} ({100*total_cross/edge_count:.1f}%)")

    # ================================================================
    # 6. Largest component: what's in it?
    # ================================================================
    log.info("\n--- 6. LARGEST COMPONENT COMPOSITION ---")

    if components:
        largest = components[0]
        largest_ids = list(largest)[:10000]  # cap for query

        # Get type distribution in largest component
        placeholders = ",".join(str(i) for i in largest_ids[:1000])
        if placeholders:
            type_dist = duck.execute(f"""
                SELECT object_type, COUNT(*) as n
                FROM objects
                WHERE id IN ({placeholders})
                GROUP BY object_type
                ORDER BY n DESC
            """).fetchall()
            log.info(f"Largest component type distribution (sample of {min(1000, len(largest_ids))}):")
            for (ot, n) in type_dist:
                log.info(f"  {ot}: {n}")

    # ================================================================
    # 7. Arithmetic invariant distribution by component
    # ================================================================
    log.info("\n--- 7. DO COMPONENTS CLUSTER BY ARITHMETIC? ---")

    # For the largest 20 components with EC nodes, check rank distribution
    for ci, comp in enumerate(components[:20]):
        if len(comp) < 5:
            break
        comp_ids = list(comp)[:500]
        placeholders = ",".join(str(i) for i in comp_ids)
        ranks = duck.execute(f"""
            SELECT ec.rank, COUNT(*) as n
            FROM elliptic_curves ec
            WHERE ec.object_id IN ({placeholders})
            GROUP BY ec.rank
            ORDER BY ec.rank
        """).fetchall()
        if ranks:
            rank_str = ", ".join(f"r{r}={n}" for r, n in ranks)
            log.info(f"  Component {ci} (size={len(comp)}): {rank_str}")

    duck.close()

    log.info(f"\n{'='*70}")
    log.info("GRAPH EXPLORATION COMPLETE")
    log.info(f"{'='*70}")


if __name__ == "__main__":
    main()
