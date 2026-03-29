"""
Probabilistic Combinatorics — Lovasz local lemma, random graphs, threshold functions

Connects to: [graph_theory, probability_theory, combinatorics, random_structures]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "probabilistic_combinatorics"
OPERATIONS = {}


def erdos_renyi_threshold(x):
    """Erdos-Renyi threshold for graph properties.
    Input: array [n, property_code] where property_code:
      1 = connectivity threshold p ~ log(n)/n
      2 = giant component threshold p ~ 1/n
      3 = Hamiltonian cycle threshold p ~ log(n)/n + log(log(n))/n
      (default: connectivity)
    Output: scalar (threshold probability).
    """
    n_val = max(int(round(x[0])), 2)
    prop = int(round(x[1])) if len(x) > 1 else 1
    if prop == 2:
        # Giant component threshold
        return np.float64(1.0 / n_val)
    elif prop == 3:
        # Hamiltonian cycle
        return np.float64((np.log(n_val) + np.log(np.log(n_val + 1))) / n_val)
    else:
        # Connectivity threshold
        return np.float64(np.log(n_val) / n_val)


OPERATIONS["erdos_renyi_threshold"] = {
    "fn": erdos_renyi_threshold,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Erdos-Renyi threshold probability for graph properties"
}


def lovasz_local_lemma_bound(x):
    """Lovasz Local Lemma (symmetric form): if each event has prob <= p
    and depends on at most d other events, and e*p*(d+1) <= 1, then
    Pr(avoid all) > 0.
    Input: array [p, d]. Output: scalar (1 if LLL condition holds, 0 if not;
    returns the value e*p*(d+1) for comparison with 1).
    """
    if len(x) < 2:
        return np.float64(np.e * x[0])
    p, d = np.abs(x[0]), np.abs(x[1])
    val = np.e * p * (d + 1)
    return np.float64(val)


OPERATIONS["lovasz_local_lemma_bound"] = {
    "fn": lovasz_local_lemma_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Lovasz Local Lemma criterion e*p*(d+1); value <= 1 means LLL applies"
}


def random_graph_edge_count(x):
    """Expected number of edges in G(n, p).
    E[edges] = C(n,2) * p.
    Input: array [n, p]. Output: scalar.
    """
    if len(x) < 2:
        return np.float64(0.0)
    n_val = max(int(round(x[0])), 0)
    p = np.clip(x[1], 0, 1)
    return np.float64(n_val * (n_val - 1) / 2.0 * p)


OPERATIONS["random_graph_edge_count"] = {
    "fn": random_graph_edge_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Expected edge count in Erdos-Renyi G(n,p)"
}


def chromatic_number_bound(x):
    """Probabilistic bound on chromatic number of G(n, 1/2).
    chi(G) ~ n / (2 * log2(n)) with high probability.
    Input: array [n]. Output: scalar.
    """
    n_val = max(int(round(x[0])), 2)
    chi = n_val / (2.0 * np.log2(n_val))
    return np.float64(chi)


OPERATIONS["chromatic_number_bound"] = {
    "fn": chromatic_number_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Asymptotic chromatic number bound for G(n, 1/2)"
}


def giant_component_threshold(x):
    """Giant component size in G(n, c/n) for c > 1.
    Input: array [n, c]. Output: scalar (expected size of giant component).
    For c > 1, the giant component has size ~ zeta * n where zeta is the
    survival probability of a Poisson(c) branching process: zeta = 1 - e^{-c*zeta}.
    """
    if len(x) < 2:
        return np.float64(0.0)
    n_val = max(x[0], 1)
    c = x[1]
    if c <= 1.0:
        return np.float64(0.0)
    # Solve zeta = 1 - exp(-c * zeta) by iteration
    zeta = 0.5
    for _ in range(200):
        zeta_new = 1.0 - np.exp(-c * zeta)
        if abs(zeta_new - zeta) < 1e-12:
            break
        zeta = zeta_new
    return np.float64(zeta * n_val)


OPERATIONS["giant_component_threshold"] = {
    "fn": giant_component_threshold,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Expected giant component size in G(n, c/n) for c > 1"
}


def random_graph_triangle_count(x):
    """Expected number of triangles in G(n, p).
    E[triangles] = C(n,3) * p^3.
    Input: array [n, p]. Output: scalar.
    """
    if len(x) < 2:
        return np.float64(0.0)
    n_val = max(int(round(x[0])), 0)
    p = np.clip(x[1], 0, 1)
    comb_n3 = n_val * (n_val - 1) * (n_val - 2) / 6.0
    return np.float64(comb_n3 * p**3)


OPERATIONS["random_graph_triangle_count"] = {
    "fn": random_graph_triangle_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Expected triangle count in G(n, p)"
}


def second_moment_method_bound(x):
    """Second moment method: Pr(X > 0) >= E[X]^2 / E[X^2].
    Input: array [E_X, E_X2] (first moment and second moment). Output: scalar.
    Returns the Paley-Zygmund lower bound.
    """
    if len(x) < 2:
        return np.float64(0.0)
    ex = x[0]
    ex2 = x[1]
    if ex2 <= 0 or ex <= 0:
        return np.float64(0.0)
    return np.float64(ex**2 / ex2)


OPERATIONS["second_moment_method_bound"] = {
    "fn": second_moment_method_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Second moment method lower bound Pr(X>0) >= E[X]^2/E[X^2]"
}


def alteration_method_bound(x):
    """Alteration (deletion) method for independent set.
    In G(n, p), greedily take all vertices and delete one endpoint of each edge.
    Expected independent set size >= n - E[edges] = n - C(n,2)*p.
    But the classic alteration bound: select each vertex independently with prob q,
    expected independent set >= n*q - C(n,2)*p*q^2. Optimize: q = 1/(np+1).
    => bound ~ n/(np+1) * (1 - p*(n-1)/(2*(np+1)))
    Simpler: alpha(G) >= n/(2*np) for p > 0.
    Input: array [n, p]. Output: scalar.
    """
    if len(x) < 2:
        return np.float64(1.0)
    n_val = max(x[0], 1)
    p = np.clip(x[1], 1e-12, 1.0)
    # Turan-type: alpha >= n / (1 + n*p*(n-1)/(n)) but simpler:
    # Alteration: pick each vertex with prob q = 1/(n*p), then delete bad edges
    # Expected size: n*q*(1-p)^{n*q} ~ 1/p * e^{-1} approximately
    # Standard result: alpha >= n/(2*d_avg + 1) where d_avg = (n-1)*p
    d_avg = (n_val - 1) * p
    return np.float64(n_val / (d_avg + 1))


OPERATIONS["alteration_method_bound"] = {
    "fn": alteration_method_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Alteration method lower bound on independence number in G(n,p)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
