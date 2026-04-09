"""
Graph Invariants — Spectral and structural comparison of math graphs.
=====================================================================
Loads graphs from isogeny adjacency matrices, mathlib imports, OEIS
cross-references, and MMLKG theorem references. Computes spectral gap,
algebraic connectivity, degree distribution, clustering coefficient.

Usage:
    python graph_invariants.py                  # all graphs
    python graph_invariants.py --source isogeny # single source
    python graph_invariants.py --max-nodes 5000 # limit graph size
"""

import argparse
import json
import sys
import time
import warnings
import numpy as np
from collections import defaultdict


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.bool_,)): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
CARTOGRAPHY = ROOT / "cartography"
CHARON = ROOT / "charon"

ISOGENY_DIR = CARTOGRAPHY / "isogenies" / "data" / "graphs"
MATHLIB_GRAPH = CARTOGRAPHY / "mathlib" / "data" / "import_graph.json"
OEIS_CROSSREFS = CARTOGRAPHY / "oeis" / "data" / "oeis_crossrefs.jsonl"
MMLKG_REFS = CHARON / "james_downloads" / "mmlkg" / "csvs" / "theorem_references.csv"

OUT_DIR = CARTOGRAPHY / "convergence" / "data"
OUT_INVARIANTS = OUT_DIR / "graph_invariants.jsonl"
OUT_COMPARISONS = OUT_DIR / "graph_comparisons.jsonl"


# ---------------------------------------------------------------------------
# Graph loaders
# ---------------------------------------------------------------------------

def load_isogeny_graphs(max_nodes=10000):
    """Load isogeny adjacency matrices from .npz files (CSR format)."""
    import scipy.sparse as sp

    graphs = []
    if not ISOGENY_DIR.exists():
        print(f"  WARNING: {ISOGENY_DIR} not found")
        return graphs

    prime_dirs = sorted(ISOGENY_DIR.iterdir())
    print(f"  Scanning {len(prime_dirs)} isogeny prime directories ...")

    for pdir in prime_dirs:
        if not pdir.is_dir():
            continue
        for npz_file in sorted(pdir.glob("*.npz")):
            try:
                data = np.load(str(npz_file), allow_pickle=True)
                shape = tuple(data["shape"])
                if shape[0] > max_nodes:
                    continue
                mat = sp.csr_matrix(
                    (data["data"], data["indices"], data["indptr"]),
                    shape=shape
                )
                name = npz_file.stem  # e.g. "10007_2"
                graphs.append({
                    "source": "isogeny",
                    "name": name,
                    "matrix": mat,
                    "n_nodes": shape[0],
                    "n_edges": mat.nnz,
                })
            except Exception as e:
                warnings.warn(f"Failed to load {npz_file}: {e}")
                continue

    print(f"  Loaded {len(graphs)} isogeny graphs")
    return graphs


def load_mathlib_graph():
    """Load mathlib import graph as edge list."""
    import networkx as nx

    if not MATHLIB_GRAPH.exists():
        print(f"  WARNING: {MATHLIB_GRAPH} not found")
        return []

    with open(MATHLIB_GRAPH) as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for src, tgt in edges:
        G.add_edge(src, tgt)

    print(f"  mathlib: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return [{"source": "mathlib", "name": "mathlib_imports", "graph": G,
             "n_nodes": G.number_of_nodes(), "n_edges": G.number_of_edges()}]


def load_oeis_crossref_graph(max_nodes=50000):
    """Load OEIS cross-reference graph from JSONL."""
    import networkx as nx

    if not OEIS_CROSSREFS.exists():
        print(f"  WARNING: {OEIS_CROSSREFS} not found")
        return []

    G = nx.Graph()
    n_lines = 0
    with open(OEIS_CROSSREFS) as f:
        for line in f:
            try:
                rec = json.loads(line.strip())
                G.add_edge(rec["source"], rec["target"])
                n_lines += 1
            except (json.JSONDecodeError, KeyError):
                continue

    if G.number_of_nodes() > max_nodes:
        # Take largest connected component
        components = sorted(nx.connected_components(G), key=len, reverse=True)
        if len(components[0]) > max_nodes:
            # Sample subgraph
            nodes = list(components[0])[:max_nodes]
            G = G.subgraph(nodes).copy()
        else:
            G = G.subgraph(components[0]).copy()

    print(f"  OEIS crossrefs: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges "
          f"({n_lines} lines read)")
    return [{"source": "oeis", "name": "oeis_crossrefs", "graph": G,
             "n_nodes": G.number_of_nodes(), "n_edges": G.number_of_edges()}]


def load_mmlkg_graph(max_nodes=50000):
    """Load MMLKG theorem reference graph from CSV."""
    import networkx as nx

    if not MMLKG_REFS.exists():
        print(f"  WARNING: {MMLKG_REFS} not found")
        return []

    G = nx.DiGraph()
    n_lines = 0
    with open(MMLKG_REFS) as f:
        header = f.readline()  # skip header
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                G.add_edge(parts[0].strip(), parts[1].strip())
                n_lines += 1
            if G.number_of_nodes() > max_nodes:
                break

    print(f"  MMLKG: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges "
          f"({n_lines} lines read)")
    return [{"source": "mmlkg", "name": "mmlkg_refs", "graph": G,
             "n_nodes": G.number_of_nodes(), "n_edges": G.number_of_edges()}]


# ---------------------------------------------------------------------------
# Invariant computation
# ---------------------------------------------------------------------------

def compute_invariants(graph_entry):
    """Compute spectral and structural invariants for a single graph."""
    import networkx as nx
    import scipy.sparse as sp
    from scipy.sparse.linalg import eigsh

    source = graph_entry["source"]
    name = graph_entry["name"]
    n_nodes = graph_entry["n_nodes"]

    result = {
        "source": source,
        "name": name,
        "n_nodes": n_nodes,
        "n_edges": graph_entry["n_edges"],
    }

    # Convert to networkx Graph (undirected) for structural invariants
    if "graph" in graph_entry:
        G_raw = graph_entry["graph"]
        if isinstance(G_raw, nx.DiGraph):
            G = G_raw.to_undirected()
        else:
            G = G_raw
    elif "matrix" in graph_entry:
        mat = graph_entry["matrix"]
        # Symmetrize for undirected
        sym = mat + mat.T
        sym = (sym > 0).astype(float)
        G = nx.from_scipy_sparse_array(sym)
    else:
        print(f"  WARNING: no graph data for {name}")
        return result

    if G.number_of_nodes() < 3:
        print(f"  WARNING: {name} too small ({G.number_of_nodes()} nodes)")
        return result

    # Connected components
    components = list(nx.connected_components(G))
    result["n_components"] = len(components)
    largest_cc = max(components, key=len)
    result["largest_cc_size"] = len(largest_cc)

    # Work on largest connected component
    Gcc = G.subgraph(largest_cc).copy()
    n_cc = Gcc.number_of_nodes()

    # Degree distribution
    degrees = [d for _, d in Gcc.degree()]
    result["mean_degree"] = round(float(np.mean(degrees)), 4)
    result["max_degree"] = int(np.max(degrees))
    result["std_degree"] = round(float(np.std(degrees)), 4)

    # Full degree sequence (or histogram for large graphs)
    degree_sequence = sorted(degrees, reverse=True)
    if len(degree_sequence) > 10000:
        hist, bin_edges = np.histogram(degree_sequence, bins=100)
        result["degree_histogram"] = hist.tolist()
        result["degree_histogram_bin_edges"] = bin_edges.tolist()
    else:
        result["degree_sequence"] = degree_sequence

    # Power law exponent fit (on degree >= 1)
    deg_counts = defaultdict(int)
    for d in degrees:
        if d > 0:
            deg_counts[d] += 1
    if len(deg_counts) >= 3:
        x = np.log(list(deg_counts.keys()))
        y = np.log(list(deg_counts.values()))
        try:
            slope, _, _, _, _ = np.polyfit(x, y, 1, full=False, cov=False).tolist() if False else (0,) * 5
        except Exception:
            pass
        try:
            coeffs = np.polyfit(x, y, 1)
            result["power_law_exponent"] = round(float(-coeffs[0]), 4)
        except Exception:
            result["power_law_exponent"] = None
    else:
        result["power_law_exponent"] = None

    # Average clustering coefficient
    if n_cc <= 50000:
        try:
            result["avg_clustering"] = round(float(nx.average_clustering(Gcc)), 6)
        except Exception:
            result["avg_clustering"] = None
    else:
        # Sample for large graphs
        try:
            sample_nodes = list(Gcc.nodes())[:5000]
            result["avg_clustering"] = round(float(nx.average_clustering(Gcc, nodes=sample_nodes)), 6)
        except Exception:
            result["avg_clustering"] = None

    # Spectral properties via Laplacian
    if n_cc >= 3:
        try:
            L = nx.laplacian_matrix(Gcc).astype(float)
            # Algebraic connectivity = 2nd smallest eigenvalue of Laplacian
            # Use eigsh for sparse matrices; find smallest eigenvalues
            k = min(6, n_cc - 1)
            if n_cc <= 500:
                # Dense eigenvalue computation for small graphs
                L_dense = L.toarray()
                evals = np.sort(np.linalg.eigvalsh(L_dense))
            else:
                evals = eigsh(L, k=k, which='SM', return_eigenvectors=False)
                evals = np.sort(evals)

            # lambda_1 should be ~0, lambda_2 is algebraic connectivity
            result["eigenvalues_small"] = [round(float(e), 6) for e in evals[:k]]
            result["algebraic_connectivity"] = round(float(evals[1]), 6) if len(evals) > 1 else None
            result["spectral_gap"] = round(float(evals[1] - evals[0]), 6) if len(evals) > 1 else None

        except Exception as e:
            warnings.warn(f"Spectral computation failed for {name}: {e}")
            result["algebraic_connectivity"] = None
            result["spectral_gap"] = None
    else:
        result["algebraic_connectivity"] = None
        result["spectral_gap"] = None

    return result


# ---------------------------------------------------------------------------
# Cross-domain comparison
# ---------------------------------------------------------------------------

def compare_invariants(invariants):
    """Pairwise comparison of invariant vectors across domains."""
    # Only compare graphs from DIFFERENT sources
    comparisons = []

    for i, j in combinations(range(len(invariants)), 2):
        a, b = invariants[i], invariants[j]
        if a["source"] == b["source"]:
            continue

        # Build comparable feature vectors
        keys = ["mean_degree", "std_degree", "power_law_exponent",
                "avg_clustering", "algebraic_connectivity", "spectral_gap"]

        vec_a, vec_b = [], []
        shared_keys = []
        for k in keys:
            va = a.get(k)
            vb = b.get(k)
            if va is not None and vb is not None:
                vec_a.append(va)
                vec_b.append(vb)
                shared_keys.append(k)

        if len(vec_a) < 2:
            continue

        vec_a = np.array(vec_a)
        vec_b = np.array(vec_b)

        # Normalize for comparison
        norms = np.maximum(np.abs(vec_a) + np.abs(vec_b), 1e-10)
        diff = np.abs(vec_a - vec_b) / norms
        similarity = 1.0 - float(np.mean(diff))

        # Correlation
        if np.std(vec_a) > 0 and np.std(vec_b) > 0:
            corr = float(np.corrcoef(vec_a, vec_b)[0, 1])
        else:
            corr = 0.0

        comparisons.append({
            "graph_a": f"{a['source']}/{a['name']}",
            "graph_b": f"{b['source']}/{b['name']}",
            "source_a": a["source"],
            "source_b": b["source"],
            "n_features_compared": len(shared_keys),
            "features_compared": shared_keys,
            "values_a": [round(v, 4) for v in vec_a.tolist()],
            "values_b": [round(v, 4) for v in vec_b.tolist()],
            "similarity": round(similarity, 4),
            "correlation": round(corr, 4),
        })

    comparisons.sort(key=lambda x: x["similarity"], reverse=True)
    return comparisons


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def save_jsonl(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for entry in data:
            f.write(json.dumps(entry, cls=_NumpyEncoder) + "\n")
    print(f"  Wrote {len(data)} entries to {path}")


def main():
    parser = argparse.ArgumentParser(description="Graph Invariants — spectral comparison of math graphs")
    parser.add_argument("--source", type=str, default=None,
                        choices=["isogeny", "mathlib", "oeis", "mmlkg"],
                        help="Only process this source")
    parser.add_argument("--max-nodes", type=int, default=10000,
                        help="Max nodes per graph (default: 10000)")
    parser.add_argument("--max-isogeny", type=int, default=50,
                        help="Max isogeny graphs to process (default: 50)")
    args = parser.parse_args()

    t_start = time.time()

    # Load graphs
    all_graphs = []
    sources = [args.source] if args.source else ["isogeny", "mathlib", "oeis", "mmlkg"]

    print("--- Loading graphs ---")
    if "isogeny" in sources:
        iso_graphs = load_isogeny_graphs(max_nodes=args.max_nodes)
        # Limit number of isogeny graphs
        if len(iso_graphs) > args.max_isogeny:
            # Sample evenly across primes
            step = max(1, len(iso_graphs) // args.max_isogeny)
            iso_graphs = iso_graphs[::step][:args.max_isogeny]
            print(f"  Sampled {len(iso_graphs)} isogeny graphs")
        all_graphs.extend(iso_graphs)

    if "mathlib" in sources:
        all_graphs.extend(load_mathlib_graph())

    if "oeis" in sources:
        all_graphs.extend(load_oeis_crossref_graph(max_nodes=args.max_nodes))

    if "mmlkg" in sources:
        all_graphs.extend(load_mmlkg_graph(max_nodes=args.max_nodes))

    print(f"\nTotal graphs loaded: {len(all_graphs)}")

    # Compute invariants
    print("\n--- Computing invariants ---")
    invariants = []
    for i, g in enumerate(all_graphs):
        t0 = time.time()
        print(f"  [{i+1}/{len(all_graphs)}] {g['source']}/{g['name']} "
              f"({g['n_nodes']} nodes, {g['n_edges']} edges) ...", end="", flush=True)
        inv = compute_invariants(g)
        elapsed = time.time() - t0
        print(f" {elapsed:.1f}s")
        invariants.append(inv)

    # Clean up: remove non-serializable fields
    for inv in invariants:
        inv.pop("matrix", None)
        inv.pop("graph", None)

    save_jsonl(invariants, OUT_INVARIANTS)

    # Cross-domain comparisons
    print("\n--- Cross-domain comparisons ---")
    comparisons = compare_invariants(invariants)
    save_jsonl(comparisons, OUT_COMPARISONS)

    # Battery testing on top cross-domain pairs using degree sequences
    print("\n--- Battery testing on degree sequences ---")
    try:
        from falsification_battery import run_battery

        # Build lookup from source/name -> invariant entry
        inv_lookup = {f"{inv['source']}/{inv['name']}": inv for inv in invariants}

        top_pairs = comparisons[:10]
        battery_results = []
        for rank, comp in enumerate(top_pairs):
            ga, gb = comp["graph_a"], comp["graph_b"]
            inv_a = inv_lookup.get(ga, {})
            inv_b = inv_lookup.get(gb, {})

            # Get degree data — prefer full sequence, fall back to histogram
            deg_a = inv_a.get("degree_sequence") or inv_a.get("degree_histogram")
            deg_b = inv_b.get("degree_sequence") or inv_b.get("degree_histogram")

            if deg_a is None or deg_b is None:
                print(f"  [{rank+1}] {ga} ~ {gb}: SKIP (no degree data)")
                continue

            deg_a = np.array(deg_a, dtype=float)
            deg_b = np.array(deg_b, dtype=float)

            # Truncate to same length for battery (shorter of the two)
            min_len = min(len(deg_a), len(deg_b))
            deg_a_trunc = deg_a[:min_len]
            deg_b_trunc = deg_b[:min_len]

            claim = f"degree_seq: {ga} ~ {gb}"
            try:
                verdict, tests = run_battery(deg_a_trunc, deg_b_trunc, claim=claim)
                n_pass = sum(1 for t in tests if t.get("pass", False))
                n_total = len(tests)
                print(f"  [{rank+1}] {ga} <-> {gb}: {verdict} ({n_pass}/{n_total} tests)")
                battery_results.append({
                    "rank": rank + 1,
                    "graph_a": ga,
                    "graph_b": gb,
                    "similarity": comp["similarity"],
                    "verdict": verdict,
                    "n_pass": n_pass,
                    "n_total": n_total,
                })
            except Exception as e:
                print(f"  [{rank+1}] {ga} <-> {gb}: ERROR ({e})")

        if battery_results:
            survivors = [r for r in battery_results if r["verdict"] == "SURVIVES"]
            print(f"\n  Battery summary: {len(survivors)}/{len(battery_results)} pairs survive")
            for s in survivors:
                print(f"    {s['graph_a']} <-> {s['graph_b']} (sim={s['similarity']:.4f})")

    except ImportError as e:
        print(f"  WARNING: Could not import falsification_battery: {e}")
    except Exception as e:
        print(f"  WARNING: Battery testing failed: {e}")

    # Summary
    elapsed = time.time() - t_start
    by_source = defaultdict(int)
    for inv in invariants:
        by_source[inv["source"]] += 1

    print(f"\n{'='*60}")
    print(f"Graph Invariants Summary")
    print(f"  Graphs analyzed: {len(invariants)}")
    for src, cnt in sorted(by_source.items()):
        print(f"    {src}: {cnt}")
    print(f"  Cross-domain comparisons: {len(comparisons)}")
    if comparisons:
        top = comparisons[0]
        print(f"  Most similar pair: {top['graph_a']} <-> {top['graph_b']} "
              f"(sim={top['similarity']:.4f}, corr={top['correlation']:.4f})")
    n_high = sum(1 for c in comparisons if c["similarity"] > 0.8)
    print(f"  High similarity (>0.8): {n_high}")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
