"""
Lattice Theory — meet, join, Moebius function, lattice reduction

Connects to: [number_theory, algebra, combinatorics, geometry_of_numbers]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "lattice_theory"
OPERATIONS = {}


def lattice_meet(x):
    """Compute the meet (greatest lower bound) of integer array elements
    using GCD as the meet operation on the divisibility lattice.
    Input: array. Output: scalar."""
    result = int(abs(x[0]))
    for val in x[1:]:
        result = int(np.gcd(result, int(abs(val))))
    return float(result)


OPERATIONS["lattice_meet"] = {
    "fn": lattice_meet,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Meet (GCD) on the divisibility lattice"
}


def lattice_join(x):
    """Compute the join (least upper bound) of integer array elements
    using LCM as the join operation on the divisibility lattice.
    Input: array. Output: scalar."""
    result = int(abs(x[0]))
    for val in x[1:]:
        v = int(abs(val))
        result = result * v // int(np.gcd(result, v)) if v != 0 else 0
    return float(result)


OPERATIONS["lattice_join"] = {
    "fn": lattice_join,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Join (LCM) on the divisibility lattice"
}


def mobius_function_lattice(x):
    """Compute the classical Moebius function mu(n) for each integer in x.
    mu(n) = 0 if n has squared prime factor, (-1)^k if n is product of k distinct primes.
    Input: array. Output: array."""
    results = []
    for val in x:
        n = int(abs(val))
        if n <= 0:
            results.append(0.0)
            continue
        if n == 1:
            results.append(1.0)
            continue
        # Factor and check for squares
        num_factors = 0
        temp = n
        has_square = False
        for p in range(2, int(np.sqrt(temp)) + 2):
            if temp % p == 0:
                num_factors += 1
                temp //= p
                if temp % p == 0:
                    has_square = True
                    break
        if has_square:
            results.append(0.0)
        else:
            if temp > 1:
                num_factors += 1
            results.append(float((-1) ** num_factors))
    return np.array(results)


OPERATIONS["mobius_function_lattice"] = {
    "fn": mobius_function_lattice,
    "input_type": "array",
    "output_type": "array",
    "description": "Classical Moebius function mu(n) for each element"
}


def lattice_dimension(x):
    """Estimate the dimension of a lattice from a basis matrix.
    Interprets x as a flattened square matrix and returns its rank.
    Input: array. Output: scalar."""
    n = int(np.sqrt(len(x)))
    if n * n != len(x):
        n = int(np.ceil(np.sqrt(len(x))))
    mat = np.zeros((n, n))
    mat.flat[:len(x)] = x[:n*n]
    return float(np.linalg.matrix_rank(mat))


OPERATIONS["lattice_dimension"] = {
    "fn": lattice_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rank/dimension of lattice from flattened basis matrix"
}


def lll_reduce_2d(x):
    """LLL lattice basis reduction for a 2D lattice.
    Input: array of length 4 [b1x, b1y, b2x, b2y]. Output: array of length 4.
    Uses the Lagrange/Gauss algorithm for 2D reduction (equivalent to LLL in 2D)."""
    if len(x) < 4:
        padded = np.zeros(4)
        padded[:len(x)] = x[:len(x)]
        x = padded
    b1 = np.array([x[0], x[1]], dtype=float)
    b2 = np.array([x[2], x[3]], dtype=float)
    # Ensure b1 is shorter
    if np.dot(b1, b1) > np.dot(b2, b2):
        b1, b2 = b2, b1
    for _ in range(100):
        mu = np.dot(b2, b1) / np.dot(b1, b1) if np.dot(b1, b1) > 1e-15 else 0
        b2 = b2 - np.round(mu) * b1
        if np.dot(b1, b1) <= np.dot(b2, b2):
            break
        b1, b2 = b2, b1
    return np.array([b1[0], b1[1], b2[0], b2[1]])


OPERATIONS["lll_reduce_2d"] = {
    "fn": lll_reduce_2d,
    "input_type": "array",
    "output_type": "array",
    "description": "2D lattice basis reduction (Lagrange/Gauss algorithm)"
}


def lattice_determinant(x):
    """Compute determinant of lattice from flattened basis matrix.
    The absolute value of the determinant gives the fundamental domain volume.
    Input: array. Output: scalar."""
    n = int(np.round(np.sqrt(len(x))))
    if n * n > len(x):
        n = int(np.sqrt(len(x)))
    mat = np.zeros((n, n))
    mat.flat[:min(len(x), n*n)] = x[:n*n]
    return float(abs(np.linalg.det(mat)))


OPERATIONS["lattice_determinant"] = {
    "fn": lattice_determinant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Absolute determinant (covolume) of lattice basis"
}


def closest_vector_approx(x):
    """Approximate closest vector problem: given target point as first half of x
    and a lattice basis vector as second half, find the nearest lattice point
    using Babai's nearest plane (rounding) method for 1D.
    Input: array. Output: array."""
    mid = len(x) // 2
    target = x[:mid]
    basis_vec = x[mid:2*mid] if mid <= len(x) // 2 else x[mid:]
    if len(basis_vec) == 0:
        return target.copy()
    # Babai rounding: project target onto basis and round coefficients
    norm_sq = np.dot(basis_vec, basis_vec)
    if norm_sq < 1e-15:
        return target.copy()
    coeff = np.round(np.dot(target, basis_vec) / norm_sq)
    return basis_vec * coeff


OPERATIONS["closest_vector_approx"] = {
    "fn": closest_vector_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Babai rounding approximation to closest lattice vector"
}


def lattice_theta_series(x):
    """Compute first few terms of the theta series of the integer lattice Z,
    theta(q) = sum_{n=-N}^{N} q^{n^2}, evaluated at q = x[i] for each element.
    Input: array (values of q). Output: array (theta series values)."""
    N = 20  # sum from -N to N
    ns = np.arange(-N, N + 1)
    results = []
    for q in x:
        if abs(q) >= 1.0:
            # Series diverges, return partial sum capped
            results.append(float(2 * N + 1))
        else:
            val = np.sum(q ** (ns ** 2))
            results.append(float(val))
    return np.array(results)


OPERATIONS["lattice_theta_series"] = {
    "fn": lattice_theta_series,
    "input_type": "array",
    "output_type": "array",
    "description": "Theta series of Z lattice evaluated at given q values"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
