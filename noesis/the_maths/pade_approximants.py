"""
Pade Approximants -- Rational function approximation from power series, convergence acceleration

Connects to: [divergent_series, continued_fractions, analytic_combinatorics, hypergeometric_functions]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "pade_approximants"
OPERATIONS = {}


def pade_approximant(x):
    """Compute [L/M] Pade approximant coefficients from power series coefficients.
    L=M=len(x)//2. Input: array (power series coeffs). Output: array (numerator, denominator coeffs)."""
    n = len(x)
    L = n // 2
    M = n - L - 1
    if M <= 0:
        return x.astype(float)
    # Build the system for denominator coefficients
    # sum_{j=1}^{M} b_j * c_{L-M+i+j} = -c_{L+i+1} for i=0..M-1
    A = np.zeros((M, M))
    rhs = np.zeros(M)
    for i in range(M):
        for j in range(M):
            idx = L - M + i + j + 1
            A[i, j] = x[idx] if 0 <= idx < n else 0.0
        rhs[i] = -x[L + i + 1] if L + i + 1 < n else 0.0
    try:
        b = np.linalg.solve(A, rhs)
    except np.linalg.LinAlgError:
        b = np.linalg.lstsq(A, rhs, rcond=None)[0]
    # Denominator: 1, b_1, ..., b_M
    denom = np.concatenate([[1.0], b])
    # Numerator: a_i = sum_{j=0}^{min(i,M)} b_j * c_{i-j}
    numer = np.zeros(L + 1)
    for i in range(L + 1):
        for j in range(min(i, M) + 1):
            numer[i] += denom[j] * (x[i - j] if 0 <= i - j < n else 0.0)
    return np.concatenate([numer, denom])


OPERATIONS["pade_approximant"] = {
    "fn": pade_approximant,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute Pade approximant [L/M] numerator and denominator coefficients"
}


def pade_table_entry(x):
    """Evaluate the [1/1] Pade approximant at z=1 from series coefficients.
    Input: array. Output: scalar."""
    if len(x) < 3:
        return float(np.sum(x))
    c0, c1, c2 = x[0], x[1], x[2]
    # [1/1] Pade: (c0 + (c1 - c0*c2/c1)*z) / (1 - (c2/c1)*z) if c1 != 0
    if abs(c1) < 1e-15:
        return float(c0)
    b1 = -c2 / c1
    a0 = c0
    a1 = c1 + c0 * b1
    denom = 1.0 + b1
    if abs(denom) < 1e-15:
        return float(c0 + c1)
    return float((a0 + a1) / denom)


OPERATIONS["pade_table_entry"] = {
    "fn": pade_table_entry,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Evaluate [1/1] Pade approximant at z=1"
}


def convergence_acceleration_epsilon(x):
    """Wynn's epsilon algorithm for convergence acceleration of a sequence.
    Input: array (sequence of partial sums). Output: scalar (accelerated limit)."""
    n = len(x)
    if n < 3:
        return float(x[-1])
    # Epsilon table
    eps = np.zeros((n + 1, n + 1))
    # eps_{-1} = 0, eps_0 = x
    for i in range(n):
        eps[i, 0] = 0.0
        eps[i, 1] = x[i]
    for j in range(2, n + 1):
        for i in range(n - j + 1):
            diff = eps[i + 1, j - 1] - eps[i, j - 1]
            if abs(diff) < 1e-30:
                eps[i, j] = 1e30
            else:
                eps[i, j] = eps[i + 1, j - 2] + 1.0 / diff
    # Even columns contain accelerated estimates; take the highest even column
    best_col = 2 * ((n - 1) // 2)
    if best_col < 2:
        best_col = 2
    best_col = min(best_col, n)
    if best_col % 2 == 1:
        best_col -= 1
    return float(eps[0, best_col]) if best_col >= 2 else float(x[-1])


OPERATIONS["convergence_acceleration_epsilon"] = {
    "fn": convergence_acceleration_epsilon,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Wynn epsilon algorithm for convergence acceleration"
}


def shanks_transform(x):
    """Shanks transformation (e_1 transform) of a sequence.
    Input: array (sequence). Output: scalar."""
    n = len(x)
    if n < 3:
        return float(x[-1])
    # e_1(S_n) = (S_{n+1}*S_{n-1} - S_n^2) / (S_{n+1} - 2*S_n + S_{n-1})
    results = []
    for i in range(1, n - 1):
        denom = x[i + 1] - 2.0 * x[i] + x[i - 1]
        if abs(denom) < 1e-30:
            results.append(x[i])
        else:
            results.append((x[i + 1] * x[i - 1] - x[i] ** 2) / denom)
    return float(results[-1]) if results else float(x[-1])


OPERATIONS["shanks_transform"] = {
    "fn": shanks_transform,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shanks e_1 transformation for sequence acceleration"
}


def wynn_epsilon(x):
    """Wynn epsilon algorithm (full table). Input: array. Output: array (diagonal of epsilon table)."""
    n = len(x)
    if n < 2:
        return x.copy()
    eps_prev_col = np.zeros(n)  # eps_{-1}
    eps_curr_col = x.copy().astype(float)  # eps_0
    diag = [eps_curr_col[0]]
    for j in range(1, n):
        eps_next = np.zeros(n - j)
        for i in range(n - j):
            diff = eps_curr_col[i + 1] - eps_curr_col[i]
            if abs(diff) < 1e-30:
                eps_next[i] = 1e30
            else:
                eps_next[i] = eps_prev_col[i + 1] + 1.0 / diff
        if len(eps_next) > 0:
            diag.append(eps_next[0])
        eps_prev_col = eps_curr_col
        eps_curr_col = eps_next
    return np.array(diag)


OPERATIONS["wynn_epsilon"] = {
    "fn": wynn_epsilon,
    "input_type": "array",
    "output_type": "array",
    "description": "Full Wynn epsilon table diagonal"
}


def richardson_extrapolation(x):
    """Richardson extrapolation assuming error ~ h^p. Treats array as f(h) for h=1,1/2,1/3,...
    Input: array. Output: scalar."""
    n = len(x)
    if n < 2:
        return float(x[0])
    h = 1.0 / np.arange(1, n + 1)
    # Neville-Aitken scheme
    table = x.copy().astype(float)
    for j in range(1, n):
        new_table = np.zeros(n - j)
        for i in range(n - j):
            r = (h[i] / h[i + j]) ** 2
            new_table[i] = (r * table[i + 1] - table[i]) / (r - 1.0) if abs(r - 1.0) > 1e-30 else table[i]
        table = new_table
    return float(table[0])


OPERATIONS["richardson_extrapolation"] = {
    "fn": richardson_extrapolation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Richardson extrapolation to the limit"
}


def aitken_delta_squared(x):
    """Aitken's delta-squared acceleration. Input: array. Output: array (accelerated sequence)."""
    n = len(x)
    if n < 3:
        return x.copy()
    result = []
    for i in range(n - 2):
        denom = x[i + 2] - 2 * x[i + 1] + x[i]
        if abs(denom) < 1e-30:
            result.append(x[i + 2])
        else:
            result.append(x[i] - (x[i + 1] - x[i]) ** 2 / denom)
    return np.array(result)


OPERATIONS["aitken_delta_squared"] = {
    "fn": aitken_delta_squared,
    "input_type": "array",
    "output_type": "array",
    "description": "Aitken delta-squared process for sequence acceleration"
}


def continued_fraction_from_series(x):
    """Convert power series coefficients to continued fraction coefficients.
    Uses quotient-difference algorithm. Input: array. Output: array."""
    n = len(x)
    if n < 2:
        return x.copy()
    # QD algorithm
    e = np.zeros(n)
    q = np.zeros(n)
    # Initialize
    for i in range(1, n):
        e[i] = x[i] / x[i - 1] if abs(x[i - 1]) > 1e-30 else 0.0
    cf_coeffs = [x[0], e[1] if n > 1 else 0.0]
    for k in range(2, min(n, 10)):
        q_new = np.zeros(n)
        e_new = np.zeros(n)
        for i in range(1, n - k + 1):
            q_new[i] = e[i + 1] - e[i] + q[i]
            if abs(q_new[i]) > 1e-30:
                e_new[i] = e[i + 1] * q[i + 1] / q_new[i] if i + 1 < n else 0.0
        cf_coeffs.append(q_new[1] if n > 2 else 0.0)
        e = e_new
        q = q_new
    return np.array(cf_coeffs[:n])


OPERATIONS["continued_fraction_from_series"] = {
    "fn": continued_fraction_from_series,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert power series to continued fraction via QD algorithm"
}


def pade_pole_locations(x):
    """Find poles of the Pade approximant (roots of denominator).
    Input: array (series coeffs). Output: array (pole locations)."""
    result = pade_approximant(x)
    n = len(x)
    L = n // 2
    M = n - L - 1
    if M <= 0:
        return np.array([])
    denom_coeffs = result[L + 1:]
    # Denominator polynomial: 1 + b_1*z + ... + b_M*z^M
    # numpy.roots wants highest degree first
    poly_coeffs = denom_coeffs[::-1]
    if len(poly_coeffs) < 2:
        return np.array([])
    roots = np.roots(poly_coeffs)
    return np.sort(np.abs(roots))


OPERATIONS["pade_pole_locations"] = {
    "fn": pade_pole_locations,
    "input_type": "array",
    "output_type": "array",
    "description": "Locations (magnitudes) of Pade approximant poles"
}


def rational_approximation_error(x):
    """Error of [L/M] Pade approximant vs truncated series at z=0.5.
    Input: array. Output: scalar."""
    n = len(x)
    z = 0.5
    # Direct series evaluation
    series_val = np.sum(x * z ** np.arange(n))
    # Pade evaluation
    result = pade_approximant(x)
    L = n // 2
    M = n - L - 1
    if M <= 0:
        return 0.0
    numer_coeffs = result[:L + 1]
    denom_coeffs = result[L + 1:]
    numer_val = np.sum(numer_coeffs * z ** np.arange(len(numer_coeffs)))
    denom_val = np.sum(denom_coeffs * z ** np.arange(len(denom_coeffs)))
    if abs(denom_val) < 1e-30:
        return float('inf')
    pade_val = numer_val / denom_val
    return float(abs(pade_val - series_val))


OPERATIONS["rational_approximation_error"] = {
    "fn": rational_approximation_error,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Error between Pade approximant and truncated series at z=0.5"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
