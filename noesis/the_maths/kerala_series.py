"""
Kerala Series — Madhava's series with non-European convergence acceleration

Connects to: [egyptian_fractions, vedic_square, pingala_prosody]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "kerala_series"
OPERATIONS = {}


def madhava_pi_series(x):
    """Madhava-Leibniz series for pi/4 with correction terms. Input: array (n_terms). Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(1, int(arr[0])) if len(arr) > 0 else 100
    # pi/4 = sum_{k=0}^{n-1} (-1)^k / (2k+1) + correction
    k = np.arange(n)
    s = np.sum((-1.0) ** k / (2.0 * k + 1.0))
    # Madhava correction term: (-1)^n * (n) / (2*(n^2 + 1))  (rational approximation)
    correction = (-1.0) ** n * n / (2.0 * (n * n + 1.0))
    return float((s + correction) * 4.0)


OPERATIONS["madhava_pi_series"] = {
    "fn": madhava_pi_series,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Madhava-Leibniz pi series with rational correction terms"
}


def madhava_sine_series(x):
    """Madhava's sine series: sin(theta) via Taylor. Input: array (theta values). Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for theta in arr:
        s = 0.0
        term = theta
        for k in range(15):
            s += term
            term *= -theta * theta / ((2 * k + 2) * (2 * k + 3))
        results.append(s)
    return np.array(results)


OPERATIONS["madhava_sine_series"] = {
    "fn": madhava_sine_series,
    "input_type": "array",
    "output_type": "array",
    "description": "Madhava's infinite series for sine"
}


def madhava_cosine_series(x):
    """Madhava's cosine series: cos(theta) via Taylor. Input: array (theta values). Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for theta in arr:
        s = 0.0
        term = 1.0
        for k in range(15):
            s += term
            term *= -theta * theta / ((2 * k + 1) * (2 * k + 2))
        results.append(s)
    return np.array(results)


OPERATIONS["madhava_cosine_series"] = {
    "fn": madhava_cosine_series,
    "input_type": "array",
    "output_type": "array",
    "description": "Madhava's infinite series for cosine"
}


def madhava_arctangent_series(x):
    """Madhava's arctangent series: arctan(t) = t - t^3/3 + t^5/5 - ... Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for t in arr:
        s = 0.0
        term = t
        t2 = t * t
        for k in range(50):
            s += term / (2 * k + 1)
            term *= -t2
            if abs(term) < 1e-15:
                break
        results.append(s)
    return np.array(results)


OPERATIONS["madhava_arctangent_series"] = {
    "fn": madhava_arctangent_series,
    "input_type": "array",
    "output_type": "array",
    "description": "Madhava's arctangent power series"
}


def madhava_correction_term(x):
    """Madhava's rational correction for truncated pi/4 series after n terms. Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for n in arr:
        n = max(1, int(n))
        # Three increasingly accurate correction terms from Kerala school:
        # f1(n) = 1/(2n)
        # f2(n) = n/(2(n^2+1))
        # f3(n) = (n^2+4)/(2n(n^2+5))
        # We return f3 (most accurate)
        f3 = (n * n + 4.0) / (2.0 * n * (n * n + 5.0))
        # Apply sign: (-1)^n
        results.append((-1.0) ** n * f3)
    return np.array(results)


OPERATIONS["madhava_correction_term"] = {
    "fn": madhava_correction_term,
    "input_type": "array",
    "output_type": "array",
    "description": "Madhava's rational correction term for truncated Leibniz series"
}


def convergence_rate_comparison(x):
    """Compare convergence: raw Leibniz vs corrected series. Input: array (n values). Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for n in arr:
        n = max(1, int(n))
        k = np.arange(n)
        raw = 4.0 * np.sum((-1.0) ** k / (2.0 * k + 1.0))
        # With correction
        correction = (-1.0) ** n * (n * n + 4.0) / (2.0 * n * (n * n + 5.0))
        corrected = 4.0 * (np.sum((-1.0) ** k / (2.0 * k + 1.0)) + correction)
        raw_err = abs(raw - np.pi)
        corr_err = abs(corrected - np.pi)
        # Return ratio: how many times better the corrected version is
        if corr_err > 0:
            results.append(raw_err / corr_err)
        else:
            results.append(np.inf)
    return np.array(results)


OPERATIONS["convergence_rate_comparison"] = {
    "fn": convergence_rate_comparison,
    "input_type": "array",
    "output_type": "array",
    "description": "Ratio of raw to corrected Leibniz series error (improvement factor)"
}


def series_partial_sum_error(x):
    """Error of Madhava pi series partial sum vs true pi. Input: array (n terms). Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for n in arr:
        n = max(1, int(n))
        k = np.arange(n)
        s = 4.0 * np.sum((-1.0) ** k / (2.0 * k + 1.0))
        results.append(abs(s - np.pi))
    return np.array(results)


OPERATIONS["series_partial_sum_error"] = {
    "fn": series_partial_sum_error,
    "input_type": "array",
    "output_type": "array",
    "description": "Absolute error of truncated Madhava-Leibniz pi series"
}


def nilakantha_pi_series(x):
    """Nilakantha's faster pi series: 3 + 4/(2*3*4) - 4/(4*5*6) + ... Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(1, int(arr[0])) if len(arr) > 0 else 100
    s = 3.0
    sign = 1.0
    for k in range(1, n + 1):
        d = 2 * k
        s += sign * 4.0 / (d * (d + 1) * (d + 2))
        sign = -sign
    return float(s)


OPERATIONS["nilakantha_pi_series"] = {
    "fn": nilakantha_pi_series,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Nilakantha's faster-converging pi series"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
