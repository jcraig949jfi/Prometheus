"""Demonstrate tensor concepts with real organism data."""
import numpy as np
import sys, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))

from organisms.explorer import load_all_organisms

organisms = load_all_organisms()

# ============================================================
# WHAT GOES INTO A TENSOR
# ============================================================
print("=== WHAT A TENSOR STORES ===\n")

# Feature dimensions: properties of each organism
feature_dims = [
    'produces_scalar', 'produces_array', 'produces_matrix', 'produces_structure',
    'takes_scalar', 'takes_array', 'takes_matrix',
    'n_operations', 'type_diversity', 'cross_domain_potential',
]

scalar_types = {'scalar', 'integer', 'real', 'float', 'number', 'complex_value',
                'density_comparison', 'analytic_estimate', 'statistical_estimate'}
array_types = {'array', 'vector', 'timeseries', 'sequence', 'list', 'distribution',
               'probability_distribution', 'population_vector', 'observation_vector',
               'prime_list', 'coordinate_list'}
matrix_types = {'matrix', 'adjacency_matrix', 'distance_matrix', 'joint_distribution'}
struct_types = {'dict', 'factorization', 'lattice_structure', 'persistence_diagram',
                'classification', 'anomaly_detection', 'invariant_vector',
                'algebraic_structure', 'partition_count', 'geometric_structure'}

org_names = list(organisms.keys())
n_orgs = len(org_names)
n_feats = len(feature_dims)
features = np.zeros((n_orgs, n_feats), dtype=np.float32)

for i, name in enumerate(org_names):
    org = organisms[name]
    ops = org.operations
    out_types = {op.get('output_type', '') for op in ops.values()}
    in_types = {op.get('input_type', '') for op in ops.values()}
    all_types = out_types | in_types

    features[i, 0] = len(out_types & scalar_types) / max(len(ops), 1)
    features[i, 1] = len(out_types & array_types) / max(len(ops), 1)
    features[i, 2] = len(out_types & matrix_types) / max(len(ops), 1)
    features[i, 3] = len(out_types & struct_types) / max(len(ops), 1)
    features[i, 4] = len(in_types & scalar_types) / max(len(ops), 1)
    features[i, 5] = len(in_types & array_types) / max(len(ops), 1)
    features[i, 6] = len(in_types & matrix_types) / max(len(ops), 1)
    features[i, 7] = len(ops) / 10.0
    features[i, 8] = len(all_types) / 10.0  # type diversity
    features[i, 9] = len(out_types - in_types) / max(len(all_types), 1)  # cross-domain

print(f"Feature matrix: {features.shape} ({n_orgs} organisms x {n_feats} features)")
print(f"Memory: {features.nbytes} bytes")
print()

# Show profiles
for name in ['topology', 'chaos_theory', 'prime_theory', 'immune_systems']:
    i = org_names.index(name)
    top_feats = sorted(zip(feature_dims, features[i]), key=lambda x: -x[1])[:4]
    profile = ', '.join(f"{f}={v:.2f}" for f, v in top_feats)
    print(f"  {name}: {profile}")
print()

# ============================================================
# HOW IT'S ORGANIZED: Dimensions have meaning
# ============================================================
print("=== HOW A TENSOR IS ORGANIZED ===\n")
print("Each DIMENSION is an axis of meaning:")
print("  Dim 0 (rows):    which organism")
print("  Dim 1 (columns): which feature")
print("  Dim 2 (depth):   which second organism (for pairwise)")
print("  Dim 3+:          which third organism (for triples), etc.")
print()

# Pairwise interaction: 2D matrix (organism x organism)
print("PAIRWISE NOVELTY MATRIX (organism x organism):")
novelty = np.zeros((n_orgs, n_orgs), dtype=np.float32)
complement = np.zeros((n_orgs, n_orgs), dtype=np.float32)

for i in range(n_orgs):
    for j in range(n_orgs):
        if i == j:
            continue
        interface = np.outer(features[i], features[j])
        diag_e = np.sum(np.diag(interface) ** 2)
        total_e = np.sum(interface ** 2)
        novelty[i, j] = 1.0 - diag_e / total_e if total_e > 0 else 0
        complement[i, j] = np.mean(np.abs(features[i] - features[j]))

print(f"  Shape: {novelty.shape}")
print(f"  Memory: {novelty.nbytes + complement.nbytes} bytes")
print()

# Top pairs
pairs = []
for i in range(n_orgs):
    for j in range(i + 1, n_orgs):
        combined = novelty[i, j] + complement[i, j]
        pairs.append((org_names[i], org_names[j], novelty[i, j], complement[i, j], combined))
pairs.sort(key=lambda x: -x[4])

print("TOP 10 MOST PROMISING PAIRS:")
for rank, (a, b, nov, comp, comb) in enumerate(pairs[:10], 1):
    print(f"  {rank:2d}. [{comb:.3f}] {a} x {b}  (novelty={nov:.2f}, complement={comp:.2f})")
print()

# ============================================================
# HOW IT'S SEARCHED: Navigation without full materialization
# ============================================================
print("=== HOW YOU SEARCH A TENSOR ===\n")

print("Method 1: DIRECT LOOKUP (fast, exact)")
print("  'What is the novelty between topology and chaos_theory?'")
ti = org_names.index('topology')
ci = org_names.index('chaos_theory')
print(f"  Answer: novelty[{ti}, {ci}] = {novelty[ti, ci]:.4f}  (one array access)\n")

print("Method 2: SLICE (fast, one dimension)")
print("  'What are ALL novelty scores for topology?'")
topo_row = novelty[ti, :]
top3 = np.argsort(topo_row)[-3:][::-1]
for idx in top3:
    print(f"  topology x {org_names[idx]}: {topo_row[idx]:.4f}")
print(f"  (scanned {n_orgs} values in one array operation)\n")

print("Method 3: TOP-K (fast, global)")
print("  'What are the top 5 pairs across ALL organisms?'")
flat_idx = np.argsort(novelty.flatten())[-10:][::-1]  # top 10, take unique pairs
seen = set()
count = 0
for idx in flat_idx:
    i, j = divmod(idx, n_orgs)
    key = (min(i, j), max(i, j))
    if key not in seen and i != j:
        seen.add(key)
        count += 1
        print(f"  {org_names[i]} x {org_names[j]}: {novelty[i, j]:.4f}")
        if count >= 5:
            break
print(f"  (one argsort over {n_orgs*n_orgs} values)\n")

print("Method 4: CONDITIONAL (fast, filtered)")
print("  'Which pairs have novelty > 0.9 AND complementarity > 0.1?'")
mask = (novelty > 0.9) & (complement > 0.1)
hits = np.argwhere(mask)
print(f"  Found {len(hits)} pairs matching condition")
for i, j in hits[:5]:
    print(f"    {org_names[i]} x {org_names[j]}: nov={novelty[i,j]:.3f} comp={complement[i,j]:.3f}")
print()

# ============================================================
# HOW TENSOR TRAINS COMPRESS FOR SCALE
# ============================================================
print("=== TENSOR TRAIN COMPRESSION ===\n")

# The problem: triple interactions
print("Problem: Triple interaction tensor")
print(f"  Full tensor: {n_orgs} x {n_orgs} x {n_orgs} = {n_orgs**3:,} entries")
print(f"  With features: {n_orgs} x {n_orgs} x {n_orgs} x {n_feats} = {n_orgs**3 * n_feats:,} entries")
print(f"  Memory: {n_orgs**3 * n_feats * 4 / 1024 / 1024:.1f} MB")
print()

# At 95 organisms (target):
n95 = 95
print(f"At scale (95 organisms, 50 features):")
print(f"  Full: {n95**3 * 50:,} entries = {n95**3 * 50 * 4 / 1024 / 1024:.0f} MB")
print()

# Tensor train compression
print("Tensor Train (TT) decomposition:")
print("  Instead of one huge tensor, store a chain of small matrices:")
print("  T[i,j,k] ~ G1[i] x G2[j] x G3[k]")
print("  where G1, G2, G3 are 'cores' of size (1 x n x r), (r x n x r), (r x n x 1)")
print()

for r in [3, 5, 10, 20]:
    tt_entries = (1 * n_orgs * r) + (r * n_orgs * r) + (r * n_orgs * 1)
    full_entries = n_orgs ** 3
    ratio = full_entries / tt_entries
    print(f"  Rank {r:2d}: {tt_entries:,} entries ({tt_entries*4/1024:.1f} KB) = {ratio:.0f}x compression")

print()

# At scale
print("At scale (95 organisms):")
for r in [5, 10, 20]:
    tt_entries = (1 * n95 * r) + (r * n95 * r) + (r * n95 * 1)
    full_entries = n95 ** 3
    ratio = full_entries / tt_entries
    print(f"  Rank {r:2d}: {tt_entries:,} entries ({tt_entries*4/1024:.1f} KB) vs {full_entries:,} full ({full_entries*4/1024/1024:.1f} MB) = {ratio:.0f}x")

print()
print("The TT cores ARE the search index.")
print("To find the highest-value triple:")
print("  1. Scan G1 to find the best organism A (18 values)")
print("  2. Given A, scan G2 to find best organism B (18 values)")
print("  3. Given A,B, scan G3 to find best organism C (18 values)")
print("  Total: 54 operations instead of 5,832 (18^3)")
print("  This is why THOR is fast: it never builds the full tensor.")
print()

# ============================================================
# WHAT ARCANUM ADDS
# ============================================================
print("=== WHAT ARCANUM DOES TO THE TENSOR ===\n")
print("When Poros discovers a composition with emergent properties:")
print("  1. The composition becomes a NEW NODE (organism)")
print("  2. Its feature vector is COMPUTED from the composition output")
print("  3. The feature matrix grows: (18, 10) -> (19, 10)")
print("  4. The interaction tensors update incrementally")
print("  5. NEW interfaces appear that didn't exist before")
print()
print("The Arcanum specimen is a node that no human put in the tensor.")
print("It emerged from composition. Its feature vector describes what it DOES,")
print("not what field of mathematics it came from (because it didn't come from any).")
print("It creates edges to existing nodes that nobody predicted.")
print()
print("The density of the tensor IS the value of the substrate.")
print("More nodes. More edges. More signal for THOR to navigate.")
print("Pack -> Search -> Discover -> Pack -> Search Faster.")
