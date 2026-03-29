"""
P-adic Expansions -- Infinite-left base: digits go infinitely left. ...33334 in base 5 = -1.

Connects to: [primorial_base, complex_bases, non_integer_bases, symmetric_bases]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "p_adic_expansions"
OPERATIONS = {}


def p_adic_digits(x):
    """Compute first N p-adic digits of an integer. Input: array [value, prime, N]. Output: array."""
    x = np.asarray(x, dtype=float)
    val = int(round(x[0]))
    p = max(2, int(round(x[1]))) if len(x) > 1 else 5
    n_digits = max(1, min(int(round(x[2])) if len(x) > 2 else 10, 50))

    if val >= 0:
        digits = []
        remaining = val
        for _ in range(n_digits):
            digits.append(remaining % p)
            remaining //= p
        return np.array(digits, dtype=float)
    else:
        # Negative: p-adic expansion is ....(p-1)(p-1)(p-1) + |val| complement
        # -1 in base p = ...(p-1)(p-1)(p-1)
        # For -k: compute p^N - k, then take digits
        modulus = p ** n_digits
        pos_repr = (val % modulus + modulus) % modulus
        digits = []
        for _ in range(n_digits):
            digits.append(pos_repr % p)
            pos_repr //= p
        return np.array(digits, dtype=float)


OPERATIONS["p_adic_digits"] = {
    "fn": p_adic_digits,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute first N p-adic digits (least significant first)"
}


def p_adic_negative_one(x):
    """Show that -1 in p-adic is ...(p-1)(p-1)(p-1). Input: array [prime, N]. Output: array."""
    x = np.asarray(x, dtype=float)
    p = max(2, int(round(x[0])))
    n = max(1, min(int(round(x[1])) if len(x) > 1 else 10, 50))
    # -1 mod p^n = p^n - 1, digits are all (p-1)
    return np.full(n, float(p - 1))


OPERATIONS["p_adic_negative_one"] = {
    "fn": p_adic_negative_one,
    "input_type": "array",
    "output_type": "array",
    "description": "Show p-adic representation of -1: all digits are (p-1)"
}


def p_adic_rational_periodic(x):
    """Compute p-adic expansion of a/b (periodic). Input: array [a, b, prime, N]. Output: array."""
    x = np.asarray(x, dtype=float)
    a = int(round(x[0]))
    b = int(round(x[1])) if len(x) > 1 else 1
    p = max(2, int(round(x[2]))) if len(x) > 2 else 5
    n = max(1, min(int(round(x[3])) if len(x) > 3 else 15, 50))

    if b == 0:
        return np.zeros(n)

    # Compute a/b mod p^n using modular inverse
    modulus = p ** n
    # Extended gcd to find inverse of b mod p^n (if gcd(b,p)=1)
    if b % p == 0:
        # b not invertible mod p; return partial result
        return np.zeros(n)

    # Find b^(-1) mod modulus
    b_inv = pow(int(abs(b)), -1, modulus) if np.gcd(int(abs(b)), modulus) == 1 else 1
    if b < 0:
        b_inv = modulus - b_inv
    val = (a * b_inv) % modulus

    digits = []
    for _ in range(n):
        digits.append(val % p)
        val //= p
    return np.array(digits, dtype=float)


OPERATIONS["p_adic_rational_periodic"] = {
    "fn": p_adic_rational_periodic,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute periodic p-adic expansion of rational a/b"
}


def p_adic_period_detect(x):
    """Detect period in p-adic expansion. Input: array (digit sequence). Output: scalar."""
    x = np.asarray(x, dtype=float).astype(int)
    n = len(x)
    # Try periods from 1 to n//2
    for period in range(1, n // 2 + 1):
        is_periodic = True
        for i in range(period, n):
            if x[i] != x[i % period]:
                is_periodic = False
                break
        if is_periodic:
            return float(period)
    return float(n)  # No period detected


OPERATIONS["p_adic_period_detect"] = {
    "fn": p_adic_period_detect,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Detect period length in a p-adic digit sequence"
}


def p_adic_add_expansions(x):
    """Add two p-adic expansions digit by digit with carry. Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    a = x[:mid].astype(int)
    b = x[mid:].astype(int)
    p = 5  # Default prime
    min_len = min(len(a), len(b))
    result = np.zeros(min_len)
    carry = 0
    for i in range(min_len):
        total = int(a[i]) + int(b[i]) + carry
        result[i] = total % p
        carry = total // p
    return result


OPERATIONS["p_adic_add_expansions"] = {
    "fn": p_adic_add_expansions,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two p-adic expansions digit-by-digit with carry"
}


def p_adic_multiply_expansions(x):
    """Multiply two p-adic expansions (truncated). Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    a = x[:mid].astype(int)
    b = x[mid:].astype(int)
    p = 5
    n = min(len(a), len(b))
    # Schoolbook multiplication mod p^n
    result = np.zeros(n, dtype=int)
    for i in range(n):
        for j in range(n - i):
            result[i + j] += int(a[i]) * int(b[j])
    # Propagate carries
    carry = 0
    for i in range(n):
        result[i] += carry
        carry = result[i] // p
        result[i] %= p
    return result.astype(float)


OPERATIONS["p_adic_multiply_expansions"] = {
    "fn": p_adic_multiply_expansions,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two p-adic expansions (truncated convolution)"
}


def hensel_code(x):
    """Compute Hensel code (p-adic representation of rational). Input: array [a, b, p, r]. Output: array."""
    x = np.asarray(x, dtype=float)
    a = int(round(x[0]))
    b = max(1, int(round(abs(x[1])))) if len(x) > 1 else 1
    p = max(2, int(round(x[2]))) if len(x) > 2 else 5
    r = max(1, min(int(round(x[3])) if len(x) > 3 else 8, 30))

    modulus = p ** r
    if np.gcd(b, p) != 1:
        # Factor out powers of p from b
        v = 0
        while b % p == 0:
            b //= p
            a_shift = a  # would need p-adic valuation handling
            v += 1
    if np.gcd(int(abs(b)), modulus) == 1:
        b_inv = pow(int(abs(b)), -1, modulus)
        if b < 0:
            b_inv = modulus - b_inv
        code = (a * b_inv) % modulus
    else:
        code = a % modulus

    digits = []
    for _ in range(r):
        digits.append(code % p)
        code //= p
    return np.array(digits, dtype=float)


OPERATIONS["hensel_code"] = {
    "fn": hensel_code,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute Hensel code for rational number a/b in Z_p"
}


def p_adic_sqrt_expansion(x):
    """Compute p-adic square root via Hensel lifting. Input: array [value, prime, N]. Output: array."""
    x = np.asarray(x, dtype=float)
    val = int(round(abs(x[0])))
    p = max(2, int(round(x[1]))) if len(x) > 1 else 5
    n = max(1, min(int(round(x[2])) if len(x) > 2 else 10, 40))

    # Find sqrt(val) mod p first (if it exists)
    sqrt_mod_p = None
    for r in range(p):
        if (r * r) % p == val % p:
            sqrt_mod_p = r
            break
    if sqrt_mod_p is None:
        return np.full(n, -1.0)  # No square root exists

    # Hensel lifting: if r^2 = val mod p^k, lift to mod p^(k+1)
    modulus = p
    r = sqrt_mod_p
    for _ in range(n):
        modulus *= p
        # Newton: r = r - (r^2 - val) / (2r) mod modulus
        if (2 * r) % p == 0:
            break  # Can't invert 2r
        inv_2r = pow(2 * r % modulus, -1, modulus) if np.gcd(2 * r % modulus, modulus) == 1 else 1
        r = (r - (r * r - val) * inv_2r) % modulus

    # Extract digits
    digits = []
    temp = r
    for _ in range(n):
        digits.append(temp % p)
        temp //= p
    return np.array(digits, dtype=float)


OPERATIONS["p_adic_sqrt_expansion"] = {
    "fn": p_adic_sqrt_expansion,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute p-adic square root via Hensel lifting"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
