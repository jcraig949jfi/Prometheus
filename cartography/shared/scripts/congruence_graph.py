"""
Congruence Graph — topology of elliptic curve a_p congruences.

Build a graph where EC are nodes and edges represent a_p congruences mod ell.
The topology of this graph IS the mathematical structure. No feature vectors,
no metric comparisons — pure graph properties.

For each prime ell in {2, 3, 5, 7, 11}:
  - Edge if >= 70% of first 10 a_p values are congruent mod ell
  - Measure: degree distribution, clustering, components, Ollivier-Ricci curvature
  - Test: do graph communities predict rank better than conductor alone?

Reads: charon/data/charon.duckdb (elliptic_curves table)
Saves: cartography/convergence/data/congruence_graph_results.json
"""
import sys
import json
import time
import warnings
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

warnings.filterwarnings("ignore")


class NumpyEncoder(json.JSONEncoder):
    """Handle numpy types in JSON serialization."""
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "charon" / "data" / "charon.duckdb"
OUT_PATH = ROOT / "cartography" / "convergence" / "data" / "congruence_graph_results.json"

# ---------- parameters ----------
PRIMES_ELL = [2, 3, 5, 7, 11]
NUM_AP = 10          # first 10 a_p values for congruence check
THRESHOLD = 0.7      # fraction of a_p that must agree mod ell
SUBSAMPLE = 5000     # max EC to keep
ORC_SAMPLES = 1000   # random edges for curvature estimation
K_NEIGHBORS = 10     # neighborhood size for ORC
N_COMMUNITIES = 5    # spectral clustering communities
NULL_TRIALS = 200    # permutation trials for chi-squared null


def load_data():
    """Load EC data from DuckDB, subsample to SUBSAMPLE curves."""
    import duckdb
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT lmfdb_label, conductor, rank, torsion, aplist
        FROM elliptic_curves
        WHERE aplist IS NOT NULL
    """).fetchall()
    con.close()

    print(f"Loaded {len(df)} elliptic curves with aplist")

    # Deduplicate by aplist (isogeny classes share a_p) — keep one per iso class
    seen_ap = {}
    unique = []
    for row in df:
        label, conductor, rank, torsion, aplist = row
        ap_key = tuple(aplist[:NUM_AP])
        if ap_key not in seen_ap:
            seen_ap[ap_key] = True
            unique.append(row)
    print(f"After dedup by first {NUM_AP} a_p: {len(unique)} unique curves")

    # Subsample
    rng = np.random.RandomState(42)
    if len(unique) > SUBSAMPLE:
        idx = rng.choice(len(unique), SUBSAMPLE, replace=False)
        idx.sort()
        unique = [unique[i] for i in idx]
    print(f"Working with {len(unique)} curves")

    labels = [r[0] for r in unique]
    conductors = np.array([r[1] for r in unique], dtype=np.int64)
    ranks = np.array([r[2] for r in unique], dtype=np.int32)
    torsions = np.array([r[3] for r in unique], dtype=np.int32)
    ap_matrix = np.array([list(r[4][:NUM_AP]) for r in unique], dtype=np.int64)

    return labels, conductors, ranks, torsions, ap_matrix


def build_congruence_graph(ap_matrix, ell, threshold=THRESHOLD):
    """
    Build adjacency list: edge if fraction of a_p congruent mod ell >= threshold.
    Returns adjacency dict and edge list with weights.
    """
    n = len(ap_matrix)
    # Precompute residues mod ell
    residues = ap_matrix % ell  # shape (n, NUM_AP)

    adjacency = defaultdict(list)
    edges = []
    min_agree = int(np.ceil(threshold * NUM_AP))

    # Vectorized pairwise comparison
    # For 5000 nodes this is 12.5M pairs — do in batches
    batch_size = 500
    for i in range(0, n, batch_size):
        i_end = min(i + batch_size, n)
        # residues[i:i_end] has shape (batch, NUM_AP)
        # residues has shape (n, NUM_AP)
        # Compare: (batch, 1, NUM_AP) == (1, n, NUM_AP) -> (batch, n, NUM_AP)
        agree = (residues[i:i_end, None, :] == residues[None, :, :]).sum(axis=2)
        # agree shape: (batch, n)

        for bi, gi in enumerate(range(i, i_end)):
            for gj in range(gi + 1, n):
                if agree[bi, gj] >= min_agree:
                    w = float(agree[bi, gj]) / NUM_AP
                    adjacency[gi].append(gj)
                    adjacency[gj].append(gi)
                    edges.append((gi, gj, w))

        if (i // batch_size) % 2 == 0:
            sys.stdout.write(f"\r  Building graph ell={ell}: {i_end}/{n} rows processed, {len(edges)} edges so far")
            sys.stdout.flush()

    print(f"\r  ell={ell}: {len(edges)} edges among {n} nodes" + " " * 30)
    return adjacency, edges


def degree_distribution(adjacency, n):
    """Compute degree distribution stats."""
    degrees = np.array([len(adjacency.get(i, [])) for i in range(n)])
    isolated = int(np.sum(degrees == 0))
    return {
        "mean": float(np.mean(degrees)),
        "median": float(np.median(degrees)),
        "max": int(np.max(degrees)),
        "std": float(np.std(degrees)),
        "isolated_nodes": isolated,
        "histogram_bins": list(map(int, np.histogram(degrees, bins=20)[0])),
        "histogram_edges": list(map(float, np.histogram(degrees, bins=20)[1])),
    }


def connected_components(adjacency, n):
    """BFS-based connected components."""
    visited = set()
    components = []
    for start in range(n):
        if start in visited:
            continue
        if start not in adjacency or len(adjacency[start]) == 0:
            visited.add(start)
            components.append([start])
            continue
        # BFS
        queue = [start]
        visited.add(start)
        comp = []
        while queue:
            node = queue.pop(0)
            comp.append(node)
            for nb in adjacency[node]:
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
        components.append(comp)
    components.sort(key=len, reverse=True)
    sizes = [len(c) for c in components]
    return components, {
        "num_components": len(components),
        "largest": sizes[0] if sizes else 0,
        "top5_sizes": sizes[:5],
        "isolated": sum(1 for s in sizes if s == 1),
    }


def clustering_coefficient(adjacency, n):
    """Mean local clustering coefficient."""
    coeffs = []
    for i in range(n):
        neighbors = adjacency.get(i, [])
        k = len(neighbors)
        if k < 2:
            continue
        # Count edges among neighbors
        nb_set = set(neighbors)
        triangles = 0
        for ni in neighbors:
            for nj in adjacency.get(ni, []):
                if nj in nb_set and nj > ni:
                    triangles += 1
        possible = k * (k - 1) / 2
        coeffs.append(triangles / possible)

    if not coeffs:
        return {"mean": 0.0, "median": 0.0, "std": 0.0, "n_nodes_with_2plus_neighbors": 0}
    return {
        "mean": float(np.mean(coeffs)),
        "median": float(np.median(coeffs)),
        "std": float(np.std(coeffs)),
        "n_nodes_with_2plus_neighbors": len(coeffs),
    }


def approximate_orc(adjacency, edges, n, n_samples=ORC_SAMPLES, k=K_NEIGHBORS):
    """
    Approximate Ollivier-Ricci curvature for random edges.
    ORC(x,y) = 1 - W1(mu_x, mu_y) / d(x,y)
    where mu_x is uniform on k-nearest neighbors of x (by graph distance=1).
    W1 approximated by sorting neighbor degree sequences.
    """
    rng = np.random.RandomState(123)
    if len(edges) == 0:
        return {"mean": 0.0, "fraction_positive": 0.0, "fraction_negative": 0.0, "n_sampled": 0}

    sample_idx = rng.choice(len(edges), min(n_samples, len(edges)), replace=False)
    curvatures = []

    for idx in sample_idx:
        u, v, w = edges[idx]
        # Neighborhoods
        nb_u = adjacency.get(u, [])
        nb_v = adjacency.get(v, [])
        if len(nb_u) < 2 or len(nb_v) < 2:
            continue

        # Take up to k neighbors
        nu = nb_u[:k] if len(nb_u) >= k else nb_u
        nv = nb_v[:k] if len(nb_v) >= k else nb_v

        # Uniform measures on neighborhoods
        # W1 approximation: fraction of shared neighbors
        set_u = set(nu)
        set_v = set(nv)
        overlap = len(set_u & set_v)
        union = len(set_u | set_v)

        if union == 0:
            continue

        # Better W1 approximation: use sorted degree sequences
        deg_u = sorted([len(adjacency.get(x, [])) for x in nu])
        deg_v = sorted([len(adjacency.get(x, [])) for x in nv])

        # Pad to same length
        max_len = max(len(deg_u), len(deg_v))
        while len(deg_u) < max_len:
            deg_u.append(0)
        while len(deg_v) < max_len:
            deg_v.append(0)

        # W1 on sorted empirical distributions
        deg_u = np.array(deg_u, dtype=float)
        deg_v = np.array(deg_v, dtype=float)

        # Normalize
        if deg_u.sum() > 0:
            deg_u /= deg_u.sum()
        if deg_v.sum() > 0:
            deg_v /= deg_v.sum()

        w1 = float(np.sum(np.abs(np.cumsum(deg_u) - np.cumsum(deg_v))))

        # d(u,v) = 1 for adjacent nodes
        orc = 1.0 - w1
        curvatures.append(orc)

    if not curvatures:
        return {"mean": 0.0, "fraction_positive": 0.0, "fraction_negative": 0.0, "n_sampled": 0}

    curv = np.array(curvatures)
    return {
        "mean": float(np.mean(curv)),
        "median": float(np.median(curv)),
        "std": float(np.std(curv)),
        "fraction_positive": float(np.mean(curv > 0)),
        "fraction_negative": float(np.mean(curv < 0)),
        "fraction_zero": float(np.mean(curv == 0)),
        "n_sampled": len(curvatures),
    }


def spectral_communities(adjacency, n, n_clusters=N_COMMUNITIES):
    """Spectral clustering on the graph Laplacian."""
    from scipy.sparse import lil_matrix
    from scipy.sparse.linalg import eigsh
    from sklearn.cluster import KMeans

    # Build sparse adjacency matrix
    A = lil_matrix((n, n), dtype=float)
    for i, neighbors in adjacency.items():
        for j in neighbors:
            A[i, j] = 1.0
    A = A.tocsr()

    # Degree matrix
    degrees = np.array(A.sum(axis=1)).flatten()
    # Isolated nodes get degree 1 to avoid division by zero
    degrees[degrees == 0] = 1

    # Normalized Laplacian: L = I - D^{-1/2} A D^{-1/2}
    D_inv_sqrt = 1.0 / np.sqrt(degrees)
    # We want the smallest eigenvalues of L, which correspond to
    # largest eigenvalues of D^{-1/2} A D^{-1/2}
    from scipy.sparse import diags
    D_inv_sqrt_mat = diags(D_inv_sqrt)
    L_norm = D_inv_sqrt_mat @ A @ D_inv_sqrt_mat

    # Get top-k eigenvectors
    try:
        vals, vecs = eigsh(L_norm, k=n_clusters, which='LM')
    except Exception as e:
        print(f"  Eigsh failed: {e}, falling back to random assignment")
        return np.random.randint(0, n_clusters, size=n)

    # Normalize rows
    row_norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    row_norms[row_norms == 0] = 1
    vecs = vecs / row_norms

    # KMeans
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = km.fit_predict(vecs)
    return labels


def chi_squared_rank_test(community_labels, ranks, n_clusters=N_COMMUNITIES):
    """Chi-squared test: is rank distribution different across communities?"""
    from scipy.stats import chi2_contingency

    # Build contingency table: communities x rank
    unique_ranks = sorted(set(ranks))
    table = np.zeros((n_clusters, len(unique_ranks)), dtype=int)
    rank_to_col = {r: i for i, r in enumerate(unique_ranks)}
    for c, r in zip(community_labels, ranks):
        table[c, rank_to_col[r]] += 1

    # Remove empty rows/cols
    row_mask = table.sum(axis=1) > 0
    col_mask = table.sum(axis=0) > 0
    table_clean = table[row_mask][:, col_mask]

    if table_clean.shape[0] < 2 or table_clean.shape[1] < 2:
        return {"chi2": 0.0, "p_value": 1.0, "contingency_table": table.tolist(), "note": "degenerate table"}

    chi2, p, dof, expected = chi2_contingency(table_clean)
    return {
        "chi2": float(chi2),
        "p_value": float(p),
        "dof": int(dof),
        "contingency_table": table.tolist(),
        "rank_labels": unique_ranks,
    }


def null_chi_squared(ranks, n_clusters, n_trials=NULL_TRIALS):
    """Null distribution: random community assignment."""
    from scipy.stats import chi2_contingency

    rng = np.random.RandomState(99)
    chi2_nulls = []
    unique_ranks = sorted(set(ranks))
    rank_to_col = {r: i for i, r in enumerate(unique_ranks)}

    for _ in range(n_trials):
        fake_labels = rng.randint(0, n_clusters, size=len(ranks))
        table = np.zeros((n_clusters, len(unique_ranks)), dtype=int)
        for c, r in zip(fake_labels, ranks):
            table[c, rank_to_col[r]] += 1
        row_mask = table.sum(axis=1) > 0
        col_mask = table.sum(axis=0) > 0
        table_clean = table[row_mask][:, col_mask]
        if table_clean.shape[0] < 2 or table_clean.shape[1] < 2:
            chi2_nulls.append(0.0)
            continue
        try:
            chi2, p, dof, expected = chi2_contingency(table_clean)
            chi2_nulls.append(float(chi2))
        except:
            chi2_nulls.append(0.0)

    return chi2_nulls


def community_rank_profiles(community_labels, ranks, n_clusters=N_COMMUNITIES):
    """Rank distribution per community."""
    profiles = {}
    for c in range(n_clusters):
        mask = community_labels == c
        r = ranks[mask]
        if len(r) == 0:
            continue
        counter = Counter(r.tolist())
        profiles[str(c)] = {
            "size": int(len(r)),
            "rank_distribution": {str(k): v for k, v in sorted(counter.items())},
            "fraction_rank0": float(np.mean(r == 0)),
            "fraction_rank1": float(np.mean(r == 1)),
            "mean_rank": float(np.mean(r)),
        }
    return profiles


def community_arithmetic_test(community_labels, conductors):
    """Do communities share conductor divisors more than across communities?"""
    from math import gcd

    rng = np.random.RandomState(77)
    n = len(conductors)

    # Sample pairs within same community
    within_gcds = []
    across_gcds = []

    for _ in range(2000):
        i, j = rng.randint(0, n, size=2)
        if i == j:
            continue
        g = gcd(int(conductors[i]), int(conductors[j]))
        if community_labels[i] == community_labels[j]:
            within_gcds.append(g)
        else:
            across_gcds.append(g)

    # Also sample explicitly
    for _ in range(2000):
        # Force within-community pair
        c = rng.randint(0, N_COMMUNITIES)
        members = np.where(community_labels == c)[0]
        if len(members) < 2:
            continue
        i, j = rng.choice(members, 2, replace=False)
        within_gcds.append(gcd(int(conductors[i]), int(conductors[j])))

    for _ in range(2000):
        # Force across-community pair
        i, j = rng.randint(0, n, size=2)
        while community_labels[i] == community_labels[j]:
            j = rng.randint(0, n)
        across_gcds.append(gcd(int(conductors[i]), int(conductors[j])))

    return {
        "within_community_mean_gcd": float(np.mean(within_gcds)) if within_gcds else 0,
        "across_community_mean_gcd": float(np.mean(across_gcds)) if across_gcds else 0,
        "within_community_median_gcd": float(np.median(within_gcds)) if within_gcds else 0,
        "across_community_median_gcd": float(np.median(across_gcds)) if across_gcds else 0,
        "within_frac_gcd_gt1": float(np.mean(np.array(within_gcds) > 1)) if within_gcds else 0,
        "across_frac_gcd_gt1": float(np.mean(np.array(across_gcds) > 1)) if across_gcds else 0,
        "n_within_pairs": len(within_gcds),
        "n_across_pairs": len(across_gcds),
    }


def edge_conductor_distance(adjacency, edges, conductors, n):
    """Is |conductor_i - conductor_j| smaller for connected vs non-connected pairs?"""
    rng = np.random.RandomState(55)

    # Connected pairs
    if len(edges) == 0:
        return {"connected_mean_delta": 0, "random_mean_delta": 0}

    sample_edges = edges[:min(5000, len(edges))]
    connected_deltas = [abs(int(conductors[e[0]]) - int(conductors[e[1]])) for e in sample_edges]

    # Random non-connected pairs
    random_deltas = []
    for _ in range(len(sample_edges)):
        i, j = rng.randint(0, n, size=2)
        random_deltas.append(abs(int(conductors[i]) - int(conductors[j])))

    return {
        "connected_mean_delta_conductor": float(np.mean(connected_deltas)),
        "connected_median_delta_conductor": float(np.median(connected_deltas)),
        "random_mean_delta_conductor": float(np.mean(random_deltas)),
        "random_median_delta_conductor": float(np.median(random_deltas)),
        "n_connected_pairs": len(connected_deltas),
        "n_random_pairs": len(random_deltas),
    }


def community_torsion_alignment(community_labels, torsions, n_clusters=N_COMMUNITIES):
    """Do communities align with torsion structure?"""
    from scipy.stats import chi2_contingency

    unique_torsion = sorted(set(torsions.tolist()))
    table = np.zeros((n_clusters, len(unique_torsion)), dtype=int)
    tor_to_col = {t: i for i, t in enumerate(unique_torsion)}
    for c, t in zip(community_labels, torsions):
        table[c, tor_to_col[t]] += 1

    row_mask = table.sum(axis=1) > 0
    col_mask = table.sum(axis=0) > 0
    table_clean = table[row_mask][:, col_mask]

    if table_clean.shape[0] < 2 or table_clean.shape[1] < 2:
        return {"chi2": 0.0, "p_value": 1.0}

    chi2, p, dof, expected = chi2_contingency(table_clean)
    return {
        "chi2": float(chi2),
        "p_value": float(p),
        "dof": int(dof),
        "torsion_values": unique_torsion,
    }


def analyze_curvature_vs_rank(adjacency, edges, ranks, n, n_samples=ORC_SAMPLES):
    """Do high-curvature edges sit at rank boundaries?"""
    rng = np.random.RandomState(200)
    if len(edges) == 0:
        return {}

    sample_idx = rng.choice(len(edges), min(n_samples, len(edges)), replace=False)

    boundary_curv = []  # edges between different ranks
    interior_curv = []  # edges between same rank

    for idx in sample_idx:
        u, v, w = edges[idx]
        nb_u = adjacency.get(u, [])
        nb_v = adjacency.get(v, [])
        if len(nb_u) < 2 or len(nb_v) < 2:
            continue

        nu = nb_u[:K_NEIGHBORS]
        nv = nb_v[:K_NEIGHBORS]

        deg_u = sorted([len(adjacency.get(x, [])) for x in nu])
        deg_v = sorted([len(adjacency.get(x, [])) for x in nv])
        max_len = max(len(deg_u), len(deg_v))
        while len(deg_u) < max_len:
            deg_u.append(0)
        while len(deg_v) < max_len:
            deg_v.append(0)

        deg_u = np.array(deg_u, dtype=float)
        deg_v = np.array(deg_v, dtype=float)
        if deg_u.sum() > 0:
            deg_u /= deg_u.sum()
        if deg_v.sum() > 0:
            deg_v /= deg_v.sum()

        w1 = float(np.sum(np.abs(np.cumsum(deg_u) - np.cumsum(deg_v))))
        orc = 1.0 - w1

        if ranks[u] != ranks[v]:
            boundary_curv.append(orc)
        else:
            interior_curv.append(orc)

    result = {}
    if boundary_curv:
        result["boundary_mean_orc"] = float(np.mean(boundary_curv))
        result["boundary_median_orc"] = float(np.median(boundary_curv))
        result["boundary_n"] = len(boundary_curv)
    if interior_curv:
        result["interior_mean_orc"] = float(np.mean(interior_curv))
        result["interior_median_orc"] = float(np.median(interior_curv))
        result["interior_n"] = len(interior_curv)

    if boundary_curv and interior_curv:
        from scipy.stats import mannwhitneyu
        stat, p = mannwhitneyu(boundary_curv, interior_curv, alternative='two-sided')
        result["boundary_vs_interior_U"] = float(stat)
        result["boundary_vs_interior_p"] = float(p)

    return result


def main():
    t0 = time.time()
    print("=" * 70)
    print("CONGRUENCE GRAPH — Elliptic Curve a_p Topology")
    print("=" * 70)

    labels, conductors, ranks, torsions, ap_matrix = load_data()
    n = len(labels)

    print(f"\nRank distribution: {dict(Counter(ranks.tolist()))}")
    print(f"Torsion distribution: {dict(Counter(torsions.tolist()))}")
    print(f"Conductor range: [{conductors.min()}, {conductors.max()}]")

    all_results = {
        "metadata": {
            "n_curves": n,
            "num_ap_used": NUM_AP,
            "threshold": THRESHOLD,
            "primes": PRIMES_ELL,
            "rank_distribution": {str(k): int(v) for k, v in Counter(ranks.tolist()).items()},
            "torsion_distribution": {str(k): int(v) for k, v in Counter(torsions.tolist()).items()},
        },
        "per_prime": {},
    }

    for ell in PRIMES_ELL:
        print(f"\n{'='*50}")
        print(f"  PRIME ell = {ell}")
        print(f"{'='*50}")
        t1 = time.time()

        # Build graph
        adjacency, edges = build_congruence_graph(ap_matrix, ell)

        # Degree distribution
        print("  Computing degree distribution...")
        deg_dist = degree_distribution(adjacency, n)
        print(f"    Mean degree: {deg_dist['mean']:.1f}, max: {deg_dist['max']}, isolated: {deg_dist['isolated_nodes']}")

        # Connected components
        print("  Computing connected components...")
        components, comp_stats = connected_components(adjacency, n)
        print(f"    Components: {comp_stats['num_components']}, largest: {comp_stats['largest']}, isolated: {comp_stats['isolated']}")

        # Clustering coefficient
        print("  Computing clustering coefficient...")
        clust = clustering_coefficient(adjacency, n)
        print(f"    Mean clustering: {clust['mean']:.4f}")

        # Ollivier-Ricci curvature
        print("  Computing Ollivier-Ricci curvature...")
        orc = approximate_orc(adjacency, edges, n)
        print(f"    Mean ORC: {orc['mean']:.4f}, frac positive: {orc['fraction_positive']:.3f}, frac negative: {orc['fraction_negative']:.3f}")

        # Spectral communities
        print("  Computing spectral communities...")
        comm_labels = spectral_communities(adjacency, n)
        print(f"    Community sizes: {dict(Counter(comm_labels.tolist()))}")

        # Community rank profiles
        profiles = community_rank_profiles(comm_labels, ranks)
        for c, p in profiles.items():
            print(f"    Community {c}: n={p['size']}, rank0={p['fraction_rank0']:.3f}, rank1={p['fraction_rank1']:.3f}")

        # Chi-squared test: rank vs community
        print("  Chi-squared test (rank ~ community)...")
        chi2_result = chi_squared_rank_test(comm_labels, ranks)
        print(f"    chi2={chi2_result['chi2']:.2f}, p={chi2_result['p_value']:.4e}")

        # Null distribution
        print("  Computing null chi-squared distribution...")
        null_chi2s = null_chi_squared(ranks, N_COMMUNITIES)
        observed_chi2 = chi2_result['chi2']
        null_mean = float(np.mean(null_chi2s))
        null_std = float(np.std(null_chi2s))
        frac_exceeding = float(np.mean(np.array(null_chi2s) >= observed_chi2))
        print(f"    Null chi2: mean={null_mean:.2f}, std={null_std:.2f}")
        print(f"    Observed chi2={observed_chi2:.2f}, fraction of nulls >= observed: {frac_exceeding:.4f}")

        # Torsion alignment
        print("  Torsion alignment test...")
        torsion_result = community_torsion_alignment(comm_labels, torsions)
        print(f"    Torsion chi2={torsion_result['chi2']:.2f}, p={torsion_result['p_value']:.4e}")

        # Community arithmetic test
        print("  Community arithmetic (GCD) test...")
        arith = community_arithmetic_test(comm_labels, conductors)
        print(f"    Within-community mean GCD: {arith['within_community_mean_gcd']:.2f}")
        print(f"    Across-community mean GCD: {arith['across_community_mean_gcd']:.2f}")

        # Edge conductor distance
        print("  Edge conductor distance test...")
        edge_cond = edge_conductor_distance(adjacency, edges, conductors, n)
        print(f"    Connected pairs mean |delta cond|: {edge_cond.get('connected_mean_delta_conductor', 0):.1f}")
        print(f"    Random pairs mean |delta cond|:    {edge_cond.get('random_mean_delta_conductor', 0):.1f}")

        # Curvature vs rank boundary
        print("  Curvature vs rank boundary analysis...")
        curv_rank = analyze_curvature_vs_rank(adjacency, edges, ranks, n)
        if 'boundary_mean_orc' in curv_rank:
            print(f"    Boundary edges mean ORC: {curv_rank['boundary_mean_orc']:.4f} (n={curv_rank['boundary_n']})")
            print(f"    Interior edges mean ORC: {curv_rank['interior_mean_orc']:.4f} (n={curv_rank['interior_n']})")
            if 'boundary_vs_interior_p' in curv_rank:
                print(f"    Mann-Whitney p: {curv_rank['boundary_vs_interior_p']:.4e}")

        dt = time.time() - t1
        print(f"  Time for ell={ell}: {dt:.1f}s")

        all_results["per_prime"][str(ell)] = {
            "n_edges": len(edges),
            "degree_distribution": deg_dist,
            "connected_components": comp_stats,
            "clustering_coefficient": clust,
            "ollivier_ricci_curvature": orc,
            "community_rank_profiles": profiles,
            "chi_squared_rank_vs_community": chi2_result,
            "null_chi_squared": {
                "null_mean": null_mean,
                "null_std": null_std,
                "observed_chi2": observed_chi2,
                "frac_null_exceeding_observed": frac_exceeding,
            },
            "torsion_alignment": torsion_result,
            "community_arithmetic": arith,
            "edge_conductor_distance": edge_cond,
            "curvature_vs_rank_boundary": curv_rank,
            "time_seconds": dt,
        }

    # Summary across primes
    print(f"\n{'='*70}")
    print("SUMMARY ACROSS PRIMES")
    print(f"{'='*70}")
    summary = {}
    for ell_str, data in all_results["per_prime"].items():
        chi2_obs = data["chi_squared_rank_vs_community"]["chi2"]
        chi2_p = data["chi_squared_rank_vs_community"]["p_value"]
        null_frac = data["null_chi_squared"]["frac_null_exceeding_observed"]
        orc_mean = data["ollivier_ricci_curvature"]["mean"]
        n_edges = data["n_edges"]
        clust_mean = data["clustering_coefficient"]["mean"]

        print(f"  ell={ell_str:>2}: edges={n_edges:>7}, clustering={clust_mean:.4f}, "
              f"ORC={orc_mean:+.4f}, chi2={chi2_obs:>8.2f} (p={chi2_p:.2e}, null_frac={null_frac:.4f})")

        summary[ell_str] = {
            "n_edges": n_edges,
            "clustering": clust_mean,
            "mean_orc": orc_mean,
            "rank_chi2": chi2_obs,
            "rank_chi2_p": chi2_p,
            "null_frac_exceeding": null_frac,
        }

    all_results["summary"] = summary
    all_results["total_time_seconds"] = time.time() - t0

    # Save
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(all_results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Total time: {all_results['total_time_seconds']:.1f}s")


if __name__ == "__main__":
    main()
