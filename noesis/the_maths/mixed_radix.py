"""
Mixed Radix -- Each position has a different radix. Time, calendars, combinatorial number system.

Connects to: [factoradic, primorial_base, balanced_ternary, bijective_bases]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import comb

FIELD_NAME = "mixed_radix"
OPERATIONS = {}


def mixed_radix_encode(x):
    """Encode integer into mixed radix with given bases. Input: array [value, b0, b1, ...]. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0])))
    bases = [max(2, int(round(b))) for b in x[1:]] if len(x) > 1 else [2, 3, 5, 7]
    digits = []
    for b in bases:
        digits.append(n % b)
        n //= b
    if n > 0:
        digits.append(n)
    return np.array(digits[::-1], dtype=float)


OPERATIONS["mixed_radix_encode"] = {
    "fn": mixed_radix_encode,
    "input_type": "array",
    "output_type": "array",
    "description": "Encode integer in mixed radix with given bases"
}


def mixed_radix_decode(x):
    """Decode mixed radix digits. Input: array [d0, d1, ..., b0, b1, ...] (first half digits, second half bases). Output: scalar."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    digits = x[:mid].astype(int)
    bases = [max(2, int(b)) for b in x[mid:]]
    # Digits are MSB first, bases correspond to positions LSB first
    rev_digits = digits[::-1]
    result = 0
    weight = 1
    for i, d in enumerate(rev_digits):
        result += int(d) * weight
        if i < len(bases):
            weight *= bases[i]
        else:
            weight *= 10
    return float(result)


OPERATIONS["mixed_radix_decode"] = {
    "fn": mixed_radix_decode,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Decode mixed radix digits back to integer"
}


def mixed_radix_add(x):
    """Add two mixed radix numbers. Input: array (split in half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    # Treat each half as a plain integer and add
    a = int(round(abs(x[0])))
    b = int(round(abs(x[mid])))
    bases = [2, 3, 5, 7]
    result = a + b
    digits = []
    for base in bases:
        digits.append(result % base)
        result //= base
    if result > 0:
        digits.append(result)
    return np.array(digits[::-1], dtype=float)


OPERATIONS["mixed_radix_add"] = {
    "fn": mixed_radix_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two numbers and express in mixed radix"
}


def mixed_radix_successor(x):
    """Increment a mixed radix number. Input: array [value, bases...]. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0]))) + 1
    bases = [max(2, int(round(b))) for b in x[1:]] if len(x) > 1 else [2, 3, 5, 7]
    digits = []
    for b in bases:
        digits.append(n % b)
        n //= b
    if n > 0:
        digits.append(n)
    return np.array(digits[::-1], dtype=float)


OPERATIONS["mixed_radix_successor"] = {
    "fn": mixed_radix_successor,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute mixed radix successor (increment by 1)"
}


def time_to_mixed_radix(x):
    """Convert seconds to time (60-60-24 mixed radix). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    results = []
    for val in x:
        total_seconds = int(round(abs(val)))
        seconds = total_seconds % 60
        total_seconds //= 60
        minutes = total_seconds % 60
        total_seconds //= 60
        hours = total_seconds % 24
        days = total_seconds // 24
        results.extend([days, hours, minutes, seconds])
    return np.array(results, dtype=float)


OPERATIONS["time_to_mixed_radix"] = {
    "fn": time_to_mixed_radix,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert seconds to days-hours-minutes-seconds (60-60-24 mixed radix)"
}


def combinatorial_number_system(x):
    """Represent integer in combinatorial number system C(c_k,k)+...+C(c_1,1). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0])))
    k = int(round(abs(x[1]))) if len(x) > 1 else 3
    k = max(1, min(k, 10))
    # Find combinatorial representation
    digits = []
    remaining = n
    for i in range(k, 0, -1):
        # Find largest c such that C(c, i) <= remaining
        c = i
        while comb(c + 1, i) <= remaining:
            c += 1
        if comb(c, i) <= remaining:
            digits.append(c)
            remaining -= comb(c, i)
        else:
            digits.append(0)
    return np.array(digits, dtype=float)


OPERATIONS["combinatorial_number_system"] = {
    "fn": combinatorial_number_system,
    "input_type": "array",
    "output_type": "array",
    "description": "Represent integer in combinatorial number system"
}


def optimal_radix_selection(x):
    """Find optimal mixed radix bases for given range. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    max_val = max(2, int(round(abs(x[0]))))
    # Optimal: minimize total digit slots needed = sum of (radix_i - 1)
    # For fixed product >= max_val, use bases close to e ~ 2.718, so prefer 3s
    bases = []
    product = 1
    while product < max_val:
        # Use base 3 (closest integer to e)
        bases.append(3)
        product *= 3
    # Radix economy for comparison
    economies = {}
    for b in [2, 3, 5, 10]:
        import math
        digits = math.ceil(math.log(max_val + 1) / math.log(b)) if max_val > 0 else 1
        economies[b] = b * digits
    return np.array(bases + [economies.get(3, 0)], dtype=float)


OPERATIONS["optimal_radix_selection"] = {
    "fn": optimal_radix_selection,
    "input_type": "array",
    "output_type": "array",
    "description": "Find optimal mixed radix bases for a given range"
}


def mixed_radix_overflow_check(x):
    """Check if digits overflow their respective radix bounds. Input: array [d0,d1,...,b0,b1,...]. Output: scalar."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    digits = x[:mid]
    bases = x[mid:]
    overflows = 0
    for i in range(min(len(digits), len(bases))):
        if digits[i] < 0 or digits[i] >= bases[i]:
            overflows += 1
    return float(overflows)


OPERATIONS["mixed_radix_overflow_check"] = {
    "fn": mixed_radix_overflow_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check how many digit positions overflow their radix bounds"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
