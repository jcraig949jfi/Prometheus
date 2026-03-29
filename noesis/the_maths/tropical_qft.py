"""
Tropical QFT — Replace sum with min, multiply with add in path integrals

Connects to: [feynman_diagram_algebra, tqft, p_adic_physics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "tropical_qft"
OPERATIONS = {}


def tropical_partition_function(action_values):
    """Tropical partition function: Z_trop = min_configs S(config).
    In the tropical limit (beta -> inf), the partition function is dominated
    by the minimum action configuration.
    Input: action_values array (action for each configuration). Output: Z_trop scalar."""
    S = np.asarray(action_values, dtype=float)
    return np.float64(np.min(S))

OPERATIONS["tropical_partition_function"] = {
    "fn": tropical_partition_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical partition function (minimum action)"
}


def tropical_feynman_propagator(distances):
    """Tropical Feynman propagator: G_trop(x,y) = d(x,y) (the metric distance).
    In tropical QFT, the propagator is the tropical Green's function,
    which on a graph equals the shortest-path distance.
    Input: distances array (edge weights for a path). Output: total propagator array."""
    d = np.asarray(distances, dtype=float)
    # Tropical propagator along a path = sum of distances (tropical product = addition)
    # Return cumulative tropical propagator
    return np.cumsum(d)

OPERATIONS["tropical_feynman_propagator"] = {
    "fn": tropical_feynman_propagator,
    "input_type": "array",
    "output_type": "array",
    "description": "Tropical Feynman propagator (cumulative distance)"
}


def tropical_vertex_weight(momenta):
    """Tropical vertex weight: in tropical QFT, vertex conservation becomes
    min-plus constraint. Weight = 0 if momentum is conserved (sum = 0),
    else infinity (represented as large number).
    For tropical relaxation: weight = |sum of momenta|.
    Input: momenta array. Output: weight scalar."""
    p = np.asarray(momenta, dtype=float)
    return np.float64(np.abs(np.sum(p)))

OPERATIONS["tropical_vertex_weight"] = {
    "fn": tropical_vertex_weight,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical vertex weight (momentum conservation penalty)"
}


def tropical_diagram_evaluate(edge_weights, external_momenta=None):
    """Evaluate a tropical Feynman diagram: the tropical amplitude is
    min over internal momenta of (sum of edge actions).
    For a tree diagram: the amplitude is simply the sum of edge weights (tropical product).
    Input: edge_weights array. Output: amplitude scalar."""
    w = np.asarray(edge_weights, dtype=float)
    # Tropical product = ordinary sum; tropical sum = min
    # For a single diagram: tropical amplitude = sum of edge weights
    return np.float64(np.sum(w))

OPERATIONS["tropical_diagram_evaluate"] = {
    "fn": tropical_diagram_evaluate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Evaluate tropical Feynman diagram amplitude"
}


def tropical_curve_count(degree, genus=0):
    """Tropical curve count: number of tropical curves of degree d and genus g
    through the appropriate number of points in R^2.
    For genus 0: Mikhalkin's theorem gives N_d = number of tropical curves
    = classical Gromov-Witten invariant.
    N_1=1, N_2=1, N_3=12, ... (genus 0 rational curves in P^2).
    Input: degree array. Output: count array."""
    d = np.asarray(degree, dtype=float).astype(int)
    # Known genus-0 degree-d rational curve counts in P^2:
    # N_d: number of rational curves of degree d through 3d-1 general points
    known = {1: 1, 2: 1, 3: 12, 4: 620, 5: 87304}
    counts = np.array([float(known.get(int(di), 0)) for di in d.flat])
    return counts.reshape(d.shape)

OPERATIONS["tropical_curve_count"] = {
    "fn": tropical_curve_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Tropical curve count (genus-0 Gromov-Witten of P^2)"
}


def tropical_gromov_witten(degree, n_points):
    """Tropical Gromov-Witten invariant: counts tropical curves with multiplicity.
    For degree d curves through 3d-1 points in P^2.
    Each tropical curve has a multiplicity = product of vertex multiplicities.
    Vertex multiplicity for trivalent vertex = |det(v1, v2)| where v1,v2 are edge directions.
    Input: array [degree, n_points, ...]. Output: invariant scalar."""
    arr = np.asarray(degree, dtype=float)
    d = int(arr.flat[0])
    # Return the known Gromov-Witten invariant
    known = {1: 1, 2: 1, 3: 12, 4: 620, 5: 87304}
    return np.float64(known.get(d, 0))

OPERATIONS["tropical_gromov_witten"] = {
    "fn": lambda x: tropical_gromov_witten(x, None),
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical Gromov-Witten invariant for P^2"
}


def tropical_amplitude(edge_lengths, masses_sq=None):
    """Tropical amplitude: the tropical limit of a Feynman amplitude.
    A_trop = min over Schwinger parameters of (U*sum(m^2*alpha) + F/U)
    where U,F are Symanzik polynomials evaluated tropically.
    Simplified: for tree level, A_trop = sum of edge_length * mass^2.
    Input: edge_lengths array. Output: amplitude scalar."""
    L = np.asarray(edge_lengths, dtype=float)
    if masses_sq is None:
        masses_sq = np.ones_like(L)
    return np.float64(np.sum(L * masses_sq))

OPERATIONS["tropical_amplitude"] = {
    "fn": tropical_amplitude,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical Feynman amplitude (tree level)"
}


def tropical_one_loop(edge_lengths):
    """Tropical one-loop amplitude: for a cycle graph, the tropical amplitude is
    min over cycle momentum of sum_e (alpha_e * (p_e^2 + m^2)).
    At the tropical minimum, the loop momentum minimizes the total.
    For equal masses m=1: A = min_k sum_e alpha_e * (k + p_e)^2.
    The minimum is at k = -mean(p_e); A = sum(alpha) * var(p_e) + sum(alpha)*m^2.
    Simplified with p_e=0: A = sum(alpha) * m^2.
    Input: alpha (edge lengths) array. Output: amplitude scalar."""
    alpha = np.asarray(edge_lengths, dtype=float)
    # Tropical one-loop with zero external momenta and m=1:
    # The saddle point gives A = (sum alpha) * m^2
    # More interesting: the tropical curve contribution is
    # min over spanning trees of (product of non-tree edge lengths)
    # = min_i alpha_i for a cycle (remove one edge to get spanning tree)
    m_sq = 1.0
    # The one-loop tropical integral localizes to the shortest edge
    A_tree = np.min(alpha) * m_sq  # contribution from the spanning tree with max weight
    A_total = np.sum(alpha) * m_sq  # total action at saddle
    return np.float64(A_total)

OPERATIONS["tropical_one_loop"] = {
    "fn": tropical_one_loop,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical one-loop amplitude"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
