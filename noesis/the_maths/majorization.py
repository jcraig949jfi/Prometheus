"""
Majorization — Schur convexity, Lorenz curves, doubly stochastic matrices

Connects to: [linear_algebra, optimization, information_theory, rook_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "majorization"
OPERATIONS = {}


def majorizes(x):
    """Check if first half of x majorizes the second half.
    a majorizes b iff for all k: sum of k largest a_i >= sum of k largest b_i,
    and sum(a) = sum(b). Returns 1.0 if yes, 0.0 if no.
    Input: array. Output: scalar."""
    half = len(x) // 2
    if half == 0:
        return 1.0
    a = np.sort(x[:half])[::-1]  # decreasing
    b = np.sort(x[half:2 * half])[::-1]
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    # Check sum equality (with tolerance)
    if abs(np.sum(a) - np.sum(b)) > 1e-10:
        return 0.0
    # Check partial sum condition
    cum_a = np.cumsum(a)
    cum_b = np.cumsum(b)
    if np.all(cum_a >= cum_b - 1e-10):
        return 1.0
    return 0.0


OPERATIONS["majorizes"] = {
    "fn": majorizes,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Test if first half majorizes second half"
}


def lorenz_curve(x):
    """Compute Lorenz curve values. Sort x ascending, compute cumulative share.
    L(k/n) = (sum of k smallest) / (sum of all). Input: array. Output: array."""
    sx = np.sort(x)
    total = np.sum(sx)
    if abs(total) < 1e-30:
        return np.linspace(0, 1, len(x))
    cumulative = np.cumsum(sx)
    return cumulative / total


OPERATIONS["lorenz_curve"] = {
    "fn": lorenz_curve,
    "input_type": "array",
    "output_type": "array",
    "description": "Lorenz curve: cumulative share of sorted values"
}


def gini_coefficient(x):
    """Compute the Gini coefficient from the Lorenz curve.
    G = 1 - 2 * integral of Lorenz curve.
    Input: array. Output: scalar."""
    n = len(x)
    if n == 0:
        return 0.0
    sx = np.sort(x)
    total = np.sum(sx)
    if abs(total) < 1e-30:
        return 0.0
    # G = (2 * sum_i (i+1)*x_{(i)} - (n+1)*sum) / (n * sum)
    # where x_{(i)} is sorted in ascending order, i is 0-indexed
    numerator = 2.0 * np.sum(np.arange(1, n + 1) * sx) - (n + 1) * total
    return float(numerator / (n * total))


OPERATIONS["gini_coefficient"] = {
    "fn": gini_coefficient,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Gini coefficient measuring inequality"
}


def birkhoff_decompose_approx(x):
    """Approximate Birkhoff decomposition of a doubly stochastic matrix.
    Reshape x into square matrix, project to doubly stochastic first,
    then greedily decompose into permutation matrices.
    Returns coefficients of the decomposition. Input: array. Output: array."""
    n = int(np.ceil(np.sqrt(len(x))))
    padded = np.zeros(n * n)
    padded[:len(x)] = np.abs(x)
    M = padded.reshape(n, n)
    # Project to doubly stochastic via Sinkhorn iteration
    for _ in range(50):
        M = M / (np.sum(M, axis=1, keepdims=True) + 1e-30)
        M = M / (np.sum(M, axis=0, keepdims=True) + 1e-30)
    # Greedy Birkhoff decomposition
    coeffs = []
    residual = M.copy()
    for _ in range(n * n):
        if np.max(np.abs(residual)) < 1e-10:
            break
        # Find minimum positive entry
        pos = residual[residual > 1e-10]
        if len(pos) == 0:
            break
        alpha = np.min(pos)
        # Find a permutation matrix supported on positive entries
        # Greedy matching
        perm = np.zeros((n, n))
        used_rows = set()
        used_cols = set()
        for i in range(n):
            for j in range(n):
                if residual[i, j] > 1e-10 and i not in used_rows and j not in used_cols:
                    perm[i, j] = 1.0
                    used_rows.add(i)
                    used_cols.add(j)
                    break
        if np.sum(perm) < n:
            break
        coeffs.append(alpha)
        residual -= alpha * perm
        residual = np.maximum(residual, 0)
    return np.array(coeffs) if coeffs else np.array([1.0])


OPERATIONS["birkhoff_decompose_approx"] = {
    "fn": birkhoff_decompose_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximate Birkhoff decomposition coefficients"
}


def schur_convex_test(x):
    """Test if the function f(x) = sum(x^2) is Schur-convex by checking
    majorization implies f(a) >= f(b). Split x into two halves.
    Returns [f(a), f(b), majorizes_flag]. Input: array. Output: array."""
    half = len(x) // 2
    if half == 0:
        return np.array([np.sum(x ** 2), 0.0, 1.0])
    a = x[:half]
    b = x[half:2 * half]
    fa = np.sum(a ** 2)
    fb = np.sum(b ** 2)
    # Check if a majorizes b
    sa = np.sort(a)[::-1]
    sb = np.sort(b)[::-1]
    n = min(len(sa), len(sb))
    maj = 1.0
    if abs(np.sum(sa[:n]) - np.sum(sb[:n])) > 1e-10 * n:
        maj = 0.0
    else:
        for k in range(1, n + 1):
            if np.sum(sa[:k]) < np.sum(sb[:k]) - 1e-10:
                maj = 0.0
                break
    return np.array([fa, fb, maj])


OPERATIONS["schur_convex_test"] = {
    "fn": schur_convex_test,
    "input_type": "array",
    "output_type": "array",
    "description": "Test Schur convexity of sum(x^2) on two halves"
}


def theil_index(x):
    """Compute the Theil index (generalized entropy index with alpha=1).
    T = (1/n) sum_i (x_i / mu) * ln(x_i / mu).
    Input: array. Output: scalar."""
    x_pos = np.maximum(x, 1e-30)  # Theil requires positive values
    n = len(x_pos)
    mu = np.mean(x_pos)
    if mu < 1e-30:
        return 0.0
    ratios = x_pos / mu
    return float(np.mean(ratios * np.log(ratios)))


OPERATIONS["theil_index"] = {
    "fn": theil_index,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Theil index (generalized entropy measure of inequality)"
}


def doubly_stochastic_projection(x):
    """Project a matrix onto the set of doubly stochastic matrices
    using Sinkhorn-Knopp iteration. Input: array. Output: matrix."""
    n = int(np.ceil(np.sqrt(len(x))))
    padded = np.ones(n * n)
    padded[:len(x)] = np.abs(x) + 1e-10
    M = padded.reshape(n, n)
    for _ in range(100):
        M = M / np.sum(M, axis=1, keepdims=True)
        M = M / np.sum(M, axis=0, keepdims=True)
    return M


OPERATIONS["doubly_stochastic_projection"] = {
    "fn": doubly_stochastic_projection,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Sinkhorn projection onto doubly stochastic matrices"
}


def majorization_lattice_meet(x):
    """Compute the meet (greatest lower bound) in the majorization order.
    Given two vectors a, b (halves of x), find the largest c majorized by both.
    The meet has Lorenz curve = pointwise min of Lorenz curves.
    Input: array. Output: array."""
    half = len(x) // 2
    if half == 0:
        return x.copy()
    a = x[:half]
    b = x[half:2 * half]
    n = len(a)
    # Compute Lorenz curves (from sorted descending partial sums)
    sa = np.sort(a)[::-1]
    sb = np.sort(b)[::-1]
    cum_a = np.cumsum(sa)
    cum_b = np.cumsum(sb)
    # Meet Lorenz curve = pointwise minimum
    cum_meet = np.minimum(cum_a, cum_b)
    # Ensure total sums match (take min total)
    cum_meet[-1] = min(cum_a[-1], cum_b[-1])
    # Recover the vector from cumulative sums (sorted descending)
    result = np.zeros(n)
    result[0] = cum_meet[0]
    for i in range(1, n):
        result[i] = cum_meet[i] - cum_meet[i - 1]
    return result


OPERATIONS["majorization_lattice_meet"] = {
    "fn": majorization_lattice_meet,
    "input_type": "array",
    "output_type": "array",
    "description": "Meet in majorization lattice (greatest lower bound)"
}


def entropy_schur(x):
    """Shannon entropy is Schur-concave. Compute H(p) where p = softmax(x).
    H(p) = -sum p_i log(p_i). Input: array. Output: scalar."""
    # Convert to probability distribution via softmax
    x_shifted = x - np.max(x)
    exp_x = np.exp(x_shifted)
    p = exp_x / np.sum(exp_x)
    # Shannon entropy
    H = -np.sum(p * np.log(p + 1e-30))
    return float(H)


OPERATIONS["entropy_schur"] = {
    "fn": entropy_schur,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of softmax(x), a Schur-concave function"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
