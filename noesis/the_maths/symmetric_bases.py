"""
Symmetric Bases -- Base 2k+1 with digits {-k,...,0,...,k}. Generalization of balanced ternary.

Connects to: [balanced_ternary, redundant_representations, negabinary, non_integer_bases]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "symmetric_bases"
OPERATIONS = {}


def to_symmetric_base(x):
    """Convert integer to symmetric base. Input: array [value, base(odd)]. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(x[0]))
    base = max(3, int(round(x[1]))) if len(x) > 1 else 3
    # Ensure base is odd
    if base % 2 == 0:
        base += 1
    k = (base - 1) // 2  # digit range [-k, k]

    if n == 0:
        return np.array([0.0])

    digits = []
    while n != 0:
        rem = n % base
        if rem > k:
            rem -= base
        digits.append(rem)
        n = (n - rem) // base
    return np.array(digits[::-1], dtype=float)


OPERATIONS["to_symmetric_base"] = {
    "fn": to_symmetric_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert integer to symmetric base (digits {-k,...,k} for base 2k+1)"
}


def from_symmetric_base(x):
    """Convert symmetric base digits to integer. Input: array [d0, d1, ..., base]. Output: scalar."""
    x = np.asarray(x, dtype=float)
    base = max(3, int(round(x[-1]))) if len(x) > 1 else 3
    if base % 2 == 0:
        base += 1
    digits = x[:-1] if len(x) > 1 else x
    result = 0
    for d in digits:
        result = result * base + int(round(d))
    return float(result)


OPERATIONS["from_symmetric_base"] = {
    "fn": from_symmetric_base,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert symmetric base digits back to integer"
}


def symmetric_add(x):
    """Add two symmetric-base numbers. Input: array (split half, default base 5). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    base = 5
    a_val = 0
    for d in x[:mid]:
        a_val = a_val * base + int(round(d))
    b_val = 0
    for d in x[mid:]:
        b_val = b_val * base + int(round(d))
    return to_symmetric_base(np.array([float(a_val + b_val), float(base)]))


OPERATIONS["symmetric_add"] = {
    "fn": symmetric_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two symmetric-base numbers"
}


def symmetric_multiply(x):
    """Multiply two symmetric-base numbers. Input: array (split half, base 5). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    base = 5
    a_val = 0
    for d in x[:mid]:
        a_val = a_val * base + int(round(d))
    b_val = 0
    for d in x[mid:]:
        b_val = b_val * base + int(round(d))
    return to_symmetric_base(np.array([float(a_val * b_val), float(base)]))


OPERATIONS["symmetric_multiply"] = {
    "fn": symmetric_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two symmetric-base numbers"
}


def symmetric_round_truncate(x):
    """Round by truncating symmetric base digits (inherent rounding). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    base = 5
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = int(round(val))
        digits = to_symmetric_base(np.array([float(n), float(base)]))
        # Truncate to half the digits
        keep = max(1, len(digits) // 2)
        truncated = np.zeros(len(digits))
        truncated[:keep] = digits[:keep]
        # Reconstruct
        result = 0
        for d in truncated:
            result = result * base + int(d)
        results[i] = result
    return results


OPERATIONS["symmetric_round_truncate"] = {
    "fn": symmetric_round_truncate,
    "input_type": "array",
    "output_type": "array",
    "description": "Round by truncating symmetric base digits"
}


def optimal_symmetric_base(x):
    """Find optimal symmetric base for a range of values. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    max_val = max(2, np.max(np.abs(x)))
    # Compare odd bases 3, 5, 7, 9, 11
    bases = [3, 5, 7, 9, 11]
    economies = np.zeros(len(bases))
    for i, b in enumerate(bases):
        digits = np.ceil(np.log(max_val + 1) / np.log(b))
        k = (b - 1) // 2
        # Symmetric base economy: base * digits, but information per digit is log2(base)
        economies[i] = b * digits
    return economies


OPERATIONS["optimal_symmetric_base"] = {
    "fn": optimal_symmetric_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Compare radix economy across symmetric bases 3,5,7,9,11"
}


def symmetric_vs_standard_efficiency(x):
    """Compare symmetric vs standard representation efficiency. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = max(2, int(round(abs(val))))
        # Standard base 5: digits in [0,4], need sign bit for negatives
        std_digits = np.ceil(np.log(n + 1) / np.log(5)) + 1  # +1 for sign
        # Symmetric base 5: digits in [-2,2], no sign needed
        sym_digits = np.ceil(np.log(n + 1) / np.log(5))
        results[i] = std_digits - sym_digits  # Savings
    return results


OPERATIONS["symmetric_vs_standard_efficiency"] = {
    "fn": symmetric_vs_standard_efficiency,
    "input_type": "array",
    "output_type": "array",
    "description": "Compare digit savings of symmetric vs standard representation"
}


def digit_range_for_base(x):
    """Return digit range {-k,...,k} for each odd base. Input: array (bases). Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x) * 2)
    for i, val in enumerate(x):
        base = max(3, int(round(abs(val))))
        if base % 2 == 0:
            base += 1
        k = (base - 1) // 2
        results[2 * i] = float(-k)
        results[2 * i + 1] = float(k)
    return results


OPERATIONS["digit_range_for_base"] = {
    "fn": digit_range_for_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Return digit range [-k, k] for each symmetric base"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
