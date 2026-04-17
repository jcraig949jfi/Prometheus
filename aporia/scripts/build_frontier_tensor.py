"""
Aporia Frontier Tensor Builder
Maps the real frontier of mathematics as a measurable geometric object.
Each open problem becomes a POINT in a coordinate space.
The geometry tells us where barriers are thinnest.

Filter: if a problem doesn't have measurable coordinates, it's a thought experiment, not a frontier point.
"""

import json
import numpy as np
from collections import Counter

# Load data
problems = []
with open('aporia/mathematics/questions.jsonl') as f:
    for line in f:
        problems.append(json.loads(line.strip()))

triage = []
with open('aporia/mathematics/triage.jsonl') as f:
    for line in f:
        triage.append(json.loads(line.strip()))

triage_map = {t['id']: t for t in triage}

# ============================================================
# COORDINATE DEFINITIONS
# Each is measurable, not philosophical
# ============================================================

# Coordinate 1: BARRIER TYPE (1-5, continuous)
barrier_map = {
    'combinatorics': 1, 'graph_theory': 1, 'ramsey_theory': 1,
    'discrete_geometry': 1, 'combinatorial_geometry': 1, 'combinatorial_set_theory': 1,
    'number_theory': 2, 'analytic_number_theory': 2, 'additive_number_theory': 2,
    'additive_combinatorics': 2, 'diophantine_equations': 2,
    'algebraic_geometry': 3, 'homological_algebra': 3, 'algebraic_topology': 3,
    'category_theory': 3, 'k_theory': 3, 'algebraic_k_theory': 3,
    'homotopy_theory': 3, 'differential_algebra': 3, 'commutative_algebra': 3,
    'mathematical_physics': 4, 'dynamical_systems': 4, 'pde': 4,
    'partial_differential_equations': 4, 'fluid_dynamics': 4,
    'quantum_field_theory': 4, 'quantum_mechanics': 4, 'quantum_chaos': 4,
    'celestial_mechanics': 4, 'statistical_physics': 4,
    'set_theory': 5, 'model_theory': 5, 'computability': 5,
    'automorphic_forms': 2.5, 'diophantine_geometry': 2.5,
    'arithmetic_geometry': 2.5, 'algebraic_number_theory': 2.5,
    'topology': 3.5, 'differential_geometry': 3.5,
    'symplectic_geometry': 3.5, 'spectral_geometry': 3.5,
    'geometric_topology': 3.5, 'symplectic_topology': 3.5,
    'computational_complexity': 1.5, 'knot_theory': 3,
    'group_theory': 2.5, 'ring_theory': 3, 'representation_theory': 3,
    'operator_algebra': 3.5, 'functional_analysis': 3.5,
    'complex_analysis': 2.5, 'harmonic_analysis': 2.5,
    'ergodic_theory': 3, 'probability_theory': 2, 'analysis': 2.5,
    'real_algebraic_geometry': 3, 'real_algebra': 3,
    'galois_cohomology': 3, 'galois_theory': 3,
    'matroid_theory': 1.5, 'linear_algebra': 1.5, 'matrix_theory': 1.5,
    'combinatorial_matrix_theory': 1.5, 'combinatorial_group_theory': 2,
    'universal_algebra': 3, 'geometric_algebra': 2,
    'modular_representation_theory': 3, 'character_theory': 3,
    'order_theory': 1.5, 'game_theory': 1.5,
    'optimization': 1.5, 'intelligence': 4,
    'operator_k_theory': 3.5, 'diophantine_approximation': 2,
    'fractal_geometry': 2.5, 'spectral_graph_theory': 1.5,
    'random_matrix_theory': 2.5, 'frame_theory': 3,
    'approximation_theory': 2, 'signal_processing': 1.5,
    'applied_mathematics': 2, 'stochastic_geometry': 2.5,
    'chaos_theory': 3, 'complex_dynamics': 3,
    'polyhedral_geometry': 1.5, 'convex_geometry': 1.5,
    'discrepancy_theory': 2, 'potential_theory': 2.5,
    'numerical_analysis': 1.5, 'queueing_theory': 1.5,
    'geometry': 2, 'quantum_information': 2,
}

# Coordinate 2: DATA COUPLING (0-1)
data_coupling = {
    'number_theory': 0.9, 'analytic_number_theory': 0.85,
    'algebraic_geometry': 0.55, 'automorphic_forms': 0.7,
    'knot_theory': 0.65, 'diophantine_geometry': 0.5,
    'combinatorics': 0.35, 'additive_combinatorics': 0.25,
    'graph_theory': 0.15, 'discrete_geometry': 0.1,
    'group_theory': 0.3, 'algebra': 0.2,
    'algebraic_number_theory': 0.6, 'arithmetic_geometry': 0.6,
    'matrix_theory': 0.2, 'random_matrix_theory': 0.8,
    'diophantine_equations': 0.4, 'additive_number_theory': 0.3,
    'topology': 0.15, 'differential_geometry': 0.1,
    'mathematical_physics': 0.15, 'dynamical_systems': 0.1,
    'pde': 0.05, 'set_theory': 0.0, 'model_theory': 0.0,
    'quantum_information': 0.3, 'spectral_graph_theory': 0.3,
    'complex_analysis': 0.3, 'harmonic_analysis': 0.2,
    'ergodic_theory': 0.1, 'probability_theory': 0.15,
    'computational_complexity': 0.2, 'combinatorial_group_theory': 0.15,
}

# Coordinate 3: FINGERPRINT COUNT (0-6 modalities: spectral, arithmetic, p-adic, algebraic, geometric, operator)
fingerprint_count = {
    'number_theory': 5, 'analytic_number_theory': 6,
    'algebraic_geometry': 4, 'automorphic_forms': 5,
    'knot_theory': 3, 'diophantine_geometry': 3,
    'combinatorics': 2, 'graph_theory': 2,
    'additive_combinatorics': 2, 'discrete_geometry': 1,
    'topology': 3, 'group_theory': 3,
    'algebraic_number_theory': 5, 'arithmetic_geometry': 5,
    'random_matrix_theory': 6, 'dynamical_systems': 3,
    'mathematical_physics': 4, 'pde': 2,
    'set_theory': 0, 'model_theory': 0, 'computability': 1,
    'complex_analysis': 3, 'harmonic_analysis': 3,
    'quantum_information': 3, 'matrix_theory': 2,
    'ring_theory': 2, 'commutative_algebra': 2,
    'representation_theory': 3, 'operator_algebra': 3,
    'ergodic_theory': 2, 'probability_theory': 2,
    'spectral_graph_theory': 3, 'fractal_geometry': 2,
}

# Coordinate 4: CROSS-DOMAIN BRIDGE COUNT (how many other subdomains it connects to in known mathematics)
bridge_count = {
    'number_theory': 8, 'analytic_number_theory': 7,
    'algebraic_geometry': 8, 'automorphic_forms': 7,
    'knot_theory': 2, 'diophantine_geometry': 5,
    'combinatorics': 3, 'graph_theory': 3,
    'additive_combinatorics': 3, 'discrete_geometry': 2,
    'topology': 5, 'group_theory': 6,
    'algebraic_number_theory': 7, 'arithmetic_geometry': 7,
    'random_matrix_theory': 6, 'dynamical_systems': 4,
    'mathematical_physics': 5, 'pde': 3,
    'set_theory': 2, 'model_theory': 2,
    'complex_analysis': 4, 'harmonic_analysis': 4,
    'representation_theory': 6, 'operator_algebra': 4,
    'quantum_information': 4, 'spectral_graph_theory': 3,
}

# Coordinate 5: TESTABILITY (from triage bucket: A=3, B=2, C=1)
# Already in triage data

# ============================================================
# BUILD THE FRONTIER TENSOR
# ============================================================

frontier_points = []
for p in problems:
    t = triage_map.get(p['id'], {})
    sd = p['subdomain']

    barrier = barrier_map.get(sd, 3.0)
    coupling = data_coupling.get(sd, 0.1)
    fp = fingerprint_count.get(sd, 1)
    bridges = bridge_count.get(sd, 2)
    bucket = {'A': 3, 'B': 2, 'C': 1}.get(t.get('bucket', 'C'), 1)

    # Normalize to [0, 1]
    coords = [
        barrier / 5.0,        # barrier depth (0=shallow, 1=foundational)
        coupling,              # data coupling (0=none, 1=full)
        fp / 6.0,             # fingerprint density (0=none, 1=all 6 modalities)
        bridges / 8.0,        # bridge density (0=isolated, 1=fully connected)
        bucket / 3.0,         # testability (0.33=C, 0.67=B, 1.0=A)
    ]

    # FILTER: problems with zero fingerprints and zero data coupling are thought experiments
    if fp == 0 and coupling == 0:
        continue  # not a real frontier point

    frontier_points.append({
        'id': p['id'],
        'title': p['title'],
        'subdomain': sd,
        'barrier': barrier,
        'data_coupling': coupling,
        'fingerprints': fp,
        'bridges': bridges,
        'bucket': bucket,
        'coords': coords,
    })

print(f"Frontier points (after filtering thought experiments): {len(frontier_points)}")

# ============================================================
# COMPUTE THE GEOMETRY
# ============================================================

coords = np.array([fp['coords'] for fp in frontier_points])
dims = ['barrier_depth', 'data_coupling', 'fingerprint_density', 'bridge_density', 'testability']

print(f"Frontier tensor: {coords.shape}")
print(f"Dimensions: {dims}")

# PCA
coords_centered = coords - coords.mean(axis=0)
U, S, Vt = np.linalg.svd(coords_centered, full_matrices=False)
explained = S**2 / (S**2).sum()

print(f"\nPCA of the frontier geometry:")
for i in range(len(S)):
    print(f"  PC{i+1}: SV={S[i]:.4f}, explained={100*explained[i]:.1f}%")

print(f"\nPC loadings (what each dimension means):")
for i in range(min(3, len(Vt))):
    loadings = sorted(zip(dims, Vt[i]), key=lambda x: -abs(x[1]))
    desc = ", ".join(f"{n}={v:+.3f}" for n, v in loadings)
    print(f"  PC{i+1}: {desc}")

# ============================================================
# ATTACKABILITY SCORE
# ============================================================

print(f"\n{'='*80}")
print(f"ATTACKABILITY RANKING")
print(f"Score = (data_coupling * fingerprints * testability) / barrier_depth")
print(f"High score = most vulnerable to Prometheus-style attack")
print(f"{'='*80}")

for fp in frontier_points:
    fp['attackability'] = (fp['data_coupling'] * fp['fingerprints'] * fp['bucket']) / max(fp['barrier'], 0.5)

frontier_points.sort(key=lambda x: -x['attackability'])

print(f"\n{'Rank':>4} {'ID':>12} {'Title':<45} {'Attack':>7} {'Barr':>5} {'Data':>5} {'FP':>3} {'Bkt':>4}")
print("-" * 90)
for i, fp in enumerate(frontier_points[:25]):
    print(f"{i+1:4d} {fp['id']:>12} {fp['title'][:45]:<45} {fp['attackability']:7.3f} {fp['barrier']:5.1f} {fp['data_coupling']:5.2f} {fp['fingerprints']:3d} {fp['bucket']:>4}")

# ============================================================
# FRONTIER EDGE (high fingerprints, low coupling = where new data matters most)
# ============================================================

print(f"\n{'='*80}")
print(f"FRONTIER EDGE: High fingerprints but low data coupling")
print(f"These are where ONE new dataset would open an entire frontier")
print(f"{'='*80}")

edge = sorted([fp for fp in frontier_points if fp['fingerprints'] >= 3 and fp['data_coupling'] < 0.2],
              key=lambda x: -x['fingerprints'])
for fp in edge[:15]:
    print(f"  {fp['id']:>12} {fp['title'][:45]:<45} fp={fp['fingerprints']} coupling={fp['data_coupling']:.2f} barrier={fp['barrier']}")

# ============================================================
# SILENT ZONE (low fingerprints, low bridges = genuinely isolated)
# ============================================================

print(f"\n{'='*80}")
print(f"SILENT ZONE: Low fingerprints AND low bridges")
print(f"These need fundamentally new measurement modalities")
print(f"{'='*80}")

silent = sorted([fp for fp in frontier_points if fp['fingerprints'] <= 2 and fp['bridges'] <= 3],
                key=lambda x: x['fingerprints'])
for fp in silent[:15]:
    print(f"  {fp['id']:>12} {fp['title'][:45]:<45} fp={fp['fingerprints']} bridges={fp['bridges']} barrier={fp['barrier']}")

# ============================================================
# GEOMETRY: pairwise distances, clustering
# ============================================================

from scipy.spatial.distance import pdist, squareform
dists = pdist(coords, metric='euclidean')
dist_matrix = squareform(dists)

# Average distance by barrier type
print(f"\n{'='*80}")
print(f"FRONTIER GEOMETRY: Average pairwise distance by barrier type")
print(f"{'='*80}")

for b in [1, 1.5, 2, 2.5, 3, 3.5, 4, 5]:
    idx = [i for i, fp in enumerate(frontier_points) if fp['barrier'] == b]
    if len(idx) >= 2:
        within = np.mean([dist_matrix[i, j] for i in idx for j in idx if i != j])
        print(f"  Barrier {b:3.1f}: {len(idx):3d} problems, avg within-barrier dist = {within:.4f}")

# Overall statistics
print(f"\n  Overall: mean dist = {np.mean(dists):.4f}, std = {np.std(dists):.4f}")
print(f"  Max dist = {np.max(dists):.4f}, min dist = {np.min(dists):.4f}")

# ============================================================
# SAVE
# ============================================================

output = {
    'n_problems': len(frontier_points),
    'n_filtered': len(problems) - len(frontier_points),
    'dimensions': dims,
    'pca': {
        'singular_values': S.tolist(),
        'explained_variance': explained.tolist(),
        'loadings': Vt.tolist(),
    },
    'statistics': {
        'mean_coords': coords.mean(axis=0).tolist(),
        'std_coords': coords.std(axis=0).tolist(),
        'mean_distance': float(np.mean(dists)),
    },
    'problems': frontier_points,
}

with open('aporia/mathematics/frontier_tensor.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved: aporia/mathematics/frontier_tensor.json")
print(f"  {len(frontier_points)} measurable frontier points x {len(dims)} dimensions")
print(f"  {len(problems) - len(frontier_points)} thought experiments filtered out")
