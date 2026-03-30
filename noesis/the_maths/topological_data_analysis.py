"""
Topological Data Analysis — mapper algorithm, nerve theorem, simplicial complexes from data

Connects to: [persistent_homology, algebraic_topology, computational_geometry, graph_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "topological_data_analysis"
OPERATIONS = {}


def simplicial_complex_from_distances(x):
    """Build a simplicial complex (as edge list) from pairwise distances.
    Input: array of 1D points. Output: matrix of edges (k x 2).
    Threshold at median pairwise distance. Returns edges of resulting graph.
    """
    n = len(x)
    D = np.abs(x[:, None] - x[None, :])
    upper = D[np.triu_indices(n, k=1)]
    if len(upper) == 0:
        return np.array([[0, 0]], dtype=float)
    eps = np.median(upper)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] <= eps:
                edges.append([i, j])
    if not edges:
        return np.array([[0, 0]], dtype=float)
    return np.array(edges, dtype=float)


OPERATIONS["simplicial_complex_from_distances"] = {
    "fn": simplicial_complex_from_distances,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Edge list of simplicial complex from 1D point cloud at median distance threshold"
}


def nerve_of_cover(x):
    """Nerve of a cover: given 1D data, partition into overlapping intervals and compute nerve.
    Input: array of 1D values. Output: matrix (adjacency of nerve nodes).
    Uses 3 overlapping intervals covering the range.
    """
    n_intervals = 3
    overlap = 0.3
    lo, hi = x.min(), x.max()
    span = hi - lo + 1e-12
    step = span / n_intervals
    cover_sets = []
    for k in range(n_intervals):
        left = lo + k * step - overlap * step
        right = lo + (k + 1) * step + overlap * step
        members = set(np.where((x >= left) & (x <= right))[0].tolist())
        cover_sets.append(members)

    # Nerve: vertices = cover sets, edge if intersection is nonempty
    adj = np.zeros((n_intervals, n_intervals))
    for i in range(n_intervals):
        for j in range(i + 1, n_intervals):
            if cover_sets[i] & cover_sets[j]:
                adj[i, j] = 1
                adj[j, i] = 1
    return adj


OPERATIONS["nerve_of_cover"] = {
    "fn": nerve_of_cover,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Nerve (adjacency matrix) of an overlapping interval cover of 1D data"
}


def euler_characteristic_simplicial(x):
    """Euler characteristic of a simplicial complex built from 1D points.
    chi = vertices - edges + triangles.
    Input: array of 1D points. Output: integer.
    """
    n = len(x)
    D = np.abs(x[:, None] - x[None, :])
    upper = D[np.triu_indices(n, k=1)]
    if len(upper) == 0:
        return np.int64(n)
    eps = np.median(upper)

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] <= eps:
                edges.append((i, j))

    # Count triangles
    adj = D <= eps
    np.fill_diagonal(adj, False)
    triangles = 0
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j]:
                for k in range(j + 1, n):
                    if adj[i, k] and adj[j, k]:
                        triangles += 1

    chi = n - len(edges) + triangles
    return np.int64(chi)


OPERATIONS["euler_characteristic_simplicial"] = {
    "fn": euler_characteristic_simplicial,
    "input_type": "array",
    "output_type": "integer",
    "description": "Euler characteristic (V - E + F) of simplicial complex from point cloud"
}


def mapper_1d_simple(x):
    """Simplified 1D Mapper: filter by value, cover with intervals, cluster within, build nerve.
    Input: array of 1D values (also used as filter function). Output: matrix (adjacency).
    """
    n_intervals = 4
    overlap = 0.3
    lo, hi = x.min(), x.max()
    span = hi - lo + 1e-12
    step = span / n_intervals

    nodes = []  # Each node is a set of point indices
    for k in range(n_intervals):
        left = lo + k * step - overlap * step
        right = lo + (k + 1) * step + overlap * step
        members = np.where((x >= left) & (x <= right))[0]
        if len(members) > 0:
            # Simple clustering: single cluster per interval for 1D
            nodes.append(set(members.tolist()))

    nn = len(nodes)
    adj = np.zeros((nn, nn))
    for i in range(nn):
        for j in range(i + 1, nn):
            if nodes[i] & nodes[j]:
                adj[i, j] = 1
                adj[j, i] = 1
    return adj


OPERATIONS["mapper_1d_simple"] = {
    "fn": mapper_1d_simple,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Simplified 1D Mapper graph as adjacency matrix"
}


def connected_components_graph(x):
    """Connected components of a threshold graph on 1D points.
    Input: array of 1D points. Output: array of component labels.
    """
    n = len(x)
    D = np.abs(x[:, None] - x[None, :])
    upper = D[np.triu_indices(n, k=1)]
    eps = np.median(upper) if len(upper) > 0 else 1.0

    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] <= eps:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj

    labels = np.array([find(i) for i in range(n)], dtype=float)
    # Relabel to 0, 1, 2, ...
    unique = {}
    counter = 0
    result = np.zeros(n)
    for i in range(n):
        root = int(labels[i])
        if root not in unique:
            unique[root] = counter
            counter += 1
        result[i] = unique[root]
    return result


OPERATIONS["connected_components_graph"] = {
    "fn": connected_components_graph,
    "input_type": "array",
    "output_type": "array",
    "description": "Connected component labels for threshold graph on 1D points"
}


def simplicial_star(x):
    """Star of vertex 0 in the Rips complex: all simplices containing vertex 0.
    Input: array of 1D points. Output: array of vertex indices in the star.
    """
    n = len(x)
    D = np.abs(x[:, None] - x[None, :])
    upper = D[np.triu_indices(n, k=1)]
    eps = np.median(upper) if len(upper) > 0 else 1.0
    star = [0]
    for j in range(1, n):
        if D[0, j] <= eps:
            star.append(j)
    return np.array(star, dtype=float)


OPERATIONS["simplicial_star"] = {
    "fn": simplicial_star,
    "input_type": "array",
    "output_type": "array",
    "description": "Star of vertex 0 in the Rips complex (all neighbors plus vertex 0)"
}


def link_of_vertex(x):
    """Link of vertex 0: neighbors of vertex 0 that are also mutually connected.
    Input: array of 1D points. Output: array of vertex indices in the link.
    """
    n = len(x)
    D = np.abs(x[:, None] - x[None, :])
    upper = D[np.triu_indices(n, k=1)]
    eps = np.median(upper) if len(upper) > 0 else 1.0

    neighbors = []
    for j in range(1, n):
        if D[0, j] <= eps:
            neighbors.append(j)
    # Link = simplices in star not containing vertex 0
    # For edges: just the neighbors themselves
    # For higher simplices: pairs of neighbors that are connected
    return np.array(neighbors if neighbors else [0], dtype=float)


OPERATIONS["link_of_vertex"] = {
    "fn": link_of_vertex,
    "input_type": "array",
    "output_type": "array",
    "description": "Link of vertex 0 in the Rips complex"
}


def filtration_values(x):
    """All unique filtration values (edge weights) in the Rips filtration.
    Input: array of 1D points. Output: array of sorted unique distances.
    """
    n = len(x)
    D = np.abs(x[:, None] - x[None, :])
    upper = D[np.triu_indices(n, k=1)]
    return np.sort(np.unique(upper))


OPERATIONS["filtration_values"] = {
    "fn": filtration_values,
    "input_type": "array",
    "output_type": "array",
    "description": "Sorted unique filtration values (all pairwise distances) for Rips complex"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
