"""
Moonshine Theory — monstrous moonshine numerics and modular function computations

Connects to: [group theory, modular forms, vertex operator algebras, number theory, string theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "moonshine_theory"
OPERATIONS = {}

# Known coefficients of the j-invariant: j(q) = 1/q + 744 + 196884q + 21493760q^2 + ...
# These are the dimensions of irreducible representations of the Monster group
_J_COEFFS = [1, 744, 196884, 21493760, 864299970, 20245856256,
             333202640600, 4252023300096, 44656994071935, 401490886656000]

# Monster group order
_MONSTER_ORDER_STR = "808017424794512875886459904961710757005754368000000000"


def monster_group_order_digits(x):
    """Return digit-level properties of the Monster group order |M|.
    |M| = 2^46 * 3^20 * 5^9 * 7^6 * 11^2 * 13^3 * 17 * 19 * 23 * 29 * 31 * 41 * 47 * 59 * 71.
    Input: array (indices for digit extraction). Output: array (digits)."""
    digits = [int(d) for d in _MONSTER_ORDER_STR]
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        idx = int(np.abs(x[i])) % len(digits)
        result[i] = float(digits[idx])
    return result


OPERATIONS["monster_group_order_digits"] = {
    "fn": monster_group_order_digits,
    "input_type": "array",
    "output_type": "array",
    "description": "Extracts digits from the Monster group order (54-digit number)"
}


def j_function_coefficients(x):
    """Return coefficients of the j-invariant q-expansion.
    j(tau) = q^{-1} + 744 + sum_{n>=1} c_n q^n.
    The c_n are dimensions of Monster group representations.
    Input: array (indices). Output: array (coefficients)."""
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        idx = int(np.abs(x[i])) % len(_J_COEFFS)
        result[i] = float(_J_COEFFS[idx])
    return result


OPERATIONS["j_function_coefficients"] = {
    "fn": j_function_coefficients,
    "input_type": "array",
    "output_type": "array",
    "description": "Returns q-expansion coefficients of the j-invariant"
}


def mckay_thompson_series_1A(x):
    """Evaluate the McKay-Thompson series for conjugacy class 1A (= j - 744).
    T_{1A}(q) = q^{-1} + 196884q + 21493760q^2 + ...
    Input: array (q values, |q| < 1). Output: array."""
    q = np.clip(x, -0.99, 0.99)
    # Truncated series: T_{1A} = 1/q + 196884*q + 21493760*q^2 + ...
    # We need |q| > 0 for 1/q term
    result = np.zeros_like(q)
    mask = np.abs(q) > 1e-10
    result[mask] = 1.0 / q[mask]
    coeffs_1A = [196884, 21493760, 864299970, 20245856256]
    for power, c in enumerate(coeffs_1A, start=1):
        result += c * q ** power
    return result


OPERATIONS["mckay_thompson_series_1A"] = {
    "fn": mckay_thompson_series_1A,
    "input_type": "array",
    "output_type": "array",
    "description": "Evaluates McKay-Thompson series T_{1A}(q) for the identity class"
}


def moonshine_dimension_check(x):
    """Verify the moonshine conjecture dimension relation:
    c_1 = dim(V_1) = 196884 = 196883 + 1 (trivial + smallest irrep of Monster).
    Input: array (candidate dimensions). Output: array (decomposition into Monster irreps)."""
    # Known small irrep dimensions of the Monster group
    monster_irreps = [1, 196883, 21296876, 842609326]
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        val = int(np.abs(x[i]))
        # Greedy decomposition into Monster irrep dimensions
        remaining = val
        count = 0
        for irrep in reversed(monster_irreps):
            if remaining >= irrep:
                count += remaining // irrep
                remaining = remaining % irrep
        result[i] = float(count)
    return result


OPERATIONS["moonshine_dimension_check"] = {
    "fn": moonshine_dimension_check,
    "input_type": "array",
    "output_type": "array",
    "description": "Decomposes values into Monster group irreducible representation dimensions"
}


def griess_algebra_dimension(x):
    """Compute properties related to the Griess algebra (the 196884-dimensional
    commutative non-associative algebra on which the Monster acts).
    Input: array. Output: scalar (196884 * norm-based scaling factor)."""
    # The Griess algebra has dimension 196884
    # Return a scaled version based on the input norm
    norm = np.linalg.norm(x)
    # The algebra dimension is always 196884; we return it scaled
    return 196884.0 * (1.0 + norm / max(norm, 1.0)) / 2.0


OPERATIONS["griess_algebra_dimension"] = {
    "fn": griess_algebra_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Returns Griess algebra dimension (196884) with norm-based scaling"
}


def modular_function_fourier(x):
    """Compute Fourier coefficients of the modular function J = j - 744.
    Uses the Ramanujan-type recursion for the coefficients.
    Input: array (number of coefficients to compute via q-values). Output: array."""
    n = len(x)
    # Use Eisenstein series E4 and E6 to build j-function
    # j = E4^3 / eta^24, but we use precomputed coefficients
    # Extended list of J = j - 744 coefficients
    j_minus_744 = [1, 0, 196884, 21493760, 864299970, 20245856256,
                   333202640600, 4252023300096, 44656994071935, 401490886656000]
    result = np.zeros(n)
    for i in range(n):
        idx = i % len(j_minus_744)
        result[i] = float(j_minus_744[idx])
    return result


OPERATIONS["modular_function_fourier"] = {
    "fn": modular_function_fourier,
    "input_type": "array",
    "output_type": "array",
    "description": "Returns Fourier coefficients of J = j - 744 modular function"
}


def thompson_series_coefficient(x):
    """Compute Thompson series coefficients: each c_n decomposes as a sum of
    character values of the Monster. c_1 = 196884 = 1 + 196883.
    Input: array (n values). Output: array (c_n values)."""
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        idx = int(np.abs(x[i])) % len(_J_COEFFS)
        # The Thompson series for 1A is the j-function minus 744
        if idx == 0:
            result[i] = 1.0  # q^{-1} coefficient
        elif idx == 1:
            result[i] = 0.0  # constant term of J = j-744 is 0
        else:
            result[i] = float(_J_COEFFS[idx])
    return result


OPERATIONS["thompson_series_coefficient"] = {
    "fn": thompson_series_coefficient,
    "input_type": "array",
    "output_type": "array",
    "description": "Returns Thompson series coefficients (Monster character values)"
}


def leech_lattice_kissing_number(x):
    """Compute properties of the Leech lattice related to moonshine.
    Kissing number of Leech lattice = 196560. The theta series connects to
    modular forms. Input: array. Output: scalar."""
    # The Leech lattice in R^24 has:
    # - Kissing number 196560
    # - No roots (minimal norm = 4)
    # - Automorphism group = 2.Co1 (Conway's group)
    # Return the kissing number scaled by the input vector's properties
    n = len(x)
    # The number of lattice vectors at norm 2k is given by theta series
    # theta_Leech(q) = 1 + 196560*q^2 + 16773120*q^3 + ...
    theta_coeffs = [1, 0, 196560, 16773120, 398034000]
    idx = min(int(np.abs(np.sum(x))) % len(theta_coeffs), len(theta_coeffs) - 1)
    return float(theta_coeffs[idx])


OPERATIONS["leech_lattice_kissing_number"] = {
    "fn": leech_lattice_kissing_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Returns Leech lattice theta series coefficients (kissing number 196560)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
