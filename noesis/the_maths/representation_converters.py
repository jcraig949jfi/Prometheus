"""
Representation Converters — Explicit bridges between data types

Connects to: [spectral_transforms, invariant_extractors, constraint_feasibility, category_composition]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "representation_converters"
OPERATIONS = {}


def array_to_graph_knn(x, k=3):
    """Build kNN adjacency matrix from array values. Input: array. Output: matrix."""
    n = len(x)
    k = min(k, n - 1)
    dists = np.abs(x[:, None] - x[None, :])
    adj = np.zeros((n, n))
    for i in range(n):
        neighbors = np.argsort(dists[i])[1:k + 1]
        adj[i, neighbors] = 1
        adj[neighbors, i] = 1
    return adj


OPERATIONS["array_to_graph_knn"] = {
    "fn": array_to_graph_knn,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Convert array to kNN adjacency matrix based on value distance"
}


def array_to_graph_threshold(x, quantile=0.3):
    """Build adjacency matrix by thresholding pairwise distances. Input: array. Output: matrix."""
    dists = np.abs(x[:, None] - x[None, :])
    threshold = np.quantile(dists[dists > 0], quantile) if np.any(dists > 0) else 0
    adj = (dists <= threshold).astype(float)
    np.fill_diagonal(adj, 0)
    return adj


OPERATIONS["array_to_graph_threshold"] = {
    "fn": array_to_graph_threshold,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Convert array to adjacency matrix via distance thresholding"
}


def graph_to_laplacian(x):
    """Compute graph Laplacian from adjacency matrix. Input: matrix. Output: matrix."""
    if x.ndim == 1:
        n = int(np.sqrt(len(x)))
        if n * n == len(x):
            x = x.reshape(n, n)
        else:
            # Build adjacency from kNN on values, then compute Laplacian
            n = len(x)
            dists = np.abs(x[:, None] - x[None, :])
            k = min(3, n - 1)
            x = np.zeros((n, n))
            for i in range(n):
                neighbors = np.argsort(dists[i])[1:k + 1]
                x[i, neighbors] = 1
                x[neighbors, i] = 1
    adj = (x + x.T) / 2.0
    np.fill_diagonal(adj, 0)
    degree = np.diag(adj.sum(axis=1))
    return degree - adj


OPERATIONS["graph_to_laplacian"] = {
    "fn": graph_to_laplacian,
    "input_type": "matrix",
    "output_type": "matrix",
    "description": "Compute graph Laplacian D - A from adjacency matrix"
}


def array_to_distribution_histogram(x, bins=20):
    """Convert array to probability distribution via histogram. Input: array. Output: array."""
    counts, _ = np.histogram(x, bins=bins)
    total = counts.sum()
    if total == 0:
        return np.ones(bins) / bins
    return counts.astype(float) / total


OPERATIONS["array_to_distribution_histogram"] = {
    "fn": array_to_distribution_histogram,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert array to probability distribution via histogram binning"
}


def array_to_distribution_kde(x, n_points=50):
    """Kernel density estimate of array values. Input: array. Output: array."""
    if np.std(x) == 0:
        result = np.zeros(n_points)
        result[n_points // 2] = 1.0
        return result
    bandwidth = 1.06 * np.std(x) * len(x) ** (-0.2)  # Silverman's rule
    grid = np.linspace(x.min() - 3 * bandwidth, x.max() + 3 * bandwidth, n_points)
    density = np.zeros(n_points)
    for xi in x:
        density += np.exp(-0.5 * ((grid - xi) / bandwidth) ** 2)
    density /= (len(x) * bandwidth * np.sqrt(2 * np.pi))
    # Normalize to sum to 1
    if density.sum() > 0:
        density /= density.sum()
    return density


OPERATIONS["array_to_distribution_kde"] = {
    "fn": array_to_distribution_kde,
    "input_type": "array",
    "output_type": "array",
    "description": "Kernel density estimation of array values"
}


def signal_to_frequency_fft(x):
    """Convert time-domain signal to frequency magnitudes. Input: array. Output: array."""
    return np.abs(np.fft.rfft(x))


OPERATIONS["signal_to_frequency_fft"] = {
    "fn": signal_to_frequency_fft,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert signal to frequency domain magnitudes via FFT"
}


def matrix_to_polynomial_characteristic(x):
    """Characteristic polynomial coefficients of matrix. Input: array. Output: array."""
    n = int(np.sqrt(len(x)))
    if n * n != len(x):
        n = len(x)
        mat = np.diag(x)
    else:
        mat = x.reshape(n, n)
    eigenvalues = np.linalg.eigvals(mat)
    # Coefficients of product (lambda - lambda_i)
    coeffs = np.array([1.0])
    for ev in eigenvalues:
        coeffs = np.convolve(coeffs, [1.0, -ev])
    return np.real(coeffs)


OPERATIONS["matrix_to_polynomial_characteristic"] = {
    "fn": matrix_to_polynomial_characteristic,
    "input_type": "array",
    "output_type": "array",
    "description": "Characteristic polynomial coefficients of square matrix"
}


def polynomial_to_roots(x):
    """Find roots of polynomial given coefficients. Input: array. Output: array."""
    roots = np.roots(x)
    return np.sort_complex(roots)


OPERATIONS["polynomial_to_roots"] = {
    "fn": polynomial_to_roots,
    "input_type": "array",
    "output_type": "array",
    "description": "Roots of polynomial from coefficient array"
}


def array_to_correlation_matrix(x):
    """Build correlation matrix from sliding windows. Input: array. Output: matrix."""
    n = len(x)
    w = max(2, n // 2)
    windows = np.array([x[i:i + w] for i in range(n - w + 1)])
    if windows.shape[0] < 2:
        return np.eye(w)
    corr = np.corrcoef(windows.T)
    corr = np.nan_to_num(corr, nan=0.0)
    return corr


OPERATIONS["array_to_correlation_matrix"] = {
    "fn": array_to_correlation_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Correlation matrix from sliding window embedding of array"
}


def distribution_to_cdf(x):
    """Convert probability distribution (PMF) to cumulative distribution. Input: array. Output: array."""
    p = np.abs(x)
    total = p.sum()
    if total > 0:
        p = p / total
    return np.cumsum(p)


OPERATIONS["distribution_to_cdf"] = {
    "fn": distribution_to_cdf,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert probability mass function to cumulative distribution"
}


def graph_to_degree_sequence(x):
    """Extract sorted degree sequence from adjacency matrix. Input: array. Output: array."""
    n = int(np.sqrt(len(x)))
    if n * n == len(x):
        adj = x.reshape(n, n)
    else:
        adj = np.outer(x > np.median(x), x > np.median(x)).astype(float)
        np.fill_diagonal(adj, 0)
    degrees = adj.sum(axis=1)
    return np.sort(degrees)[::-1]


OPERATIONS["graph_to_degree_sequence"] = {
    "fn": graph_to_degree_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "Sorted degree sequence from adjacency matrix"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
