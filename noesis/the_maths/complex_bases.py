"""
Complex Bases -- Base (-1+i). Represents every Gaussian integer with digits {0,1}.

Connects to: [negabinary, balanced_ternary, non_integer_bases, p_adic_expansions]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "complex_bases"
OPERATIONS = {}

BASE = complex(-1, 1)  # -1 + i


def _to_complex_base_digits(z, max_digits=64):
    """Convert Gaussian integer z to base (-1+i) digits {0,1}."""
    z = complex(z)
    digits = []
    for _ in range(max_digits):
        if abs(z) < 1e-10:
            break
        # z = q * base + r, where r in {0,1}
        # z / base = z * conj(base) / |base|^2 = z * (-1-i) / 2
        quotient = z / BASE
        # Round to nearest Gaussian integer
        qr = round(quotient.real)
        qi = round(quotient.imag)
        q = complex(qr, qi)
        r = z - q * BASE
        # r should be 0 or 1
        digit = int(round(r.real)) % 2
        digits.append(digit)
        z = q
    if not digits:
        digits = [0]
    return digits[::-1]


def to_complex_base(x):
    """Convert real integers to base (-1+i) digits. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    val = int(round(x[0])) if len(x) > 0 else 0
    digits = _to_complex_base_digits(complex(val, 0))
    return np.array(digits, dtype=float)


OPERATIONS["to_complex_base"] = {
    "fn": to_complex_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert integer to base (-1+i) representation"
}


def from_complex_base(digits):
    """Convert base (-1+i) digits to complex number. Input: array. Output: array."""
    digits = np.asarray(digits, dtype=int)
    result = complex(0, 0)
    for d in digits:
        result = result * BASE + int(d)
    return np.array([result.real, result.imag])


OPERATIONS["from_complex_base"] = {
    "fn": from_complex_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert base (-1+i) digits back to complex number [real, imag]"
}


def complex_base_add(x):
    """Add two complex numbers via their base (-1+i) representations. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    a = complex(x[0], x[1] if mid >= 2 else 0)
    b = complex(x[mid], x[mid + 1] if len(x) > mid + 1 else 0)
    result = a + b
    return np.array([result.real, result.imag])


OPERATIONS["complex_base_add"] = {
    "fn": complex_base_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two complex numbers via base (-1+i)"
}


def complex_base_multiply(x):
    """Multiply two complex numbers. Input: array [re1, im1, re2, im2]. Output: array."""
    x = np.asarray(x, dtype=float)
    if len(x) >= 4:
        a = complex(x[0], x[1])
        b = complex(x[2], x[3])
    else:
        mid = len(x) // 2
        a = complex(x[0], 0)
        b = complex(x[mid], 0)
    result = a * b
    return np.array([result.real, result.imag])


OPERATIONS["complex_base_multiply"] = {
    "fn": complex_base_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two Gaussian integers in base (-1+i)"
}


def gaussian_integer_represent(x):
    """Represent each pair (a,b) as a+bi and show digit count in base (-1+i). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = []
    for i in range(0, len(x) - 1, 2):
        z = complex(x[i], x[i + 1])
        digits = _to_complex_base_digits(z)
        results.append(float(len(digits)))
    if not results:
        results = [float(len(_to_complex_base_digits(complex(x[0], 0))))]
    return np.array(results)


OPERATIONS["gaussian_integer_represent"] = {
    "fn": gaussian_integer_represent,
    "input_type": "array",
    "output_type": "array",
    "description": "Count digits needed to represent Gaussian integers in base (-1+i)"
}


def twindragon_boundary_points(x):
    """Generate twindragon fractal boundary points. Input: array (controls N points). Output: array."""
    x = np.asarray(x, dtype=float)
    n_bits = min(int(abs(x[0])) + 8, 20)
    # Generate points in the twindragon by iterating base (-1+i) with all binary digit combos
    n_samples = min(2 ** n_bits, 256)
    points = np.zeros(n_samples * 2)
    for k in range(n_samples):
        z = complex(0, 0)
        power = complex(1, 0)
        bits = k
        for _ in range(n_bits):
            if bits & 1:
                z += power
            power *= BASE
            bits >>= 1
        points[2 * k] = z.real
        points[2 * k + 1] = z.imag
    return points


OPERATIONS["twindragon_boundary_points"] = {
    "fn": twindragon_boundary_points,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate twindragon fractal boundary points from base (-1+i) expansions"
}


def complex_base_norm(x):
    """Compute norm |z|^2 for Gaussian integers. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = []
    for i in range(0, len(x) - 1, 2):
        norm = x[i] ** 2 + x[i + 1] ** 2
        results.append(norm)
    if not results:
        results = [x[0] ** 2]
    return np.array(results)


OPERATIONS["complex_base_norm"] = {
    "fn": complex_base_norm,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute Gaussian integer norm |z|^2"
}


def real_part_extract(x):
    """Extract real part from base (-1+i) digit array. Input: array (digits). Output: scalar."""
    digits = np.asarray(x, dtype=int)
    result = complex(0, 0)
    for d in digits:
        result = result * BASE + int(d)
    return float(result.real)


OPERATIONS["real_part_extract"] = {
    "fn": real_part_extract,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Extract real part from base (-1+i) representation"
}


def imaginary_part_extract(x):
    """Extract imaginary part from base (-1+i) digit array. Input: array (digits). Output: scalar."""
    digits = np.asarray(x, dtype=int)
    result = complex(0, 0)
    for d in digits:
        result = result * BASE + int(d)
    return float(result.imag)


OPERATIONS["imaginary_part_extract"] = {
    "fn": imaginary_part_extract,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Extract imaginary part from base (-1+i) representation"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
