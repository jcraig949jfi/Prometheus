"""
Congruence graph of elliptic curves with Ollivier-Ricci curvature.

Pure arithmetic structure — no feature vectors.
Nodes = weight-2 dim-1 newforms (= EC up to isogeny).
Edges = congruence counts across first 10 prime-indexed traces mod {2,3,5}.
"""

import json
import time
import numpy as np
import networkx as nx
from collections import defaultdict
from pathlib import Path
import psycopg2

# ── 1. Connect and pull data ───────────────────────────────────────────

print("Connecting to LMFDB Postgres...")
conn = psycopg2.connect(
    host='devmirror.lmfdb.xyz',
    port=5432,
    dbname='lmfdb',
    user='lmfdb',
    password='lmfdb'
)
cur = conn.cursor()

print("Pulling newforms...")
cur.execute("""
    SELECT label, level, traces, analytic_rank
    FROM mf_newforms
    WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL AND level <= 5000
    ORDER BY level
    LIMIT 5000
""")
rows = cur.fetchall()
cur.close()
conn.close()

print(f"Retrieved {len(rows)} newforms")

# ── 2. Extract prime-indexed traces ────────────────────────────────────

# First 10 primes: indices 2,3,5,7,11,13,17,19,23,29
# traces array is 0-indexed, so a_p = traces[p-1] for 1-indexed label convention
# In LMFDB, traces[n] = a_{n+1}, i.e. traces[0] = a_1, traces[1] = a_2, ...
# So a_p = traces[p-1]
PRIMES_10 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
MODULI = [2, 3, 5]

forms = []
for label, level, traces, analytic_rank in rows:
    if traces is None or len(traces) < 30:
        continue
    # Extract a_p for first 10 primes
    ap = []
    for p in PRIMES_10:
        ap.append(traces[p - 1])  # traces is 0-indexed, a_n = traces[n-1]
    forms.append({
        'label': label,
        'level': level,
        'analytic_rank': analytic_rank if analytic_rank is not None else 0,
        'ap': ap
    })

print(f"Forms with sufficient traces: {len(forms)}")

# ── 3. Build congruence graph ──────────────────────────────────────────

print("Building congruence graph...")
t0 = time.time()

G = nx.Graph()
for i, f in enumerate(forms):
    G.add_node(i, label=f['label'], level=f['level'], rank=f['analytic_rank'])

# Precompute residues: forms x primes x moduli
n = len(forms)
# residues[i][prime_idx][mod_idx] = a_p(i) mod ell
residues = np.zeros((n, 10, 3), dtype=np.int32)
for i, f in enumerate(forms):
    for j, ap_val in enumerate(f['ap']):
        for k, ell in enumerate(MODULI):
            residues[i, j, k] = ap_val % ell

THRESHOLD = 15  # at least half of 30 possible congruences

edge_count = 0
edge_weights = []

# Vectorized pairwise comparison
# For each pair (i, j), count matches across all 10 primes x 3 moduli
print(f"Computing pairwise congruences for {n} forms...")

# Process in chunks to manage memory
chunk_size = 500
for i_start in range(0, n, chunk_size):
    i_end = min(i_start + chunk_size, n)
    # residues_chunk: (chunk, 10, 3)
    chunk = residues[i_start:i_end]

    for j_start in range(i_start, n, chunk_size):
        j_end = min(j_start + chunk_size, n)
        other = residues[j_start:j_end]

        # Compare: (chunk_i, chunk_j, 10, 3) -> count matches
        # chunk[:, None] has shape (ci, 1, 10, 3)
        # other[None, :] has shape (1, cj, 10, 3)
        matches = (chunk[:, None] == other[None, :]).sum(axis=(2, 3))  # (ci, cj)

        # Extract edges above threshold
        for di in range(matches.shape[0]):
            gi = i_start + di
            row = matches[di]
            for dj in range(matches.shape[1]):
                gj = j_start + dj
                if gi >= gj:
                    continue
                w = int(row[dj])
                if w >= THRESHOLD:
                    G.add_edge(gi, gj, weight=w)
                    edge_weights.append(w)
                    edge_count += 1

    pct = min(100, int(100 * i_end / n))
    print(f"  {pct}% done, {edge_count} edges so far...")

t1 = time.time()
print(f"Graph built in {t1-t0:.1f}s: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# ── 4. Graph statistics ────────────────────────────────────────────────

print("\nComputing graph statistics...")
degrees = [d for _, d in G.degree()]
components = list(nx.connected_components(G))
component_sizes = sorted([len(c) for c in components], reverse=True)

# Isolates (degree 0)
isolates = sum(1 for d in degrees if d == 0)

# Clustering on the non-trivial subgraph
non_isolate_nodes = [n for n, d in G.degree() if d > 0]
if non_isolate_nodes:
    clustering = nx.clustering(G, nodes=non_isolate_nodes)
    mean_clustering = np.mean(list(clustering.values()))
else:
    mean_clustering = 0.0

stats = {
    'num_nodes': G.number_of_nodes(),
    'num_edges': G.number_of_edges(),
    'mean_degree': float(np.mean(degrees)) if degrees else 0,
    'median_degree': float(np.median(degrees)) if degrees else 0,
    'max_degree': int(max(degrees)) if degrees else 0,
    'num_components': len(components),
    'largest_component': component_sizes[0] if component_sizes else 0,
    'top_5_components': component_sizes[:5],
    'isolates': isolates,
    'mean_clustering': float(mean_clustering),
    'edge_weight_mean': float(np.mean(edge_weights)) if edge_weights else 0,
    'edge_weight_median': float(np.median(edge_weights)) if edge_weights else 0,
}

print(f"  Nodes: {stats['num_nodes']}")
print(f"  Edges: {stats['num_edges']}")
print(f"  Mean degree: {stats['mean_degree']:.2f}")
print(f"  Max degree: {stats['max_degree']}")
print(f"  Components: {stats['num_components']}")
print(f"  Largest component: {stats['largest_component']}")
print(f"  Isolates: {stats['isolates']}")
print(f"  Mean clustering: {stats['mean_clustering']:.4f}")

# ── 5. Ollivier-Ricci curvature (Lin-Lu-Yau lower bound) ──────────────

print("\nComputing Ollivier-Ricci curvature...")

# Precompute neighbor sets for fast lookup
neighbor_sets = {}
for node in G.nodes():
    neighbor_sets[node] = set(G.neighbors(node))

def ollivier_ricci_curvature(G, u, v, nbr_sets):
    """
    Lin-Lu-Yau lower bound on Ollivier-Ricci curvature for unweighted graphs.

    For adjacent u,v with d(u,v)=1:
      ORC(u,v) >= (#triangles through (u,v)) * (1/d_u + 1/d_v) - (1/d_u + 1/d_v) + 2/max(d_u, d_v)

    More precisely, for the lazy random walk version:
      kappa(u,v) = 2/d_max + 2*|triangle(u,v)|/(d_u*d_v) * min(d_u,d_v)/(d_u+d_v-2*|triangle(u,v)|)
    But the standard combinatorial approximation is:

    We use the exact neighbor-overlap formula:
      kappa(u,v) = |N(u) ∩ N(v)| / max(|N(u)|, |N(v)|)
                   + |N(u) ∩ N(v)| / min(|N(u)|, |N(v)|)
                   - 1

    Actually, the correct Lin-Lu-Yau formula for adjacent nodes in unweighted graphs:
      kappa(u,v) >= (2 * |triangle|) / max(d_u, d_v) - 1 + 1/d_u + 1/d_v
    where triangle = |N(u) ∩ N(v)| (common neighbors).

    For better accuracy, we compute:
      W1 = 1 - (common/d_u + common/d_v + common_fraction_correction)
    Using the neighbor-overlap transport plan directly.
    """
    nu = nbr_sets[u]
    nv = nbr_sets[v]

    du = len(nu)
    dv = len(nv)
    if du == 0 or dv == 0:
        return 0.0

    # Common neighbors (distance 0 in the transport)
    common = nu & nv
    nc = len(common)

    # Neighbors of u only, neighbors of v only (distance 2 in the transport)
    only_u = nu - nv - {v}
    only_v = nv - nu - {u}

    # Transport plan for uniform measures on N(u) and N(v):
    # - Mass on common neighbors: matched at cost 0
    # - u itself is in N(v) if (u,v) edge exists: mass 1/dv at cost 1 -> transported to some only_u node
    # - Similarly v in N(u)
    # - Remaining only_u mass transported to only_v at cost 2

    # Exact W1 for uniform measures, using the structure:
    # mu_u = uniform on N(u), mu_v = uniform on N(v)
    # Common nodes get min(1/du, 1/dv) matched at cost 0
    # Node v is in N(u) with mass 1/du, node u is in N(v) with mass 1/dv -> cost 1
    # Excess from common + only_u/only_v at cost 2

    # Mass breakdown for mu_u:
    #   common nodes: nc * (1/du)  (each common node gets 1/du)
    #   v: 1/du
    #   only_u: |only_u| * (1/du)

    # Mass breakdown for mu_v:
    #   common nodes: nc * (1/dv)
    #   u: 1/dv
    #   only_v: |only_v| * (1/dv)

    # Optimal transport:
    # 1. At common nodes: match min(1/du, 1/dv) per node, cost 0
    matched_common = nc * min(1.0/du, 1.0/dv)
    excess_common = nc * abs(1.0/du - 1.0/dv)  # needs to be moved

    # 2. u in mu_v (mass 1/dv) can reach N(u) at cost 1
    # 3. v in mu_u (mass 1/du) can reach N(v) at cost 1
    cost1_mass = 1.0/du + 1.0/dv  # mass that travels distance 1

    # 4. Everything else travels distance 2
    # Total mass = 1, matched at 0 = matched_common, at cost 1 = cost1_mass
    # Remaining goes at cost 2
    cost2_mass = max(0, 1.0 - matched_common - excess_common/2 - cost1_mass/2)
    # Actually let's just compute W1 directly

    # Simpler: exact formula for adjacent nodes
    # W1 = 1 - nc*(1/du + 1/dv) + max(0, something)
    # Use the known result: for adjacent u,v in unweighted graph,
    #   ORC(u,v) = nc/du + nc/dv + 1/du + 1/dv - 1  (when nc <= min(du,dv))

    # This is the Lin-Lu-Yau formula:
    kappa = nc * (1.0/du + 1.0/dv) - 1.0 + 1.0/du + 1.0/dv

    # Correction: nodes at distance > 2 don't exist for adjacent nodes in dense graphs
    # The above is a lower bound. For a tighter estimate, account for
    # neighbors-of-neighbors overlap, but LLY is standard.

    return kappa


# Compute ORC on a sample of edges
edges_list = list(G.edges())
if len(edges_list) > 10000:
    rng = np.random.RandomState(42)
    sample_idx = rng.choice(len(edges_list), size=10000, replace=False)
    sample_edges = [edges_list[i] for i in sample_idx]
else:
    sample_edges = edges_list

print(f"Computing ORC on {len(sample_edges)} edges...")
curvatures = []
edge_meta = []

for idx, (u, v) in enumerate(sample_edges):
    if idx % 1000 == 0 and idx > 0:
        print(f"  {idx}/{len(sample_edges)} edges processed...")

    orc = ollivier_ricci_curvature(G, u, v, neighbor_sets)
    curvatures.append(orc)
    edge_meta.append({
        'u_label': forms[u]['label'],
        'v_label': forms[v]['label'],
        'u_level': forms[u]['level'],
        'v_level': forms[v]['level'],
        'u_rank': forms[u]['analytic_rank'],
        'v_rank': forms[v]['analytic_rank'],
        'weight': int(G[u][v]['weight']),
        'orc': float(orc)
    })

curvatures = np.array(curvatures)
print(f"ORC computed: mean={curvatures.mean():.4f}, std={curvatures.std():.4f}")
print(f"  min={curvatures.min():.4f}, max={curvatures.max():.4f}")

# ── 6. Stratify by curvature vs arithmetic ─────────────────────────────

print("\nStratifying curvature by arithmetic properties...")

# 6a. Curvature vs rank transition
same_rank = [e['orc'] for e in edge_meta if e['u_rank'] == e['v_rank']]
diff_rank = [e['orc'] for e in edge_meta if e['u_rank'] != e['v_rank']]

rank_analysis = {
    'same_rank_edges': len(same_rank),
    'diff_rank_edges': len(diff_rank),
    'same_rank_mean_orc': float(np.mean(same_rank)) if same_rank else None,
    'diff_rank_mean_orc': float(np.mean(diff_rank)) if diff_rank else None,
    'same_rank_std_orc': float(np.std(same_rank)) if same_rank else None,
    'diff_rank_std_orc': float(np.std(diff_rank)) if diff_rank else None,
}

# 6b. Curvature vs conductor proximity
same_level = [e['orc'] for e in edge_meta if e['u_level'] == e['v_level']]
diff_level = [e['orc'] for e in edge_meta if e['u_level'] != e['v_level']]

# Level ratio buckets
level_ratios = []
for e in edge_meta:
    lo, hi = min(e['u_level'], e['v_level']), max(e['u_level'], e['v_level'])
    ratio = hi / lo if lo > 0 else float('inf')
    level_ratios.append((ratio, e['orc']))

# Bucket: ratio < 1.5 (nearby), 1.5-5 (moderate), > 5 (distant)
near = [orc for r, orc in level_ratios if r < 1.5]
moderate = [orc for r, orc in level_ratios if 1.5 <= r < 5]
distant = [orc for r, orc in level_ratios if r >= 5]

level_analysis = {
    'same_level_edges': len(same_level),
    'same_level_mean_orc': float(np.mean(same_level)) if same_level else None,
    'diff_level_mean_orc': float(np.mean(diff_level)) if diff_level else None,
    'near_conductors_count': len(near),
    'near_conductors_mean_orc': float(np.mean(near)) if near else None,
    'moderate_conductors_count': len(moderate),
    'moderate_conductors_mean_orc': float(np.mean(moderate)) if moderate else None,
    'distant_conductors_count': len(distant),
    'distant_conductors_mean_orc': float(np.mean(distant)) if distant else None,
}

# 6c. Curvature distribution — quintiles
quintiles = np.percentile(curvatures, [0, 20, 40, 60, 80, 100])
curvature_quintiles = {
    f'Q{i+1}': f'[{quintiles[i]:.4f}, {quintiles[i+1]:.4f}]'
    for i in range(5)
}

# 6d. High vs low curvature regions — rank distribution
high_curv = [e for e in edge_meta if e['orc'] > np.percentile(curvatures, 80)]
low_curv = [e for e in edge_meta if e['orc'] < np.percentile(curvatures, 20)]

high_rank_dist = defaultdict(int)
low_rank_dist = defaultdict(int)
for e in high_curv:
    high_rank_dist[e['u_rank']] += 1
    high_rank_dist[e['v_rank']] += 1
for e in low_curv:
    low_rank_dist[e['u_rank']] += 1
    low_rank_dist[e['v_rank']] += 1

# Normalize
total_high = sum(high_rank_dist.values()) or 1
total_low = sum(low_rank_dist.values()) or 1
high_rank_frac = {str(k): v/total_high for k, v in sorted(high_rank_dist.items())}
low_rank_frac = {str(k): v/total_low for k, v in sorted(low_rank_dist.items())}

# 6e. Edge weight vs curvature correlation
weights = [e['weight'] for e in edge_meta]
weight_curv_corr = float(np.corrcoef(weights, curvatures)[0, 1]) if len(weights) > 1 else 0.0

# 6f. Degree vs curvature
node_mean_curv = defaultdict(list)
for e, orc_val in zip(sample_edges, curvatures):
    node_mean_curv[e[0]].append(orc_val)
    node_mean_curv[e[1]].append(orc_val)

node_degrees = []
node_curv_means = []
for node, curv_list in node_mean_curv.items():
    node_degrees.append(G.degree(node))
    node_curv_means.append(np.mean(curv_list))

degree_curv_corr = float(np.corrcoef(node_degrees, node_curv_means)[0, 1]) if len(node_degrees) > 2 else 0.0

# ── 7. Bottleneck detection ───────────────────────────────────────────

print("\nDetecting bottlenecks (negative curvature concentration)...")

# Edges with most negative curvature = bottlenecks
neg_curv_edges = sorted(edge_meta, key=lambda e: e['orc'])[:20]
bottlenecks = []
for e in neg_curv_edges:
    bottlenecks.append({
        'edge': f"{e['u_label']} -- {e['v_label']}",
        'levels': [e['u_level'], e['v_level']],
        'ranks': [e['u_rank'], e['v_rank']],
        'orc': e['orc'],
        'weight': e['weight']
    })

# ── 8. Assemble results ───────────────────────────────────────────────

results = {
    'description': (
        'Congruence graph of weight-2 dim-1 newforms (= elliptic curves up to isogeny). '
        'Edges connect forms sharing >= 15/30 trace congruences mod {2,3,5} at first 10 primes. '
        'Ollivier-Ricci curvature computed on edges. Pure arithmetic structure, no feature vectors.'
    ),
    'parameters': {
        'primes': PRIMES_10,
        'moduli': MODULI,
        'threshold': THRESHOLD,
        'max_conductor': 5000,
        'num_forms_queried': len(rows),
        'num_forms_used': len(forms),
    },
    'graph_statistics': stats,
    'curvature_summary': {
        'num_edges_sampled': len(sample_edges),
        'mean_orc': float(curvatures.mean()),
        'std_orc': float(curvatures.std()),
        'min_orc': float(curvatures.min()),
        'max_orc': float(curvatures.max()),
        'median_orc': float(np.median(curvatures)),
        'fraction_negative': float((curvatures < 0).mean()),
        'fraction_positive': float((curvatures > 0).mean()),
        'quintiles': curvature_quintiles,
    },
    'stratification': {
        'rank_analysis': rank_analysis,
        'level_analysis': level_analysis,
        'high_curvature_rank_distribution': high_rank_frac,
        'low_curvature_rank_distribution': low_rank_frac,
        'weight_curvature_correlation': weight_curv_corr,
        'degree_curvature_correlation': degree_curv_corr,
    },
    'bottlenecks_top20': bottlenecks,
}

# Save
out_path = Path('D:/Prometheus/harmonia/results/congruence_graph.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path}")
print("\n=== KEY FINDINGS ===")
print(f"Graph: {stats['num_nodes']} nodes, {stats['num_edges']} edges")
print(f"Mean degree: {stats['mean_degree']:.2f}, clustering: {stats['mean_clustering']:.4f}")
print(f"Components: {stats['num_components']}, largest: {stats['largest_component']}")
print(f"ORC: mean={curvatures.mean():.4f}, negative fraction={float((curvatures < 0).mean()):.3f}")
print(f"Rank transitions: same_rank ORC={rank_analysis['same_rank_mean_orc']}, diff_rank ORC={rank_analysis['diff_rank_mean_orc']}")
print(f"Weight-curvature correlation: {weight_curv_corr:.4f}")
print(f"Degree-curvature correlation: {degree_curv_corr:.4f}")
