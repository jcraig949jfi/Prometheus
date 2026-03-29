"""
Persistent Homology — Vietoris-Rips complex, persistence diagrams, bottleneck distance

Connects to: [algebraic_topology, topological_data_analysis, computational_geometry, metric_spaces]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "persistent_homology"
OPERATIONS = {}


def distance_matrix(x):
    """Compute pairwise Euclidean distance matrix from 1D point cloud.
    Input: array of point coordinates. Output: matrix.
    """
    return np.abs(x[:, None] - x[None, :])


OPERATIONS["distance_matrix"] = {
    "fn": distance_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Pairwise distance matrix from 1D point cloud"
}


def vietoris_rips_edges(x):
    """Edges in the Vietoris-Rips complex at radius epsilon = median pairwise distance.
    Input: array of 1D points. Output: matrix (k x 2) of edge endpoint indices.
    """
    n = len(x)
    D = np.abs(x[:, None] - x[None, :])
    # Use median of nonzero distances as threshold
    upper = D[np.triu_indices(n, k=1)]
    if len(upper) == 0:
        return np.array([[0, 0]])
    eps = np.median(upper)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] <= eps:
                edges.append([i, j])
    if len(edges) == 0:
        return np.array([[0, 0]])
    return np.array(edges, dtype=float)


OPERATIONS["vietoris_rips_edges"] = {
    "fn": vietoris_rips_edges,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Edges of the Vietoris-Rips complex at median distance threshold"
}


def connected_components_filtration(x):
    """Track connected components as epsilon grows (0-dimensional persistence).
    Input: array of 1D points. Output: array of epsilon values where components merge.
    Uses single-linkage clustering: sorted edge weights give merge events.
    """
    n = len(x)
    if n <= 1:
        return np.array([0.0])
    D = np.abs(x[:, None] - x[None, :])
    upper = D[np.triu_indices(n, k=1)]
    merge_times = np.sort(upper)
    # Union-find to track actual merges
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edges_sorted = []
    for i in range(n):
        for j in range(i + 1, n):
            edges_sorted.append((D[i, j], i, j))
    edges_sorted.sort()

    merge_epsilons = []
    for d, i, j in edges_sorted:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
            merge_epsilons.append(d)

    if len(merge_epsilons) == 0:
        return np.array([0.0])
    return np.array(merge_epsilons)


OPERATIONS["connected_components_filtration"] = {
    "fn": connected_components_filtration,
    "input_type": "array",
    "output_type": "array",
    "description": "Epsilon values at which connected components merge (0-dim persistence)"
}


def persistence_diagram_0d(x):
    """0-dimensional persistence diagram from 1D point cloud.
    Input: array of 1D points. Output: matrix (n-1 x 2) of (birth, death) pairs.
    All components are born at 0; they die when merged into older component.
    """
    n = len(x)
    if n <= 1:
        return np.array([[0.0, 0.0]])

    D = np.abs(x[:, None] - x[None, :])
    parent = list(range(n))
    birth = np.zeros(n)  # All born at epsilon=0

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((D[i, j], i, j))
    edges.sort()

    diagram = []
    for d, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            # Younger component dies (higher index = younger in arbitrary ordering)
            younger = max(ri, rj)
            parent[younger] = min(ri, rj)
            diagram.append([birth[younger], d])

    if len(diagram) == 0:
        return np.array([[0.0, 0.0]])
    return np.array(diagram)


OPERATIONS["persistence_diagram_0d"] = {
    "fn": persistence_diagram_0d,
    "input_type": "array",
    "output_type": "matrix",
    "description": "0-dimensional persistence diagram (birth-death pairs) from 1D point cloud"
}


def bottleneck_distance_approx(x):
    """Approximate bottleneck distance between two persistence diagrams.
    Input: array of length 4k encoding two diagrams as [b1,d1,b2,d2,...,b1',d1',b2',d2',...].
    For simplicity, treats input as two sets of death times and computes
    the L-infinity distance between sorted death values.
    Output: scalar.
    """
    n = len(x)
    h = n // 2
    deaths1 = np.sort(x[:h])
    deaths2 = np.sort(x[h:])
    m = min(len(deaths1), len(deaths2))
    if m == 0:
        return np.float64(0.0)
    return np.float64(np.max(np.abs(deaths1[:m] - deaths2[:m])))


OPERATIONS["bottleneck_distance_approx"] = {
    "fn": bottleneck_distance_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate bottleneck distance between two persistence diagrams"
}


def persistence_entropy(x):
    """Persistence entropy: Shannon entropy of normalized persistence intervals.
    Input: array of 1D points (computes 0-dim persistence, then entropy). Output: scalar.
    """
    n = len(x)
    if n <= 1:
        return np.float64(0.0)

    D = np.abs(x[:, None] - x[None, :])
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((D[i, j], i, j))
    edges.sort()

    lifetimes = []
    for d, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)
            lifetimes.append(d)  # birth=0, death=d

    if len(lifetimes) == 0 or sum(lifetimes) == 0:
        return np.float64(0.0)

    lifetimes = np.array(lifetimes)
    p = lifetimes / lifetimes.sum()
    p = p[p > 0]
    return np.float64(-np.sum(p * np.log(p)))


OPERATIONS["persistence_entropy"] = {
    "fn": persistence_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of the 0-dimensional persistence diagram"
}


def betti_curve(x):
    """Betti-0 curve: number of connected components as a function of epsilon.
    Input: array of 1D points. Output: array of Betti numbers at evenly spaced epsilon.
    """
    n = len(x)
    if n <= 1:
        return np.array([1.0])

    merge_eps = connected_components_filtration(x)
    max_eps = merge_eps[-1] * 1.2 if len(merge_eps) > 0 else 1.0
    epsilons = np.linspace(0, max_eps, 20)
    betti = np.zeros(20)
    for idx, eps in enumerate(epsilons):
        components = n - np.sum(merge_eps <= eps)
        betti[idx] = components
    return betti


OPERATIONS["betti_curve"] = {
    "fn": betti_curve,
    "input_type": "array",
    "output_type": "array",
    "description": "Betti-0 curve (component count vs epsilon) for 1D point cloud"
}


def total_persistence(x):
    """Total persistence: sum of all persistence intervals raised to power p=2.
    Input: array of 1D points. Output: scalar.
    """
    n = len(x)
    if n <= 1:
        return np.float64(0.0)

    D = np.abs(x[:, None] - x[None, :])
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((D[i, j], i, j))
    edges.sort()

    lifetimes = []
    for d, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)
            lifetimes.append(d)

    if len(lifetimes) == 0:
        return np.float64(0.0)
    return np.float64(np.sum(np.array(lifetimes)**2))


OPERATIONS["total_persistence"] = {
    "fn": total_persistence,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Total persistence (sum of squared lifetimes) of 0-dim diagram"
}


def wasserstein_persistence(x):
    """Wasserstein-1 distance between a persistence diagram and the empty diagram.
    This equals the sum of all persistence (lifetimes).
    Input: array of 1D points. Output: scalar.
    """
    n = len(x)
    if n <= 1:
        return np.float64(0.0)

    D = np.abs(x[:, None] - x[None, :])
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((D[i, j], i, j))
    edges.sort()

    total = 0.0
    for d, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)
            total += d  # distance from (0, d) to diagonal = d/sqrt(2), but commonly just d

    return np.float64(total)


OPERATIONS["wasserstein_persistence"] = {
    "fn": wasserstein_persistence,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Wasserstein-1 distance from 0-dim persistence diagram to empty diagram"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
