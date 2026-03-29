"""
Multiscale Operators — Scale-dependent operations for renormalization and hierarchy

Connects to: [spectral_transforms, noise_perturbation, compression_metrics, dynamical_systems]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "multiscale_operators"
OPERATIONS = {}


def downsample_average(x, factor=2):
    """Downsample by averaging blocks. Input: array. Output: array."""
    n = len(x)
    trimmed = n - (n % factor)
    return x[:trimmed].reshape(-1, factor).mean(axis=1)


OPERATIONS["downsample_average"] = {
    "fn": downsample_average,
    "input_type": "array",
    "output_type": "array",
    "description": "Downsample array by averaging adjacent blocks"
}


def downsample_max(x, factor=2):
    """Downsample by taking block maxima. Input: array. Output: array."""
    n = len(x)
    trimmed = n - (n % factor)
    return x[:trimmed].reshape(-1, factor).max(axis=1)


OPERATIONS["downsample_max"] = {
    "fn": downsample_max,
    "input_type": "array",
    "output_type": "array",
    "description": "Downsample array by taking block maxima"
}


def upsample_linear(x, factor=2):
    """Upsample via linear interpolation. Input: array. Output: array."""
    n = len(x)
    x_old = np.arange(n)
    x_new = np.linspace(0, n - 1, n * factor)
    return np.interp(x_new, x_old, x)


OPERATIONS["upsample_linear"] = {
    "fn": upsample_linear,
    "input_type": "array",
    "output_type": "array",
    "description": "Upsample array via linear interpolation"
}


def wavelet_haar_decompose(x):
    """Single-level Haar wavelet decomposition. Input: array. Output: array (approx + detail)."""
    n = len(x)
    if n % 2 != 0:
        x = np.append(x, x[-1])
        n += 1
    approx = (x[0::2] + x[1::2]) / np.sqrt(2)
    detail = (x[0::2] - x[1::2]) / np.sqrt(2)
    return np.concatenate([approx, detail])


OPERATIONS["wavelet_haar_decompose"] = {
    "fn": wavelet_haar_decompose,
    "input_type": "array",
    "output_type": "array",
    "description": "Single-level Haar wavelet decomposition (approx | detail)"
}


def wavelet_haar_reconstruct(x):
    """Reconstruct from Haar wavelet coefficients. Input: array. Output: array."""
    n = len(x)
    h = n // 2
    approx = x[:h]
    detail = x[h:2 * h]
    even = (approx + detail) / np.sqrt(2)
    odd = (approx - detail) / np.sqrt(2)
    result = np.zeros(2 * h)
    result[0::2] = even
    result[1::2] = odd
    return result


OPERATIONS["wavelet_haar_reconstruct"] = {
    "fn": wavelet_haar_reconstruct,
    "input_type": "array",
    "output_type": "array",
    "description": "Reconstruct signal from Haar wavelet coefficients"
}


def coarse_grain_block(x, block_size=2):
    """Coarse-grain by block averaging (renormalization). Input: array. Output: array."""
    n = len(x)
    trimmed = n - (n % block_size)
    blocks = x[:trimmed].reshape(-1, block_size)
    return blocks.mean(axis=1)


OPERATIONS["coarse_grain_block"] = {
    "fn": coarse_grain_block,
    "input_type": "array",
    "output_type": "array",
    "description": "Coarse-grain via block averaging (real-space renormalization)"
}


def multigrid_restrict(x):
    """Multigrid restriction: weighted average to coarser grid. Input: array. Output: array."""
    n = len(x)
    if n < 3:
        return x.copy()
    # Full weighting restriction: 1/4, 1/2, 1/4
    coarse_n = (n + 1) // 2
    coarse = np.zeros(coarse_n)
    for i in range(coarse_n):
        j = 2 * i
        left = x[j - 1] if j > 0 else x[j]
        center = x[j] if j < n else x[-1]
        right = x[j + 1] if j + 1 < n else x[min(j, n - 1)]
        coarse[i] = 0.25 * left + 0.5 * center + 0.25 * right
    return coarse


OPERATIONS["multigrid_restrict"] = {
    "fn": multigrid_restrict,
    "input_type": "array",
    "output_type": "array",
    "description": "Multigrid restriction (full weighting) to coarser grid"
}


def multigrid_prolong(x):
    """Multigrid prolongation: linear interpolation to finer grid. Input: array. Output: array."""
    n = len(x)
    fine = np.zeros(2 * n - 1)
    fine[0::2] = x
    fine[1::2] = (x[:-1] + x[1:]) / 2.0
    return fine


OPERATIONS["multigrid_prolong"] = {
    "fn": multigrid_prolong,
    "input_type": "array",
    "output_type": "array",
    "description": "Multigrid prolongation (linear interpolation) to finer grid"
}


def scale_space_gaussian(x, sigma=1.0):
    """Gaussian scale-space smoothing. Input: array. Output: array."""
    n = len(x)
    kernel_size = max(3, int(6 * sigma + 1))
    if kernel_size % 2 == 0:
        kernel_size += 1
    half = kernel_size // 2
    t = np.arange(-half, half + 1)
    kernel = np.exp(-t ** 2 / (2 * sigma ** 2))
    kernel /= kernel.sum()
    # Convolve with padding
    padded = np.pad(x, half, mode='reflect')
    result = np.convolve(padded, kernel, mode='valid')
    return result[:n]


OPERATIONS["scale_space_gaussian"] = {
    "fn": scale_space_gaussian,
    "input_type": "array",
    "output_type": "array",
    "description": "Gaussian scale-space smoothing at given sigma"
}


def laplacian_pyramid_level(x):
    """One level of Laplacian pyramid: difference between signal and smoothed. Input: array. Output: array."""
    # Smooth
    n = len(x)
    kernel = np.array([0.25, 0.5, 0.25])
    padded = np.pad(x, 1, mode='reflect')
    smoothed = np.convolve(padded, kernel, mode='valid')[:n]
    return x - smoothed


OPERATIONS["laplacian_pyramid_level"] = {
    "fn": laplacian_pyramid_level,
    "input_type": "array",
    "output_type": "array",
    "description": "One level of Laplacian pyramid (detail = signal - smoothed)"
}


def renormalization_block_spin(x, block_size=2):
    """Block-spin renormalization: majority vote or average per block, then rescale. Input: array. Output: array."""
    n = len(x)
    trimmed = n - (n % block_size)
    blocks = x[:trimmed].reshape(-1, block_size)
    # Average and rescale by sqrt(block_size) to preserve variance
    coarse = blocks.mean(axis=1) * np.sqrt(block_size)
    return coarse


OPERATIONS["renormalization_block_spin"] = {
    "fn": renormalization_block_spin,
    "input_type": "array",
    "output_type": "array",
    "description": "Block-spin renormalization with variance-preserving rescaling"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
