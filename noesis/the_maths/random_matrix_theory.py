"""
Random Matrix Theory — Wigner semicircle, Tracy-Widom, eigenvalue spacing statistics

Connects to: [linear_algebra, probability_theory, statistical_mechanics, number_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "random_matrix_theory"
OPERATIONS = {}


def wigner_semicircle_density(x):
    """Wigner semicircle distribution density: rho(x) = (2/(pi*R^2)) * sqrt(R^2 - x^2).
    Input: array (points). Output: array (density values)."""
    R = np.max(np.abs(x)) + 1e-15
    result = np.zeros_like(x)
    mask = np.abs(x) < R
    result[mask] = (2.0 / (np.pi * R ** 2)) * np.sqrt(R ** 2 - x[mask] ** 2)
    return result


OPERATIONS["wigner_semicircle_density"] = {
    "fn": wigner_semicircle_density,
    "input_type": "array",
    "output_type": "array",
    "description": "Wigner semicircle law density for eigenvalue distribution"
}


def wigner_random_matrix(x):
    """Generate a GOE Wigner random matrix of size n = len(x).
    Input: array (used for size and seed). Output: matrix."""
    n = len(x)
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    A = rng.randn(n, n)
    # GOE: symmetric with N(0,1) off-diagonal, N(0,2) diagonal
    M = (A + A.T) / (2.0 * np.sqrt(n))
    return M


OPERATIONS["wigner_random_matrix"] = {
    "fn": wigner_random_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Generate GOE Wigner random matrix scaled by 1/sqrt(n)"
}


def eigenvalue_spacing_ratio(x):
    """Compute eigenvalue spacing ratio statistics for GOE diagnostics.
    r_n = min(s_n, s_{n+1}) / max(s_n, s_{n+1}) where s_n are spacings.
    Input: array (eigenvalues or used to generate matrix). Output: array (ratios)."""
    if len(x) < 3:
        return np.array([0.5307])  # GOE mean
    sorted_eigs = np.sort(x)
    spacings = np.diff(sorted_eigs)
    if len(spacings) < 2:
        return np.array([0.5307])
    s1 = spacings[:-1]
    s2 = spacings[1:]
    ratios = np.minimum(s1, s2) / (np.maximum(s1, s2) + 1e-15)
    return ratios


OPERATIONS["eigenvalue_spacing_ratio"] = {
    "fn": eigenvalue_spacing_ratio,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalue spacing ratio r_n (mean ~0.5307 for GOE, ~0.3863 for Poisson)"
}


def marchenko_pastur_density(x):
    """Marchenko-Pastur distribution density for ratio gamma=0.5.
    Input: array (points). Output: array (density values)."""
    gamma = 0.5
    lambda_plus = (1 + np.sqrt(gamma)) ** 2
    lambda_minus = (1 - np.sqrt(gamma)) ** 2
    result = np.zeros_like(x)
    mask = (x >= lambda_minus) & (x <= lambda_plus)
    result[mask] = (1.0 / (2.0 * np.pi * gamma * x[mask])) * \
        np.sqrt((lambda_plus - x[mask]) * (x[mask] - lambda_minus))
    return result


OPERATIONS["marchenko_pastur_density"] = {
    "fn": marchenko_pastur_density,
    "input_type": "array",
    "output_type": "array",
    "description": "Marchenko-Pastur law density for sample covariance eigenvalues"
}


def tracy_widom_approx(x):
    """Approximate Tracy-Widom CDF (TW1) using a shifted Gumbel approximation.
    F_TW1(s) ~ exp(-exp(-pi/sqrt(6) * (s - mu_TW))) with mu_TW ~ -1.2065.
    Input: array (points s). Output: array (CDF values)."""
    mu_tw = -1.2065
    sigma_tw = 1.268
    # Gumbel approximation: a good practical fit
    z = (x - mu_tw) / sigma_tw
    cdf = np.exp(-np.exp(-np.pi / np.sqrt(6) * z - 0.5772))
    return np.clip(cdf, 0.0, 1.0)


OPERATIONS["tracy_widom_approx"] = {
    "fn": tracy_widom_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximate Tracy-Widom CDF for largest eigenvalue fluctuations"
}


def level_repulsion_metric(x):
    """Measure level repulsion: ratio of smallest spacing to mean spacing.
    For GOE, spacings follow Wigner surmise p(s) ~ s * exp(-pi*s^2/4).
    Input: array (eigenvalues). Output: scalar."""
    sorted_eigs = np.sort(x)
    spacings = np.diff(sorted_eigs)
    if len(spacings) == 0:
        return 0.0
    mean_s = np.mean(spacings)
    if mean_s < 1e-15:
        return 0.0
    # Normalize spacings
    s = spacings / mean_s
    # Level repulsion strength: <s> should be ~pi/4 for GOE, 1 for Poisson
    # Return variance ratio as diagnostic
    return float(np.var(s))


OPERATIONS["level_repulsion_metric"] = {
    "fn": level_repulsion_metric,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Variance of normalized spacings (GOE~0.273, Poisson~1.0)"
}


def goe_eigenvalues(x):
    """Generate eigenvalues of a GOE (Gaussian Orthogonal Ensemble) matrix.
    Input: array (size and seed). Output: array (sorted eigenvalues)."""
    n = max(3, len(x))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    A = rng.randn(n, n)
    M = (A + A.T) / 2.0
    eigs = np.linalg.eigvalsh(M)
    return np.sort(eigs)


OPERATIONS["goe_eigenvalues"] = {
    "fn": goe_eigenvalues,
    "input_type": "array",
    "output_type": "array",
    "description": "Sorted eigenvalues of a GOE random matrix"
}


def gue_eigenvalues(x):
    """Generate eigenvalues of a GUE (Gaussian Unitary Ensemble) matrix.
    Input: array (size and seed). Output: array (sorted eigenvalues)."""
    n = max(3, len(x))
    rng = np.random.RandomState(int(abs(x[0] * 1000)) % 2**31)
    A = rng.randn(n, n) + 1j * rng.randn(n, n)
    M = (A + A.conj().T) / 2.0
    eigs = np.linalg.eigvalsh(M)
    return np.sort(eigs.real)


OPERATIONS["gue_eigenvalues"] = {
    "fn": gue_eigenvalues,
    "input_type": "array",
    "output_type": "array",
    "description": "Sorted eigenvalues of a GUE random matrix"
}


def spectral_unfolding(x):
    """Unfold eigenvalue spectrum to unit mean spacing using staircase function.
    Input: array (eigenvalues). Output: array (unfolded eigenvalues)."""
    sorted_eigs = np.sort(x)
    n = len(sorted_eigs)
    # Polynomial fit to cumulative spectral function
    cumulative = np.arange(1, n + 1, dtype=float)
    degree = min(5, n - 1)
    if degree < 1:
        return sorted_eigs
    coeffs = np.polyfit(sorted_eigs, cumulative, degree)
    unfolded = np.polyval(coeffs, sorted_eigs)
    return unfolded


OPERATIONS["spectral_unfolding"] = {
    "fn": spectral_unfolding,
    "input_type": "array",
    "output_type": "array",
    "description": "Unfold spectrum to unit mean spacing via polynomial staircase fit"
}


def nearest_neighbor_spacing(x):
    """Compute nearest-neighbor spacing distribution.
    Input: array (eigenvalues). Output: array (normalized spacings)."""
    sorted_eigs = np.sort(x)
    spacings = np.diff(sorted_eigs)
    if len(spacings) == 0:
        return np.array([0.0])
    mean_s = np.mean(spacings)
    if mean_s < 1e-15:
        return spacings
    return spacings / mean_s


OPERATIONS["nearest_neighbor_spacing"] = {
    "fn": nearest_neighbor_spacing,
    "input_type": "array",
    "output_type": "array",
    "description": "Normalized nearest-neighbor spacings for level statistics"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
