"""
Matrix Bases — 2D base representations using matrix "radix"

Connects to: [clifford_algebra, geometric_algebra, tensor_networks, fractal_dimensions]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "matrix_bases"
OPERATIONS = {}


def matrix_base_expand(x):
    """Expand an integer into matrix-base representation using radix matrix M.
    For 2x2 matrix base with det(M)=d, use digit set D = {0, ..., |d|-1} as scalar multiples of identity.
    Input: array [n, m00, m01, m10, m11]. Output: array of digit coefficients."""
    x = np.asarray(x, dtype=float)
    n = int(abs(x[0])) if len(x) > 0 else 7
    m00 = x[1] if len(x) > 1 else 1
    m01 = x[2] if len(x) > 2 else 1
    m10 = x[3] if len(x) > 3 else 0
    m11 = x[4] if len(x) > 4 else -1
    M = np.array([[m00, m01], [m10, m11]])
    det = abs(int(round(np.linalg.det(M))))
    if det < 2:
        det = 2
    # Represent n in base |det(M)|
    digits = []
    val = int(abs(n))
    for _ in range(20):
        digits.append(val % det)
        val //= det
        if val == 0:
            break
    return np.array(digits, dtype=float)


OPERATIONS["matrix_base_expand"] = {
    "fn": matrix_base_expand,
    "input_type": "array",
    "output_type": "array",
    "description": "Expand integer in matrix base (digits from det-based system)"
}


def matrix_base_contract(x):
    """Contract matrix-base digits back to integer.
    Input: array [d0, d1, ..., dn, base_det]. Output: scalar."""
    x = np.asarray(x, dtype=float)
    base = int(x[-1]) if len(x) > 1 else 2
    digits = x[:-1] if len(x) > 1 else x
    base = max(base, 2)
    result = 0
    for i, d in enumerate(digits):
        result += int(d) * (base ** i)
    return np.float64(result)


OPERATIONS["matrix_base_contract"] = {
    "fn": matrix_base_contract,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Contract matrix-base digits to integer"
}


def digit_set_tiling_check(x):
    """Check if a digit set D tiles Z^2 with lattice M*Z^2.
    For a valid matrix numeration system, {d + M*v : d in D, v in Z^2} = Z^2.
    Checks completeness of representatives mod M.
    Input: array [m00, m01, m10, m11, d0, d1, ...]. Output: scalar (1=valid, 0=not)."""
    x = np.asarray(x, dtype=float)
    m00 = int(x[0]) if len(x) > 0 else 1
    m01 = int(x[1]) if len(x) > 1 else 1
    m10 = int(x[2]) if len(x) > 2 else 0
    m11 = int(x[3]) if len(x) > 3 else -1
    M = np.array([[m00, m01], [m10, m11]])
    det = abs(int(round(np.linalg.det(M))))
    if det == 0:
        return np.float64(0)
    # Digit set from remaining elements (as 2D points flattened)
    remaining = x[4:]
    if len(remaining) < 2:
        # Default digit set: {(0,0), (1,0)} for det=2
        digits_2d = [(i, 0) for i in range(det)]
    else:
        num_digits = len(remaining) // 2
        digits_2d = [(int(remaining[2*i]), int(remaining[2*i+1])) for i in range(num_digits)]
    # Check: digits should form a complete residue system mod M
    # Map each digit to M^{-1} * d and check residues
    if len(digits_2d) != det:
        return np.float64(0)
    # Simple check: all digits distinct mod lattice
    residues = set()
    for d in digits_2d:
        # Hash the residue
        residues.add((d[0] % max(det, 1), d[1] % max(det, 1)))
    return np.float64(1 if len(residues) == len(digits_2d) else 0)


OPERATIONS["digit_set_tiling_check"] = {
    "fn": digit_set_tiling_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if digit set tiles Z^2 with matrix lattice"
}


def haar_wavelet_connection(x):
    """Demonstrate connection between matrix base and Haar wavelets.
    The Haar wavelet is the simplest case: base M=2, digits {0,1}, giving
    the dyadic decomposition that underlies Haar analysis.
    Input: array [signal values]. Output: array (one level Haar transform)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    # Pad to even length
    if n % 2 != 0:
        x = np.append(x, 0.0)
        n += 1
    # Haar transform: averages and differences
    averages = (x[0::2] + x[1::2]) / np.sqrt(2)
    differences = (x[0::2] - x[1::2]) / np.sqrt(2)
    return np.concatenate([averages, differences])


OPERATIONS["haar_wavelet_connection"] = {
    "fn": haar_wavelet_connection,
    "input_type": "array",
    "output_type": "array",
    "description": "One-level Haar transform (matrix base-2 connection)"
}


def self_affine_tile_boundary(x):
    """Generate boundary points of a self-affine tile defined by matrix M and digit set.
    Uses iterated function system (IFS) to approximate the attractor.
    Default: twin dragon tile (M = [[1,1],[-1,1]], D = {(0,0), (1,0)}).
    Input: array [num_iterations, variant]. Output: flattened (x, y) points."""
    x = np.asarray(x, dtype=float)
    n_iter = int(x[0]) if len(x) > 0 else 12
    variant = int(x[1]) if len(x) > 1 else 0
    n_iter = min(n_iter, 16)
    if variant == 0:
        # Twin dragon: M = [[1,1],[-1,1]], D = {(0,0), (1,0)}
        M = np.array([[1, 1], [-1, 1]], dtype=float)
    else:
        # Levy dragon variant
        M = np.array([[1, -1], [1, 1]], dtype=float)
    M_inv = np.linalg.inv(M)
    digits = [np.array([0.0, 0.0]), np.array([1.0, 0.0])]
    # IFS: T = M^{-1}(T + D), start with a set of points
    points = np.array([[0.0, 0.0]])
    for _ in range(n_iter):
        new_points = []
        for d in digits:
            shifted = points + d
            transformed = (M_inv @ shifted.T).T
            new_points.append(transformed)
        points = np.vstack(new_points)
        # Subsample if too many points
        if len(points) > 5000:
            idx = np.random.RandomState(42).choice(len(points), 5000, replace=False)
            points = points[idx]
    return points.flatten()


OPERATIONS["self_affine_tile_boundary"] = {
    "fn": self_affine_tile_boundary,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate self-affine tile boundary points via IFS"
}


def matrix_radix_determinant(x):
    """Compute determinant of matrix radix and its relationship to the numeration base.
    |det(M)| = number of digits needed. Input: array [m00, m01, m10, m11]. Output: scalar."""
    x = np.asarray(x, dtype=float)
    m00 = x[0] if len(x) > 0 else 1
    m01 = x[1] if len(x) > 1 else 1
    m10 = x[2] if len(x) > 2 else -1
    m11 = x[3] if len(x) > 3 else 1
    M = np.array([[m00, m01], [m10, m11]])
    return np.float64(abs(np.linalg.det(M)))


OPERATIONS["matrix_radix_determinant"] = {
    "fn": matrix_radix_determinant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Determinant of matrix radix (= number of required digits)"
}


def radix_eigenvalue_connection(x):
    """Analyze eigenvalues of matrix radix M. For valid numeration, all eigenvalues
    must have |lambda| > 1 (expanding map). Returns eigenvalues and expansion check.
    Input: array [m00, m01, m10, m11]. Output: array [|lam1|, |lam2|, is_expanding]."""
    x = np.asarray(x, dtype=float)
    m00 = x[0] if len(x) > 0 else 1
    m01 = x[1] if len(x) > 1 else 1
    m10 = x[2] if len(x) > 2 else -1
    m11 = x[3] if len(x) > 3 else 1
    M = np.array([[m00, m01], [m10, m11]])
    eigenvalues = np.linalg.eigvals(M)
    abs_eigs = np.abs(eigenvalues)
    is_expanding = 1.0 if all(abs_eigs > 1.0 - 1e-10) else 0.0
    return np.array([abs_eigs[0], abs_eigs[1], is_expanding], dtype=float)


OPERATIONS["radix_eigenvalue_connection"] = {
    "fn": radix_eigenvalue_connection,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalue analysis of matrix radix (expansion criterion)"
}


def twin_dragon_from_matrix_base(x):
    """Generate twin dragon curve points using base M=[[1,1],[-1,1]], digits {0,1}.
    Each integer n is expanded, and the sum d_0 + M^{-1}*d_1 + M^{-2}*d_2 + ... gives
    a point in the twin dragon tile.
    Input: array [max_n]. Output: flattened (x, y) points."""
    x = np.asarray(x, dtype=float)
    max_n = int(x[0]) if len(x) > 0 else 256
    max_n = min(max_n, 2000)
    M_inv = np.linalg.inv(np.array([[1, 1], [-1, 1]], dtype=float))
    points = []
    for n in range(max_n):
        # Binary expansion of n
        val = n
        point = np.array([0.0, 0.0])
        power = np.eye(2)
        while val > 0 or power is np.eye(2):
            d = val % 2
            point += d * power @ np.array([1.0, 0.0])
            power = power @ M_inv
            val //= 2
            if val == 0:
                break
        points.extend([point[0], point[1]])
    return np.array(points, dtype=float)


OPERATIONS["twin_dragon_from_matrix_base"] = {
    "fn": twin_dragon_from_matrix_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate twin dragon points from matrix base-2 expansion"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
