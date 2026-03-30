"""
Chemical Graph Theory -- Wiener index, Randic index, Zagreb indices, molecular topology

Connects to: [spectral_graph_theory, extremal_graph_theory, matroid_theory, topological_data_analysis]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "chemical_graph_theory"
OPERATIONS = {}


def _adjacency_from_array(x):
    """Convert flat array to adjacency matrix of a small graph."""
    n = int(np.ceil(np.sqrt(len(x))))
    A = np.zeros((n, n))
    for i in range(min(len(x), n * n)):
        row, col = divmod(i, n)
        A[row, col] = 1.0 if x[i] > np.median(x) else 0.0
    A = np.maximum(A, A.T)
    np.fill_diagonal(A, 0)
    return A


def _shortest_paths(A):
    """Floyd-Warshall shortest paths."""
    n = A.shape[0]
    dist = np.full((n, n), np.inf)
    dist[A > 0] = 1.0
    np.fill_diagonal(dist, 0)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
    return dist


def wiener_index(x):
    """Wiener index: sum of all shortest-path distances. Input: array (graph encoding). Output: scalar."""
    A = _adjacency_from_array(x)
    dist = _shortest_paths(A)
    dist[dist == np.inf] = 0
    return float(np.sum(dist) / 2.0)


OPERATIONS["wiener_index"] = {
    "fn": wiener_index,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Wiener index (sum of all pairwise shortest paths)"
}


def randic_index(x):
    """Randic connectivity index: sum over edges of 1/sqrt(deg(u)*deg(v)).
    Input: array. Output: scalar."""
    A = _adjacency_from_array(x)
    degrees = np.sum(A, axis=1)
    n = A.shape[0]
    result = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] > 0 and degrees[i] > 0 and degrees[j] > 0:
                result += 1.0 / np.sqrt(degrees[i] * degrees[j])
    return float(result)


OPERATIONS["randic_index"] = {
    "fn": randic_index,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Randic connectivity index"
}


def zagreb_index_first(x):
    """First Zagreb index: sum of squared degrees. Input: array. Output: scalar."""
    A = _adjacency_from_array(x)
    degrees = np.sum(A, axis=1)
    return float(np.sum(degrees ** 2))


OPERATIONS["zagreb_index_first"] = {
    "fn": zagreb_index_first,
    "input_type": "array",
    "output_type": "scalar",
    "description": "First Zagreb index M1 = sum of deg(v)^2"
}


def zagreb_index_second(x):
    """Second Zagreb index: sum over edges of deg(u)*deg(v). Input: array. Output: scalar."""
    A = _adjacency_from_array(x)
    degrees = np.sum(A, axis=1)
    n = A.shape[0]
    result = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] > 0:
                result += degrees[i] * degrees[j]
    return float(result)


OPERATIONS["zagreb_index_second"] = {
    "fn": zagreb_index_second,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Second Zagreb index M2 = sum_{edges} deg(u)*deg(v)"
}


def hosoya_index(x):
    """Hosoya Z-index: total number of matchings (including empty). Input: array. Output: scalar."""
    A = _adjacency_from_array(x)
    n = A.shape[0]
    if n > 15:
        n = 15
        A = A[:n, :n]
    # Count matchings via DP on subsets (small graphs only)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] > 0:
                edges.append((i, j))
    # Recursive matching count
    count = 0
    for size in range(n // 2 + 1):
        if size == 0:
            count += 1
            continue
        # For small n, enumerate via inclusion
        # Simple recursive approach
        break
    # Use the recurrence: Z(G) = Z(G-v) + sum_{u adj v} Z(G-v-u)
    # For efficiency, use a memo on frozenset of vertices
    memo = {}

    def count_matchings(vertices):
        key = frozenset(vertices)
        if key in memo:
            return memo[key]
        if len(vertices) <= 1:
            memo[key] = 1
            return 1
        v = min(vertices)
        rest = vertices - {v}
        total = count_matchings(rest)
        for u in rest:
            if A[v, u] > 0:
                total += count_matchings(rest - {u})
        memo[key] = total
        return total

    result = count_matchings(set(range(n)))
    return float(result)


OPERATIONS["hosoya_index"] = {
    "fn": hosoya_index,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Hosoya Z-index (total number of matchings)"
}


def balaban_j_index(x):
    """Balaban J index: m/(mu+1) * sum_{edges} 1/sqrt(D_i * D_j) where D_i = row sum of distance matrix.
    Input: array. Output: scalar."""
    A = _adjacency_from_array(x)
    n = A.shape[0]
    dist = _shortest_paths(A)
    dist[dist == np.inf] = 0
    D = np.sum(dist, axis=1)  # distance sums
    m = int(np.sum(A) / 2)  # number of edges
    mu = m - n + 1  # cyclomatic number (assumes connected)
    if mu + 1 == 0:
        return 0.0
    result = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] > 0 and D[i] > 0 and D[j] > 0:
                result += 1.0 / np.sqrt(D[i] * D[j])
    return float(m / (mu + 1) * result) if mu + 1 != 0 else 0.0


OPERATIONS["balaban_j_index"] = {
    "fn": balaban_j_index,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Balaban J index based on distance sums"
}


def estrada_index(x):
    """Estrada index: sum of exp(eigenvalues of adjacency matrix). Input: array. Output: scalar."""
    A = _adjacency_from_array(x)
    eigenvalues = np.linalg.eigvalsh(A)
    return float(np.sum(np.exp(eigenvalues)))


OPERATIONS["estrada_index"] = {
    "fn": estrada_index,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estrada index EE = sum exp(lambda_i)"
}


def molecular_connectivity(x):
    """General molecular connectivity index chi_k for k=1 (edge connectivity).
    Input: array. Output: scalar."""
    # Same as Randic for k=1
    return randic_index(x)


OPERATIONS["molecular_connectivity"] = {
    "fn": molecular_connectivity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Molecular connectivity index chi_1"
}


def topological_polar_surface(x):
    """Approximate topological polar surface area from graph encoding.
    Uses degree-based fragment contributions. Input: array. Output: scalar."""
    A = _adjacency_from_array(x)
    degrees = np.sum(A, axis=1)
    n = A.shape[0]
    # Simplified: vertices with degree 1 or 2 contribute like polar groups
    # This is a topological approximation, not true TPSA
    tpsa = 0.0
    for i in range(n):
        d = degrees[i]
        if d == 1:
            tpsa += 20.23  # terminal atom contribution
        elif d == 2:
            tpsa += 9.23  # bridge atom contribution
        elif d == 3:
            tpsa += 3.24
    return float(tpsa)


OPERATIONS["topological_polar_surface"] = {
    "fn": topological_polar_surface,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate topological polar surface area from graph topology"
}


def graph_energy_molecular(x):
    """Graph energy: sum of absolute eigenvalues of adjacency matrix. Input: array. Output: scalar."""
    A = _adjacency_from_array(x)
    eigenvalues = np.linalg.eigvalsh(A)
    return float(np.sum(np.abs(eigenvalues)))


OPERATIONS["graph_energy_molecular"] = {
    "fn": graph_energy_molecular,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Graph energy E(G) = sum |lambda_i|"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
