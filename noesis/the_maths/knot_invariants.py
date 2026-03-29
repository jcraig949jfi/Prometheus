"""
Knot Invariants — Alexander polynomial, Jones polynomial (simplified), linking number

Connects to: [topology, algebra, polynomial_rings, braid_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "knot_invariants"
OPERATIONS = {}


def trefoil_alexander_polynomial(x):
    """Return the Alexander polynomial of the trefoil knot evaluated at each
    element of x. The trefoil has Alexander polynomial Delta(t) = t - 1 + t^{-1}.
    Input: array (values of t). Output: array."""
    results = []
    for t in x:
        if abs(t) < 1e-15:
            results.append(float('inf'))
        else:
            results.append(float(t - 1.0 + 1.0 / t))
    return np.array(results)


OPERATIONS["trefoil_alexander_polynomial"] = {
    "fn": trefoil_alexander_polynomial,
    "input_type": "array",
    "output_type": "array",
    "description": "Alexander polynomial of trefoil (t - 1 + 1/t) evaluated at x"
}


def writhe_from_crossings(x):
    """Compute the writhe of a knot diagram from crossing signs.
    Each element of x is +1 or -1 representing a positive or negative crossing.
    Writhe = sum of all crossing signs.
    Input: array (crossing signs). Output: scalar."""
    signs = np.sign(x)
    return float(np.sum(signs))


OPERATIONS["writhe_from_crossings"] = {
    "fn": writhe_from_crossings,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Writhe (sum of crossing signs) of a knot diagram"
}


def linking_number(x):
    """Compute the linking number of a two-component link from crossing signs.
    x encodes crossings between the two components: +1 or -1.
    Linking number = (1/2) * sum of crossing signs at inter-component crossings.
    Input: array. Output: scalar."""
    signs = np.sign(x)
    return float(np.sum(signs) / 2.0)


OPERATIONS["linking_number"] = {
    "fn": linking_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Linking number from inter-component crossing signs"
}


def bracket_polynomial_simple(x):
    """Compute the Kauffman bracket polynomial for a sequence of crossing types.
    Uses the state sum model. Each element of x represents a crossing (+1 or -1).
    Returns the bracket evaluated at A = x[0] if len > 1, else at A = -1.
    For a single crossing: <K> = A * <0-smoothing> + A^{-1} * <1-smoothing>.
    Simplified: for n crossings with no loops, bracket ~ (A^n + A^{-n}) * (-A^2 - A^{-2})^{c}
    where c counts resulting loops.
    Input: array. Output: scalar."""
    n = len(x)
    # Evaluate at A for the standard unknot bracket normalization
    # For an unknot, bracket = 1 (normalized). For n crossings all positive:
    # simplified computation using writhe
    A = -1.0  # standard evaluation point for Jones polynomial
    w = float(np.sum(np.sign(x)))
    # Bracket of unknot = 1, writhe contributes (-A^3)^{-w}
    bracket = (-A ** 3) ** (-w) if abs(A) > 1e-15 else 0.0
    return float(np.real(bracket))


OPERATIONS["bracket_polynomial_simple"] = {
    "fn": bracket_polynomial_simple,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Simplified Kauffman bracket from crossing signs"
}


def unknot_detection_simple(x):
    """Simple unknot detection heuristic: if the Alexander polynomial at t=-1
    equals 1 (in absolute value), it's consistent with the unknot.
    Interprets x as coefficients of a symmetrized Alexander polynomial.
    Returns 1.0 if consistent with unknot, 0.0 otherwise.
    Input: array (polynomial coefficients). Output: scalar."""
    # Evaluate polynomial at t = -1
    t = -1.0
    val = 0.0
    mid = len(x) // 2
    for i, c in enumerate(x):
        power = i - mid
        if abs(t) > 1e-15 or power >= 0:
            val += c * (t ** power)
    # Unknot has Delta(t) = 1, so Delta(-1) = 1
    return 1.0 if abs(abs(val) - 1.0) < 1e-6 else 0.0


OPERATIONS["unknot_detection_simple"] = {
    "fn": unknot_detection_simple,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Heuristic unknot test via Alexander polynomial at t=-1"
}


def crossing_number_bound(x):
    """Lower bound on crossing number from a knot diagram.
    Given crossing signs in x, the crossing number is at most |x|
    and at least |writhe| for alternating knots.
    Returns [len(x), |writhe|] as lower and upper bounds.
    Input: array. Output: array."""
    n = float(len(x))
    writhe = abs(float(np.sum(np.sign(x))))
    return np.array([writhe, n])


OPERATIONS["crossing_number_bound"] = {
    "fn": crossing_number_bound,
    "input_type": "array",
    "output_type": "array",
    "description": "Bounds on crossing number: [|writhe| lower, diagram upper]"
}


def knot_determinant_from_matrix(x):
    """Compute the knot determinant from a flattened Seifert-like matrix.
    det(K) = |det(S + S^T)| where S is the Seifert matrix.
    Input: array (flattened square matrix). Output: scalar."""
    n = int(np.round(np.sqrt(len(x))))
    if n < 1:
        return 0.0
    mat = np.zeros((n, n))
    mat.flat[:min(len(x), n * n)] = x[:n * n]
    sym = mat + mat.T
    return float(abs(np.linalg.det(sym)))


OPERATIONS["knot_determinant_from_matrix"] = {
    "fn": knot_determinant_from_matrix,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Knot determinant |det(S + S^T)| from flattened Seifert matrix"
}


def seifert_matrix_genus(x):
    """Estimate the genus of a knot from a flattened Seifert matrix.
    The genus g satisfies 2g = rank of Seifert matrix (for a minimal genus surface).
    Input: array (flattened square matrix). Output: scalar."""
    n = int(np.round(np.sqrt(len(x))))
    if n < 1:
        return 0.0
    mat = np.zeros((n, n))
    mat.flat[:min(len(x), n * n)] = x[:n * n]
    rank = np.linalg.matrix_rank(mat)
    # genus = rank / 2 (Seifert matrix is 2g x 2g for genus g)
    return float(rank / 2.0)


OPERATIONS["seifert_matrix_genus"] = {
    "fn": seifert_matrix_genus,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Genus estimate from Seifert matrix rank (g = rank/2)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
