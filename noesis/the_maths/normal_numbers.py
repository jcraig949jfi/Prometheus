"""
Normal Numbers — Digit frequency analysis, normality testing in arbitrary bases

Connects to: [algorithmic_randomness, kolmogorov_complexity, p_adic_numbers, continued_fractions]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "normal_numbers"
OPERATIONS = {}


def _to_digits_base_b(n, b, num_digits=None):
    """Convert non-negative integer n to list of digits in base b."""
    n = int(abs(n))
    b = int(b)
    if n == 0:
        return [0] if num_digits is None else [0] * num_digits
    digits = []
    while n > 0:
        digits.append(n % b)
        n //= b
    digits = digits[::-1]
    if num_digits is not None and len(digits) < num_digits:
        digits = [0] * (num_digits - len(digits)) + digits
    return digits


def _fractional_digits(value, b, count):
    """Extract count digits of the fractional part of value in base b."""
    frac = abs(value) - int(abs(value))
    digits = []
    for _ in range(count):
        frac *= b
        d = int(frac)
        digits.append(d)
        frac -= d
    return digits


def digit_frequency_base_b(x):
    """Compute digit frequency histogram for a number in base b.
    Input: array [number, base, num_frac_digits]. Output: array of frequencies for digits 0..b-1."""
    x = np.asarray(x, dtype=float)
    number = x[0] if len(x) > 0 else 12345
    b = int(x[1]) if len(x) > 1 else 10
    num_digits = int(x[2]) if len(x) > 2 else 100
    b = max(b, 2)
    # Use integer digits + fractional digits
    int_part = _to_digits_base_b(int(abs(number)), b)
    frac_part = _fractional_digits(number, b, num_digits)
    all_digits = int_part + frac_part
    freq = np.zeros(b)
    for d in all_digits:
        if 0 <= d < b:
            freq[d] += 1
    freq /= len(all_digits)
    return freq


OPERATIONS["digit_frequency_base_b"] = {
    "fn": digit_frequency_base_b,
    "input_type": "array",
    "output_type": "array",
    "description": "Digit frequency histogram in base b"
}


def block_frequency_test(x):
    """Test frequency of length-k blocks in base-b expansion.
    Input: array [number, base, block_length, num_digits]. Output: scalar (chi-squared statistic)."""
    x = np.asarray(x, dtype=float)
    number = x[0] if len(x) > 0 else np.pi
    b = int(x[1]) if len(x) > 1 else 10
    k = int(x[2]) if len(x) > 2 else 1
    n = int(x[3]) if len(x) > 3 else 200
    b = max(b, 2)
    k = max(k, 1)
    digits = _fractional_digits(number, b, n)
    # Count all k-blocks
    num_blocks = b ** k
    counts = np.zeros(num_blocks)
    for i in range(len(digits) - k + 1):
        block_val = 0
        for j in range(k):
            block_val = block_val * b + digits[i + j]
        if block_val < num_blocks:
            counts[block_val] += 1
    total = len(digits) - k + 1
    expected = total / num_blocks
    if expected == 0:
        return np.float64(0.0)
    chi2 = np.sum((counts - expected) ** 2 / expected)
    return np.float64(chi2)


OPERATIONS["block_frequency_test"] = {
    "fn": block_frequency_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Chi-squared test for block frequency normality"
}


def champernowne_construct(x):
    """Construct digits of Champernowne's number in base b (0.123456789101112...).
    Input: array [num_digits, base]. Output: array of digits."""
    x = np.asarray(x, dtype=float)
    n = int(x[0]) if len(x) > 0 else 50
    b = int(x[1]) if len(x) > 1 else 10
    b = max(b, 2)
    n = min(n, 2000)
    digits = []
    num = 1
    while len(digits) < n:
        digits.extend(_to_digits_base_b(num, b))
        num += 1
    return np.array(digits[:n], dtype=float)


OPERATIONS["champernowne_construct"] = {
    "fn": champernowne_construct,
    "input_type": "array",
    "output_type": "array",
    "description": "Construct Champernowne's constant digits in base b"
}


def normality_chi_squared(x):
    """Chi-squared test for digit normality. Input: array of digits. Output: scalar (p-value approximation)."""
    x = np.asarray(x, dtype=float)
    digits = x.astype(int)
    if len(digits) == 0:
        return np.float64(1.0)
    b = int(digits.max()) + 1
    if b < 2:
        b = 2
    counts = np.bincount(digits, minlength=b).astype(float)
    expected = len(digits) / b
    chi2 = np.sum((counts - expected) ** 2 / expected)
    # Approximate p-value using chi2 distribution with b-1 degrees of freedom
    # Using Wilson-Hilferty approximation
    df = b - 1
    if df == 0:
        return np.float64(1.0)
    z = (chi2 / df) ** (1.0 / 3) - (1 - 2.0 / (9 * df))
    z /= np.sqrt(2.0 / (9 * df))
    # Standard normal CDF approximation
    p_value = 0.5 * (1 + np.tanh(z * 0.7978845608))  # erfc approx
    return np.float64(1 - p_value)


OPERATIONS["normality_chi_squared"] = {
    "fn": normality_chi_squared,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Chi-squared normality test p-value for digit sequence"
}


def copeland_erdos_construct(x):
    """Construct digits of Copeland-Erdos constant (0.2357111317...) in base b.
    Input: array [num_digits, base]. Output: array of digits."""
    x = np.asarray(x, dtype=float)
    n = int(x[0]) if len(x) > 0 else 50
    b = int(x[1]) if len(x) > 1 else 10
    b = max(b, 2)
    n = min(n, 2000)
    # Generate primes using sieve
    limit = max(n * 10, 1000)
    sieve = np.ones(limit, dtype=bool)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = False
    primes = np.where(sieve)[0]
    digits = []
    for p in primes:
        digits.extend(_to_digits_base_b(int(p), b))
        if len(digits) >= n:
            break
    return np.array(digits[:n], dtype=float)


OPERATIONS["copeland_erdos_construct"] = {
    "fn": copeland_erdos_construct,
    "input_type": "array",
    "output_type": "array",
    "description": "Construct Copeland-Erdos constant digits in base b"
}


def base_normality_compare(x):
    """Compare digit distribution chi-squared statistics across multiple bases.
    Input: array [number, max_base, num_digits]. Output: array of chi2 values."""
    x = np.asarray(x, dtype=float)
    number = x[0] if len(x) > 0 else np.sqrt(2)
    max_base = int(x[1]) if len(x) > 1 else 8
    num_digits = int(x[2]) if len(x) > 2 else 200
    results = []
    for b in range(2, max_base + 1):
        digits = _fractional_digits(number, b, num_digits)
        counts = np.zeros(b)
        for d in digits:
            if 0 <= d < b:
                counts[d] += 1
        expected = num_digits / b
        chi2 = np.sum((counts - expected) ** 2 / expected)
        results.append(chi2)
    return np.array(results, dtype=float)


OPERATIONS["base_normality_compare"] = {
    "fn": base_normality_compare,
    "input_type": "array",
    "output_type": "array",
    "description": "Compare normality chi-squared stats across bases"
}


def digit_correlation_function(x):
    """Compute autocorrelation of digit sequence at lags 1..max_lag.
    Input: array of digits. Output: array of correlations."""
    x = np.asarray(x, dtype=float)
    if len(x) < 4:
        return np.array([0.0])
    mean = np.mean(x)
    var = np.var(x)
    if var < 1e-15:
        return np.zeros(min(len(x) // 2, 20))
    max_lag = min(len(x) // 2, 20)
    corr = []
    for lag in range(1, max_lag + 1):
        c = np.mean((x[:-lag] - mean) * (x[lag:] - mean)) / var
        corr.append(c)
    return np.array(corr, dtype=float)


OPERATIONS["digit_correlation_function"] = {
    "fn": digit_correlation_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Autocorrelation of digit sequence at various lags"
}


def equidistribution_discrepancy(x):
    """Compute discrepancy D_N of fractional parts {n*alpha} for equidistribution.
    Input: array [alpha, N]. Output: scalar (star discrepancy)."""
    x = np.asarray(x, dtype=float)
    alpha = x[0] if len(x) > 0 else np.sqrt(2)
    N = int(x[1]) if len(x) > 1 else 100
    N = min(N, 5000)
    # Compute fractional parts
    fracs = np.mod(np.arange(1, N + 1) * alpha, 1.0)
    fracs_sorted = np.sort(fracs)
    # Star discrepancy: max |F_N(x) - x|
    indices = np.arange(1, N + 1) / N
    D_plus = np.max(indices - fracs_sorted)
    D_minus = np.max(fracs_sorted - (indices - 1.0 / N))
    return np.float64(max(D_plus, D_minus))


OPERATIONS["equidistribution_discrepancy"] = {
    "fn": equidistribution_discrepancy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Star discrepancy of equidistributed sequence {n*alpha}"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
