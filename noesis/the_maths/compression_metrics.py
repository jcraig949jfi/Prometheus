"""
Compression Metrics — Extended compression and complexity measures beyond kolmogorov_complexity

Connects to: [spectral_transforms, invariant_extractors, multiscale_operators, optimization_landscapes]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import warnings
import numpy as np

FIELD_NAME = "compression_metrics"
OPERATIONS = {}


def pca_variance_explained(x, n_components=None):
    """Fraction of variance explained by top PCA components from sliding windows. Input: array. Output: array."""
    n = len(x)
    w = max(2, n // 2)
    windows = np.array([x[i:i + w] for i in range(n - w + 1)])
    if windows.shape[0] < 2:
        return np.array([1.0])
    cov = np.cov(windows.T)
    if cov.ndim == 0:
        return np.array([1.0])
    eigenvalues = np.linalg.eigvalsh(cov)[::-1]
    eigenvalues = np.maximum(eigenvalues, 0)
    total = eigenvalues.sum()
    if total == 0:
        return np.ones(len(eigenvalues)) / len(eigenvalues)
    return eigenvalues / total


OPERATIONS["pca_variance_explained"] = {
    "fn": pca_variance_explained,
    "input_type": "array",
    "output_type": "array",
    "description": "Fraction of variance explained by each principal component"
}


def rank_approximation_error(x, rank=1):
    """Frobenius error of rank-k approximation. Input: array. Output: scalar."""
    n = len(x)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))
    padded = np.zeros(rows * cols)
    padded[:n] = x
    mat = padded.reshape(rows, cols)
    U, S, Vt = np.linalg.svd(mat, full_matrices=False)
    r = min(rank, len(S))
    approx = (U[:, :r] * S[:r]) @ Vt[:r, :]
    error = np.linalg.norm(mat - approx, 'fro')
    total = np.linalg.norm(mat, 'fro')
    if total == 0:
        return 0.0
    return float(error / total)


OPERATIONS["rank_approximation_error"] = {
    "fn": rank_approximation_error,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Relative Frobenius error of rank-1 approximation"
}


def sparsity_l0(x, threshold=1e-6):
    """L0 sparsity: fraction of near-zero entries. Input: array. Output: scalar."""
    return float(np.sum(np.abs(x) < threshold) / len(x))


OPERATIONS["sparsity_l0"] = {
    "fn": sparsity_l0,
    "input_type": "array",
    "output_type": "scalar",
    "description": "L0 sparsity (fraction of near-zero entries)"
}


def sparsity_l1(x):
    """L1 norm (promotes sparsity). Input: array. Output: scalar."""
    return float(np.sum(np.abs(x)))


OPERATIONS["sparsity_l1"] = {
    "fn": sparsity_l1,
    "input_type": "array",
    "output_type": "scalar",
    "description": "L1 norm of array"
}


def matrix_nuclear_norm(x):
    """Nuclear norm (sum of singular values) of reshaped matrix. Input: array. Output: scalar."""
    n = len(x)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))
    padded = np.zeros(rows * cols)
    padded[:n] = x
    mat = padded.reshape(rows, cols)
    return float(np.sum(np.linalg.svd(mat, compute_uv=False)))


OPERATIONS["matrix_nuclear_norm"] = {
    "fn": matrix_nuclear_norm,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Nuclear norm (sum of singular values)"
}


def low_rank_approximation(x, rank=1):
    """Best rank-k approximation of reshaped matrix, returned flat. Input: array. Output: array."""
    n = len(x)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))
    padded = np.zeros(rows * cols)
    padded[:n] = x
    mat = padded.reshape(rows, cols)
    U, S, Vt = np.linalg.svd(mat, full_matrices=False)
    r = min(rank, len(S))
    approx = (U[:, :r] * S[:r]) @ Vt[:r, :]
    return approx.flatten()[:n]


OPERATIONS["low_rank_approximation"] = {
    "fn": low_rank_approximation,
    "input_type": "array",
    "output_type": "array",
    "description": "Best rank-1 approximation of matrix formed from array"
}


def information_bottleneck_approx(x, beta=1.0):
    """Approximate information bottleneck: trade-off between compression and preservation. Input: array. Output: scalar."""
    # Quantize into bins as compressed representation
    n_bins = max(2, int(np.sqrt(len(x))))
    hist, bin_edges = np.histogram(x, bins=n_bins)
    p = hist.astype(float) / hist.sum()
    p = p[p > 0]
    # H(T) - entropy of compressed
    h_compressed = -np.sum(p * np.log2(p))
    # Distortion: quantization error
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    indices = np.digitize(x, bin_edges[1:-1])
    distortion = np.mean((x - bin_centers[indices]) ** 2)
    # IB objective: H(T) + beta * distortion
    return float(h_compressed + beta * distortion)


OPERATIONS["information_bottleneck_approx"] = {
    "fn": information_bottleneck_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate information bottleneck objective"
}


def rate_distortion_bound(x, n_levels=10):
    """Estimate rate-distortion curve point via uniform quantization. Input: array. Output: scalar."""
    x_range = x.max() - x.min()
    if x_range == 0:
        return 0.0
    # Rate = log2(n_levels)
    rate = np.log2(n_levels)
    # Distortion with n_levels uniform quantization
    step = x_range / n_levels
    quantized = np.round((x - x.min()) / step) * step + x.min()
    distortion = np.mean((x - quantized) ** 2)
    # Return rate needed per unit distortion
    if distortion == 0:
        return float(rate)
    return float(rate / distortion)


OPERATIONS["rate_distortion_bound"] = {
    "fn": rate_distortion_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rate-distortion ratio from uniform quantization"
}


def minimum_description_length(x, max_poly_degree=5):
    """MDL: model complexity + data fit for polynomial model. Input: array. Output: scalar."""
    n = len(x)
    t = np.linspace(0, 1, n)
    best_mdl = float('inf')
    for deg in range(max_poly_degree + 1):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            coeffs = np.polyfit(t, x, deg)
        fitted = np.polyval(coeffs, t)
        residuals = x - fitted
        sse = np.sum(residuals ** 2)
        # MDL = model_cost + data_cost
        model_cost = (deg + 1) * np.log2(n) / 2.0
        data_cost = n / 2.0 * np.log2(sse / n + 1e-10) if sse > 0 else 0
        mdl = model_cost + data_cost
        best_mdl = min(best_mdl, mdl)
    return float(best_mdl)


OPERATIONS["minimum_description_length"] = {
    "fn": minimum_description_length,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Minimum description length for best polynomial fit"
}


def compressibility_ratio(x):
    """Ratio of energy in top-k coefficients to total (FFT-based). Input: array. Output: scalar."""
    ft = np.abs(np.fft.rfft(x))
    total_energy = np.sum(ft ** 2)
    if total_energy == 0:
        return 1.0
    sorted_coeffs = np.sort(ft ** 2)[::-1]
    k = max(1, len(sorted_coeffs) // 4)  # top 25%
    top_k_energy = np.sum(sorted_coeffs[:k])
    return float(top_k_energy / total_energy)


OPERATIONS["compressibility_ratio"] = {
    "fn": compressibility_ratio,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fraction of energy in top-25% FFT coefficients"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
