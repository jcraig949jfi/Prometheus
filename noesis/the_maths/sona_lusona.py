"""
Sona/Lusona — Chokwe sand drawings: continuous closed curves visiting all grid regions

Connects to: [islamic_geometric_patterns, warlpiri_kinship, bambara_divination]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

Sona drawings are continuous closed curves on rectangular grids that
visit every region. They relate to Eulerian paths on dual graphs.
We model grids derived from input array dimensions.
"""

import numpy as np

FIELD_NAME = "sona_lusona"
OPERATIONS = {}


def _grid_size(x):
    """Derive grid dimensions from array: rows = ceil(sqrt(len)), cols = ceil(len/rows)."""
    n = max(len(x), 2)
    rows = max(int(np.ceil(np.sqrt(n))), 2)
    cols = max(int(np.ceil(n / rows)), 2)
    return rows, cols


def _build_dual_adjacency(rows, cols):
    """Build adjacency matrix for the dual graph of a rows x cols grid.
    The dual graph has (rows+1)*(cols+1) - 4 outer face merged into 1 node.
    Simplified: treat each cell as a node, adjacent cells share an edge."""
    n = rows * cols
    adj = np.zeros((n, n), dtype=float)
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            if c + 1 < cols:
                adj[idx, idx + 1] = 1.0
                adj[idx + 1, idx] = 1.0
            if r + 1 < rows:
                adj[idx, idx + cols] = 1.0
                adj[idx + cols, idx] = 1.0
    return adj


def sona_grid_dual_graph(x):
    """Construct dual graph adjacency matrix for grid derived from x.
    Input: array. Output: matrix (flattened)."""
    rows, cols = _grid_size(x)
    adj = _build_dual_adjacency(rows, cols)
    return adj.flatten()


OPERATIONS["sona_grid_dual_graph"] = {
    "fn": sona_grid_dual_graph,
    "input_type": "array",
    "output_type": "array",
    "description": "Dual graph adjacency matrix for the sona grid"
}


def eulerian_path_on_dual(x):
    """Check Eulerian path conditions on dual graph: count vertices with odd degree.
    Euler path exists iff 0 or 2 vertices have odd degree.
    Returns [num_odd_vertices, has_euler_path, has_euler_circuit].
    Input: array. Output: array."""
    rows, cols = _grid_size(x)
    adj = _build_dual_adjacency(rows, cols)
    degrees = np.sum(adj, axis=1)
    odd_count = int(np.sum(degrees % 2 != 0))
    has_path = 1.0 if odd_count in (0, 2) else 0.0
    has_circuit = 1.0 if odd_count == 0 else 0.0
    return np.array([float(odd_count), has_path, has_circuit])


OPERATIONS["eulerian_path_on_dual"] = {
    "fn": eulerian_path_on_dual,
    "input_type": "array",
    "output_type": "array",
    "description": "Eulerian path/circuit conditions on dual graph"
}


def monolinearity_test(x):
    """Test if the sona pattern can be drawn in one stroke (monolinear).
    A grid sona is monolinear iff the dual graph has an Euler circuit (all even degree).
    Returns 1.0 if monolinear, 0.0 otherwise. Input: array. Output: scalar."""
    result = eulerian_path_on_dual(x)
    return float(result[2])


OPERATIONS["monolinearity_test"] = {
    "fn": monolinearity_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tests if the pattern is drawable in one continuous stroke"
}


def sona_pattern_generate(x):
    """Generate a sona crossing pattern on the grid. At each cell, compute
    a crossing direction based on position parity. Returns crossing angles
    (0, 45, 90, 135 degrees). Input: array. Output: array."""
    rows, cols = _grid_size(x)
    pattern = np.zeros(rows * cols)
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            # Classic sona: crossing direction alternates based on parity
            if (r + c) % 2 == 0:
                pattern[idx] = 45.0   # diagonal NE-SW
            else:
                pattern[idx] = 135.0  # diagonal NW-SE
    return pattern


OPERATIONS["sona_pattern_generate"] = {
    "fn": sona_pattern_generate,
    "input_type": "array",
    "output_type": "array",
    "description": "Generates crossing angle pattern for sona grid"
}


def sona_symmetry_classify(x):
    """Classify symmetry of the sona pattern:
    0=none, 1=horizontal, 2=vertical, 3=both, 4=rotational.
    Uses the grid values. Input: array. Output: scalar."""
    rows, cols = _grid_size(x)
    n = rows * cols
    grid = np.zeros(n)
    grid[:min(len(x), n)] = x[:min(len(x), n)]
    grid = grid.reshape(rows, cols)

    h_sym = np.allclose(grid, grid[::-1, :], atol=0.1)
    v_sym = np.allclose(grid, grid[:, ::-1], atol=0.1)
    r_sym = np.allclose(grid, grid[::-1, ::-1], atol=0.1)

    if h_sym and v_sym:
        return 3.0
    elif r_sym:
        return 4.0
    elif h_sym:
        return 1.0
    elif v_sym:
        return 2.0
    return 0.0


OPERATIONS["sona_symmetry_classify"] = {
    "fn": sona_symmetry_classify,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Classifies symmetry type of the sona pattern"
}


def region_visit_check(x):
    """Check what fraction of grid regions are 'visited' (nonzero).
    A proper sona visits all regions. Input: array. Output: scalar."""
    rows, cols = _grid_size(x)
    n = rows * cols
    grid = np.zeros(n)
    grid[:min(len(x), n)] = x[:min(len(x), n)]
    visited = np.sum(np.abs(grid) > 1e-12)
    return float(visited / n)


OPERATIONS["region_visit_check"] = {
    "fn": region_visit_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fraction of grid regions visited (nonzero)"
}


def sona_crossing_number(x):
    """Compute crossing number: for the grid-based sona, the number of
    self-crossings equals (rows-1)*(cols-1) for a standard pattern.
    Input: array. Output: scalar."""
    rows, cols = _grid_size(x)
    return float((rows - 1) * (cols - 1))


OPERATIONS["sona_crossing_number"] = {
    "fn": sona_crossing_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of self-crossings in the sona pattern"
}


def sona_genus_estimate(x):
    """Estimate the genus of the surface needed to embed the sona pattern
    without crossings. genus = ceil(crossings / 6) by Euler's formula estimate.
    Input: array. Output: scalar."""
    crossings = sona_crossing_number(x)
    return float(np.ceil(crossings / 6.0))


OPERATIONS["sona_genus_estimate"] = {
    "fn": sona_genus_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimated genus of surface for crossing-free embedding"
}


def dual_lattice_construct(x):
    """Construct dual lattice: for each grid point, compute the centroid
    of surrounding cells. Returns dual lattice coordinates as flat array.
    Input: array. Output: array."""
    rows, cols = _grid_size(x)
    # Dual lattice has (rows-1)*(cols-1) points
    dr = max(rows - 1, 1)
    dc = max(cols - 1, 1)
    dual = np.zeros(dr * dc * 2)  # x,y pairs
    for r in range(dr):
        for c in range(dc):
            idx = (r * dc + c) * 2
            dual[idx] = r + 0.5      # x coordinate
            dual[idx + 1] = c + 0.5  # y coordinate
    return dual


OPERATIONS["dual_lattice_construct"] = {
    "fn": dual_lattice_construct,
    "input_type": "array",
    "output_type": "array",
    "description": "Dual lattice centroid coordinates"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
