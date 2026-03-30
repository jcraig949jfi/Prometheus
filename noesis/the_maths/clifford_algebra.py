"""
Clifford Algebra — Cl(p,q) construction, spinors, pin groups

Connects to: [geometric_algebra, linear_algebra, differential_geometry, topology, representation_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

Representation: Multivectors in Cl(p,q) are stored as arrays of length 2^n
where n = p + q. Basis blades are indexed in binary: index k corresponds to
the blade formed by generators whose bits are set in k.
E.g., for n=3: index 0=scalar, 1=e1, 2=e2, 3=e12, 4=e3, 5=e13, 6=e23, 7=e123.
"""

import numpy as np

FIELD_NAME = "clifford_algebra"
OPERATIONS = {}

# Default signature: Cl(3,0) — Euclidean 3-space
_DEFAULT_P = 3
_DEFAULT_Q = 0
_DEFAULT_N = _DEFAULT_P + _DEFAULT_Q
_DEFAULT_DIM = 2 ** _DEFAULT_N


def _metric_sign(i, p=_DEFAULT_P, q=_DEFAULT_Q):
    """Metric signature: generator e_i squares to +1 for i<p, -1 for p<=i<p+q."""
    if i < p:
        return 1
    else:
        return -1


def _blade_product(a_idx, b_idx, p=_DEFAULT_P, q=_DEFAULT_Q):
    """Compute the product of two basis blades.
    Returns (sign, result_index)."""
    n = p + q
    sign = 1
    result = a_idx

    for i in range(n):
        if not (b_idx & (1 << i)):
            continue
        # We need to move generator e_i past all generators in result that are > i
        # Count swaps needed
        swaps = 0
        for j in range(i + 1, n):
            if result & (1 << j):
                swaps += 1
        if swaps % 2 == 1:
            sign *= -1

        if result & (1 << i):
            # e_i * e_i = metric sign
            sign *= _metric_sign(i, p, q)
            result ^= (1 << i)  # Remove e_i
        else:
            result ^= (1 << i)  # Add e_i

    return sign, result


def _full_product(a, b, p=_DEFAULT_P, q=_DEFAULT_Q):
    """Full Clifford product of two multivectors."""
    n = p + q
    dim = 2 ** n
    a_padded = np.zeros(dim)
    b_padded = np.zeros(dim)
    a_padded[:min(len(a), dim)] = a[:min(len(a), dim)]
    b_padded[:min(len(b), dim)] = b[:min(len(b), dim)]

    result = np.zeros(dim)
    for i in range(dim):
        if abs(a_padded[i]) < 1e-15:
            continue
        for j in range(dim):
            if abs(b_padded[j]) < 1e-15:
                continue
            sign, idx = _blade_product(i, j, p, q)
            result[idx] += sign * a_padded[i] * b_padded[j]
    return result


def _grade_of_blade(idx):
    """Grade (number of set bits) of a basis blade index."""
    return bin(idx).count('1')


def clifford_product(x):
    """Clifford (geometric) product of two multivectors in Cl(3,0).
    Input: array (two multivectors concatenated, each of length 8).
    Output: array (product multivector of length 8).
    Input: array. Output: array."""
    dim = _DEFAULT_DIM
    a = np.zeros(dim)
    b = np.zeros(dim)
    half = min(len(x) // 2, dim) if len(x) >= 2 else min(len(x), dim)
    a[:half] = x[:half]
    b[:min(len(x) - half, dim)] = x[half:half + dim]
    return _full_product(a, b)


OPERATIONS["clifford_product"] = {
    "fn": clifford_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Clifford (geometric) product of two multivectors in Cl(3,0)"
}


def clifford_basis_blade(x):
    """Return the basis blade multivector for index k = int(x[0]) mod 2^n.
    Input: array. Output: array."""
    dim = _DEFAULT_DIM
    k = int(x[0]) % dim
    result = np.zeros(dim)
    result[k] = 1.0
    return result


OPERATIONS["clifford_basis_blade"] = {
    "fn": clifford_basis_blade,
    "input_type": "array",
    "output_type": "array",
    "description": "Unit basis blade multivector for given index in Cl(3,0)"
}


def clifford_grade_involution(x):
    """Grade involution (main involution): reverses sign of odd-grade components.
    hat(A) = sum_k (-1)^k <A>_k.
    Input: array (multivector). Output: array."""
    dim = _DEFAULT_DIM
    mv = np.zeros(dim)
    mv[:min(len(x), dim)] = x[:min(len(x), dim)]
    result = np.zeros(dim)
    for i in range(dim):
        grade = _grade_of_blade(i)
        result[i] = mv[i] * ((-1) ** grade)
    return result


OPERATIONS["clifford_grade_involution"] = {
    "fn": clifford_grade_involution,
    "input_type": "array",
    "output_type": "array",
    "description": "Grade involution: negate odd-grade components"
}


def clifford_conjugation(x):
    """Clifford conjugation: composition of reverse and grade involution.
    bar(A) = sum_k (-1)^{k(k+1)/2} <A>_k.
    Input: array (multivector). Output: array."""
    dim = _DEFAULT_DIM
    mv = np.zeros(dim)
    mv[:min(len(x), dim)] = x[:min(len(x), dim)]
    result = np.zeros(dim)
    for i in range(dim):
        grade = _grade_of_blade(i)
        # Conjugation sign: (-1)^{k(k+1)/2}
        sign = (-1) ** (grade * (grade + 1) // 2)
        result[i] = mv[i] * sign
    return result


OPERATIONS["clifford_conjugation"] = {
    "fn": clifford_conjugation,
    "input_type": "array",
    "output_type": "array",
    "description": "Clifford conjugation: reverse composed with grade involution"
}


def clifford_norm(x):
    """Norm of a multivector: |A| = sqrt(|scalar_part(A * A_conjugate)|).
    Input: array (multivector). Output: scalar."""
    dim = _DEFAULT_DIM
    mv = np.zeros(dim)
    mv[:min(len(x), dim)] = x[:min(len(x), dim)]
    conj = clifford_conjugation(mv)
    product = _full_product(mv, conj)
    return float(np.sqrt(abs(product[0])))


OPERATIONS["clifford_norm"] = {
    "fn": clifford_norm,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Clifford norm: sqrt(|scalar(A * bar(A))|)"
}


def spin_group_element(x):
    """Construct a Spin group element from a bivector via exponentiation.
    S = exp(B) where B is a bivector. Uses the input to form a bivector.
    Input: array [b12, b13, b23] (bivector components). Output: array (multivector).
    Input: array. Output: array."""
    dim = _DEFAULT_DIM
    # Bivector in Cl(3,0): b12*e12 + b13*e13 + b23*e23
    # Indices: e12=3, e13=5, e23=6
    B = np.zeros(dim)
    if len(x) >= 1:
        B[3] = x[0]  # e12
    if len(x) >= 2:
        B[5] = x[1]  # e13
    if len(x) >= 3:
        B[6] = x[2]  # e23

    # For a bivector B in Cl(3,0), B^2 is a scalar
    B2 = _full_product(B, B)
    theta_sq = -B2[0]  # B^2 = -|B|^2 for Euclidean signature bivectors

    if theta_sq < 1e-15:
        # Small angle: exp(B) ~ 1 + B
        result = np.zeros(dim)
        result[0] = 1.0
        result += B
        return result

    theta = np.sqrt(theta_sq)
    # exp(B) = cos(theta) + sin(theta)/theta * B
    result = np.zeros(dim)
    result[0] = np.cos(theta)
    result += (np.sin(theta) / theta) * B
    return result


OPERATIONS["spin_group_element"] = {
    "fn": spin_group_element,
    "input_type": "array",
    "output_type": "array",
    "description": "Spin group element from bivector via exponential map"
}


def clifford_exponential(x):
    """Exponential of a general multivector via Taylor series (truncated).
    Input: array (multivector). Output: array (multivector).
    Input: array. Output: array."""
    dim = _DEFAULT_DIM
    mv = np.zeros(dim)
    mv[:min(len(x), dim)] = x[:min(len(x), dim)]

    # Scale down for convergence
    norm = np.max(np.abs(mv))
    if norm > 1.0:
        scale = int(np.ceil(np.log2(norm))) + 1
        mv = mv / (2 ** scale)
    else:
        scale = 0

    # Taylor series: exp(A) = sum A^k / k!
    result = np.zeros(dim)
    result[0] = 1.0  # Identity
    term = np.zeros(dim)
    term[0] = 1.0
    for k in range(1, 15):
        term = _full_product(term, mv) / k
        result += term
        if np.max(np.abs(term)) < 1e-14:
            break

    # Square back up: exp(A) = exp(A/2^s)^{2^s}
    for _ in range(scale):
        result = _full_product(result, result)

    return result


OPERATIONS["clifford_exponential"] = {
    "fn": clifford_exponential,
    "input_type": "array",
    "output_type": "array",
    "description": "Exponential of a multivector via Taylor series with scaling"
}


def clifford_commutator(x):
    """Commutator [A, B] = A*B - B*A of two multivectors.
    Input: array (two multivectors concatenated). Output: array.
    Input: array. Output: array."""
    dim = _DEFAULT_DIM
    a = np.zeros(dim)
    b = np.zeros(dim)
    half = min(len(x) // 2, dim) if len(x) >= 2 else min(len(x), dim)
    a[:half] = x[:half]
    b[:min(len(x) - half, dim)] = x[half:half + dim]
    ab = _full_product(a, b)
    ba = _full_product(b, a)
    return ab - ba


OPERATIONS["clifford_commutator"] = {
    "fn": clifford_commutator,
    "input_type": "array",
    "output_type": "array",
    "description": "Clifford commutator [A,B] = AB - BA"
}


def clifford_even_subalgebra(x):
    """Project multivector onto the even subalgebra (grades 0, 2, ...).
    Input: array (multivector). Output: array.
    Input: array. Output: array."""
    dim = _DEFAULT_DIM
    mv = np.zeros(dim)
    mv[:min(len(x), dim)] = x[:min(len(x), dim)]
    result = np.zeros(dim)
    for i in range(dim):
        if _grade_of_blade(i) % 2 == 0:
            result[i] = mv[i]
    return result


OPERATIONS["clifford_even_subalgebra"] = {
    "fn": clifford_even_subalgebra,
    "input_type": "array",
    "output_type": "array",
    "description": "Projection onto even subalgebra (spin subalgebra)"
}


def clifford_hodge_dual(x):
    """Hodge dual: A* = A * I^{-1} where I is the pseudoscalar.
    In Cl(3,0), I = e123 (index 7), I^{-1} = -e123.
    Input: array (multivector). Output: array.
    Input: array. Output: array."""
    dim = _DEFAULT_DIM
    mv = np.zeros(dim)
    mv[:min(len(x), dim)] = x[:min(len(x), dim)]
    # I^{-1} for Cl(3,0): I = e123, I^2 = e123*e123 = -1, so I^{-1} = -I
    I_inv = np.zeros(dim)
    I_inv[7] = -1.0  # -e123
    return _full_product(mv, I_inv)


OPERATIONS["clifford_hodge_dual"] = {
    "fn": clifford_hodge_dual,
    "input_type": "array",
    "output_type": "array",
    "description": "Hodge dual via right multiplication by pseudoscalar inverse"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
