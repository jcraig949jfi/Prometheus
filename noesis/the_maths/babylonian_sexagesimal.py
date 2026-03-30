"""
Babylonian Sexagesimal — Base-60 positional arithmetic

Connects to: [plimpton322_triples, egyptian_fractions, mayan_vigesimal]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "babylonian_sexagesimal"
OPERATIONS = {}


def to_sexagesimal(x):
    """Convert decimal number to sexagesimal digits. Input: scalar. Output: array."""
    val = float(np.asarray(x).flat[0])
    negative = val < 0
    val = abs(val)
    integer_part = int(val)
    frac_part = val - integer_part
    digits = []
    if integer_part == 0:
        digits = [0]
    else:
        while integer_part > 0:
            digits.append(integer_part % 60)
            integer_part //= 60
        digits.reverse()
    # Add up to 3 fractional sexagesimal places
    for _ in range(3):
        frac_part *= 60
        digits.append(int(frac_part))
        frac_part -= int(frac_part)
    result = np.array(digits, dtype=np.float64)
    if negative:
        result[0] = -result[0]
    return result


OPERATIONS["to_sexagesimal"] = {
    "fn": to_sexagesimal,
    "input_type": "scalar",
    "output_type": "array",
    "description": "Convert decimal number to base-60 digit array"
}


def from_sexagesimal(x):
    """Convert sexagesimal digit array to decimal. Input: array. Output: scalar."""
    digits = np.asarray(x, dtype=np.float64)
    # Treat as integer sexagesimal places
    result = 0.0
    for d in digits:
        result = result * 60.0 + d
    return result


OPERATIONS["from_sexagesimal"] = {
    "fn": from_sexagesimal,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert base-60 digit array to decimal number"
}


def sexagesimal_add(x):
    """Add two sexagesimal numbers encoded in first/second half of array. Input: array. Output: array."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x) // 2
    a = x[:n]
    b = x[n:2*n]
    # Convert both to decimal, add, convert back
    val_a = from_sexagesimal(a)
    val_b = from_sexagesimal(b)
    return to_sexagesimal(val_a + val_b)


OPERATIONS["sexagesimal_add"] = {
    "fn": sexagesimal_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two base-60 numbers (array split in half)"
}


def sexagesimal_multiply(x):
    """Multiply two sexagesimal numbers encoded in first/second half of array. Input: array. Output: array."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x) // 2
    a = x[:n]
    b = x[n:2*n]
    val_a = from_sexagesimal(a)
    val_b = from_sexagesimal(b)
    return to_sexagesimal(val_a * val_b)


OPERATIONS["sexagesimal_multiply"] = {
    "fn": sexagesimal_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two base-60 numbers (array split in half)"
}


def reciprocal_table_entry(x):
    """Babylonian reciprocal table: for regular n, give 1/n in sexagesimal. Input: scalar. Output: array."""
    val = int(np.asarray(x).flat[0])
    if val <= 0:
        return np.array([0.0])
    recip = 1.0 / val
    return to_sexagesimal(recip)


OPERATIONS["reciprocal_table_entry"] = {
    "fn": reciprocal_table_entry,
    "input_type": "scalar",
    "output_type": "array",
    "description": "Compute reciprocal of n in sexagesimal (Babylonian table)"
}


def is_regular_number(x):
    """Check if each element is a regular number (2^a * 3^b * 5^c). Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.int64).flatten()
    results = []
    for val in arr:
        n = abs(int(val))
        if n == 0:
            results.append(0.0)
            continue
        for p in [2, 3, 5]:
            while n % p == 0:
                n //= p
        results.append(1.0 if n == 1 else 0.0)
    return np.array(results)


OPERATIONS["is_regular_number"] = {
    "fn": is_regular_number,
    "input_type": "array",
    "output_type": "array",
    "description": "Check if numbers are regular (only factors 2, 3, 5)"
}


def geometric_mean_babylonian(x):
    """Geometric mean via Babylonian method: sqrt(a*b) iteratively. Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=np.float64)
    arr = arr[arr > 0]
    if len(arr) == 0:
        return 0.0
    # Geometric mean = exp(mean(log(arr)))
    return float(np.exp(np.mean(np.log(arr))))


OPERATIONS["geometric_mean_babylonian"] = {
    "fn": geometric_mean_babylonian,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Compute geometric mean (Babylonian averaging method)"
}


def quadratic_solve_geometric(x):
    """Solve x^2 + bx = c using Babylonian geometric cut-and-paste. Input: array [b, c]. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    b = arr[0] if len(arr) > 0 else 1.0
    c = arr[1] if len(arr) > 1 else 1.0
    # x^2 + bx = c => x = -b/2 + sqrt((b/2)^2 + c)
    half_b = b / 2.0
    discriminant = half_b ** 2 + c
    if discriminant < 0:
        return np.array([np.nan])
    root = np.sqrt(discriminant)
    x1 = -half_b + root
    x2 = -half_b - root
    return np.array([x1, x2])


OPERATIONS["quadratic_solve_geometric"] = {
    "fn": quadratic_solve_geometric,
    "input_type": "array",
    "output_type": "array",
    "description": "Solve x^2+bx=c by Babylonian geometric (cut-and-paste) method"
}


def sexagesimal_reciprocal(x):
    """Compute reciprocal using sexagesimal long division for regular numbers. Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for val in arr:
        if val == 0:
            results.append(np.inf)
        else:
            results.append(1.0 / val)
    return np.array(results)


OPERATIONS["sexagesimal_reciprocal"] = {
    "fn": sexagesimal_reciprocal,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute elementwise reciprocals (sexagesimal division)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
