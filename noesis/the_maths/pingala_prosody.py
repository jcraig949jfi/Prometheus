"""
Pingala Prosody — Sanskrit binary enumeration and combinatorial algorithms

Connects to: [vedic_square, kerala_series, rod_calculus]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "pingala_prosody"
OPERATIONS = {}


def meru_prastara_row(x):
    """Generate row n of Meru Prastara (Pascal's triangle). Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(0, int(arr[0])) if len(arr) > 0 else 5
    n = min(n, 100)
    row = np.zeros(n + 1, dtype=np.float64)
    row[0] = 1.0
    for i in range(1, n + 1):
        row[i] = row[i - 1] * (n - i + 1) / i
    return row


OPERATIONS["meru_prastara_row"] = {
    "fn": meru_prastara_row,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate row n of Meru Prastara (Pascal's triangle)"
}


def pingala_binary_enumerate(x):
    """Enumerate all binary patterns of length n (Pingala's prastaara). Input: array. Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(1, int(arr[0])) if len(arr) > 0 else 4
    n = min(n, 12)  # cap for performance (2^12 = 4096 rows)
    total = 2 ** n
    result = np.zeros((total, n), dtype=np.float64)
    for i in range(total):
        for j in range(n):
            result[i, n - 1 - j] = (i >> j) & 1
    return result


OPERATIONS["pingala_binary_enumerate"] = {
    "fn": pingala_binary_enumerate,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Enumerate all binary patterns of length n (Pingala's prastaara)"
}


def laghu_guru_count(x):
    """Count combinations of laghu (short=1) and guru (long=2) syllables summing to n beats.
    This gives Fibonacci numbers. Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for val in arr:
        n = max(1, int(val))
        # Number of ways to compose n as ordered sum of 1s and 2s = F(n)
        # F(1) = 1, F(2) = 2, F(n) = F(n-1) + F(n-2)
        if n == 1:
            results.append(1.0)
        elif n == 2:
            results.append(2.0)
        else:
            a, b = 1.0, 2.0
            for _ in range(n - 2):
                a, b = b, a + b
            results.append(b)
    return np.array(results)


OPERATIONS["laghu_guru_count"] = {
    "fn": laghu_guru_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Count laghu/guru syllable combinations (Fibonacci sequence)"
}


def pingala_fast_power(x):
    """Pingala's recursive squaring algorithm for fast exponentiation.
    Input: array [base, exponent]. Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    base = arr[0] if len(arr) > 0 else 2.0
    exp = max(0, int(arr[1])) if len(arr) > 1 else 10
    # Binary method (Pingala's original algorithm from Chandahsutra)
    result = 1.0
    b = base
    e = exp
    while e > 0:
        if e % 2 == 1:
            result *= b
        b *= b
        e //= 2
    return float(result)


OPERATIONS["pingala_fast_power"] = {
    "fn": pingala_fast_power,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fast exponentiation via Pingala's recursive squaring"
}


def hemachandra_fibonacci(x):
    """Hemachandra-Fibonacci sequence. Input: array (indices). Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for val in arr:
        n = max(0, int(val))
        if n == 0:
            results.append(0.0)
        elif n == 1:
            results.append(1.0)
        else:
            a, b = 0.0, 1.0
            for _ in range(n - 1):
                a, b = b, a + b
            results.append(b)
    return np.array(results)


OPERATIONS["hemachandra_fibonacci"] = {
    "fn": hemachandra_fibonacci,
    "input_type": "array",
    "output_type": "array",
    "description": "Hemachandra-Fibonacci sequence at given indices"
}


def prosodic_pattern_count(x):
    """Count distinct prosodic patterns of length n with k guru syllables.
    Input: array [n, k]. Output: scalar (binomial coefficient C(n,k))."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(0, int(arr[0])) if len(arr) > 0 else 5
    k = max(0, int(arr[1])) if len(arr) > 1 else 2
    if k > n:
        return 0.0
    # C(n, k) using multiplicative formula
    result = 1.0
    for i in range(min(k, n - k)):
        result = result * (n - i) / (i + 1)
    return float(result)


OPERATIONS["prosodic_pattern_count"] = {
    "fn": prosodic_pattern_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count prosodic patterns: C(n, k) guru syllables in n positions"
}


def binary_to_meter(x):
    """Convert binary pattern to metrical pattern (0=laghu/short, 1=guru/long).
    Input: array of 0/1. Output: array of beat durations (1 or 2)."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    result = []
    for bit in arr:
        if int(bit) == 0:
            result.append(1.0)  # laghu = 1 beat
        else:
            result.append(2.0)  # guru = 2 beats
    return np.array(result)


OPERATIONS["binary_to_meter"] = {
    "fn": binary_to_meter,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert binary pattern to metrical durations (laghu=1, guru=2)"
}


def chandas_enumeration(x):
    """Enumerate chandas (meters) of total duration n. Input: array. Output: matrix.
    Each row is a composition of n into 1s and 2s (up to a limit)."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(1, int(arr[0])) if len(arr) > 0 else 4
    n = min(n, 10)  # cap for performance
    # Generate all compositions of n into parts of 1 and 2
    compositions = []

    def generate(remaining, current):
        if remaining == 0:
            compositions.append(current[:])
            return
        if remaining >= 1:
            current.append(1)
            generate(remaining - 1, current)
            current.pop()
        if remaining >= 2:
            current.append(2)
            generate(remaining - 2, current)
            current.pop()

    generate(n, [])
    if not compositions:
        return np.array([[0.0]])
    max_len = max(len(c) for c in compositions)
    result = np.zeros((len(compositions), max_len), dtype=np.float64)
    for i, c in enumerate(compositions):
        for j, v in enumerate(c):
            result[i, j] = v
    return result


OPERATIONS["chandas_enumeration"] = {
    "fn": chandas_enumeration,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Enumerate all chandas (meters) of given total duration"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
