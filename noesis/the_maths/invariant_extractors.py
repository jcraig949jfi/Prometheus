"""
Invariant Extractors — Universal meeting points between fields: collapse complexity into stable descriptors

Connects to: [spectral_transforms, representation_converters, compression_metrics, category_composition]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "invariant_extractors"
OPERATIONS = {}


def topological_betti_0(x):
    """Estimate Betti-0 (connected components) via threshold on distance graph. Input: array. Output: scalar."""
    n = len(x)
    if n <= 1:
        return float(n)
    dists = np.abs(x[:, None] - x[None, :])
    threshold = np.median(dists[dists > 0])
    # Union-find for connected components
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        for j in range(i + 1, n):
            if dists[i, j] <= threshold:
                union(i, j)

    components = len(set(find(i) for i in range(n)))
    return float(components)


OPERATIONS["topological_betti_0"] = {
    "fn": topological_betti_0,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Betti-0 number (connected components) of threshold graph"
}


def topological_euler_characteristic(x):
    """Euler characteristic V - E of threshold graph. Input: array. Output: scalar."""
    n = len(x)
    dists = np.abs(x[:, None] - x[None, :])
    threshold = np.median(dists[dists > 0]) if np.any(dists > 0) else 0
    adj = (dists <= threshold).astype(int)
    np.fill_diagonal(adj, 0)
    edges = adj.sum() // 2
    return float(n - edges)


OPERATIONS["topological_euler_characteristic"] = {
    "fn": topological_euler_characteristic,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Euler characteristic (V - E) of threshold graph"
}


def algebraic_rank(x):
    """Matrix rank of reshaped array. Input: array. Output: scalar."""
    n = len(x)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))
    padded = np.zeros(rows * cols)
    padded[:n] = x
    mat = padded.reshape(rows, cols)
    return float(np.linalg.matrix_rank(mat))


OPERATIONS["algebraic_rank"] = {
    "fn": algebraic_rank,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Matrix rank of array reshaped to near-square matrix"
}


def algebraic_determinant(x):
    """Determinant of square matrix from array. Input: array. Output: scalar."""
    n = int(np.sqrt(len(x)))
    if n * n == len(x):
        mat = x.reshape(n, n)
    else:
        mat = np.outer(x, x) + np.eye(len(x))
    return float(np.linalg.det(mat))


OPERATIONS["algebraic_determinant"] = {
    "fn": algebraic_determinant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Determinant of matrix formed from array"
}


def algebraic_trace(x):
    """Trace of square matrix from array. Input: array. Output: scalar."""
    n = int(np.sqrt(len(x)))
    if n * n == len(x):
        mat = x.reshape(n, n)
        return float(np.trace(mat))
    return float(np.sum(x))


OPERATIONS["algebraic_trace"] = {
    "fn": algebraic_trace,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Trace of matrix formed from array (or sum if not square)"
}


def algebraic_characteristic_polynomial(x):
    """Coefficients of characteristic polynomial. Input: array. Output: array."""
    n = int(np.sqrt(len(x)))
    if n * n == len(x):
        mat = x.reshape(n, n)
    else:
        mat = np.diag(x)
    eigs = np.linalg.eigvals(mat)
    coeffs = np.array([1.0])
    for ev in eigs:
        coeffs = np.convolve(coeffs, [1.0, -ev])
    return np.real(coeffs)


OPERATIONS["algebraic_characteristic_polynomial"] = {
    "fn": algebraic_characteristic_polynomial,
    "input_type": "array",
    "output_type": "array",
    "description": "Characteristic polynomial coefficients"
}


def statistical_entropy(x):
    """Shannon entropy of normalized absolute values. Input: array. Output: scalar."""
    p = np.abs(x)
    total = p.sum()
    if total == 0:
        return 0.0
    p = p / total
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


OPERATIONS["statistical_entropy"] = {
    "fn": statistical_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of normalized array"
}


def statistical_moments(x):
    """First four statistical moments: mean, variance, skewness, kurtosis. Input: array. Output: array."""
    mean = np.mean(x)
    var = np.var(x)
    std = np.std(x)
    if std == 0:
        return np.array([mean, var, 0.0, 0.0])
    skew = float(np.mean(((x - mean) / std) ** 3))
    kurt = float(np.mean(((x - mean) / std) ** 4) - 3.0)  # excess kurtosis
    return np.array([mean, var, skew, kurt])


OPERATIONS["statistical_moments"] = {
    "fn": statistical_moments,
    "input_type": "array",
    "output_type": "array",
    "description": "First four statistical moments (mean, var, skew, kurtosis)"
}


def statistical_mutual_information(x):
    """Mutual information between first and second halves. Input: array. Output: scalar."""
    n = len(x)
    h1 = n // 2
    a, b = x[:h1], x[h1:2 * h1]
    if len(a) < 2:
        return 0.0
    bins = max(3, int(np.sqrt(len(a))))
    hist_ab, _, _ = np.histogram2d(a, b, bins=bins)
    pxy = hist_ab / hist_ab.sum()
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)
    mi = 0.0
    for i in range(len(px)):
        for j in range(len(py)):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))
    return float(mi)


OPERATIONS["statistical_mutual_information"] = {
    "fn": statistical_mutual_information,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Mutual information between first and second halves of array"
}


def norm_lp(x, p=2):
    """Lp norm of array. Input: array. Output: scalar."""
    return float(np.sum(np.abs(x) ** p) ** (1.0 / p))


OPERATIONS["norm_lp"] = {
    "fn": norm_lp,
    "input_type": "array",
    "output_type": "scalar",
    "description": "L2 norm of array"
}


def condition_number(x):
    """Condition number of matrix formed from array. Input: array. Output: scalar."""
    n = len(x)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))
    padded = np.zeros(rows * cols)
    padded[:n] = x
    mat = padded.reshape(rows, cols)
    sv = np.linalg.svd(mat, compute_uv=False)
    if sv[-1] == 0:
        return float('inf')
    return float(sv[0] / sv[-1])


OPERATIONS["condition_number"] = {
    "fn": condition_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Condition number (ratio of largest to smallest singular value)"
}


def sparsity_measure(x):
    """Fraction of near-zero entries (Hoyer sparsity). Input: array. Output: scalar."""
    n = len(x)
    if n == 0:
        return 0.0
    l1 = np.sum(np.abs(x))
    l2 = np.sqrt(np.sum(x ** 2))
    if l2 == 0:
        return 1.0
    sqn = np.sqrt(n)
    return float((sqn - l1 / l2) / (sqn - 1))


OPERATIONS["sparsity_measure"] = {
    "fn": sparsity_measure,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Hoyer sparsity measure of array"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
