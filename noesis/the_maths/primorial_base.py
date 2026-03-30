"""
Primorial Base -- Positions weighted by primorials (2, 6, 30, 210, 2310...).

Connects to: [factoradic, mixed_radix, p_adic_expansions, modular_arithmetic_exotic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "primorial_base"
OPERATIONS = {}

# First primes and primorials
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
PRIMORIALS = [1]
for p in PRIMES:
    PRIMORIALS.append(PRIMORIALS[-1] * p)
# PRIMORIALS = [1, 2, 6, 30, 210, 2310, ...]


def to_primorial_base(x):
    """Convert integer to primorial base digits. Input: array (first elem). Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0])))
    if n == 0:
        return np.array([0.0])
    digits = []
    for i in range(len(PRIMES) - 1, -1, -1):
        if i < len(PRIMORIALS) - 1:
            d = n // PRIMORIALS[i + 1]
            # Digit range for position i is [0, PRIMES[i]-1] but we use standard mixed-radix
            pass
    # Mixed radix decomposition: position i has radix PRIMES[i]
    digits = []
    remaining = n
    for i in range(len(PRIMES)):
        digits.append(remaining % PRIMES[i])
        remaining //= PRIMES[i]
        if remaining == 0:
            break
    # Reverse so most significant first
    return np.array(digits[::-1], dtype=float)


OPERATIONS["to_primorial_base"] = {
    "fn": to_primorial_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert integer to primorial base representation"
}


def from_primorial_base(digits):
    """Convert primorial base digits to integer. Input: array. Output: scalar."""
    digits = np.asarray(digits, dtype=int)
    # Digits are MSB first; reverse to get position 0 = least significant
    rev = digits[::-1]
    result = 0
    weight = 1
    for i, d in enumerate(rev):
        result += int(d) * weight
        if i < len(PRIMES):
            weight *= PRIMES[i]
    return float(result)


OPERATIONS["from_primorial_base"] = {
    "fn": from_primorial_base,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert primorial base digits back to integer"
}


def primorial_digit_pattern(x):
    """Show digit ranges for each primorial position. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n_positions = min(int(abs(x[0])) + 3, len(PRIMES))
    # Each position i allows digits [0, prime_i - 1]
    return np.array([float(PRIMES[i] - 1) for i in range(n_positions)])


OPERATIONS["primorial_digit_pattern"] = {
    "fn": primorial_digit_pattern,
    "input_type": "array",
    "output_type": "array",
    "description": "Show maximum digit at each primorial base position"
}


def prime_fingerprint(x):
    """Compute prime fingerprint: residues mod first few primes. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = []
    for val in x:
        n = int(round(val))
        for p in PRIMES[:5]:
            results.append(float(n % p))
    return np.array(results)


OPERATIONS["prime_fingerprint"] = {
    "fn": prime_fingerprint,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute residues mod first primes (prime fingerprint)"
}


def crt_connection(x):
    """Show CRT decomposition: primorial base digits ARE the CRT residues. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0])))
    # CRT: n mod p_i for each prime
    crt_residues = np.array([float(n % p) for p in PRIMES[:6]])
    # Primorial base digits (least significant)
    pb = to_primorial_base(np.array([float(n)]))
    pb_rev = pb[::-1]  # LSB first
    # The least significant digit equals n mod 2, next involves n mod 3, etc.
    return np.concatenate([crt_residues, pb_rev[:6]])


OPERATIONS["crt_connection"] = {
    "fn": crt_connection,
    "input_type": "array",
    "output_type": "array",
    "description": "Show how primorial base digits relate to CRT residues"
}


def primorial_add(x):
    """Add two numbers in primorial base. Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    a = int(round(from_primorial_base(x[:mid].astype(int))))
    b = int(round(from_primorial_base(x[mid:].astype(int))))
    return to_primorial_base(np.array([float(a + b)]))


OPERATIONS["primorial_add"] = {
    "fn": primorial_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two primorial base numbers"
}


def primorial_regularity(x):
    """Measure regularity of primorial representations. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        n = max(1, int(round(abs(val))))
        digits = to_primorial_base(np.array([float(n)]))
        # Regularity: ratio of non-zero digits to total
        results[i] = float(np.sum(digits > 0)) / max(1, len(digits))
    return results


OPERATIONS["primorial_regularity"] = {
    "fn": primorial_regularity,
    "input_type": "array",
    "output_type": "array",
    "description": "Measure density of non-zero digits in primorial representation"
}


def primorial_nth_weight(x):
    """Return the nth primorial weight. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = np.zeros(len(x))
    for i, val in enumerate(x):
        idx = max(0, min(int(round(abs(val))), len(PRIMORIALS) - 1))
        results[i] = float(PRIMORIALS[idx])
    return results


OPERATIONS["primorial_nth_weight"] = {
    "fn": primorial_nth_weight,
    "input_type": "array",
    "output_type": "array",
    "description": "Return the nth primorial (product of first n primes)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
