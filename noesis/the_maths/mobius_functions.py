"""
Mobius Functions — number-theoretic Mobius, Mobius inversion, Mertens function

Connects to: [number_theory, analytic_number_theory, combinatorics, algebra]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "mobius_functions"
OPERATIONS = {}


def _factorize(n):
    """Return list of (prime, exponent) pairs for n."""
    n = int(abs(n))
    if n <= 1:
        return []
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                n //= d
                exp += 1
            factors.append((d, exp))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return factors


def _mobius(n):
    """Compute mu(n) for a single integer."""
    n = int(abs(n))
    if n <= 0:
        return 0
    if n == 1:
        return 1
    factors = _factorize(n)
    for _, exp in factors:
        if exp > 1:
            return 0  # Not squarefree
    return (-1) ** len(factors)


def mobius_mu(x):
    """Compute the Mobius function mu(n) for each element.
    mu(n) = 0 if n has squared prime factor, (-1)^k if n is product of k distinct primes.
    Input: array. Output: array."""
    result = np.array([float(_mobius(max(1, int(abs(v))))) for v in x])
    return result


OPERATIONS["mobius_mu"] = {
    "fn": mobius_mu,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Mobius function mu(n) for each array element"
}


def mertens_function(x):
    """Compute the Mertens function M(n) = sum_{k=1}^{n} mu(k) for each element.
    Input: array. Output: array."""
    results = []
    for v in x:
        n = max(1, int(abs(v)))
        M = sum(_mobius(k) for k in range(1, n + 1))
        results.append(float(M))
    return np.array(results)


OPERATIONS["mertens_function"] = {
    "fn": mertens_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Mertens function M(n) = cumulative sum of mu(k) for k=1..n"
}


def euler_totient(x):
    """Compute Euler's totient function phi(n) for each element.
    phi(n) = n * product(1 - 1/p) for each prime p dividing n.
    Input: array. Output: array."""
    results = []
    for v in x:
        n = max(1, int(abs(v)))
        result = n
        temp = n
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                while temp % d == 0:
                    temp //= d
                result -= result // d
            d += 1
        if temp > 1:
            result -= result // temp
        results.append(float(result))
    return np.array(results)


OPERATIONS["euler_totient"] = {
    "fn": euler_totient,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Euler totient phi(n) for each array element"
}


def mobius_inversion(x):
    """Apply Mobius inversion: if g(n) = sum_{d|n} f(d), recover f(n).
    Given array as g values at indices 1..n, compute f via inversion.
    f(n) = sum_{d|n} mu(n/d) * g(d).
    Input: array. Output: array."""
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        ni = i + 1  # 1-indexed
        total = 0.0
        for d in range(1, ni + 1):
            if ni % d == 0:
                total += _mobius(ni // d) * x[d - 1]
        result[i] = total
    return result


OPERATIONS["mobius_inversion"] = {
    "fn": mobius_inversion,
    "input_type": "array",
    "output_type": "array",
    "description": "Applies Mobius inversion formula to recover f from its divisor sum"
}


def liouville_lambda(x):
    """Compute Liouville's lambda function for each element.
    lambda(n) = (-1)^Omega(n) where Omega(n) counts prime factors with multiplicity.
    Input: array. Output: array."""
    results = []
    for v in x:
        n = max(1, int(abs(v)))
        if n == 1:
            results.append(1.0)
            continue
        omega = sum(exp for _, exp in _factorize(n))
        results.append(float((-1) ** omega))
    return np.array(results)


OPERATIONS["liouville_lambda"] = {
    "fn": liouville_lambda,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Liouville lambda: (-1)^Omega(n) for each element"
}


def divisor_sum_mobius(x):
    """Compute divisor sum using Mobius function identity:
    sum_{d|n} mu(d) = [n==1] (Kronecker delta).
    Returns array where each element is sum_{d|n} mu(d).
    Input: array. Output: array."""
    results = []
    for v in x:
        n = max(1, int(abs(v)))
        total = 0
        for d in range(1, n + 1):
            if n % d == 0:
                total += _mobius(d)
        results.append(float(total))
    return np.array(results)


OPERATIONS["divisor_sum_mobius"] = {
    "fn": divisor_sum_mobius,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes sum of mu(d) over divisors d|n (equals 1 iff n=1, else 0)"
}


def squarefree_count(x):
    """Count squarefree numbers up to n for each element.
    Q(n) = sum_{k=1}^{n} |mu(k)| ~ 6n/pi^2.
    Input: array. Output: array."""
    results = []
    for v in x:
        n = max(1, int(abs(v)))
        count = sum(1 for k in range(1, n + 1) if _mobius(k) != 0)
        results.append(float(count))
    return np.array(results)


OPERATIONS["squarefree_count"] = {
    "fn": squarefree_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Counts squarefree integers up to n (where |mu(k)| = 1)"
}


def prime_omega_big(x):
    """Compute big Omega(n): number of prime factors counted with multiplicity.
    Input: array. Output: array."""
    results = []
    for v in x:
        n = max(1, int(abs(v)))
        if n == 1:
            results.append(0.0)
            continue
        omega = sum(exp for _, exp in _factorize(n))
        results.append(float(omega))
    return np.array(results)


OPERATIONS["prime_omega_big"] = {
    "fn": prime_omega_big,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Omega(n): prime factor count with multiplicity"
}


def prime_omega_small(x):
    """Compute small omega(n): number of distinct prime factors.
    Input: array. Output: array."""
    results = []
    for v in x:
        n = max(1, int(abs(v)))
        if n == 1:
            results.append(0.0)
            continue
        omega = len(_factorize(n))
        results.append(float(omega))
    return np.array(results)


OPERATIONS["prime_omega_small"] = {
    "fn": prime_omega_small,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes omega(n): count of distinct prime factors"
}


def mobius_transform(x):
    """Apply the Mobius transform (summatory): g(n) = sum_{d|n} f(d).
    This is the inverse of Mobius inversion.
    Input: array. Output: array."""
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        ni = i + 1
        total = 0.0
        for d in range(1, ni + 1):
            if ni % d == 0:
                total += x[d - 1]
        result[i] = total
    return result


OPERATIONS["mobius_transform"] = {
    "fn": mobius_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Applies Mobius transform (divisor sum): g(n) = sum_{d|n} f(d)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
