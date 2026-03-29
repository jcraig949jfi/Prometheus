"""
Modular Arithmetic Exotic — weird modular structures

Connects to: [number_theory, cryptography, algebraic_structures, finite_fields]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "modular_arithmetic_exotic"
OPERATIONS = {}


def chinese_remainder_solve(x):
    """Solve system of congruences via Chinese Remainder Theorem.
    Input pairs: [r1, m1, r2, m2, ...] meaning x ≡ r_i (mod m_i).
    Returns the smallest non-negative solution.
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    pairs = []
    for i in range(0, len(x) - 1, 2):
        r = int(np.round(np.abs(x[i])))
        m = int(np.round(np.abs(x[i+1])))
        if m > 0:
            pairs.append((r % m, m))
    if not pairs:
        return 0.0

    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        g, x1, y1 = extended_gcd(b % a, a)
        return g, y1 - (b // a) * x1, x1

    r, m = pairs[0]
    for r2, m2 in pairs[1:]:
        g, p, q = extended_gcd(m, m2)
        if (r2 - r) % g != 0:
            return -1.0  # No solution
        lcm = m * m2 // g
        r = (r + m * ((r2 - r) // g) * p) % lcm
        m = lcm
    return float(r)

OPERATIONS["chinese_remainder_solve"] = {
    "fn": chinese_remainder_solve,
    "input_type": "array",
    "output_type": "scalar",
    "description": "CRT solver: find x satisfying system of congruences"
}


def primitive_root_find(x):
    """Find the smallest primitive root modulo p for p = first element.
    A primitive root g has multiplicative order phi(p) = p-1.
    Input: array (first element used as modulus). Output: scalar."""
    x = np.asarray(x, dtype=float)
    p = int(np.round(np.abs(x[0])))
    if p < 2:
        return 0.0
    # Ensure p is prime-ish (use small p for speed)
    p = min(p, 1000)

    def euler_phi(n):
        result = n
        d = 2
        temp = n
        while d * d <= temp:
            if temp % d == 0:
                while temp % d == 0:
                    temp //= d
                result -= result // d
            d += 1
        if temp > 1:
            result -= result // temp
        return result

    phi = euler_phi(p)
    if phi == 0:
        return 0.0

    # Factor phi
    factors = []
    temp = phi
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)

    for g in range(2, p):
        is_primitive = True
        for f in factors:
            if pow(g, phi // f, p) == 1:
                is_primitive = False
                break
        if is_primitive:
            return float(g)
    return 0.0

OPERATIONS["primitive_root_find"] = {
    "fn": primitive_root_find,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Find smallest primitive root modulo p"
}


def quadratic_residue_count(x):
    """Count quadratic residues modulo n. QR(n) = number of distinct a^2 mod n.
    Input: array (first element = modulus). Output: scalar."""
    x = np.asarray(x, dtype=float)
    n = int(np.round(np.abs(x[0])))
    n = max(2, min(n, 10000))
    residues = set()
    for a in range(n):
        residues.add((a * a) % n)
    return float(len(residues))

OPERATIONS["quadratic_residue_count"] = {
    "fn": quadratic_residue_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count of distinct quadratic residues modulo n"
}


def legendre_symbol(x):
    """Compute the Legendre symbol (a/p) for each element a mod p.
    p = last element (must be odd prime). Returns array of {-1, 0, 1}.
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return np.array([0.0])
    p = int(np.round(np.abs(x[-1])))
    p = max(3, p)
    # Make p odd
    if p % 2 == 0:
        p += 1
    result = []
    for val in x[:-1]:
        a = int(np.round(val)) % p
        if a == 0:
            result.append(0.0)
        else:
            # Euler's criterion: (a/p) = a^((p-1)/2) mod p
            ls = pow(a, (p - 1) // 2, p)
            result.append(float(ls if ls <= 1 else -1))  # p-1 ≡ -1
    return np.array(result)

OPERATIONS["legendre_symbol"] = {
    "fn": legendre_symbol,
    "input_type": "array",
    "output_type": "array",
    "description": "Legendre symbol (a/p) via Euler's criterion for each element"
}


def jacobi_symbol(x):
    """Compute the Jacobi symbol (a/n) where a = first element, n = second.
    Generalizes Legendre to composite odd n.
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return 0.0
    a = int(np.round(x[0]))
    n = int(np.round(np.abs(x[1])))
    if n <= 0 or n % 2 == 0:
        return 0.0
    a = a % n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n
    return float(result) if n == 1 else 0.0

OPERATIONS["jacobi_symbol"] = {
    "fn": jacobi_symbol,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Jacobi symbol (a/n) via quadratic reciprocity algorithm"
}


def carmichael_lambda(x):
    """Compute Carmichael's lambda function lambda(n) = lcm of lambda(p^k).
    This is the smallest m such that a^m ≡ 1 (mod n) for all gcd(a,n)=1.
    Input: array (first element = n). Output: scalar."""
    x = np.asarray(x, dtype=float)
    n = int(np.round(np.abs(x[0])))
    n = max(1, min(n, 100000))
    if n <= 2:
        return 1.0

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    def lcm(a, b):
        return a * b // gcd(a, b)

    # Factor n
    factors = {}
    temp = n
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1

    result = 1
    for p, k in factors.items():
        if p == 2:
            if k == 1:
                lam = 1
            elif k == 2:
                lam = 2
            else:
                lam = 2 ** (k - 2)
        else:
            lam = (p - 1) * (p ** (k - 1))
        result = lcm(result, lam)
    return float(result)

OPERATIONS["carmichael_lambda"] = {
    "fn": carmichael_lambda,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Carmichael lambda function: smallest universal exponent mod n"
}


def multiplicative_order(x):
    """Compute multiplicative order of a modulo n: smallest k>0 with a^k ≡ 1 (mod n).
    Input: array [a, n]. Output: scalar."""
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return 0.0
    a = int(np.round(x[0]))
    n = int(np.round(np.abs(x[1])))
    n = max(2, min(n, 100000))
    a = a % n
    if a == 0:
        return 0.0
    # Check gcd(a, n) = 1
    def gcd(x, y):
        while y:
            x, y = y, x % y
        return x
    if gcd(a, n) != 1:
        return 0.0  # Order undefined
    power = a
    for k in range(1, n + 1):
        if power % n == 1:
            return float(k)
        power = (power * a) % n
    return 0.0

OPERATIONS["multiplicative_order"] = {
    "fn": multiplicative_order,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Multiplicative order of a mod n: smallest k with a^k ≡ 1"
}


def discrete_logarithm_shanks(x):
    """Baby-step giant-step algorithm for discrete log: find k such that g^k ≡ h (mod p).
    Input: [g, h, p]. Output: scalar (k, or -1 if not found)."""
    x = np.asarray(x, dtype=float)
    if len(x) < 3:
        return -1.0
    g = int(np.round(np.abs(x[0])))
    h = int(np.round(np.abs(x[1])))
    p = int(np.round(np.abs(x[2])))
    p = max(2, min(p, 100000))
    g = g % p
    h = h % p
    if g == 0:
        return -1.0

    m = int(np.ceil(np.sqrt(p)))
    # Baby steps: g^j for j = 0..m-1
    table = {}
    power = 1
    for j in range(m):
        table[power] = j
        power = (power * g) % p

    # Giant step factor: g^(-m) mod p
    g_inv_m = pow(g, p - 1 - m, p)  # Using Fermat's little theorem

    # Giant steps
    gamma = h
    for i in range(m):
        if gamma in table:
            return float(i * m + table[gamma])
        gamma = (gamma * g_inv_m) % p

    return -1.0

OPERATIONS["discrete_logarithm_shanks"] = {
    "fn": discrete_logarithm_shanks,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Baby-step giant-step discrete logarithm: find k with g^k ≡ h (mod p)"
}


def sum_of_squares_representation(x):
    """Find representation of n as sum of two squares: n = a^2 + b^2.
    Returns [a, b] or [0, 0] if impossible.
    Input: array (first element = n). Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(np.round(np.abs(x[0])))
    n = max(0, min(n, 1000000))
    if n == 0:
        return np.array([0.0, 0.0])
    max_a = int(np.sqrt(n))
    for a in range(max_a + 1):
        remainder = n - a * a
        b = int(np.round(np.sqrt(remainder)))
        if b * b == remainder:
            return np.array([float(a), float(b)])
    return np.array([0.0, 0.0])

OPERATIONS["sum_of_squares_representation"] = {
    "fn": sum_of_squares_representation,
    "input_type": "array",
    "output_type": "array",
    "description": "Represent n as sum of two squares a^2 + b^2"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
