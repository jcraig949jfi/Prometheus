"""
Sandpile Groups — abelian sandpile model operations and chip-firing dynamics

Connects to: [combinatorics, graph theory, algebraic geometry, lattice models, cellular automata]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "sandpile_groups"
OPERATIONS = {}


def _to_grid(x):
    """Convert flat array to square-ish grid of chip counts."""
    n = int(np.ceil(np.sqrt(len(x))))
    padded = np.zeros(n * n)
    padded[:len(x)] = np.abs(x).astype(int)
    return padded.reshape(n, n).astype(int)


def _stabilize_grid(grid):
    """Stabilize a sandpile grid (threshold = 4 for interior cells)."""
    g = grid.copy()
    rows, cols = g.shape
    max_iter = 10000
    for _ in range(max_iter):
        unstable = g >= 4
        if not np.any(unstable):
            break
        for i in range(rows):
            for j in range(cols):
                if g[i, j] >= 4:
                    topples = g[i, j] // 4
                    g[i, j] -= 4 * topples
                    if i > 0:
                        g[i - 1, j] += topples
                    if i < rows - 1:
                        g[i + 1, j] += topples
                    if j > 0:
                        g[i, j - 1] += topples
                    if j < cols - 1:
                        g[i, j + 1] += topples
    return g


def sandpile_add(x):
    """Add two sandpile configurations and stabilize. Input: array (split in half).
    Output: array (stabilized sum)."""
    n = len(x) // 2
    if n == 0:
        return x.copy()
    a = np.abs(x[:n]).astype(int)
    b = np.abs(x[n:2 * n]).astype(int)
    side = int(np.ceil(np.sqrt(n)))
    a_pad = np.zeros(side * side, dtype=int)
    b_pad = np.zeros(side * side, dtype=int)
    a_pad[:n] = a
    b_pad[:n] = b
    combined = (a_pad + b_pad).reshape(side, side)
    result = _stabilize_grid(combined)
    return result.flatten()[:n].astype(float)


OPERATIONS["sandpile_add"] = {
    "fn": sandpile_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Adds two sandpile configurations and stabilizes the result"
}


def sandpile_stabilize(x):
    """Stabilize a sandpile configuration. Input: array. Output: array."""
    grid = _to_grid(x)
    result = _stabilize_grid(grid)
    return result.flatten()[:len(x)].astype(float)


OPERATIONS["sandpile_stabilize"] = {
    "fn": sandpile_stabilize,
    "input_type": "array",
    "output_type": "array",
    "description": "Stabilizes a sandpile configuration by toppling all unstable cells"
}


def sandpile_identity(x):
    """Compute the identity element of the sandpile group for a grid derived from x.
    Input: array. Output: array."""
    n = int(np.ceil(np.sqrt(len(x))))
    # Identity = stabilize(2 * max_stable - stabilize(2 * max_stable))
    # max_stable has all cells = 3
    max_stable = np.full((n, n), 3, dtype=int)
    double_max = 2 * max_stable
    first_stab = _stabilize_grid(double_max)
    # e = stabilize(2*m - stabilize(2*m)) where m is max stable
    candidate = 2 * max_stable - first_stab
    identity = _stabilize_grid(candidate)
    return identity.flatten()[:len(x)].astype(float)


OPERATIONS["sandpile_identity"] = {
    "fn": sandpile_identity,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes the identity element of the sandpile group"
}


def sandpile_topple(x):
    """Perform a single toppling pass on all unstable cells. Input: array. Output: array."""
    grid = _to_grid(x)
    rows, cols = grid.shape
    new_grid = grid.copy()
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] >= 4:
                topples = grid[i, j] // 4
                new_grid[i, j] -= 4 * topples
                if i > 0:
                    new_grid[i - 1, j] += topples
                if i < rows - 1:
                    new_grid[i + 1, j] += topples
                if j > 0:
                    new_grid[i, j - 1] += topples
                if j < cols - 1:
                    new_grid[i, j + 1] += topples
    return new_grid.flatten()[:len(x)].astype(float)


OPERATIONS["sandpile_topple"] = {
    "fn": sandpile_topple,
    "input_type": "array",
    "output_type": "array",
    "description": "Performs one parallel toppling pass on all unstable cells"
}


def sandpile_group_order(x):
    """Estimate the sandpile group order for an n x n grid using the number of
    spanning trees (det of reduced Laplacian). Input: array. Output: scalar."""
    n = int(np.ceil(np.sqrt(len(x))))
    n = max(n, 2)
    # Build graph Laplacian for n x n grid
    size = n * n
    L = np.zeros((size, size))
    for i in range(n):
        for j in range(n):
            idx = i * n + j
            deg = 0
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < n:
                    nidx = ni * n + nj
                    L[idx, nidx] = -1
                    deg += 1
            L[idx, idx] = deg
    # Number of spanning trees = det of any (n-1) x (n-1) minor of L (Kirchhoff's theorem)
    reduced = L[1:, 1:]
    det_val = np.linalg.det(reduced)
    return float(np.round(np.abs(det_val)))


OPERATIONS["sandpile_group_order"] = {
    "fn": sandpile_group_order,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes sandpile group order via Kirchhoff's matrix tree theorem"
}


def sandpile_firing_script(x):
    """Compute the firing script (number of times each cell topples during stabilization).
    Input: array. Output: array."""
    grid = _to_grid(x)
    rows, cols = grid.shape
    firings = np.zeros_like(grid)
    g = grid.copy()
    max_iter = 10000
    for _ in range(max_iter):
        unstable = g >= 4
        if not np.any(unstable):
            break
        for i in range(rows):
            for j in range(cols):
                if g[i, j] >= 4:
                    topples = g[i, j] // 4
                    firings[i, j] += topples
                    g[i, j] -= 4 * topples
                    if i > 0:
                        g[i - 1, j] += topples
                    if i < rows - 1:
                        g[i + 1, j] += topples
                    if j > 0:
                        g[i, j - 1] += topples
                    if j < cols - 1:
                        g[i, j + 1] += topples
    return firings.flatten()[:len(x)].astype(float)


OPERATIONS["sandpile_firing_script"] = {
    "fn": sandpile_firing_script,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes the firing script (topple counts) during stabilization"
}


def sandpile_recurrent_check(x):
    """Check if a configuration is recurrent (stable and equivalent to identity + something).
    A stable config c is recurrent iff c = stabilize(c + identity). Input: array. Output: scalar (1=recurrent, 0=not)."""
    grid = _to_grid(x)
    n = grid.shape[0]
    # Must be stable first
    if np.any(grid >= 4):
        return 0.0
    # Compute identity
    max_stable = np.full((n, n), 3, dtype=int)
    double_max = 2 * max_stable
    first_stab = _stabilize_grid(double_max)
    identity = _stabilize_grid(2 * max_stable - first_stab)
    # Check: stabilize(c + identity) == c
    summed = grid + identity
    stabilized = _stabilize_grid(summed)
    if np.array_equal(stabilized, grid):
        return 1.0
    return 0.0


OPERATIONS["sandpile_recurrent_check"] = {
    "fn": sandpile_recurrent_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Checks if a sandpile configuration is recurrent"
}


def chip_firing_step(x):
    """Perform one chip-firing step: fire the first unstable vertex.
    Input: array (chip counts on a path graph). Output: array."""
    chips = np.abs(x).astype(int).copy()
    n = len(chips)
    # Degree of vertex i in path graph
    for i in range(n):
        deg = (1 if i > 0 else 0) + (1 if i < n - 1 else 0)
        if chips[i] >= deg and deg > 0:
            chips[i] -= deg
            if i > 0:
                chips[i - 1] += 1
            if i < n - 1:
                chips[i + 1] += 1
            break  # Fire only one vertex per step
    return chips.astype(float)


OPERATIONS["chip_firing_step"] = {
    "fn": chip_firing_step,
    "input_type": "array",
    "output_type": "array",
    "description": "Fires the first unstable vertex in a chip-firing game on a path graph"
}


def sandpile_laplacian(x):
    """Compute the graph Laplacian for a grid whose size is derived from x.
    Input: array. Output: matrix (flattened)."""
    n = int(np.ceil(np.sqrt(len(x))))
    n = max(n, 2)
    size = n * n
    L = np.zeros((size, size))
    for i in range(n):
        for j in range(n):
            idx = i * n + j
            deg = 0
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni_, nj_ = i + di, j + dj
                if 0 <= ni_ < n and 0 <= nj_ < n:
                    nidx = ni_ * n + nj_
                    L[idx, nidx] = -1.0
                    deg += 1
            L[idx, idx] = float(deg)
    return L


OPERATIONS["sandpile_laplacian"] = {
    "fn": sandpile_laplacian,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Computes the graph Laplacian matrix for a grid sandpile"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
