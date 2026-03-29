"""
Fibonacci Base -- Zeckendorf representation: sums of non-consecutive Fibonacci numbers.

Connects to: [balanced_ternary, non_integer_bases, bijective_bases, factoradic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "fibonacci_base"
OPERATIONS = {}


def _fibs_up_to(n):
    """Generate Fibonacci numbers up to n."""
    fibs = [1, 2]
    while fibs[-1] <= n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs


def zeckendorf_encode(x):
    """Encode integer as Zeckendorf (non-consecutive Fibonacci sum). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    val = max(1, int(round(abs(x[0]))))
    fibs = _fibs_up_to(val)
    digits = []
    remaining = val
    for f in reversed(fibs):
        if f <= remaining:
            digits.append(1)
            remaining -= f
        else:
            digits.append(0)
        if remaining == 0:
            break
    # Pad to length
    while len(digits) < len(fibs):
        digits.append(0)
    return np.array(digits, dtype=float)


OPERATIONS["zeckendorf_encode"] = {
    "fn": zeckendorf_encode,
    "input_type": "array",
    "output_type": "array",
    "description": "Encode integer in Zeckendorf (Fibonacci base) representation"
}


def zeckendorf_decode(digits):
    """Decode Zeckendorf digits to integer. Input: array (binary digits). Output: scalar."""
    digits = np.asarray(digits, dtype=int)
    fibs = [1, 2]
    while len(fibs) < len(digits):
        fibs.append(fibs[-1] + fibs[-2])
    # digits[0] = largest fib, digits[-1] = smallest
    total = 0
    for i, d in enumerate(digits):
        if d and i < len(fibs):
            total += fibs[len(digits) - 1 - i]
    return float(total)


OPERATIONS["zeckendorf_decode"] = {
    "fn": zeckendorf_decode,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Decode Zeckendorf digits back to integer"
}


def fibonacci_base_add(x):
    """Add two Fibonacci-base numbers using substitution carry (011->100). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    # Decode both halves, add, re-encode
    a = int(round(abs(zeckendorf_decode(x[:mid]))))
    b = int(round(abs(zeckendorf_decode(x[mid:]))))
    total = a + b
    if total == 0:
        return np.array([0.0])
    return zeckendorf_encode(np.array([float(total)]))


OPERATIONS["fibonacci_base_add"] = {
    "fn": fibonacci_base_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two Fibonacci-base numbers with substitution carry (011->100)"
}


def fibonacci_base_successor(x):
    """Compute successor (n+1) for each element. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = int(round(abs(val)))
        enc = zeckendorf_encode(np.array([float(n + 1)]))
        results[i] = float(len(enc))  # Return digit count of successor
    return results


OPERATIONS["fibonacci_base_successor"] = {
    "fn": fibonacci_base_successor,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute Zeckendorf successor and return digit counts"
}


def golden_ratio_connection(x):
    """Show connection: Fibonacci base relates to base phi. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    phi = (1 + np.sqrt(5)) / 2
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = max(1, int(round(abs(val))))
        # Zeckendorf digits are also base-phi integer-part digits
        # Number of Fibonacci numbers <= n grows as log_phi(n)
        results[i] = np.log(n + 1) / np.log(phi)
    return results


OPERATIONS["golden_ratio_connection"] = {
    "fn": golden_ratio_connection,
    "input_type": "array",
    "output_type": "array",
    "description": "Show log_phi relationship between Fibonacci base and golden ratio"
}


def fibonacci_base_digit_count(x):
    """Count digits in Zeckendorf representation. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = max(1, int(round(abs(val))))
        enc = zeckendorf_encode(np.array([float(n)]))
        results[i] = float(len(enc))
    return results


OPERATIONS["fibonacci_base_digit_count"] = {
    "fn": fibonacci_base_digit_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Count digits needed in Zeckendorf representation"
}


def fibonacci_base_density(x):
    """Compute density of 1s in Zeckendorf representation. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = max(1, int(round(abs(val))))
        enc = zeckendorf_encode(np.array([float(n)]))
        results[i] = float(np.sum(enc > 0)) / max(1, len(enc))
    return results


OPERATIONS["fibonacci_base_density"] = {
    "fn": fibonacci_base_density,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute density of 1-digits in Zeckendorf representation"
}


def canonical_check(x):
    """Check if array is valid Zeckendorf (no consecutive 1s). Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    digits = (x > 0.5).astype(int)
    # Check no two consecutive 1s
    for i in range(len(digits) - 1):
        if digits[i] == 1 and digits[i + 1] == 1:
            return 0.0
    return 1.0


OPERATIONS["canonical_check"] = {
    "fn": canonical_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if digit array is valid Zeckendorf (no consecutive 1s)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
