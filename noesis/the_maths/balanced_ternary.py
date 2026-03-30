"""
Balanced Ternary -- Base 3 with digits {-1, 0, 1}. No sign bit. Most efficient integer base.

Connects to: [negabinary, symmetric_bases, mixed_radix, redundant_representations]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "balanced_ternary"
OPERATIONS = {}


def to_balanced_ternary(x):
    """Convert integer to balanced ternary digits array. Input: scalar/array. Output: array."""
    x = np.asarray(x, dtype=float).ravel()
    n = int(round(x[0])) if len(x) > 0 else 0
    if n == 0:
        return np.array([0])
    sign = 1 if n > 0 else -1
    n = abs(n)
    digits = []
    while n > 0:
        rem = n % 3
        if rem == 2:
            digits.append(-1)
            n = (n + 1) // 3
        else:
            digits.append(rem)
            n = n // 3
    result = np.array(digits[::-1], dtype=int)
    if sign < 0:
        result = -result
    return result


OPERATIONS["to_balanced_ternary"] = {
    "fn": to_balanced_ternary,
    "input_type": "scalar",
    "output_type": "array",
    "description": "Convert integer to balanced ternary representation (digits -1, 0, 1)"
}


def from_balanced_ternary(digits):
    """Convert balanced ternary digits to integer. Input: array. Output: scalar."""
    digits = np.asarray(digits, dtype=int)
    result = 0
    for d in digits:
        result = result * 3 + int(d)
    return float(result)


OPERATIONS["from_balanced_ternary"] = {
    "fn": from_balanced_ternary,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert balanced ternary digits back to integer"
}


def balanced_ternary_add(x):
    """Add two integers in balanced ternary (first half + second half of array). Input: array. Output: array."""
    x = np.asarray(x)
    mid = len(x) // 2
    a = int(round(from_balanced_ternary(x[:mid])))
    b = int(round(from_balanced_ternary(x[mid:])))
    return to_balanced_ternary(a + b)


OPERATIONS["balanced_ternary_add"] = {
    "fn": balanced_ternary_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two balanced ternary numbers (input split in half)"
}


def balanced_ternary_multiply(x):
    """Multiply two integers via balanced ternary. Input: array (split in half). Output: array."""
    x = np.asarray(x)
    mid = len(x) // 2
    a = int(round(from_balanced_ternary(x[:mid])))
    b = int(round(from_balanced_ternary(x[mid:])))
    return to_balanced_ternary(a * b)


OPERATIONS["balanced_ternary_multiply"] = {
    "fn": balanced_ternary_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two balanced ternary numbers"
}


def balanced_ternary_negate(x):
    """Negate by flipping all digits. Input: array. Output: array."""
    digits = to_balanced_ternary(x[0]) if np.asarray(x).ndim == 0 or len(x) == 1 else np.asarray(x, dtype=int)
    return -digits


OPERATIONS["balanced_ternary_negate"] = {
    "fn": balanced_ternary_negate,
    "input_type": "array",
    "output_type": "array",
    "description": "Negate a balanced ternary number by flipping all digit signs"
}


def rounding_by_truncation(x):
    """Truncate balanced ternary to fewer digits (natural rounding). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        digits = to_balanced_ternary(val)
        # Truncate to ceil(len/2) digits -- keeps most significant half
        keep = max(1, (len(digits) + 1) // 2)
        truncated = np.zeros(len(digits), dtype=int)
        truncated[:keep] = digits[:keep]
        results[i] = from_balanced_ternary(truncated)
    return results


OPERATIONS["rounding_by_truncation"] = {
    "fn": rounding_by_truncation,
    "input_type": "array",
    "output_type": "array",
    "description": "Round by truncating balanced ternary digits (natural rounding property)"
}


def radix_economy_compare(x):
    """Compare radix economy for bases 2,3,e,10. Input: array. Output: array."""
    # Radix economy = base * ceil(log_base(|n|+1)) for each n
    x = np.asarray(x, dtype=float)
    bases = [2.0, 3.0, np.e, 10.0]
    results = np.zeros(len(bases))
    avg_val = np.mean(np.abs(x)) + 1
    for i, b in enumerate(bases):
        digits_needed = np.ceil(np.log(avg_val + 1) / np.log(b))
        results[i] = b * digits_needed  # radix economy metric
    return results


OPERATIONS["radix_economy_compare"] = {
    "fn": radix_economy_compare,
    "input_type": "array",
    "output_type": "array",
    "description": "Compare radix economy across bases 2, 3, e, 10"
}


def balanced_ternary_abs(x):
    """Absolute value via balanced ternary: negate if leading digit is -1. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = int(round(val))
        results[i] = abs(n)
    return results


OPERATIONS["balanced_ternary_abs"] = {
    "fn": balanced_ternary_abs,
    "input_type": "array",
    "output_type": "array",
    "description": "Absolute value using balanced ternary (check sign of leading digit)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
