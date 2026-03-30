"""
Combinatorial Species — generating functions, labeled/unlabeled counting

Connects to: [combinatorics, algebra, graph_theory, number_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "combinatorial_species"
OPERATIONS = {}


def exponential_generating_function(x):
    """Compute coefficients of the EGF for the sequence given by x.
    EGF coefficient a_n / n! for each a_n in x.
    Input: array. Output: array."""
    from math import factorial
    factorials = np.array([float(factorial(i)) for i in range(len(x))])
    return x / factorials


OPERATIONS["exponential_generating_function"] = {
    "fn": exponential_generating_function,
    "input_type": "array",
    "output_type": "array",
    "description": "EGF coefficients a_n/n! from sequence a_n"
}


def ordinary_generating_function(x):
    """Evaluate the ordinary generating function sum(a_n * t^n) at t=0.5.
    Input: array (coefficients). Output: scalar."""
    t = 0.5
    powers = t ** np.arange(len(x))
    return float(np.sum(x * powers))


OPERATIONS["ordinary_generating_function"] = {
    "fn": ordinary_generating_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "OGF evaluated at t=0.5"
}


def bell_numbers(x):
    """Compute Bell numbers B_0, B_1, ..., B_{n-1} where n = len(x).
    Uses the Bell triangle. Input: array (length determines count). Output: array."""
    n = len(x)
    if n == 0:
        return np.array([])
    bell = np.zeros(n, dtype=float)
    bell[0] = 1.0
    if n == 1:
        return bell
    # Bell triangle
    tri = np.zeros((n, n))
    tri[0, 0] = 1.0
    for i in range(1, n):
        tri[i, 0] = tri[i - 1, i - 1]
        for j in range(1, i + 1):
            tri[i, j] = tri[i, j - 1] + tri[i - 1, j - 1]
        bell[i] = tri[i, 0]
    return bell


OPERATIONS["bell_numbers"] = {
    "fn": bell_numbers,
    "input_type": "array",
    "output_type": "array",
    "description": "First n Bell numbers (n = length of input)"
}


def stirling_second_kind(x):
    """Compute Stirling numbers of the second kind S(n, k) for n = len(x)
    and all k from 0 to n. S(n,k) = number of ways to partition n elements
    into k non-empty subsets.
    Input: array (length determines n). Output: array."""
    n = len(x)
    # S(n, k) using recurrence S(n,k) = k*S(n-1,k) + S(n-1,k-1)
    S = np.zeros((n + 1, n + 1))
    S[0, 0] = 1.0
    for i in range(1, n + 1):
        for k in range(1, i + 1):
            S[i, k] = k * S[i - 1, k] + S[i - 1, k - 1]
    return S[n, :n + 1]


OPERATIONS["stirling_second_kind"] = {
    "fn": stirling_second_kind,
    "input_type": "array",
    "output_type": "array",
    "description": "Stirling numbers S(n,k) for n=len(input), k=0..n"
}


def labeled_trees_count(x):
    """Cayley's formula: the number of labeled trees on n vertices is n^{n-2}.
    Computes n^{n-2} for each element of x treated as n (rounded to int).
    Input: array. Output: array."""
    results = []
    for val in x:
        n = max(1, int(round(abs(val))))
        if n <= 2:
            results.append(1.0)
        else:
            results.append(float(n ** (n - 2)))
    return np.array(results)


OPERATIONS["labeled_trees_count"] = {
    "fn": labeled_trees_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Cayley's formula n^(n-2) for labeled trees on n vertices"
}


def species_sum_coefficients(x):
    """Sum of two species: coefficient-wise addition of two halves of x.
    Splits x into two halves and adds them element-wise (species sum = disjoint union).
    Input: array. Output: array."""
    mid = len(x) // 2
    a = x[:mid]
    b = x[mid:2 * mid]
    return a + b


OPERATIONS["species_sum_coefficients"] = {
    "fn": species_sum_coefficients,
    "input_type": "array",
    "output_type": "array",
    "description": "Species sum: element-wise addition of two coefficient sequences"
}


def species_product_coefficients(x):
    """Product of two species: Cauchy product (convolution) of two halves of x.
    (F*G)_n = sum_{k=0}^{n} C(n,k) * f_k * g_{n-k} for EGF product.
    Input: array. Output: array."""
    mid = len(x) // 2
    a = x[:mid]
    b = x[mid:2 * mid]
    n = len(a)
    result = np.zeros(n)
    for i in range(n):
        for j in range(n - i):
            # Binomial product for EGF: C(i+j, i) * a_i * b_j
            from math import comb
            result[i + j] += comb(i + j, i) * a[i] * b[j]
    return result


OPERATIONS["species_product_coefficients"] = {
    "fn": species_product_coefficients,
    "input_type": "array",
    "output_type": "array",
    "description": "Species product via binomial convolution of EGF coefficients"
}


def derangement_count(x):
    """Count derangements D(n) = n! * sum_{k=0}^{n} (-1)^k / k! for each
    element of x treated as n. A derangement is a permutation with no fixed points.
    Input: array. Output: array."""
    results = []
    for val in x:
        n = max(0, int(round(abs(val))))
        if n == 0:
            results.append(1.0)
        elif n == 1:
            results.append(0.0)
        else:
            # D(n) = (n-1) * (D(n-1) + D(n-2))
            d_prev2 = 1.0  # D(0)
            d_prev1 = 0.0  # D(1)
            for k in range(2, n + 1):
                d_curr = (k - 1) * (d_prev1 + d_prev2)
                d_prev2 = d_prev1
                d_prev1 = d_curr
            results.append(float(d_prev1))
    return np.array(results)


OPERATIONS["derangement_count"] = {
    "fn": derangement_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of derangements D(n) for each element as n"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
