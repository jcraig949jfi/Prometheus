"""
q-Analogues — q-factorials, q-binomials, q-exponentials, q-series

Connects to: [umbral_calculus, combinatorics, partition_theory, tropical_semirings]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "q_analogues"
OPERATIONS = {}


def _q_int(n, q):
    """Compute [n]_q = 1 + q + q^2 + ... + q^{n-1} = (1 - q^n)/(1 - q)."""
    if abs(q - 1.0) < 1e-12:
        return float(n)
    return (1.0 - q ** n) / (1.0 - q)


def _q_fact(n, q):
    """Compute [n]_q! = [1]_q * [2]_q * ... * [n]_q."""
    result = 1.0
    for k in range(1, n + 1):
        result *= _q_int(k, q)
    return result


def _q_poch(a, n, q):
    """q-Pochhammer (a;q)_n = prod_{k=0}^{n-1} (1 - a*q^k)."""
    result = 1.0
    for k in range(n):
        result *= (1.0 - a * q ** k)
    return result


def q_factorial(x):
    """Compute [n]_q! for n = index, q = x[index].
    Input: array. Output: array."""
    result = np.zeros(len(x))
    for i, q in enumerate(x):
        result[i] = _q_fact(i, q)
    return result


OPERATIONS["q_factorial"] = {
    "fn": q_factorial,
    "input_type": "array",
    "output_type": "array",
    "description": "q-factorial [k]_q! where q=x[k] for each index k"
}


def q_binomial(x):
    """Compute q-binomial coefficient [n choose k]_q.
    Uses n=len(x), k=n//2, q=x[0]. Input: array. Output: scalar."""
    n = len(x)
    k = n // 2
    q = x[0]
    if k < 0 or k > n:
        return 0.0
    # [n choose k]_q = [n]_q! / ([k]_q! * [n-k]_q!)
    num = _q_fact(n, q)
    den = _q_fact(k, q) * _q_fact(n - k, q)
    if abs(den) < 1e-30:
        return 0.0
    return float(num / den)


OPERATIONS["q_binomial"] = {
    "fn": q_binomial,
    "input_type": "array",
    "output_type": "scalar",
    "description": "q-binomial coefficient [n choose n//2]_q with q=x[0]"
}


def q_exponential(x):
    """Compute q-exponential e_q(x) = sum_{n=0}^{N} x^n / [n]_q!
    with q=0.5 and N=20. Input: array. Output: array."""
    q = 0.5
    N = 20
    result = np.zeros(len(x))
    for i, xv in enumerate(x):
        s = 0.0
        for n in range(N + 1):
            denom = _q_fact(n, q)
            if abs(denom) > 1e-30:
                s += xv ** n / denom
        result[i] = s
    return result


OPERATIONS["q_exponential"] = {
    "fn": q_exponential,
    "input_type": "array",
    "output_type": "array",
    "description": "q-exponential e_q(x) with q=0.5, truncated at 20 terms"
}


def q_pochhammer(x):
    """Compute q-Pochhammer symbol (x[0]; q)_n for q=x[1] if len>=2, else q=0.5.
    n = len(x). Input: array. Output: scalar."""
    a = x[0]
    q = x[1] if len(x) >= 2 else 0.5
    n = len(x)
    return float(_q_poch(a, n, q))


OPERATIONS["q_pochhammer"] = {
    "fn": q_pochhammer,
    "input_type": "array",
    "output_type": "scalar",
    "description": "q-Pochhammer symbol (a; q)_n"
}


def q_integer(x):
    """Compute [n]_q for each element, with q=0.5. Input: array. Output: array."""
    q = 0.5
    return np.array([_q_int(v, q) for v in x])


OPERATIONS["q_integer"] = {
    "fn": q_integer,
    "input_type": "array",
    "output_type": "array",
    "description": "q-integer [x_i]_q with q=0.5"
}


def q_analog_derivative(x):
    """q-derivative of polynomial with coefficients x. D_q p(t) at t=1 with q=0.5.
    D_q f(t) = (f(qt) - f(t)) / (qt - t). We return new polynomial coefficients
    a_k' = [k+1]_q * a_{k+1}. Input: array. Output: array."""
    q = 0.5
    n = len(x)
    if n <= 1:
        return np.array([0.0])
    result = np.zeros(n - 1)
    for k in range(n - 1):
        result[k] = _q_int(k + 1, q) * x[k + 1]
    return result


OPERATIONS["q_analog_derivative"] = {
    "fn": q_analog_derivative,
    "input_type": "array",
    "output_type": "array",
    "description": "q-derivative of polynomial (coefficients) with q=0.5"
}


def q_series_partial_sum(x):
    """Partial sum of the q-series sum_{n=0}^{N} x[0]^n * prod_{k=1}^{n}(1 - x[1]^k)
    where N = len(x). A Jacobi-theta-like partial sum. Input: array. Output: scalar."""
    if len(x) < 2:
        return float(x[0])
    a = x[0]
    q = x[1] if abs(x[1]) < 1.0 else 0.5
    N = len(x)
    s = 0.0
    prod = 1.0
    for n in range(N):
        s += a ** n * prod
        prod *= (1.0 - q ** (n + 1))
    return float(s)


OPERATIONS["q_series_partial_sum"] = {
    "fn": q_series_partial_sum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Partial sum of a q-series with parameters from x"
}


def q_hypergeometric_1phi0(x):
    """Compute 1phi0(a; -; q, z) = sum_{n=0}^{N} (a;q)_n / (q;q)_n * z^n.
    a=x[0], q=0.5, z=x[1] if available else 0.3, N=20. Input: array. Output: scalar."""
    a = x[0]
    q = 0.5
    z = x[1] if len(x) >= 2 else 0.3
    N = 20
    s = 0.0
    for n in range(N + 1):
        num = _q_poch(a, n, q)
        den = _q_poch(q, n, q)
        if abs(den) < 1e-30:
            break
        s += (num / den) * z ** n
    return float(s)


OPERATIONS["q_hypergeometric_1phi0"] = {
    "fn": q_hypergeometric_1phi0,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Basic hypergeometric series 1phi0(a; -; q, z)"
}


def ramanujan_q_series(x):
    """Compute Ramanujan's partial theta: sum_{n=0}^{N} q^{n(n+1)/2} * x[0]^n
    where q = x[1] if available (|q|<1), else q=0.5. N=30. Input: array. Output: scalar."""
    a = x[0]
    q = x[1] if len(x) >= 2 and abs(x[1]) < 1.0 else 0.5
    N = 30
    s = 0.0
    for n in range(N + 1):
        s += q ** (n * (n + 1) / 2.0) * a ** n
    return float(s)


OPERATIONS["ramanujan_q_series"] = {
    "fn": ramanujan_q_series,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Ramanujan partial theta series"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
