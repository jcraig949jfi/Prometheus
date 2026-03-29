"""
Umbral Calculus — Sheffer sequences, Appell polynomials, umbral composition

Connects to: [combinatorics, polynomial_algebra, species_arithmetic, q_analogues]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import comb, factorial

FIELD_NAME = "umbral_calculus"
OPERATIONS = {}


def bernoulli_polynomial(x):
    """Evaluate Bernoulli polynomials B_0(x) through B_n(x) where n=len(x)-1,
    evaluated at each corresponding x value. Input: array. Output: array."""
    n = len(x)
    # Compute Bernoulli numbers via Akiyama-Tanigawa algorithm
    b = [0.0] * n
    a = [0.0] * n
    for m in range(n):
        a[m] = 1.0 / (m + 1)
        for j in range(m, 0, -1):
            a[j - 1] = j * (a[j - 1] - a[j])
        b[m] = a[0]
    # B_k(x_k) = sum_{j=0}^{k} C(k,j) * b[j] * x_k^{k-j}
    result = np.zeros(n)
    for k in range(n):
        val = 0.0
        for j in range(k + 1):
            val += comb(k, j) * b[j] * (x[k] ** (k - j))
        result[k] = val
    return result


OPERATIONS["bernoulli_polynomial"] = {
    "fn": bernoulli_polynomial,
    "input_type": "array",
    "output_type": "array",
    "description": "Evaluates B_k(x_k) for each index k"
}


def euler_polynomial(x):
    """Evaluate Euler polynomials E_0(x) through E_n(x).
    E_n(x) = sum_{k=0}^{n} C(n,k) * (E_k / 2^k) * (x - 1/2)^{n-k}
    where E_k are Euler numbers. Input: array. Output: array."""
    n = len(x)
    # Euler numbers via explicit formula: E_k for even k
    # We use the relation: E_n(x) = (2/(n+1)) * (B_{n+1}(x) - 2^{n+1} * B_{n+1}(x/2))
    # Compute Bernoulli numbers
    b = [0.0] * (n + 2)
    a = [0.0] * (n + 2)
    for m in range(n + 2):
        a[m] = 1.0 / (m + 1)
        for j in range(m, 0, -1):
            a[j - 1] = j * (a[j - 1] - a[j])
        b[m] = a[0]

    def bernoulli_poly_eval(k, xv):
        val = 0.0
        for j in range(k + 1):
            val += comb(k, j) * b[j] * (xv ** (k - j))
        return val

    result = np.zeros(n)
    for k in range(n):
        bk1_x = bernoulli_poly_eval(k + 1, x[k])
        bk1_xh = bernoulli_poly_eval(k + 1, x[k] / 2.0)
        result[k] = (2.0 / (k + 1)) * (bk1_x - (2.0 ** (k + 1)) * bk1_xh)
    return result


OPERATIONS["euler_polynomial"] = {
    "fn": euler_polynomial,
    "input_type": "array",
    "output_type": "array",
    "description": "Evaluates E_k(x_k) for each index k using Bernoulli polynomials"
}


def appell_sequence_eval(x):
    """Evaluate an Appell sequence with generating coefficients a_k = 1/k!.
    A_n(x) = sum_{k=0}^{n} C(n,k) * a_k * x^{n-k}. Input: array. Output: array."""
    n = len(x)
    result = np.zeros(n)
    for deg in range(n):
        val = 0.0
        for k in range(deg + 1):
            a_k = 1.0 / factorial(k)
            val += comb(deg, k) * a_k * (x[deg] ** (deg - k))
        result[deg] = val
    return result


OPERATIONS["appell_sequence_eval"] = {
    "fn": appell_sequence_eval,
    "input_type": "array",
    "output_type": "array",
    "description": "Evaluates Appell sequence with a_k=1/k! at given points"
}


def sheffer_sequence_coeffs(x):
    """Compute coefficients of Sheffer sequence for the pair (e^t, t),
    which gives ordinary monomials. Returns coefficient matrix lower-triangular.
    Uses len(x) as the order. Input: array. Output: matrix."""
    n = len(x)
    # For (g(t), f(t)) = (e^t, t), the Sheffer sequence is s_n(x) = sum C(n,k) x^k / ...
    # Actually (e^t, t) gives s_n(x) = sum_{k=0}^n C(n,k) * (1/factorial(n-k)) * x^k
    coeffs = np.zeros((n, n))
    for deg in range(n):
        for k in range(deg + 1):
            coeffs[deg, k] = comb(deg, k) / factorial(deg - k)
    return coeffs


OPERATIONS["sheffer_sequence_coeffs"] = {
    "fn": sheffer_sequence_coeffs,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Coefficient matrix for Sheffer sequence (e^t, t)"
}


def umbral_composition(x):
    """Umbral composition of two polynomial sequences represented by coefficients.
    Given array x of length 2n, split into two sequences of coefficients and compose.
    (p . q)_n = sum_{k} p_{n,k} * q_k. Input: array. Output: array."""
    n = len(x) // 2
    if n == 0:
        return np.array([0.0])
    p = x[:n]
    q = x[n:2 * n]
    # Umbral composition: treat p as polynomial, evaluate at "umbral" q
    # result_k = sum_{j=0}^{k} C(k,j) * p[j] * q[k-j]
    result = np.zeros(n)
    for k in range(n):
        val = 0.0
        for j in range(k + 1):
            if j < n and (k - j) < n:
                val += comb(k, j) * p[j] * q[k - j]
        result[k] = val
    return result


OPERATIONS["umbral_composition"] = {
    "fn": umbral_composition,
    "input_type": "array",
    "output_type": "array",
    "description": "Umbral composition of two coefficient sequences via binomial convolution"
}


def falling_factorial(x):
    """Compute falling factorial x_(n) = x(x-1)(x-2)...(x-n+1) for n=index.
    Input: array (values). Output: array."""
    result = np.zeros(len(x))
    for i, v in enumerate(x):
        prod = 1.0
        for j in range(i):
            prod *= (v - j)
        result[i] = prod
    return result


OPERATIONS["falling_factorial"] = {
    "fn": falling_factorial,
    "input_type": "array",
    "output_type": "array",
    "description": "Falling factorial x_(k) for each index k"
}


def rising_factorial(x):
    """Compute rising factorial x^(n) = x(x+1)(x+2)...(x+n-1) for n=index.
    Input: array (values). Output: array."""
    result = np.zeros(len(x))
    for i, v in enumerate(x):
        prod = 1.0
        for j in range(i):
            prod *= (v + j)
        result[i] = prod
    return result


OPERATIONS["rising_factorial"] = {
    "fn": rising_factorial,
    "input_type": "array",
    "output_type": "array",
    "description": "Rising factorial (Pochhammer) x^(k) for each index k"
}


def bell_polynomial_partial(x):
    """Partial Bell polynomial B_{n,k}(x_1,...,x_{n-k+1}).
    Uses len(x) to determine n, k = n//2. Input: array. Output: scalar."""
    n = len(x)
    k = max(1, n // 2)
    # B_{n,k}(x1,...) = sum over partitions of n into k parts
    # For simplicity, use the determinantal formula via Faa di Bruno
    # B_{n,k} = n! / k! * sum over partitions pi of n with k parts of prod x_{pi_j}/pi_j!
    # We use a recursive DP approach
    if n == 0 and k == 0:
        return 1.0
    if k == 0 or k > n:
        return 0.0
    # dp[i][j] = B_{i,j}(x1,...) / i! * j!  ... use recurrence
    # B_{n,k} = sum_{i=1}^{n-k+1} C(n-1, i-1) * x[i-1] * B_{n-i, k-1}
    dp = np.zeros((n + 1, k + 1))
    dp[0][0] = 1.0
    for nn in range(1, n + 1):
        for kk in range(1, min(nn, k) + 1):
            s = 0.0
            for i in range(1, nn - kk + 2):
                if i - 1 < len(x):
                    s += comb(nn - 1, i - 1) * x[i - 1] * dp[nn - i][kk - 1]
            dp[nn][kk] = s
    return float(dp[n][k])


OPERATIONS["bell_polynomial_partial"] = {
    "fn": bell_polynomial_partial,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Partial Bell polynomial B_{n, n//2} evaluated at x"
}


def umbral_shift(x):
    """Apply the umbral shift operator E: p(x) -> p(x+1).
    Given polynomial coefficients in x, return shifted coefficients.
    Input: array (polynomial coefficients). Output: array."""
    n = len(x)
    # If p(t) = sum a_k t^k, then p(t+1) = sum_k a_k sum_j C(k,j) t^j
    result = np.zeros(n)
    for k in range(n):
        for j in range(k + 1):
            result[j] += x[k] * comb(k, j)
    return result


OPERATIONS["umbral_shift"] = {
    "fn": umbral_shift,
    "input_type": "array",
    "output_type": "array",
    "description": "Umbral shift operator: translates polynomial by +1"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
