"""
Species Arithmetic — addition, multiplication, composition of species

Connects to: [operads, combinatorics, umbral_calculus, rook_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import factorial, comb

FIELD_NAME = "species_arithmetic"
OPERATIONS = {}


def species_sum(x):
    """Sum of two combinatorial species F + G. If F[n] and G[n] count structures
    on n elements, (F+G)[n] = F[n] + G[n]. Split x into two halves.
    Input: array. Output: array."""
    half = len(x) // 2
    if half == 0:
        return x.copy()
    f = x[:half]
    g = x[half:2 * half]
    return f + g


OPERATIONS["species_sum"] = {
    "fn": species_sum,
    "input_type": "array",
    "output_type": "array",
    "description": "Sum of two species: (F+G)[n] = F[n] + G[n]"
}


def species_product(x):
    """Product of two species F * G. (F*G)[n] = sum_{k=0}^{n} C(n,k) F[k] G[n-k].
    This is the binomial convolution. Split x into two halves.
    Input: array. Output: array."""
    half = len(x) // 2
    if half == 0:
        return x.copy()
    f = x[:half]
    g = x[half:2 * half]
    n = len(f)
    result = np.zeros(n)
    for k in range(n):
        for j in range(k + 1):
            if j < n and (k - j) < n:
                result[k] += comb(k, j) * f[j] * g[k - j]
    return result


OPERATIONS["species_product"] = {
    "fn": species_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Product of two species via binomial convolution"
}


def species_composition_coeffs(x):
    """Composition of species F(G). If f_n = F[n]/n! and g_n = G[n]/n! are
    exponential coefficients, compute the exponential coefficients of F(G).
    Uses Faa di Bruno's formula. Input: array. Output: array."""
    n = len(x)
    half = n // 2
    if half == 0:
        return x.copy()
    # f = EGF coefficients of F, g = EGF coefficients of G (with g[0]=0 required)
    f = x[:half].copy()
    g = x[half:2 * half].copy()
    g[0] = 0.0  # G must have G[0] = 0 for composition
    m = len(f)
    # Compute powers of g up to m-1 via convolution
    g_powers = [np.zeros(m) for _ in range(m)]
    g_powers[0][0] = 1.0  # g^0 = 1
    for p in range(1, m):
        for i in range(m):
            for j in range(i + 1):
                if j < m and (i - j) < m:
                    g_powers[p][i] += g_powers[p - 1][j] * g[i - j]
    # F(G)[n] = sum_k f[k] * g^k[n]
    result = np.zeros(m)
    for k in range(m):
        for i in range(m):
            result[i] += f[k] * g_powers[k][i]
    return result


OPERATIONS["species_composition_coeffs"] = {
    "fn": species_composition_coeffs,
    "input_type": "array",
    "output_type": "array",
    "description": "Composition of species F(G) via EGF coefficient computation"
}


def species_derivative(x):
    """Derivative of a species. F'[n] = F[n+1] * (n+1).
    In terms of EGF: derivative shifts coefficients.
    Input: array. Output: array."""
    n = len(x)
    if n <= 1:
        return np.array([0.0])
    result = np.zeros(n - 1)
    for i in range(n - 1):
        result[i] = x[i + 1] * (i + 1)
    return result


OPERATIONS["species_derivative"] = {
    "fn": species_derivative,
    "input_type": "array",
    "output_type": "array",
    "description": "Derivative of species: F'[n] = (n+1)*F[n+1]"
}


def species_pointing(x):
    """Pointing of a species. F^bullet[n] = n * F[n].
    Pointing selects a distinguished element. Input: array. Output: array."""
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        result[i] = i * x[i]
    return result


OPERATIONS["species_pointing"] = {
    "fn": species_pointing,
    "input_type": "array",
    "output_type": "array",
    "description": "Pointing of species: F^bullet[n] = n * F[n]"
}


def type_generating_function(x):
    """Type generating function (OGF) from species counts.
    tilde_F(x) = sum_{n>=0} |F[n]/S_n| * t^n where |F[n]/S_n| = F[n]/n! (isomorphism types).
    Evaluate at t = x[0]. Input: array. Output: scalar."""
    t = x[0] if abs(x[0]) < 1.0 else 0.5
    s = 0.0
    for n in range(len(x)):
        # Number of isomorphism types ~ F[n] / n!
        coeff = abs(x[n]) / factorial(n)
        s += coeff * t ** n
    return float(s)


OPERATIONS["type_generating_function"] = {
    "fn": type_generating_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Type generating function evaluated at x[0]"
}


def cycle_index_symmetric(x):
    """Cycle index of the symmetric group S_n, evaluated at x_i = x[i].
    Z_{S_n} = (1/n!) sum_{lambda} (n!/prod m_i! i^{m_i}) prod x_i^{m_i}
    where n = len(x). Returns the evaluated cycle index. Input: array. Output: scalar."""
    n = len(x)
    if n == 0:
        return 1.0
    # Generate partitions of n
    def partitions(n, max_val=None):
        if max_val is None:
            max_val = n
        if n == 0:
            yield []
            return
        for i in range(min(n, max_val), 0, -1):
            for p in partitions(n - i, i):
                yield [i] + p

    total = 0.0
    for part in partitions(n):
        # Count multiplicity of each part
        counts = {}
        for p in part:
            counts[p] = counts.get(p, 0) + 1
        # Coefficient: n! / prod(i^{m_i} * m_i!)
        denom = 1.0
        prod_x = 1.0
        for i, m in counts.items():
            denom *= (float(i) ** m) * factorial(m)
            idx = min(i - 1, n - 1)  # x_i uses 0-indexed
            prod_x *= x[idx] ** m
        total += prod_x / denom
    return float(total)


OPERATIONS["cycle_index_symmetric"] = {
    "fn": cycle_index_symmetric,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Cycle index of S_n evaluated at given variables"
}


def exponential_species_coeffs(x):
    """Compute EGF coefficients for the species of sets (E), permutations (S),
    and linear orders (L). Returns matrix: rows = [E, S, L], columns = degrees.
    E[n] = 1/n!, S[n] = 1 (number of permutations / n!), L[n] = 1.
    Scaled by x values. Input: array. Output: matrix."""
    n = len(x)
    result = np.zeros((3, n))
    for k in range(n):
        # Species of sets E: EGF coeff = 1/k! (one structure)
        result[0, k] = 1.0 / factorial(k) * abs(x[k])
        # Species of permutations S: |S[k]| = k!, EGF coeff = k!/k! = 1
        result[1, k] = 1.0 * abs(x[k])
        # Species of linear orders L: |L[k]| = k!, EGF coeff = 1
        result[2, k] = 1.0 * abs(x[k])
    return result


OPERATIONS["exponential_species_coeffs"] = {
    "fn": exponential_species_coeffs,
    "input_type": "array",
    "output_type": "matrix",
    "description": "EGF coefficients for species E, S, L scaled by input"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
