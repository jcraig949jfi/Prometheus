"""
Fractal Dimensions — box-counting, correlation dimension, Hausdorff estimation

Connects to: [topology, dynamical_systems, measure_theory, information_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "fractal_dimensions"
OPERATIONS = {}


def box_counting_dimension(x):
    """Estimate fractal dimension via box-counting method.
    Treats the array as a 1D point set, counts boxes at multiple scales,
    and fits log(count) vs log(1/scale).
    Input: array. Output: scalar."""
    if len(x) < 2:
        return 0.0
    # Normalize to [0, 1]
    xmin, xmax = np.min(x), np.max(x)
    if xmax - xmin < 1e-12:
        return 0.0
    normalized = (x - xmin) / (xmax - xmin)

    scales = [2, 4, 8, 16, 32, 64]
    log_scales = []
    log_counts = []
    for s in scales:
        if s > len(x) * 2:
            break
        bins = np.floor(normalized * s).astype(int)
        bins = np.clip(bins, 0, s - 1)
        count = len(np.unique(bins))
        if count > 0:
            log_scales.append(np.log(s))
            log_counts.append(np.log(count))

    if len(log_scales) < 2:
        return 1.0
    # Linear regression: dimension = slope
    coeffs = np.polyfit(log_scales, log_counts, 1)
    return float(coeffs[0])


OPERATIONS["box_counting_dimension"] = {
    "fn": box_counting_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates fractal dimension via box-counting at multiple scales"
}


def correlation_dimension(x):
    """Estimate correlation dimension from pairwise distances.
    Computes C(r) = fraction of pairs within distance r, fits log-log slope.
    Input: array. Output: scalar."""
    n = len(x)
    if n < 3:
        return 0.0
    # Pairwise distances
    dists = np.abs(np.subtract.outer(x, x))
    dists = dists[np.triu_indices(n, k=1)]
    if len(dists) == 0:
        return 0.0
    dists = np.sort(dists)
    dists = dists[dists > 1e-12]
    if len(dists) < 2:
        return 0.0

    # Compute correlation integral at several radii
    radii = np.percentile(dists, [10, 25, 50, 75, 90])
    radii = np.unique(radii)
    radii = radii[radii > 1e-12]
    if len(radii) < 2:
        return 0.0

    total_pairs = n * (n - 1) / 2
    log_r = []
    log_c = []
    for r in radii:
        c = np.sum(dists <= r) / total_pairs
        if c > 0:
            log_r.append(np.log(r))
            log_c.append(np.log(c))

    if len(log_r) < 2:
        return 0.0
    coeffs = np.polyfit(log_r, log_c, 1)
    return float(coeffs[0])


OPERATIONS["correlation_dimension"] = {
    "fn": correlation_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates correlation dimension from pairwise distance scaling"
}


def information_dimension(x):
    """Estimate information (Renyi) dimension D1.
    D1 = lim (sum p_i log p_i) / log(epsilon).
    Input: array. Output: scalar."""
    if len(x) < 2:
        return 0.0
    xmin, xmax = np.min(x), np.max(x)
    if xmax - xmin < 1e-12:
        return 0.0
    normalized = (x - xmin) / (xmax - xmin)

    scales = [4, 8, 16, 32, 64]
    log_eps = []
    entropies = []
    for s in scales:
        if s > len(x) * 2:
            break
        bins = np.floor(normalized * s).astype(int)
        bins = np.clip(bins, 0, s - 1)
        counts = np.bincount(bins, minlength=s).astype(float)
        probs = counts[counts > 0] / len(x)
        entropy = -np.sum(probs * np.log(probs))
        log_eps.append(np.log(1.0 / s))
        entropies.append(entropy)

    if len(log_eps) < 2:
        return 1.0
    # D1 = lim H(eps) / log(1/eps)
    coeffs = np.polyfit(log_eps, entropies, 1)
    return float(-coeffs[0])


OPERATIONS["information_dimension"] = {
    "fn": information_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates information dimension D1 from entropy scaling"
}


def lacunarity(x):
    """Compute lacunarity (gappiness) of the array.
    Lacunarity = Var(box mass) / Mean(box mass)^2 + 1 at a given scale.
    Input: array. Output: scalar."""
    if len(x) < 2:
        return 1.0
    # Use a sliding window (gliding box)
    box_size = max(2, len(x) // 4)
    masses = []
    for i in range(len(x) - box_size + 1):
        masses.append(np.sum(np.abs(x[i:i + box_size])))
    masses = np.array(masses)
    mean_m = np.mean(masses)
    if mean_m < 1e-12:
        return 1.0
    var_m = np.var(masses)
    return float(var_m / (mean_m ** 2) + 1.0)


OPERATIONS["lacunarity"] = {
    "fn": lacunarity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes lacunarity (texture gappiness) via gliding box method"
}


def hurst_exponent(x):
    """Estimate the Hurst exponent using rescaled range (R/S) analysis.
    H > 0.5 indicates persistence, H < 0.5 anti-persistence.
    Input: array. Output: scalar."""
    n = len(x)
    if n < 4:
        return 0.5

    # R/S analysis at multiple scales
    sizes = []
    rs_values = []
    for size in [n // 4, n // 2, n]:
        if size < 2:
            continue
        seg = x[:size]
        mean_seg = np.mean(seg)
        deviations = np.cumsum(seg - mean_seg)
        R = np.max(deviations) - np.min(deviations)
        S = np.std(seg, ddof=1) if np.std(seg, ddof=1) > 1e-12 else 1e-12
        sizes.append(np.log(size))
        rs_values.append(np.log(R / S) if R / S > 1e-12 else 0.0)

    if len(sizes) < 2:
        return 0.5
    coeffs = np.polyfit(sizes, rs_values, 1)
    H = float(np.clip(coeffs[0], 0.0, 1.0))
    return H


OPERATIONS["hurst_exponent"] = {
    "fn": hurst_exponent,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates Hurst exponent via rescaled range (R/S) analysis"
}


def lyapunov_exponent_1d(x):
    """Estimate the largest Lyapunov exponent for a 1D map.
    Treats the array as an orbit and estimates average log divergence rate.
    Input: array. Output: scalar."""
    n = len(x)
    if n < 3:
        return 0.0
    # Estimate derivative along orbit: |f'(x_i)| ~ |x_{i+1} - x_i| / delta
    # For logistic-like maps, lambda = (1/n) * sum(log|f'(x_i)|)
    diffs = np.abs(np.diff(x))
    diffs = diffs[diffs > 1e-15]
    if len(diffs) == 0:
        return float('-inf')
    lyap = np.mean(np.log(diffs))
    return float(lyap)


OPERATIONS["lyapunov_exponent_1d"] = {
    "fn": lyapunov_exponent_1d,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates largest Lyapunov exponent from 1D orbit differences"
}


def menger_sponge_dimension(x):
    """Return the Hausdorff dimension of the Menger sponge: log(20)/log(3).
    The input array is used to compute a weighted perturbation.
    Input: array. Output: scalar."""
    # Exact dimension of Menger sponge
    d = np.log(20) / np.log(3)  # ~2.7268
    # Small perturbation based on variance of input (for tensor coupling)
    perturbation = np.var(x) * 1e-10
    return float(d + perturbation)


OPERATIONS["menger_sponge_dimension"] = {
    "fn": menger_sponge_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Returns Hausdorff dimension of Menger sponge: log(20)/log(3) ~ 2.727"
}


def sierpinski_dimension(x):
    """Return the Hausdorff dimension of the Sierpinski triangle: log(3)/log(2).
    Input: array. Output: scalar."""
    d = np.log(3) / np.log(2)  # ~1.585
    perturbation = np.var(x) * 1e-10
    return float(d + perturbation)


OPERATIONS["sierpinski_dimension"] = {
    "fn": sierpinski_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Returns Hausdorff dimension of Sierpinski triangle: log(3)/log(2) ~ 1.585"
}


def cantor_set_dimension(x):
    """Return the Hausdorff dimension of the Cantor set: log(2)/log(3).
    Input: array. Output: scalar."""
    d = np.log(2) / np.log(3)  # ~0.6309
    perturbation = np.var(x) * 1e-10
    return float(d + perturbation)


OPERATIONS["cantor_set_dimension"] = {
    "fn": cantor_set_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Returns Hausdorff dimension of Cantor set: log(2)/log(3) ~ 0.631"
}


def multifractal_spectrum(x):
    """Compute a simplified multifractal spectrum f(alpha).
    Returns array of generalized dimensions D_q for q = -2, -1, 0, 1, 2.
    Input: array. Output: array."""
    if len(x) < 2:
        return np.array([0.0] * 5)
    xmin, xmax = np.min(np.abs(x)), np.max(np.abs(x))
    vals = np.abs(x)
    total = np.sum(vals)
    if total < 1e-12:
        return np.array([1.0] * 5)
    probs = vals / total

    qs = [-2.0, -1.0, 0.0, 1.0, 2.0]
    dims = []
    for q in qs:
        if q == 1.0:
            # D1 = information dimension (entropy-based)
            p = probs[probs > 1e-12]
            d1 = -np.sum(p * np.log(p)) / np.log(len(x))
            dims.append(d1)
        else:
            p = probs[probs > 1e-12]
            partition = np.sum(p ** q)
            if partition > 0:
                dq = np.log(partition) / ((q - 1) * np.log(len(x)))
                dims.append(dq)
            else:
                dims.append(0.0)
    return np.array(dims)


OPERATIONS["multifractal_spectrum"] = {
    "fn": multifractal_spectrum,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes generalized dimensions D_q for q in {-2,-1,0,1,2}"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
