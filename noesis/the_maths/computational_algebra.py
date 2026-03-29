"""
Computational Algebra — Groebner bases (toy), polynomial ideals, elimination theory

Connects to: [abstract_algebra, algebraic_geometry, commutative_algebra, symbolic_computation]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "computational_algebra"
OPERATIONS = {}


def polynomial_gcd_univariate(x):
    """GCD of two univariate polynomials using numpy's polynomial module.
    Input: array of length 2n, first half = coefficients of P, second half = coefficients of Q.
    Coefficients are in increasing degree order: [a0, a1, a2, ...] = a0 + a1*x + a2*x^2 + ...
    Output: polynomial (array of GCD coefficients).
    """
    n = len(x) // 2
    if n < 1:
        return x.copy()
    p = np.trim_zeros(x[:n], 'b')
    q = np.trim_zeros(x[n:2*n], 'b')
    if len(p) == 0:
        return q if len(q) > 0 else np.array([0.0])
    if len(q) == 0:
        return p

    # Euclidean algorithm for polynomial GCD
    while len(q) > 0 and not (len(q) == 1 and abs(q[0]) < 1e-12):
        # Polynomial division: p = quotient * q + remainder
        _, r = np.polydiv(p[::-1], q[::-1])  # numpy uses decreasing degree
        r = r[::-1]
        # Trim near-zero leading coefficients
        while len(r) > 1 and abs(r[-1]) < 1e-10:
            r = r[:-1]
        p = q
        q = r
    # Normalize: make leading coefficient 1
    if len(p) > 0 and abs(p[-1]) > 1e-12:
        p = p / p[-1]
    return p


OPERATIONS["polynomial_gcd_univariate"] = {
    "fn": polynomial_gcd_univariate,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "GCD of two univariate polynomials via Euclidean algorithm"
}


def polynomial_lcm(x):
    """LCM of two univariate polynomials: LCM(P, Q) = P * Q / GCD(P, Q).
    Input: array of length 2n. Output: polynomial.
    """
    n = len(x) // 2
    if n < 1:
        return x.copy()
    p_coeffs = x[:n]
    q_coeffs = x[n:2*n]
    gcd_coeffs = polynomial_gcd_univariate(x)
    # P * Q using convolution
    prod = np.convolve(p_coeffs, q_coeffs)
    # Divide by GCD
    if len(gcd_coeffs) > 0 and not (len(gcd_coeffs) == 1 and abs(gcd_coeffs[0]) < 1e-12):
        _, lcm = np.polydiv(prod[::-1], gcd_coeffs[::-1])
        # Actually we need quotient, not remainder
        quotient, remainder = np.polydiv(prod[::-1], gcd_coeffs[::-1])
        result = quotient[::-1]
        # Trim
        while len(result) > 1 and abs(result[-1]) < 1e-10:
            result = result[:-1]
        return result
    return prod


OPERATIONS["polynomial_lcm"] = {
    "fn": polynomial_lcm,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "LCM of two univariate polynomials"
}


def polynomial_remainder(x):
    """Remainder of dividing first polynomial by second.
    Input: array of length 2n. Output: polynomial.
    """
    n = len(x) // 2
    if n < 1:
        return x.copy()
    p = x[:n]
    q = x[n:2*n]
    # Remove trailing zeros
    q_trimmed = np.trim_zeros(q, 'b')
    if len(q_trimmed) == 0:
        return p  # division by zero polynomial
    _, r = np.polydiv(p[::-1], q_trimmed[::-1])
    result = r[::-1]
    while len(result) > 1 and abs(result[-1]) < 1e-10:
        result = result[:-1]
    return result


OPERATIONS["polynomial_remainder"] = {
    "fn": polynomial_remainder,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "Remainder of polynomial division P mod Q"
}


def leading_monomial(x):
    """Leading monomial (coefficient and degree) of a univariate polynomial.
    Input: array of coefficients [a0, a1, ..., an]. Output: array [degree, leading_coeff].
    """
    coeffs = np.array(x)
    # Find highest nonzero coefficient
    for i in range(len(coeffs) - 1, -1, -1):
        if abs(coeffs[i]) > 1e-12:
            return np.array([float(i), coeffs[i]])
    return np.array([0.0, 0.0])


OPERATIONS["leading_monomial"] = {
    "fn": leading_monomial,
    "input_type": "array",
    "output_type": "array",
    "description": "Leading monomial [degree, coefficient] of a univariate polynomial"
}


def s_polynomial(x):
    """S-polynomial of two univariate polynomials (used in Buchberger's algorithm).
    S(f, g) = (LCM(LM(f), LM(g)) / LT(f)) * f - (LCM(LM(f), LM(g)) / LT(g)) * g.
    For univariate: if deg(f) = m, deg(g) = n with m >= n,
    S(f, g) = f - (lc(f)/lc(g)) * x^{m-n} * g.
    Input: array of length 2k. Output: polynomial.
    """
    k = len(x) // 2
    if k < 1:
        return np.array([0.0])
    f = x[:k].copy()
    g = x[k:2*k].copy()
    # Trim
    while len(f) > 1 and abs(f[-1]) < 1e-12:
        f = f[:-1]
    while len(g) > 1 and abs(g[-1]) < 1e-12:
        g = g[:-1]
    deg_f = len(f) - 1
    deg_g = len(g) - 1
    if abs(g[-1]) < 1e-12:
        return f
    lcm_deg = max(deg_f, deg_g)
    # Multiply f by x^{lcm_deg - deg_f} / lc(f) and g by x^{lcm_deg - deg_g} / lc(g)
    f_scaled = np.zeros(lcm_deg + 1)
    g_scaled = np.zeros(lcm_deg + 1)
    shift_f = lcm_deg - deg_f
    shift_g = lcm_deg - deg_g
    f_scaled[shift_f:shift_f + len(f)] = f / f[-1]
    g_scaled[shift_g:shift_g + len(g)] = g / g[-1]
    result = f_scaled - g_scaled
    # Trim
    while len(result) > 1 and abs(result[-1]) < 1e-10:
        result = result[:-1]
    return result


OPERATIONS["s_polynomial"] = {
    "fn": s_polynomial,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "S-polynomial of two univariate polynomials (Buchberger algorithm step)"
}


def buchberger_criterion_check(x):
    """Buchberger's criterion: check if the S-polynomial reduces to zero.
    If S(f, g) reduces to 0 mod {f, g}, the pair is unnecessary.
    Input: array of length 2k. Output: integer (1 if reduces to 0, 0 otherwise).
    """
    s_poly = s_polynomial(x)
    # Check if the S-polynomial is approximately zero
    if np.max(np.abs(s_poly)) < 1e-8:
        return np.int64(1)
    # Try reducing by both polynomials
    k = len(x) // 2
    f = x[:k]
    g = x[k:2*k]
    f_trimmed = np.trim_zeros(f, 'b')
    g_trimmed = np.trim_zeros(g, 'b')
    remainder = s_poly.copy()
    # Reduce by f
    if len(f_trimmed) > 0 and abs(f_trimmed[-1]) > 1e-12:
        _, remainder = np.polydiv(remainder[::-1], f_trimmed[::-1])
        remainder = remainder[::-1]
    # Reduce by g
    if len(g_trimmed) > 0 and abs(g_trimmed[-1]) > 1e-12:
        _, remainder = np.polydiv(remainder[::-1], g_trimmed[::-1])
        remainder = remainder[::-1]
    if np.max(np.abs(remainder)) < 1e-8:
        return np.int64(1)
    return np.int64(0)


OPERATIONS["buchberger_criterion_check"] = {
    "fn": buchberger_criterion_check,
    "input_type": "array",
    "output_type": "integer",
    "description": "Check if S-polynomial reduces to zero (Buchberger criterion)"
}


def ideal_membership_test_univariate(x):
    """Test if a polynomial f is in the ideal generated by g (univariate case).
    f in <g> iff g divides f, i.e., f mod g == 0.
    Input: array of length 2k, first half f, second half g. Output: integer (1=yes, 0=no).
    """
    k = len(x) // 2
    if k < 1:
        return np.int64(0)
    f = x[:k]
    g = x[k:2*k]
    g_trimmed = np.trim_zeros(g, 'b')
    if len(g_trimmed) == 0:
        return np.int64(0)
    f_trimmed = np.trim_zeros(f, 'b')
    if len(f_trimmed) == 0:
        return np.int64(1)  # 0 is in every ideal
    _, r = np.polydiv(f_trimmed[::-1], g_trimmed[::-1])
    if np.max(np.abs(r)) < 1e-8:
        return np.int64(1)
    return np.int64(0)


OPERATIONS["ideal_membership_test_univariate"] = {
    "fn": ideal_membership_test_univariate,
    "input_type": "array",
    "output_type": "integer",
    "description": "Test if polynomial f belongs to ideal <g> (univariate divisibility test)"
}


def resultant_2_polynomials(x):
    """Resultant of two univariate polynomials.
    The resultant is the determinant of the Sylvester matrix.
    Input: array of length 2k. Output: scalar.
    """
    k = len(x) // 2
    if k < 1:
        return np.float64(0.0)
    f = np.trim_zeros(x[:k], 'b')
    g = np.trim_zeros(x[k:2*k], 'b')
    if len(f) == 0 or len(g) == 0:
        return np.float64(0.0)
    m = len(f) - 1  # degree of f
    n = len(g) - 1  # degree of g
    if m == 0 and n == 0:
        return np.float64(0.0)
    # Build Sylvester matrix of size (m+n) x (m+n)
    size = m + n
    if size == 0:
        return np.float64(f[0] if len(f) > 0 else 0.0)
    S = np.zeros((size, size))
    # f coefficients in decreasing order for rows 0..n-1
    f_rev = f[::-1]
    for i in range(n):
        for j, c in enumerate(f_rev):
            if i + j < size:
                S[i, i + j] = c
    # g coefficients in decreasing order for rows n..m+n-1
    g_rev = g[::-1]
    for i in range(m):
        for j, c in enumerate(g_rev):
            if i + j < size:
                S[n + i, i + j] = c
    return np.float64(np.linalg.det(S))


OPERATIONS["resultant_2_polynomials"] = {
    "fn": resultant_2_polynomials,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Resultant of two univariate polynomials via Sylvester matrix"
}


def discriminant_polynomial(x):
    """Discriminant of a univariate polynomial.
    disc(f) = (-1)^{n(n-1)/2} * Res(f, f') / lc(f).
    Input: array of coefficients. Output: scalar.
    """
    f = np.trim_zeros(x, 'b')
    if len(f) <= 1:
        return np.float64(0.0)
    n = len(f) - 1  # degree
    lc = f[-1]
    if abs(lc) < 1e-12:
        return np.float64(0.0)
    # Compute f' (derivative)
    fp = np.array([f[i] * i for i in range(1, len(f))])
    if len(fp) == 0:
        return np.float64(0.0)
    # Resultant of f and f'
    combined = np.concatenate([f, fp])
    res = resultant_2_polynomials(combined)
    sign = (-1)**(n * (n - 1) // 2)
    disc = sign * res / lc
    return np.float64(disc)


OPERATIONS["discriminant_polynomial"] = {
    "fn": discriminant_polynomial,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Discriminant of a univariate polynomial via resultant"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
