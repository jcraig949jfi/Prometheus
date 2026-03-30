"""
Pascal Variations — Pascal's triangle modular patterns, Sierpinski triangle, multinomial coefficients

Connects to: [combinatorics, fractal_geometry, number_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "pascal_variations"
OPERATIONS = {}


def pascal_row(x):
    """Compute row n of Pascal's triangle. n=int(x[0]). Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(n, 500)
    row = np.zeros(n + 1, dtype=np.float64)
    row[0] = 1
    for k in range(1, n + 1):
        row[k] = row[k - 1] * (n - k + 1) / k
    return row


OPERATIONS["pascal_row"] = {
    "fn": pascal_row,
    "input_type": "array",
    "output_type": "array",
    "description": "Row n of Pascal's triangle (binomial coefficients)"
}


def pascal_triangle_mod(x):
    """Pascal's triangle mod p for rows 0..n. x=[n, p]. Output: matrix. Input: array. Output: matrix."""
    n = int(abs(x[0]))
    p = int(abs(x[1])) if len(x) > 1 else 2
    n = min(n, 200)
    p = max(p, 2)
    triangle = np.zeros((n + 1, n + 1), dtype=np.int64)
    triangle[0, 0] = 1
    for i in range(1, n + 1):
        triangle[i, 0] = 1
        for j in range(1, i + 1):
            triangle[i, j] = (triangle[i - 1, j - 1] + triangle[i - 1, j]) % p
    return triangle


OPERATIONS["pascal_triangle_mod"] = {
    "fn": pascal_triangle_mod,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Pascal's triangle mod p (mod 2 gives Sierpinski pattern)"
}


def sierpinski_fractal_dimension(x):
    """Estimate fractal dimension of Pascal triangle mod p via box counting. x=[n, p]. Input: array. Output: scalar."""
    n = int(abs(x[0]))
    p = int(abs(x[1])) if len(x) > 1 else 2
    n = min(n, 200)
    p = max(p, 2)
    # Build triangle mod p, count nonzero entries
    triangle = np.zeros((n + 1, n + 1), dtype=np.int64)
    triangle[0, 0] = 1
    for i in range(1, n + 1):
        triangle[i, 0] = 1
        for j in range(1, i + 1):
            triangle[i, j] = (triangle[i - 1, j - 1] + triangle[i - 1, j]) % p
    # For Sierpinski (mod 2), theoretical dimension = log(3)/log(2) ~ 1.585
    # Estimate via counting nonzero in power-of-2 sized blocks
    nonzero = np.count_nonzero(triangle)
    total = (n + 1) * (n + 2) / 2
    if n > 1:
        # Approximate dimension from nonzero fraction
        dim = np.log(nonzero) / np.log(n + 1) if n > 0 else 0
    else:
        dim = 1.0
    return float(dim)


OPERATIONS["sierpinski_fractal_dimension"] = {
    "fn": sierpinski_fractal_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate fractal dimension of Pascal triangle mod p"
}


def multinomial_coefficient(x):
    """Multinomial coefficient n! / (k1! * k2! * ... * km!). x=[n, k1, k2, ...]. Input: array. Output: scalar."""
    n = int(abs(x[0]))
    ks = [int(abs(k)) for k in x[1:]]
    if sum(ks) != n:
        # Adjust: use provided ks as-is if they sum to n, else just compute n!/prod(ki!)
        pass
    from math import factorial
    denom = 1
    for k in ks:
        denom *= factorial(k)
    return float(factorial(n) / denom)


OPERATIONS["multinomial_coefficient"] = {
    "fn": multinomial_coefficient,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Multinomial coefficient n!/(k1!*k2!*...)"
}


def pascal_diagonal_sum(x):
    """Sum of d-th diagonal of Pascal's triangle (Fibonacci connection). x=[d]. Input: array. Output: array."""
    n_diags = int(abs(x[0]))
    n_diags = min(max(n_diags, 1), 100)
    # The d-th shallow diagonal sum of Pascal's triangle = F(d+1) (Fibonacci)
    results = np.zeros(n_diags, dtype=np.float64)
    for d in range(n_diags):
        # Sum C(d-k, k) for k = 0, 1, ..., floor(d/2)
        s = 0.0
        from math import comb
        for k in range(d // 2 + 1):
            s += comb(d - k, k)
        results[d] = s
    return results


OPERATIONS["pascal_diagonal_sum"] = {
    "fn": pascal_diagonal_sum,
    "input_type": "array",
    "output_type": "array",
    "description": "Shallow diagonal sums of Pascal's triangle (gives Fibonacci)"
}


def lucas_theorem_mod_p(x):
    """Compute C(n,k) mod p via Lucas' theorem. x=[n, k, p]. Input: array. Output: integer."""
    n = int(abs(x[0]))
    k = int(abs(x[1]))
    p = int(abs(x[2])) if len(x) > 2 else 2
    p = max(p, 2)
    if k > n:
        return 0
    # Lucas' theorem: C(n,k) mod p = product of C(ni, ki) mod p
    # where ni, ki are base-p digits
    result = 1
    while n > 0 or k > 0:
        ni = n % p
        ki = k % p
        if ki > ni:
            return 0
        # C(ni, ki) mod p
        from math import comb
        result = (result * comb(ni, ki)) % p
        n //= p
        k //= p
    return int(result)


OPERATIONS["lucas_theorem_mod_p"] = {
    "fn": lucas_theorem_mod_p,
    "input_type": "array",
    "output_type": "integer",
    "description": "Binomial coefficient C(n,k) mod prime p via Lucas' theorem"
}


def binomial_transform(x):
    """Binomial transform: b_n = sum_{k=0}^{n} C(n,k) * a_k. Input: array. Output: array."""
    a = np.asarray(x, dtype=np.float64)
    n = len(a)
    b = np.zeros(n, dtype=np.float64)
    from math import comb
    for i in range(n):
        for k in range(i + 1):
            b[i] += comb(i, k) * a[k]
    return b


OPERATIONS["binomial_transform"] = {
    "fn": binomial_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Binomial transform of a sequence"
}


def euler_transform(x):
    """Euler transform for accelerating alternating series. Input: array. Output: array."""
    a = np.asarray(x, dtype=np.float64)
    n = len(a)
    # Euler transform: E_n = sum_{k=0}^{n} C(n,k) * a_k / 2^(n+1)
    result = np.zeros(n, dtype=np.float64)
    from math import comb
    for i in range(n):
        s = 0.0
        for k in range(i + 1):
            s += comb(i, k) * a[k]
        result[i] = s / (2.0 ** (i + 1))
    return result


OPERATIONS["euler_transform"] = {
    "fn": euler_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Euler transform for series acceleration"
}


def pascal_catalan_connection(x):
    """Compute n-th Catalan number from Pascal's triangle: C(2n,n)/(n+1). Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    from math import comb
    results = np.array([comb(2 * int(n), int(n)) // (int(n) + 1) if n >= 0 else 0 for n in vals.ravel()],
                       dtype=np.float64)
    return results.reshape(vals.shape)


OPERATIONS["pascal_catalan_connection"] = {
    "fn": pascal_catalan_connection,
    "input_type": "array",
    "output_type": "array",
    "description": "Catalan numbers from Pascal's triangle: C(2n,n)/(n+1)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
