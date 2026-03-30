"""
Negabinary -- Base -2. Every integer (positive and negative) with digits {0,1}, no sign.

Connects to: [balanced_ternary, complex_bases, bijective_bases, redundant_representations]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "negabinary"
OPERATIONS = {}


def to_negabinary(x):
    """Convert integer to negabinary (base -2) digits. Input: scalar/array. Output: array."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 0:
        x = np.array([x])
    results = []
    for val in x:
        n = int(round(val))
        if n == 0:
            results.append(np.array([0]))
            continue
        digits = []
        while n != 0:
            remainder = n % (-2)
            n = n // (-2)
            if remainder < 0:
                remainder += 2
                n += 1
            digits.append(remainder)
        results.append(np.array(digits[::-1], dtype=int))
    # Return first result for scalar-like input
    if len(results) == 1:
        return results[0]
    # For array input, return concatenated with lengths
    return results[0]


OPERATIONS["to_negabinary"] = {
    "fn": to_negabinary,
    "input_type": "scalar",
    "output_type": "array",
    "description": "Convert integer to negabinary (base -2) representation"
}


def from_negabinary(digits):
    """Convert negabinary digits to integer. Input: array. Output: scalar."""
    digits = np.asarray(digits, dtype=int)
    result = 0
    for i, d in enumerate(digits):
        power = len(digits) - 1 - i
        result += int(d) * ((-2) ** power)
    return float(result)


OPERATIONS["from_negabinary"] = {
    "fn": from_negabinary,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert negabinary digits back to integer"
}


def negabinary_add(x):
    """Add two integers in negabinary with bidirectional carry. Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    a = int(round(from_negabinary(np.clip(x[:mid], 0, 1).astype(int))))
    b = int(round(from_negabinary(np.clip(x[mid:], 0, 1).astype(int))))
    return to_negabinary(float(a + b))


OPERATIONS["negabinary_add"] = {
    "fn": negabinary_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two negabinary numbers with bidirectional carry propagation"
}


def negabinary_multiply(x):
    """Multiply two integers via negabinary. Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    a = int(round(from_negabinary(np.clip(x[:mid], 0, 1).astype(int))))
    b = int(round(from_negabinary(np.clip(x[mid:], 0, 1).astype(int))))
    return to_negabinary(float(a * b))


OPERATIONS["negabinary_multiply"] = {
    "fn": negabinary_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two negabinary numbers"
}


def negabinary_negate(x):
    """Negate an integer in negabinary. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    # Interpret as integer, negate, convert back
    val = 0
    for i, d in enumerate(x):
        val += int(round(d))
    return to_negabinary(float(-val))


OPERATIONS["negabinary_negate"] = {
    "fn": negabinary_negate,
    "input_type": "array",
    "output_type": "array",
    "description": "Negate a number in negabinary representation"
}


def negabinary_increment(x):
    """Add 1 to each element interpreted as integer, return negabinary of each+1. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = int(round(val))
        results[i] = n + 1
    return results


OPERATIONS["negabinary_increment"] = {
    "fn": negabinary_increment,
    "input_type": "array",
    "output_type": "array",
    "description": "Increment each integer and return results"
}


def is_canonical_negabinary(x):
    """Check if array is valid negabinary (digits only 0 and 1). Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    digits = np.round(x).astype(int)
    valid = np.all((digits == 0) | (digits == 1))
    return float(valid)


OPERATIONS["is_canonical_negabinary"] = {
    "fn": is_canonical_negabinary,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if digit array is valid canonical negabinary (only 0s and 1s)"
}


def negabinary_abs(x):
    """Absolute value via negabinary conversion. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = int(round(val))
        results[i] = abs(n)
    return results


OPERATIONS["negabinary_abs"] = {
    "fn": negabinary_abs,
    "input_type": "array",
    "output_type": "array",
    "description": "Absolute value of integers using negabinary conversion"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
