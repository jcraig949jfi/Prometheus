"""
Extremal Graph Theory — Turan numbers, Zarankiewicz problem bounds, Ramsey graph construction

Connects to: [graph_theory, combinatorics, probabilistic_method, spectral_graph_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import comb, floor, ceil

FIELD_NAME = "extremal_graph_theory"
OPERATIONS = {}


def turan_number(x):
    """Turan number ex(n, K_r): maximum edges in an n-vertex graph with no K_r subgraph.
    Uses n = len(x), r = max(int(x[0]), 3).
    Formula: ex(n, K_r) = (1 - 1/(r-1)) * n^2 / 2 (Turan's theorem, exact formula).
    Exact: T(n,r-1) edges = (1 - 1/(r-1)) * n^2/2 adjusted for integer parts.
    Input: array. Output: scalar."""
    n = len(x)
    arr = np.asarray(x, dtype=float)
    r = max(int(abs(arr[0])), 3)  # forbid K_r, r >= 3
    # Exact Turan number: edges in the complete (r-1)-partite Turan graph
    p = r - 1  # number of parts
    # Parts have sizes floor(n/p) or ceil(n/p)
    small = n // p
    large = small + 1
    num_large = n % p
    num_small = p - num_large
    # Total edges = C(n,2) - sum of C(part_size, 2)
    total = comb(n, 2)
    total -= num_large * comb(large, 2)
    total -= num_small * comb(small, 2)
    return float(total)


OPERATIONS["turan_number"] = {
    "fn": turan_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Turan number ex(n, K_r): max edges avoiding K_r, n=len(x), r=max(int(x[0]),3)"
}


def turan_graph_edges(x):
    """Number of edges in the Turan graph T(n, r-1), the extremal graph for K_r-free.
    Uses n = len(x), r-1 = max(int(x[0]), 2) parts.
    Input: array. Output: scalar."""
    # Same as turan_number but parameterized differently for clarity
    return turan_number(x)


OPERATIONS["turan_graph_edges"] = {
    "fn": turan_graph_edges,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Edges in Turan graph T(n, r-1), equivalent to ex(n, K_r)"
}


def zarankiewicz_bound(x):
    """Kovari-Sos-Turan bound for the Zarankiewicz problem z(m, n; s, t).
    z(m,n;s,t) <= ((t-1)^{1/s} * (n - s + 1) * m^{1-1/s}) / 2 + (s-1)*n/2.
    Uses m=n=len(x), s=2, t=max(int(x[0]),2).
    Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=float)
    n = len(arr)
    m = n
    s = 2
    t = max(int(abs(arr[0])), 2)
    # KST bound: z(m,n;s,t) <= 0.5 * ((t-1)^{1/s} * m^{1-1/s} * n + (s-1)*m)
    # Standard form: z(m,n;s,t) <= 0.5 * ((t-1)^{1/s} * (m-s+1)^{1-...} * n^{...} + ...)
    # Simplified standard bound:
    bound = 0.5 * ((t - 1) ** (1.0 / s) * m ** (1.0 - 1.0 / s) * n + (s - 1) * m)
    return float(bound)


OPERATIONS["zarankiewicz_bound"] = {
    "fn": zarankiewicz_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Kovari-Sos-Turan upper bound on Zarankiewicz number z(n,n;2,t)"
}


def ex_complete_bipartite(x):
    """Upper bound on ex(n, K_{s,t}): max edges in K_{s,t}-free graph on n vertices.
    Uses Kovari-Sos-Turan theorem: ex(n, K_{s,t}) <= 0.5 * ((t-1)^{1/s} * n^{2-1/s} + (s-1)*n).
    s=2, t=max(int(x[0]),2), n=len(x).
    Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=float)
    n = len(arr)
    s = 2
    t = max(int(abs(arr[0])), 2)
    bound = 0.5 * ((t - 1) ** (1.0 / s) * n ** (2.0 - 1.0 / s) + (s - 1) * n)
    return float(bound)


OPERATIONS["ex_complete_bipartite"] = {
    "fn": ex_complete_bipartite,
    "input_type": "array",
    "output_type": "scalar",
    "description": "KST upper bound on ex(n, K_{2,t})"
}


def ramsey_graph_lower(x):
    """Lower bound on Ramsey number R(s, s) via Erdos probabilistic argument.
    R(s, s) >= floor(s * 2^{(s-1)/2} / e) approximately, or more precisely
    R(s,s) > floor(2^{s/2}) for s >= 3.
    Uses s = max(int(x[0]), 3).
    Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=float)
    s = max(int(abs(arr[0])), 3)
    # Erdos 1947 probabilistic lower bound: R(s,s) > floor(2^{s/2})
    # More precise: R(s,s) >= floor(s / (e * sqrt(2)) * 2^{s/2})
    # We use the simpler standard bound
    bound = floor(2 ** (s / 2.0))
    return float(bound)


OPERATIONS["ramsey_graph_lower"] = {
    "fn": ramsey_graph_lower,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Erdos probabilistic lower bound R(s,s) > floor(2^{s/2})"
}


def graph_density(x):
    """Density of a graph: |E| / C(n, 2) for a path graph on n = len(x) vertices.
    Path graph has n-1 edges out of C(n,2) possible.
    Input: array. Output: scalar."""
    n = len(np.asarray(x))
    if n < 2:
        return 0.0
    edges = n - 1  # path graph
    max_edges = comb(n, 2)
    return float(edges / max_edges)


OPERATIONS["graph_density"] = {
    "fn": graph_density,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Edge density of path graph on n vertices: (n-1)/C(n,2)"
}


def max_triangle_free_edges(x):
    """Maximum number of edges in a triangle-free graph on n vertices.
    By Mantel's theorem (Turan for r=3): ex(n, K_3) = floor(n^2 / 4).
    Input: array. Output: scalar."""
    n = len(np.asarray(x))
    return float(n * n // 4)


OPERATIONS["max_triangle_free_edges"] = {
    "fn": max_triangle_free_edges,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Mantel's theorem: max triangle-free edges = floor(n^2/4)"
}


def kruskal_katona_bound(x):
    """Kruskal-Katona theorem gives the minimum number of (r-1)-element shadows
    given m r-element sets. For simplicity, compute the shadow of m edges (2-sets)
    among n vertices, i.e., how many vertices are covered.
    Uses m = int(x[0]) edges, n = len(x) vertices. Shadow = min(n, vertex coverage).
    Approximate: each edge covers 2 vertices, so shadow >= min(n, ceil(sqrt(2m))).
    Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=float)
    n = len(arr)
    m = max(int(abs(arr[0])), 1)
    # Kruskal-Katona: for m k-sets, the shadow (number of (k-1)-subsets) is minimized
    # when the k-sets form an initial segment of the colex order.
    # For k=2: m edges have at least ceil((1 + sqrt(1 + 8m))/2) vertices in their shadow.
    # This is the inverse of C(v,2) >= m, so v >= ceil((1+sqrt(1+8m))/2)
    v = ceil((1 + np.sqrt(1 + 8 * m)) / 2)
    v = min(v, n)
    # The number of 1-subsets (vertices) in the shadow of m 2-subsets
    return float(v)


OPERATIONS["kruskal_katona_bound"] = {
    "fn": kruskal_katona_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Kruskal-Katona: min vertices needed to contain m edges"
}


def graph_girth_bound(x):
    """Moore bound: a graph with n vertices and girth g has at most
    n^{1+1/floor((g-1)/2)} edges (approximately).
    For a given n=len(x) and target girth g=max(int(x[0]),3),
    returns upper bound on number of edges.
    The exact bound: ex(n; {C_3,...,C_{g-1}}) <= O(n^{1+2/(g-1)}) / 2.
    We use: m <= (n^{1+2/(g-1)})/2.
    Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=float)
    n = len(arr)
    g = max(int(abs(arr[0])), 3)  # girth >= 3
    # Bondy-Simonovits: ex(n; C_<=g-1) = O(n^{1+1/floor((g-1)/2)})
    k = (g - 1) // 2
    if k == 0:
        k = 1
    bound = 0.5 * n ** (1.0 + 1.0 / k)
    return float(bound)


OPERATIONS["graph_girth_bound"] = {
    "fn": graph_girth_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Moore/Bondy-Simonovits upper bound on edges for given girth"
}


def extremal_density(x):
    """Asymptotic extremal density: lim ex(n, K_r)/C(n,2) = 1 - 1/(r-1).
    Uses r = max(int(x[0]), 3).
    Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=float)
    r = max(int(abs(arr[0])), 3)
    density = 1.0 - 1.0 / (r - 1)
    return float(density)


OPERATIONS["extremal_density"] = {
    "fn": extremal_density,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Asymptotic Turan density 1 - 1/(r-1) for K_r-free graphs"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
