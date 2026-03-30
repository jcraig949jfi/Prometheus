"""
Bijective Bases -- Base k with digits {1,...,k}. No zero. Every positive integer has exactly one representation.

Connects to: [factoradic, mixed_radix, balanced_ternary, non_integer_bases]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "bijective_bases"
OPERATIONS = {}


def to_bijective_base(x):
    """Convert positive integer to bijective base-k. Input: array [value, base]. Output: array."""
    x = np.asarray(x, dtype=float)
    n = max(1, int(round(abs(x[0]))))
    k = max(1, int(round(x[1]))) if len(x) > 1 else 2
    digits = []
    while n > 0:
        n -= 1  # Shift to 0-indexed
        digits.append((n % k) + 1)
        n //= k
    return np.array(digits[::-1], dtype=float)


OPERATIONS["to_bijective_base"] = {
    "fn": to_bijective_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert positive integer to bijective base-k (digits 1..k)"
}


def from_bijective_base(x):
    """Convert bijective base-k digits to integer. Input: array [d1, d2, ..., base]. Output: scalar."""
    x = np.asarray(x, dtype=float)
    k = max(1, int(round(x[-1]))) if len(x) > 1 else 2
    digits = x[:-1] if len(x) > 1 else x
    result = 0
    for d in digits:
        result = result * k + int(round(d))
    return float(result)


OPERATIONS["from_bijective_base"] = {
    "fn": from_bijective_base,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert bijective base-k digits back to integer"
}


def bijective_add(x):
    """Add two bijective base-k numbers. Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    k = 2  # default base
    a_val = 0
    for d in x[:mid]:
        a_val = a_val * k + int(round(d))
    b_val = 0
    for d in x[mid:]:
        b_val = b_val * k + int(round(d))
    total = max(1, a_val + b_val)
    return to_bijective_base(np.array([float(total), float(k)]))


OPERATIONS["bijective_add"] = {
    "fn": bijective_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two bijective base-k numbers"
}


def bijective_successor(x):
    """Compute successor in bijective base-k. Input: array [value, base]. Output: array."""
    x = np.asarray(x, dtype=float)
    n = max(1, int(round(abs(x[0]))))
    k = max(1, int(round(x[1]))) if len(x) > 1 else 2
    return to_bijective_base(np.array([float(n + 1), float(k)]))


OPERATIONS["bijective_successor"] = {
    "fn": bijective_successor,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute bijective base-k successor"
}


def excel_column_name(x):
    """Convert column number to Excel name (bijective base-26: A=1,...,Z=26). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = []
    for val in x:
        n = max(1, int(round(abs(val))))
        name = []
        while n > 0:
            n -= 1
            name.append(float(n % 26 + 1))  # 1=A, 26=Z
            n //= 26
        results.extend(name[::-1])
    return np.array(results, dtype=float)


OPERATIONS["excel_column_name"] = {
    "fn": excel_column_name,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert column number to Excel-style name (bijective base-26)"
}


def excel_column_to_number(x):
    """Convert Excel column digits (1=A..26=Z) to number. Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    result = 0
    for d in x:
        result = result * 26 + int(round(d))
    return float(result)


OPERATIONS["excel_column_to_number"] = {
    "fn": excel_column_to_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert Excel column digits back to column number"
}


def bijective_multiply(x):
    """Multiply two bijective base-k numbers. Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    k = 2
    a_val = 0
    for d in x[:mid]:
        a_val = a_val * k + int(round(d))
    b_val = 0
    for d in x[mid:]:
        b_val = b_val * k + int(round(d))
    product = max(1, a_val * b_val)
    return to_bijective_base(np.array([float(product), float(k)]))


OPERATIONS["bijective_multiply"] = {
    "fn": bijective_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two bijective base-k numbers"
}


def string_integer_bijection(x):
    """Bijection between positive integers and finite strings over k symbols. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = max(1, int(round(abs(x[0]))))
    k = max(2, int(round(x[1]))) if len(x) > 1 else 26
    # Bijective base-k gives the string representation
    digits = to_bijective_base(np.array([float(n), float(k)]))
    # Return [length, digit1, digit2, ...]
    return np.concatenate([[float(len(digits))], digits])


OPERATIONS["string_integer_bijection"] = {
    "fn": string_integer_bijection,
    "input_type": "array",
    "output_type": "array",
    "description": "Bijection between positive integers and strings over k-symbol alphabet"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
