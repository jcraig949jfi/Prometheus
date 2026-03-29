"""
Homological Algebra — chain complexes, boundary operators, Betti numbers (simplicial)

Connects to: [algebraic_topology, linear_algebra, category_theory, differential_geometry]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "homological_algebra"
OPERATIONS = {}


def boundary_operator_1(x):
    """Boundary operator d1 for a simplicial complex built from a path graph.
    Given n = len(x) vertices 0..n-1 with edges (i, i+1), d1 maps edges to vertices.
    d1 has shape (n, n-1): column j (edge j->j+1) has -1 at row j, +1 at row j+1.
    Input: array. Output: matrix."""
    n = len(np.asarray(x))
    if n < 2:
        return np.zeros((n, 0), dtype=int)
    num_edges = n - 1
    d1 = np.zeros((n, num_edges), dtype=int)
    for j in range(num_edges):
        d1[j, j] = -1      # source vertex
        d1[j + 1, j] = 1   # target vertex
    return d1


OPERATIONS["boundary_operator_1"] = {
    "fn": boundary_operator_1,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Boundary operator d1 for path graph on n vertices: edges -> vertices"
}


def boundary_operator_2(x):
    """Boundary operator d2 for a simplicial complex.
    Given n = len(x) vertices, if n >= 3 we form a single 2-simplex (0,1,2)
    with edges (0,1), (0,2), (1,2). d2 maps 2-simplices to edges.
    d2[(0,1)] = +1, d2[(0,2)] = -1, d2[(1,2)] = +1 for the triangle (0,1,2).
    Input: array. Output: matrix."""
    n = len(np.asarray(x))
    if n < 3:
        num_edges = max(n - 1, 0)
        return np.zeros((num_edges, 0), dtype=int)
    # Edges of the full simplex on vertices 0,1,2: (0,1), (0,2), (1,2)
    edges = [(0, 1), (0, 2), (1, 2)]
    # One 2-simplex: (0, 1, 2)
    # Boundary: d(0,1,2) = (1,2) - (0,2) + (0,1)
    d2 = np.zeros((len(edges), 1), dtype=int)
    d2[0, 0] = 1    # (0,1)
    d2[1, 0] = -1   # (0,2)
    d2[2, 0] = 1    # (1,2)
    return d2


OPERATIONS["boundary_operator_2"] = {
    "fn": boundary_operator_2,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Boundary operator d2 for triangle (0,1,2): 2-simplices -> edges"
}


def betti_numbers_simplicial(x):
    """Compute Betti numbers for a simplicial complex built from a path graph on n vertices.
    Path graph: n vertices, n-1 edges, 0 triangles.
    b0 = 1 (one connected component), b1 = 0 (no cycles).
    For general input: b0 = n - rank(d1), b1 = nullity(d1) - rank(d2).
    Input: array. Output: array [b0, b1]."""
    n = len(np.asarray(x))
    if n == 0:
        return np.array([0, 0], dtype=int)
    if n == 1:
        return np.array([1, 0], dtype=int)

    # Build d1 for path graph
    d1 = boundary_operator_1(x)
    rank_d1 = int(np.linalg.matrix_rank(d1.astype(float)))
    nullity_d1 = d1.shape[1] - rank_d1

    # Path graph has no 2-simplices
    rank_d2 = 0

    b0 = n - rank_d1
    b1 = nullity_d1 - rank_d2
    return np.array([b0, b1], dtype=int)


OPERATIONS["betti_numbers_simplicial"] = {
    "fn": betti_numbers_simplicial,
    "input_type": "array",
    "output_type": "array",
    "description": "Betti numbers [b0, b1] for path graph on n vertices"
}


def euler_characteristic_from_betti(x):
    """Euler characteristic from Betti numbers: chi = sum(-1)^k * b_k.
    For a path graph: chi = b0 - b1 = 1 - 0 = 1.
    Also equals V - E + F = n - (n-1) + 0 = 1.
    Input: array. Output: scalar."""
    betti = betti_numbers_simplicial(x)
    chi = 0
    for k, b in enumerate(betti):
        chi += ((-1) ** k) * int(b)
    return int(chi)


OPERATIONS["euler_characteristic_from_betti"] = {
    "fn": euler_characteristic_from_betti,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Euler characteristic chi = sum(-1)^k * b_k from Betti numbers"
}


def chain_complex_homology_rank(x):
    """Rank of homology groups H_k = ker(d_k) / im(d_{k+1}) for a path graph.
    Returns array of ranks [rank H_0, rank H_1].
    Input: array. Output: array."""
    return betti_numbers_simplicial(x)


OPERATIONS["chain_complex_homology_rank"] = {
    "fn": chain_complex_homology_rank,
    "input_type": "array",
    "output_type": "array",
    "description": "Ranks of homology groups H_0 and H_1 for path graph"
}


def simplicial_complex_from_points(x):
    """Build a Vietoris-Rips-like adjacency matrix from 1D point cloud.
    Points are x values; threshold epsilon = median of pairwise distances.
    Entry (i,j) = 1 if |x_i - x_j| < epsilon.
    Input: array. Output: matrix (adjacency)."""
    pts = np.asarray(x, dtype=float)
    n = len(pts)
    if n < 2:
        return np.eye(max(n, 1), dtype=int)
    dists = np.abs(pts[:, None] - pts[None, :])
    # Use median of nonzero distances as threshold
    mask = np.ones((n, n), dtype=bool)
    np.fill_diagonal(mask, False)
    epsilon = np.median(dists[mask])
    adj = (dists < epsilon).astype(int)
    np.fill_diagonal(adj, 0)
    return adj


OPERATIONS["simplicial_complex_from_points"] = {
    "fn": simplicial_complex_from_points,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Adjacency matrix from 1D point cloud using median distance threshold"
}


def persistent_betti_0(x):
    """Persistent Betti-0 numbers at multiple thresholds for a 1D point cloud.
    b0(epsilon) = number of connected components at threshold epsilon.
    Uses union-find on sorted pairwise distances.
    Input: array. Output: array (b0 at n-1 threshold values)."""
    pts = np.sort(np.asarray(x, dtype=float))
    n = len(pts)
    if n <= 1:
        return np.array([n], dtype=int)

    # Pairwise distances between consecutive sorted points
    gaps = np.diff(pts)
    # At threshold eps, components merge when gap < eps
    # Sort all pairwise distances
    all_dists = []
    for i in range(n):
        for j in range(i + 1, n):
            all_dists.append(abs(pts[i] - pts[j]))
    all_dists = np.sort(all_dists)

    # Pick n-1 evenly spaced thresholds
    num_thresholds = n - 1
    thresholds = np.linspace(0, all_dists[-1] * 1.1, num_thresholds + 1)[1:]

    betti0_vals = []
    for eps in thresholds:
        # Count connected components via union-find
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for i in range(n):
            for j in range(i + 1, n):
                if abs(pts[i] - pts[j]) < eps:
                    ri, rj = find(i), find(j)
                    if ri != rj:
                        parent[ri] = rj

        components = len(set(find(i) for i in range(n)))
        betti0_vals.append(components)

    return np.array(betti0_vals, dtype=int)


OPERATIONS["persistent_betti_0"] = {
    "fn": persistent_betti_0,
    "input_type": "array",
    "output_type": "array",
    "description": "Persistent Betti-0 at multiple thresholds for 1D point cloud"
}


def smith_normal_form_mod2(x):
    """Smith normal form of a matrix over Z/2Z (GF(2)).
    Input: array (flattened matrix, reshaped to nearest square or rectangular).
    Output: array (diagonal entries of Smith normal form)."""
    arr = np.asarray(x, dtype=int) % 2
    n = len(arr)
    # Try to make it a reasonable matrix
    side = int(np.sqrt(n))
    if side * side == n:
        mat = arr.reshape(side, side)
    else:
        # Make it a column vector
        mat = arr.reshape(-1, 1)

    rows, cols = mat.shape
    mat = mat.copy() % 2

    # Gaussian elimination over GF(2) to get Smith normal form
    pivot_row = 0
    pivot_col = 0
    while pivot_row < rows and pivot_col < cols:
        # Find pivot
        found = False
        for r in range(pivot_row, rows):
            if mat[r, pivot_col] == 1:
                found = True
                # Swap rows
                mat[[pivot_row, r]] = mat[[r, pivot_row]]
                break
        if not found:
            pivot_col += 1
            continue
        # Eliminate below and above
        for r in range(rows):
            if r != pivot_row and mat[r, pivot_col] == 1:
                mat[r] = (mat[r] + mat[pivot_row]) % 2
        pivot_row += 1
        pivot_col += 1

    # Diagonal entries (invariant factors)
    diag = np.array([mat[i, i] if i < rows and i < cols else 0
                     for i in range(min(rows, cols))], dtype=int)
    return diag


OPERATIONS["smith_normal_form_mod2"] = {
    "fn": smith_normal_form_mod2,
    "input_type": "array",
    "output_type": "array",
    "description": "Smith normal form diagonal over GF(2) of reshaped input matrix"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
