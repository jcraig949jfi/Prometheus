"""
Spectral Transforms — Universal spectral adapters that turn ANY structure into comparable signatures

Connects to: [representation_converters, invariant_extractors, multiscale_operators, compression_metrics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "spectral_transforms"
OPERATIONS = {}


def eigen_decomposition(x):
    """Compute eigenvalues from array reshaped as square matrix or covariance. Input: array. Output: array."""
    n = int(np.sqrt(len(x)))
    if n * n == len(x):
        mat = x.reshape(n, n)
    else:
        mat = np.outer(x, x)
    mat = (mat + mat.T) / 2.0
    eigenvalues = np.linalg.eigvalsh(mat)
    return eigenvalues


OPERATIONS["eigen_decomposition"] = {
    "fn": eigen_decomposition,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalues of symmetric matrix formed from input"
}


def singular_value_spectrum(x):
    """Compute singular values of matrix formed from array. Input: array. Output: array."""
    n = len(x)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))
    padded = np.zeros(rows * cols)
    padded[:n] = x
    mat = padded.reshape(rows, cols)
    return np.linalg.svd(mat, compute_uv=False)


OPERATIONS["singular_value_spectrum"] = {
    "fn": singular_value_spectrum,
    "input_type": "array",
    "output_type": "array",
    "description": "Singular value decomposition spectrum of reshaped array"
}


def power_spectrum_fft(x):
    """Power spectral density via FFT. Input: array. Output: array."""
    ft = np.fft.rfft(x)
    return np.abs(ft) ** 2


OPERATIONS["power_spectrum_fft"] = {
    "fn": power_spectrum_fft,
    "input_type": "array",
    "output_type": "array",
    "description": "Power spectrum computed via FFT"
}


def laplacian_spectrum_from_array(x):
    """Eigenvalues of graph Laplacian from kNN adjacency on array values. Input: array. Output: array."""
    n = len(x)
    dists = np.abs(x[:, None] - x[None, :])
    k = min(3, n - 1)
    adj = np.zeros((n, n))
    for i in range(n):
        neighbors = np.argsort(dists[i])[1:k + 1]
        adj[i, neighbors] = 1
        adj[neighbors, i] = 1
    degree = np.diag(adj.sum(axis=1))
    laplacian = degree - adj
    return np.linalg.eigvalsh(laplacian)


OPERATIONS["laplacian_spectrum_from_array"] = {
    "fn": laplacian_spectrum_from_array,
    "input_type": "array",
    "output_type": "array",
    "description": "Spectrum of graph Laplacian built from kNN on array values"
}


def covariance_eigenstructure(x):
    """Eigenvalues of covariance matrix from sliding windows. Input: array. Output: array."""
    n = len(x)
    w = max(2, n // 2)
    windows = np.array([x[i:i + w] for i in range(n - w + 1)])
    cov = np.cov(windows.T)
    if cov.ndim == 0:
        return np.array([float(cov)])
    return np.linalg.eigvalsh(cov)


OPERATIONS["covariance_eigenstructure"] = {
    "fn": covariance_eigenstructure,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalues of covariance matrix from sliding window embedding"
}


def spectral_centroid(x):
    """Weighted mean of frequencies by magnitude spectrum. Input: array. Output: scalar."""
    mag = np.abs(np.fft.rfft(x))
    freqs = np.arange(len(mag))
    total = mag.sum()
    if total == 0:
        return 0.0
    return float(np.sum(freqs * mag) / total)


OPERATIONS["spectral_centroid"] = {
    "fn": spectral_centroid,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Centroid of the frequency spectrum"
}


def spectral_bandwidth(x):
    """Weighted std of frequencies by magnitude spectrum. Input: array. Output: scalar."""
    mag = np.abs(np.fft.rfft(x))
    freqs = np.arange(len(mag))
    total = mag.sum()
    if total == 0:
        return 0.0
    centroid = np.sum(freqs * mag) / total
    return float(np.sqrt(np.sum(mag * (freqs - centroid) ** 2) / total))


OPERATIONS["spectral_bandwidth"] = {
    "fn": spectral_bandwidth,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Bandwidth (spread) of the frequency spectrum"
}


def spectral_rolloff(x, threshold=0.85):
    """Frequency below which threshold of spectral energy is contained. Input: array. Output: scalar."""
    mag = np.abs(np.fft.rfft(x)) ** 2
    cumulative = np.cumsum(mag)
    total = cumulative[-1]
    if total == 0:
        return 0.0
    rolloff_idx = np.searchsorted(cumulative, threshold * total)
    return float(rolloff_idx / len(mag))


OPERATIONS["spectral_rolloff"] = {
    "fn": spectral_rolloff,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Frequency below which 85% of spectral energy lies"
}


def spectral_flatness(x):
    """Ratio of geometric to arithmetic mean of power spectrum (Wiener entropy). Input: array. Output: scalar."""
    ps = np.abs(np.fft.rfft(x)) ** 2
    ps = ps[ps > 0]
    if len(ps) == 0:
        return 0.0
    geo_mean = np.exp(np.mean(np.log(ps)))
    arith_mean = np.mean(ps)
    if arith_mean == 0:
        return 0.0
    return float(geo_mean / arith_mean)


OPERATIONS["spectral_flatness"] = {
    "fn": spectral_flatness,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Spectral flatness (Wiener entropy) of signal"
}


def spectral_entropy(x):
    """Shannon entropy of normalized power spectrum. Input: array. Output: scalar."""
    ps = np.abs(np.fft.rfft(x)) ** 2
    total = ps.sum()
    if total == 0:
        return 0.0
    p = ps / total
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


OPERATIONS["spectral_entropy"] = {
    "fn": spectral_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of the normalized power spectrum"
}


def mel_frequency_cepstral_approx(x, n_mfcc=8):
    """Approximate MFCCs using log power spectrum and DCT via real FFT. Input: array. Output: array."""
    ps = np.abs(np.fft.rfft(x)) ** 2
    n_filters = max(n_mfcc + 2, 10)
    filter_len = len(ps)
    mel_points = np.linspace(0, 2595 * np.log10(1 + filter_len / 2 / 700), n_filters + 2)
    hz_points = 700 * (10 ** (mel_points / 2595) - 1)
    bins = np.floor((filter_len) * hz_points / filter_len).astype(int)
    bins = np.clip(bins, 0, filter_len - 1)
    mel_energies = np.zeros(n_filters)
    for i in range(n_filters):
        lo, mid, hi = bins[i], bins[i + 1], bins[i + 2]
        if mid == lo:
            mid = lo + 1
        if hi == mid:
            hi = mid + 1
        lo, mid, hi = min(lo, filter_len - 1), min(mid, filter_len - 1), min(hi, filter_len - 1)
        for j in range(lo, mid):
            if mid > lo:
                mel_energies[i] += ps[j] * (j - lo) / (mid - lo)
        for j in range(mid, hi):
            if hi > mid:
                mel_energies[i] += ps[j] * (hi - j) / (hi - mid)
    mel_energies = np.maximum(mel_energies, 1e-10)
    log_mel = np.log(mel_energies)
    # DCT-II via real computation
    N = len(log_mel)
    n_arr = np.arange(N)
    mfcc = np.zeros(n_mfcc)
    for k in range(n_mfcc):
        mfcc[k] = np.sum(log_mel * np.cos(np.pi * k * (2 * n_arr + 1) / (2 * N)))
    return mfcc


OPERATIONS["mel_frequency_cepstral_approx"] = {
    "fn": mel_frequency_cepstral_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximate mel-frequency cepstral coefficients"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
