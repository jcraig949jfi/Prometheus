"""
Finite Fields — arithmetic in GF(p^n), polynomial multiplication, discrete log

Connects to: [number_theory, abstract_algebra, coding_theory, cryptography]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "finite_fields"
OPERATIONS = {}


def _mod(val, p):
    """Ensure value is in range [0, p)."""
    return int(val) % p


def gf_add(x, p=7):
    """Add elements pairwise in GF(p). Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=int) % p
    result = 0
    for v in arr:
        result = (result + int(v)) % p
    return int(result)


OPERATIONS["gf_add"] = {
    "fn": gf_add,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Sum of array elements in GF(p), default p=7"
}


def gf_multiply(x, p=7):
    """Multiply elements pairwise in GF(p). Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=int) % p
    result = 1
    for v in arr:
        result = (result * int(v)) % p
    return int(result)


OPERATIONS["gf_multiply"] = {
    "fn": gf_multiply,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Product of array elements in GF(p), default p=7"
}


def gf_inverse(x, p=7):
    """Multiplicative inverse of each element in GF(p) using Fermat's little theorem.
    Input: array. Output: array."""
    arr = np.asarray(x, dtype=int) % p
    result = []
    for v in arr:
        v = int(v)
        if v == 0:
            result.append(0)  # 0 has no inverse; return 0 as sentinel
        else:
            # a^{-1} = a^{p-2} mod p by Fermat's little theorem
            result.append(pow(v, p - 2, p))
    return np.array(result, dtype=int)


OPERATIONS["gf_inverse"] = {
    "fn": gf_inverse,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiplicative inverse of each element in GF(p) via Fermat's little theorem"
}


def gf_power(x, exp=3, p=7):
    """Raise each element to a power in GF(p). Input: array. Output: array."""
    arr = np.asarray(x, dtype=int) % p
    return np.array([pow(int(v), exp, p) for v in arr], dtype=int)


OPERATIONS["gf_power"] = {
    "fn": gf_power,
    "input_type": "array",
    "output_type": "array",
    "description": "Each element raised to power exp in GF(p)"
}


def gf_polynomial_multiply(x, p=7):
    """Multiply two polynomials over GF(p). Input: array (coefficients of two
    polynomials concatenated, split at midpoint). Output: polynomial (array of coefficients)."""
    arr = np.asarray(x, dtype=int) % p
    mid = len(arr) // 2
    poly_a = arr[:mid]
    poly_b = arr[mid:]
    # Convolution gives polynomial multiplication
    result = np.convolve(poly_a, poly_b) % p
    return result.astype(int)


OPERATIONS["gf_polynomial_multiply"] = {
    "fn": gf_polynomial_multiply,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "Polynomial multiplication over GF(p), input split at midpoint"
}


def gf_minimal_polynomial(x, p=7):
    """Compute the minimal polynomial of the first element a in GF(p).
    For GF(p), minimal polynomial of a is (x - a) mod p, returned as coefficients [1, -a mod p].
    Input: array. Output: polynomial."""
    a = int(np.asarray(x, dtype=int).flat[0]) % p
    # Minimal polynomial of a in GF(p) is (x - a)
    return np.array([1, (-a) % p], dtype=int)


OPERATIONS["gf_minimal_polynomial"] = {
    "fn": gf_minimal_polynomial,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "Minimal polynomial of first element in GF(p): (x - a) mod p"
}


def gf_order_element(x, p=7):
    """Multiplicative order of each nonzero element in GF(p).
    Input: array. Output: array."""
    arr = np.asarray(x, dtype=int) % p
    orders = []
    for v in arr:
        v = int(v)
        if v == 0:
            orders.append(0)
        else:
            power = 1
            curr = v
            while curr != 1:
                curr = (curr * v) % p
                power += 1
                if power > p:
                    break
            orders.append(power)
    return np.array(orders, dtype=int)


OPERATIONS["gf_order_element"] = {
    "fn": gf_order_element,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiplicative order of each element in GF(p)"
}


def gf_primitive_element(x, p=7):
    """Find the smallest primitive element (generator) of GF(p)*.
    Input: array (ignored, uses p). Output: scalar."""
    # A primitive element has order p-1
    for g in range(2, p):
        seen = set()
        val = 1
        for _ in range(p - 1):
            val = (val * g) % p
            seen.add(val)
        if len(seen) == p - 1:
            return int(g)
    return int(1)


OPERATIONS["gf_primitive_element"] = {
    "fn": gf_primitive_element,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Smallest primitive element (generator) of GF(p)*"
}


def gf_discrete_log_brute(x, p=7):
    """Discrete log: find k such that g^k = a mod p, where g is the smallest
    primitive element and a is the first element of x.
    Input: array. Output: scalar."""
    a = int(np.asarray(x, dtype=int).flat[0]) % p
    if a == 0:
        return -1  # no discrete log for 0
    g = gf_primitive_element(x, p)
    val = 1
    for k in range(1, p):
        val = (val * g) % p
        if val == a:
            return int(k)
    return -1


OPERATIONS["gf_discrete_log_brute"] = {
    "fn": gf_discrete_log_brute,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Brute-force discrete logarithm in GF(p)"
}


def gf_frobenius_endomorphism(x, p=7):
    """Apply the Frobenius endomorphism x -> x^p to each element in GF(p).
    In GF(p) this is the identity, but we compute it explicitly.
    Input: array. Output: array."""
    arr = np.asarray(x, dtype=int) % p
    return np.array([pow(int(v), p, p) for v in arr], dtype=int)


OPERATIONS["gf_frobenius_endomorphism"] = {
    "fn": gf_frobenius_endomorphism,
    "input_type": "array",
    "output_type": "array",
    "description": "Frobenius endomorphism x -> x^p in GF(p) (identity on GF(p))"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
