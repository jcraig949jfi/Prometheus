"""
Percolation Theory — site/bond percolation on grids, cluster size distribution, critical threshold

Connects to: [graph_theory, statistical_mechanics, probability_theory, random_matrix_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "percolation_theory"
OPERATIONS = {}


def _find_clusters(grid):
    """Union-Find based cluster detection on a 2D binary grid."""
    rows, cols = grid.shape
    labels = np.zeros_like(grid, dtype=int)
    parent = {}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv

    label_count = 0
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == 0:
                continue
            label_count += 1
            labels[i, j] = label_count
            parent[label_count] = label_count
            # Check up and left neighbors
            if i > 0 and labels[i - 1, j] > 0:
                union(label_count, labels[i - 1, j])
            if j > 0 and labels[i, j - 1] > 0:
                union(label_count, labels[i, j - 1])

    # Relabel with root parents
    cluster_map = {}
    for i in range(rows):
        for j in range(cols):
            if labels[i, j] > 0:
                root = find(labels[i, j])
                labels[i, j] = root

    # Get cluster sizes
    unique, counts = np.unique(labels[labels > 0], return_counts=True)
    return labels, dict(zip(unique.tolist(), counts.tolist()))


def site_percolation_grid(x):
    """Generate a site percolation grid. x[0] used as probability p.
    Input: array. Output: matrix (binary grid)."""
    p = float(np.clip(x[0] / np.max(np.abs(x)), 0, 1)) if np.max(np.abs(x)) > 0 else 0.5
    n = max(5, min(50, len(x) * 5))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    grid = (rng.random((n, n)) < p).astype(float)
    return grid


OPERATIONS["site_percolation_grid"] = {
    "fn": site_percolation_grid,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Generate site percolation grid with occupation probability from input"
}


def bond_percolation_grid(x):
    """Generate a bond percolation configuration as adjacency-like matrix.
    Input: array. Output: matrix."""
    p = float(np.clip(x[0] / np.max(np.abs(x)), 0, 1)) if np.max(np.abs(x)) > 0 else 0.5
    n = max(5, min(30, len(x) * 3))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    # Horizontal and vertical bonds encoded in a matrix
    # Result is (2n-1) x (2n-1): sites at even coords, bonds at odd coords
    size = 2 * n - 1
    grid = np.zeros((size, size))
    # Sites
    for i in range(0, size, 2):
        for j in range(0, size, 2):
            grid[i, j] = 1.0
    # Horizontal bonds
    for i in range(0, size, 2):
        for j in range(1, size, 2):
            grid[i, j] = 1.0 if rng.random() < p else 0.0
    # Vertical bonds
    for i in range(1, size, 2):
        for j in range(0, size, 2):
            grid[i, j] = 1.0 if rng.random() < p else 0.0
    return grid


OPERATIONS["bond_percolation_grid"] = {
    "fn": bond_percolation_grid,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Generate bond percolation configuration on a square lattice"
}


def cluster_sizes(x):
    """Compute cluster sizes from a percolation grid generated from input.
    Input: array. Output: array (sorted cluster sizes, descending)."""
    p = float(np.clip(np.mean(x) / (np.max(np.abs(x)) + 1e-15), 0.1, 0.9))
    n = max(10, min(50, len(x) * 5))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    grid = (rng.random((n, n)) < p).astype(int)
    _, size_dict = _find_clusters(grid)
    if len(size_dict) == 0:
        return np.array([0.0])
    sizes = np.array(sorted(size_dict.values(), reverse=True), dtype=float)
    return sizes


OPERATIONS["cluster_sizes"] = {
    "fn": cluster_sizes,
    "input_type": "array",
    "output_type": "array",
    "description": "Sorted cluster sizes (descending) from site percolation"
}


def largest_cluster_fraction(x):
    """Fraction of occupied sites in the largest cluster.
    Input: array. Output: scalar."""
    p = float(np.clip(np.mean(x) / (np.max(np.abs(x)) + 1e-15), 0.1, 0.9))
    n = max(10, min(50, len(x) * 5))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    grid = (rng.random((n, n)) < p).astype(int)
    total_occupied = np.sum(grid)
    if total_occupied == 0:
        return 0.0
    _, size_dict = _find_clusters(grid)
    if len(size_dict) == 0:
        return 0.0
    return float(max(size_dict.values()) / total_occupied)


OPERATIONS["largest_cluster_fraction"] = {
    "fn": largest_cluster_fraction,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fraction of occupied sites belonging to the largest cluster"
}


def percolation_threshold_estimate(x):
    """Estimate critical percolation threshold by scanning p values.
    Input: array (used as seed). Output: scalar (estimated p_c)."""
    n = 20  # Grid size for estimation
    n_trials = 5
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    p_values = np.linspace(0.3, 0.8, 15)
    spanning_prob = []
    for p in p_values:
        spans = 0
        for _ in range(n_trials):
            grid = (rng.random((n, n)) < p).astype(int)
            labels, _ = _find_clusters(grid)
            # Check if any cluster spans top to bottom
            top_labels = set(labels[0, :][labels[0, :] > 0].tolist())
            bot_labels = set(labels[-1, :][labels[-1, :] > 0].tolist())
            if top_labels & bot_labels:
                spans += 1
        spanning_prob.append(spans / n_trials)
    spanning_prob = np.array(spanning_prob)
    # Threshold at 50% spanning probability
    idx = np.argmin(np.abs(spanning_prob - 0.5))
    return float(p_values[idx])


OPERATIONS["percolation_threshold_estimate"] = {
    "fn": percolation_threshold_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate site percolation critical threshold on square lattice (~0.593)"
}


def cluster_size_distribution(x):
    """Distribution of cluster sizes (histogram counts).
    Input: array. Output: array (counts per size bin)."""
    p = float(np.clip(np.mean(x) / (np.max(np.abs(x)) + 1e-15), 0.1, 0.9))
    n = max(10, min(50, len(x) * 5))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    grid = (rng.random((n, n)) < p).astype(int)
    _, size_dict = _find_clusters(grid)
    if len(size_dict) == 0:
        return np.array([0.0])
    sizes = list(size_dict.values())
    max_size = max(sizes)
    bins = np.arange(1, max_size + 2)
    counts, _ = np.histogram(sizes, bins=bins)
    return counts.astype(float)


OPERATIONS["cluster_size_distribution"] = {
    "fn": cluster_size_distribution,
    "input_type": "array",
    "output_type": "array",
    "description": "Histogram of cluster sizes n_s (number of clusters of size s)"
}


def correlation_length_estimate(x):
    """Estimate correlation length from cluster size distribution.
    xi^2 = (sum s^2 * n_s) / (sum s * n_s) excluding largest cluster.
    Input: array. Output: scalar."""
    p = float(np.clip(np.mean(x) / (np.max(np.abs(x)) + 1e-15), 0.1, 0.9))
    n = max(10, min(50, len(x) * 5))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    grid = (rng.random((n, n)) < p).astype(int)
    _, size_dict = _find_clusters(grid)
    if len(size_dict) < 2:
        return 0.0
    sizes = sorted(size_dict.values())
    # Exclude the largest cluster
    sizes = np.array(sizes[:-1], dtype=float)
    numerator = np.sum(sizes ** 2 * 1.0)  # sum s^2 * n_s (each cluster counted once)
    denominator = np.sum(sizes * 1.0)
    if denominator < 1e-15:
        return 0.0
    return float(np.sqrt(numerator / denominator))


OPERATIONS["correlation_length_estimate"] = {
    "fn": correlation_length_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Correlation length from second moment of cluster size distribution"
}


def spanning_cluster_exists(x):
    """Check if a spanning cluster exists (top to bottom).
    Input: array. Output: scalar (1.0 if spanning, 0.0 otherwise)."""
    p = float(np.clip(np.mean(x) / (np.max(np.abs(x)) + 1e-15), 0.1, 0.9))
    n = max(10, min(50, len(x) * 5))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    grid = (rng.random((n, n)) < p).astype(int)
    labels, _ = _find_clusters(grid)
    top_labels = set(labels[0, :][labels[0, :] > 0].tolist())
    bot_labels = set(labels[-1, :][labels[-1, :] > 0].tolist())
    return 1.0 if top_labels & bot_labels else 0.0


OPERATIONS["spanning_cluster_exists"] = {
    "fn": spanning_cluster_exists,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Whether a cluster spans from top to bottom of the grid"
}


def percolation_probability(x):
    """Estimate P_inf(p): probability a site belongs to infinite cluster.
    Approximated as largest_cluster_size / total_sites.
    Input: array. Output: scalar."""
    p = float(np.clip(np.mean(x) / (np.max(np.abs(x)) + 1e-15), 0.1, 0.9))
    n = max(10, min(50, len(x) * 5))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    grid = (rng.random((n, n)) < p).astype(int)
    total_sites = n * n
    _, size_dict = _find_clusters(grid)
    if len(size_dict) == 0:
        return 0.0
    return float(max(size_dict.values()) / total_sites)


OPERATIONS["percolation_probability"] = {
    "fn": percolation_probability,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Order parameter P_inf: fraction of sites in largest cluster"
}


def mean_cluster_size(x):
    """Mean cluster size (excluding infinite cluster): chi = sum s^2*n_s / sum s*n_s.
    Input: array. Output: scalar."""
    p = float(np.clip(np.mean(x) / (np.max(np.abs(x)) + 1e-15), 0.1, 0.9))
    n = max(10, min(50, len(x) * 5))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    grid = (rng.random((n, n)) < p).astype(int)
    _, size_dict = _find_clusters(grid)
    if len(size_dict) < 2:
        return 1.0 if len(size_dict) == 1 else 0.0
    sizes = sorted(size_dict.values())
    # Exclude the largest
    sizes = np.array(sizes[:-1], dtype=float)
    numerator = np.sum(sizes ** 2)
    denominator = np.sum(sizes)
    if denominator < 1e-15:
        return 0.0
    return float(numerator / denominator)


OPERATIONS["mean_cluster_size"] = {
    "fn": mean_cluster_size,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Mean finite cluster size (susceptibility) excluding spanning cluster"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
