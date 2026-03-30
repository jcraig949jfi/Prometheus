"""
p-adic Numbers — p-adic norm, p-adic expansion, Hensel's lemma approximation

Connects to: [number_theory, algebraic_number_theory, analysis, cryptography]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "p_adic_numbers"
OPERATIONS = {}

DEFAULT_PRIME = 5


def _valuation(n, p):
    """Compute the p-adic valuation of integer n: largest k such that p^k | n."""
    if n == 0:
        return float('inf')
    n = abs(int(round(n)))
    p = int(p)
    v = 0
    while n % p == 0:
        v += 1
        n //= p
    return v


def p_adic_valuation(x):
    """p-adic valuation v_p(n) for each element (p=5).
    Input: array. Output: array."""
    p = DEFAULT_PRIME
    result = np.array([float(_valuation(xi, p)) for xi in x])
    return result


OPERATIONS["p_adic_valuation"] = {
    "fn": p_adic_valuation,
    "input_type": "array",
    "output_type": "array",
    "description": "p-adic valuation v_p(n) for each element with p=5"
}


def p_adic_norm(x):
    """p-adic norm |n|_p = p^{-v_p(n)} for each element (p=5).
    Input: array. Output: array."""
    p = DEFAULT_PRIME
    vals = p_adic_valuation(x)
    result = np.where(np.isinf(vals), 0.0, float(p) ** (-vals))
    return result


OPERATIONS["p_adic_norm"] = {
    "fn": p_adic_norm,
    "input_type": "array",
    "output_type": "array",
    "description": "p-adic norm |n|_p = p^{-v_p(n)} for each element with p=5"
}


def p_adic_expansion(x):
    """p-adic expansion of first element as array of digits (p=5, up to 10 digits).
    Writes n in base p: n = a_0 + a_1*p + a_2*p^2 + ...
    Input: array. Output: array."""
    p = DEFAULT_PRIME
    n = abs(int(round(x[0])))
    digits = []
    for _ in range(10):
        digits.append(float(n % p))
        n //= p
        if n == 0:
            break
    return np.array(digits)


OPERATIONS["p_adic_expansion"] = {
    "fn": p_adic_expansion,
    "input_type": "array",
    "output_type": "array",
    "description": "p-adic digit expansion (base 5) of first element, least significant first"
}


def p_adic_distance(x):
    """p-adic distance |a - b|_p between first two elements (p=5).
    Input: array (at least 2 elements). Output: scalar."""
    p = DEFAULT_PRIME
    diff = int(round(x[0])) - int(round(x[1]))
    if diff == 0:
        return 0.0
    v = _valuation(diff, p)
    return float(p ** (-v))


OPERATIONS["p_adic_distance"] = {
    "fn": p_adic_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "p-adic distance between first two elements with p=5"
}


def hensel_lift_sqrt(x):
    """Hensel's lemma: lift sqrt(a) mod p to sqrt(a) mod p^k.
    Starting from a root r of x^2 - a ≡ 0 (mod p), iterate
    r_{k+1} = r_k - (r_k^2 - a) / (2*r_k) mod p^{k+1}.
    Uses first element as a, p=5. Input: array. Output: array."""
    p = DEFAULT_PRIME
    a = int(round(abs(x[0])))
    if a == 0:
        return np.array([0.0])
    # Find initial root mod p by brute force
    r = None
    for candidate in range(p):
        if (candidate * candidate - a) % p == 0:
            r = candidate
            break
    if r is None:
        # a is not a quadratic residue mod p
        return np.array([float('nan')])
    # Hensel lifting iterations
    modulus = p
    results = [float(r)]
    for _ in range(5):
        modulus *= p
        # Newton step in Z/modulus: r = r - (r^2 - a) * inv(2r) mod modulus
        f_val = r * r - a
        deriv = 2 * r
        # Modular inverse of deriv mod modulus (if it exists)
        try:
            inv_deriv = pow(deriv, -1, modulus)
        except (ValueError, ZeroDivisionError):
            break
        r = (r - f_val * inv_deriv) % modulus
        results.append(float(r))
    return np.array(results)


OPERATIONS["hensel_lift_sqrt"] = {
    "fn": hensel_lift_sqrt,
    "input_type": "array",
    "output_type": "array",
    "description": "Hensel lift: approximate sqrt(a) in p-adic integers via Newton iteration (p=5)"
}


def p_adic_absolute_value(x):
    """p-adic absolute value for rationals: |a/b|_p = p^{v_p(b)-v_p(a)}.
    Treats pairs (x[0],x[1]), (x[2],x[3]), ... as numerator/denominator.
    Input: array. Output: array."""
    p = DEFAULT_PRIME
    results = []
    for i in range(0, len(x) - 1, 2):
        a = int(round(x[i]))
        b = int(round(x[i + 1]))
        if a == 0:
            results.append(0.0)
        elif b == 0:
            results.append(float('inf'))
        else:
            va = _valuation(a, p)
            vb = _valuation(b, p)
            results.append(float(p) ** (vb - va))
    if len(x) % 2 == 1:
        # Last unpaired element treated as integer
        a = int(round(x[-1]))
        if a == 0:
            results.append(0.0)
        else:
            va = _valuation(a, p)
            results.append(float(p) ** (-va))
    return np.array(results)


OPERATIONS["p_adic_absolute_value"] = {
    "fn": p_adic_absolute_value,
    "input_type": "array",
    "output_type": "array",
    "description": "p-adic absolute value treating consecutive pairs as numerator/denominator"
}


def p_adic_digits_sum(x):
    """Sum of p-adic digits (base p=5) for each element.
    This is the digit sum in base p representation.
    Input: array. Output: array."""
    p = DEFAULT_PRIME
    results = []
    for xi in x:
        n = abs(int(round(xi)))
        s = 0
        while n > 0:
            s += n % p
            n //= p
        results.append(float(s))
    return np.array(results)


OPERATIONS["p_adic_digits_sum"] = {
    "fn": p_adic_digits_sum,
    "input_type": "array",
    "output_type": "array",
    "description": "Sum of digits in base-p (p=5) representation for each element"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
