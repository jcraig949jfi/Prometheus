"""
Algorithmic Randomness — Borel normality tests, frequency tests, serial tests

Connects to: [kolmogorov_complexity, statistics, information_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "algorithmic_randomness"
OPERATIONS = {}


def frequency_test(x):
    """Monobit frequency test: proportion of 1s in binarized sequence. Returns p-value. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    median = np.median(vals)
    bits = np.where(vals > median, 1, -1)
    n = len(bits)
    if n == 0:
        return 1.0
    s = np.abs(np.sum(bits)) / np.sqrt(n)
    # p-value from complementary error function
    from math import erfc
    p_value = erfc(s / np.sqrt(2))
    return float(p_value)


OPERATIONS["frequency_test"] = {
    "fn": frequency_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "NIST monobit frequency test p-value"
}


def serial_test(x):
    """Serial test: check uniformity of pairs in binarized sequence. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    median = np.median(vals)
    bits = (vals > median).astype(int)
    n = len(bits)
    if n < 4:
        return 1.0
    # Count pairs (00, 01, 10, 11)
    pairs = {'00': 0, '01': 0, '10': 0, '11': 0}
    for i in range(n - 1):
        key = f"{bits[i]}{bits[i+1]}"
        pairs[key] += 1
    total_pairs = n - 1
    expected = total_pairs / 4.0
    if expected == 0:
        return 1.0
    chi2 = sum((c - expected) ** 2 / expected for c in pairs.values())
    # Approximate p-value from chi-squared with 3 df
    # Using survival function approximation
    from math import exp
    p_value = exp(-chi2 / 2)  # rough approximation
    return float(min(p_value, 1.0))


OPERATIONS["serial_test"] = {
    "fn": serial_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Serial test for pair uniformity in binary sequence"
}


def runs_test(x):
    """Runs test: count runs of consecutive identical bits. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    median = np.median(vals)
    bits = (vals > median).astype(int)
    n = len(bits)
    if n < 2:
        return 1.0
    pi = np.sum(bits) / n
    if abs(pi - 0.5) > 2 / np.sqrt(n):
        return 0.0  # fails prerequisite
    # Count runs
    runs = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            runs += 1
    # Expected runs and variance
    expected = 2 * n * pi * (1 - pi) + 1 if pi > 0 and pi < 1 else 1
    var = max(2 * n * pi * (1 - pi) * (2 * n * pi * (1 - pi) - 1) / (n - 1), 1e-10) if n > 1 else 1
    z = abs(runs - expected) / np.sqrt(var)
    from math import erfc
    p_value = erfc(z / np.sqrt(2))
    return float(p_value)


OPERATIONS["runs_test"] = {
    "fn": runs_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Wald-Wolfowitz runs test p-value"
}


def block_frequency_test(x):
    """Block frequency test: check proportion of 1s in M-bit blocks. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    median = np.median(vals)
    bits = (vals > median).astype(int)
    n = len(bits)
    M = max(2, n // 4)  # block size
    N = n // M  # number of blocks
    if N < 1 or M < 1:
        return 1.0
    chi2 = 0.0
    for i in range(N):
        block = bits[i * M:(i + 1) * M]
        pi_i = np.sum(block) / M
        chi2 += (pi_i - 0.5) ** 2
    chi2 *= 4 * M
    # Approximate p-value (chi2 with N df)
    # Use incomplete gamma approximation
    from math import exp
    p_value = exp(-chi2 / (2 * N)) if N > 0 else 1.0
    return float(min(p_value, 1.0))


OPERATIONS["block_frequency_test"] = {
    "fn": block_frequency_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Block frequency test for randomness"
}


def borel_normality_digit(x):
    """Test Borel normality: check digit frequency in base b. x treated as digit sequence. Input: array. Output: scalar."""
    vals = np.asarray(np.abs(x), dtype=np.int64) % 10
    n = len(vals)
    if n == 0:
        return 1.0
    # Count digit frequencies (base 10 digits)
    counts = np.zeros(10, dtype=np.float64)
    for v in vals:
        counts[int(v)] += 1
    expected = n / 10.0
    # Chi-squared statistic
    chi2 = np.sum((counts - expected) ** 2 / expected) if expected > 0 else 0
    # Approximate p-value
    from math import exp
    p_value = exp(-chi2 / 18)  # rough approx for df=9
    return float(min(p_value, 1.0))


OPERATIONS["borel_normality_digit"] = {
    "fn": borel_normality_digit,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Borel normality test for digit frequency uniformity"
}


def spectral_test_randomness(x):
    """Discrete Fourier transform test: detect periodic features. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    median = np.median(vals)
    bits = np.where(vals > median, 1.0, -1.0)
    n = len(bits)
    if n < 4:
        return 1.0
    # DFT
    S = np.abs(np.fft.fft(bits))[:n // 2]
    # Threshold: sqrt(log(1/0.05) * n) ~ sqrt(2.9957 * n)
    T = np.sqrt(np.log(1.0 / 0.05) * n)
    # Count peaks below threshold
    N0 = 0.95 * n / 2.0  # expected count below threshold
    N1 = np.sum(S < T)
    d = (N1 - N0) / np.sqrt(n * 0.95 * 0.05 / 4.0) if n > 0 else 0
    from math import erfc
    p_value = erfc(abs(d) / np.sqrt(2))
    return float(p_value)


OPERATIONS["spectral_test_randomness"] = {
    "fn": spectral_test_randomness,
    "input_type": "array",
    "output_type": "scalar",
    "description": "DFT-based spectral test for randomness"
}


def approximate_entropy_test(x):
    """Approximate entropy (ApEn) test. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    median = np.median(vals)
    bits = (vals > median).astype(int)
    n = len(bits)
    m = 2  # block length
    if n < m + 1:
        return 0.0

    def _phi(m_val):
        from collections import Counter
        patterns = [tuple(bits[(i + j) % n] for j in range(m_val)) for i in range(n)]
        counts = Counter(patterns)
        total = len(patterns)
        probs = np.array(list(counts.values()), dtype=np.float64) / total
        return np.sum(probs * np.log(probs))

    apen = _phi(m) - _phi(m + 1)
    # Test statistic
    chi2 = 2 * n * (np.log(2) - apen)
    from math import exp
    p_value = exp(-chi2 / (2 ** (m + 1)))
    return float(min(max(p_value, 0.0), 1.0))


OPERATIONS["approximate_entropy_test"] = {
    "fn": approximate_entropy_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate entropy test for randomness"
}


def cumulative_sums_test(x):
    """Cumulative sums (CUSUM) test. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    median = np.median(vals)
    bits = np.where(vals > median, 1, -1)
    n = len(bits)
    if n == 0:
        return 1.0
    # Forward cumulative sum
    cumsum = np.cumsum(bits)
    z = np.max(np.abs(cumsum))
    # Approximate p-value
    # P(max |S_k| >= z) for random walk
    if z == 0:
        return 1.0
    from math import erfc
    # Use normal approximation
    p_value = erfc(z / np.sqrt(n) / np.sqrt(2))
    return float(min(p_value * 2, 1.0))  # two-sided


OPERATIONS["cumulative_sums_test"] = {
    "fn": cumulative_sums_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Cumulative sums (CUSUM) test for randomness"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
