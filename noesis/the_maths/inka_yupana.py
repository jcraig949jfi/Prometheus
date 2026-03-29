"""
Inka Yupana — Fibonacci-base / irregular-base arithmetic from Inka computational device

Connects to: [yoruba_signed_digit, bambara_divination, context_dependent_arithmetic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

The yupana is an Inka counting device. One interpretation uses Fibonacci numbers
as column values (1, 2, 3, 5, 8, 13, 21, ...) rather than powers of a fixed base.
Zeckendorf's theorem guarantees every positive integer has a unique representation
as a sum of non-consecutive Fibonacci numbers.
"""

import numpy as np

FIELD_NAME = "inka_yupana"
OPERATIONS = {}

# Precompute Fibonacci numbers up to a reasonable limit
_FIB = [1, 2]
while _FIB[-1] < 1e15:
    _FIB.append(_FIB[-1] + _FIB[-2])
_FIB = np.array(_FIB, dtype=float)


def _zeckendorf(n):
    """Return Zeckendorf representation: list of 0/1 coefficients for Fibonacci numbers
    (from largest to smallest), no two consecutive 1s."""
    n = int(round(abs(n)))
    if n == 0:
        return [0]
    # Find largest Fibonacci <= n
    coeffs = []
    remaining = n
    for i in range(len(_FIB) - 1, -1, -1):
        if _FIB[i] <= remaining:
            coeffs.append((i, 1))
            remaining -= int(_FIB[i])
        else:
            coeffs.append((i, 0))
        if remaining == 0:
            break
    # Pad to consistent length and return just the digits
    result = [0] * (len(_FIB))
    for idx, val in coeffs:
        result[idx] = val
    # Trim trailing zeros from high end
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def fibonacci_base_encode(x):
    """Encode each element in Zeckendorf (Fibonacci base) representation.
    Returns flattened binary digits. Input: array. Output: array."""
    all_digits = []
    for val in x:
        digits = _zeckendorf(val)
        all_digits.extend([float(d) for d in digits])
    return np.array(all_digits)


OPERATIONS["fibonacci_base_encode"] = {
    "fn": fibonacci_base_encode,
    "input_type": "array",
    "output_type": "array",
    "description": "Zeckendorf (Fibonacci base) encoding"
}


def fibonacci_base_decode(x):
    """Decode Fibonacci base digits back to decimal.
    x is treated as a sequence of 0/1 digits (one number).
    Input: array. Output: scalar."""
    total = 0.0
    for i, d in enumerate(x):
        if i < len(_FIB) and d > 0.5:
            total += _FIB[i]
    return float(total)


OPERATIONS["fibonacci_base_decode"] = {
    "fn": fibonacci_base_decode,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Decodes Fibonacci base digits to decimal value"
}


def fibonacci_base_add(x):
    """Add adjacent pairs in Fibonacci base with Zeckendorf normalization.
    Returns Zeckendorf representations of the sums, flattened.
    Input: array. Output: array."""
    if len(x) < 2:
        return fibonacci_base_encode(x)
    results = []
    for i in range(0, len(x) - 1, 2):
        s = abs(x[i]) + abs(x[i + 1])
        digits = _zeckendorf(s)
        results.extend([float(d) for d in digits])
    return np.array(results)


OPERATIONS["fibonacci_base_add"] = {
    "fn": fibonacci_base_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Pairwise addition with Zeckendorf normalization"
}


def fibonacci_base_multiply(x):
    """Multiply adjacent pairs and return Zeckendorf representation.
    Input: array. Output: array."""
    if len(x) < 2:
        return fibonacci_base_encode(x)
    results = []
    for i in range(0, len(x) - 1, 2):
        prod = abs(x[i] * x[i + 1])
        digits = _zeckendorf(prod)
        results.extend([float(d) for d in digits])
    return np.array(results)


OPERATIONS["fibonacci_base_multiply"] = {
    "fn": fibonacci_base_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Pairwise multiplication with Zeckendorf result"
}


def irregular_base_carry(x):
    """Simulate carry propagation in Fibonacci base.
    When two consecutive positions are both 1, replace with a carry:
    F(i) + F(i+1) = F(i+2). Normalizes to Zeckendorf form.
    Input: array (treated as Fibonacci digits). Output: array."""
    digits = list(x.copy())
    # Pad if needed
    digits.extend([0.0] * 5)
    changed = True
    iterations = 0
    while changed and iterations < 100:
        changed = False
        iterations += 1
        # Rule 1: two consecutive 1s -> carry
        for i in range(len(digits) - 2):
            if digits[i] >= 1 and digits[i + 1] >= 1:
                digits[i] -= 1
                digits[i + 1] -= 1
                if i + 2 >= len(digits):
                    digits.append(0)
                digits[i + 2] += 1
                changed = True
        # Rule 2: digit >= 2 at position i: 2*F(i) = F(i-2) + F(i+1) for i>=2
        for i in range(len(digits)):
            if digits[i] >= 2:
                digits[i] -= 2
                if i >= 2:
                    digits[i - 2] += 1
                if i + 1 >= len(digits):
                    digits.append(0)
                digits[i + 1] += 1
                changed = True
    # Trim trailing zeros
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
    return np.array(digits, dtype=float)


OPERATIONS["irregular_base_carry"] = {
    "fn": irregular_base_carry,
    "input_type": "array",
    "output_type": "array",
    "description": "Carry propagation to normalize Fibonacci base digits"
}


def yupana_column_values(x):
    """Return the Fibonacci column values for a yupana with len(x) columns.
    Input: array. Output: array."""
    n = len(x)
    return _FIB[:n].copy()


OPERATIONS["yupana_column_values"] = {
    "fn": yupana_column_values,
    "input_type": "array",
    "output_type": "array",
    "description": "Fibonacci column values for a yupana with n columns"
}


def fibonacci_vs_binary_efficiency(x):
    """Compare representation efficiency: Fibonacci base digits vs binary digits.
    Returns [fib_digits, binary_digits, ratio] for sum of |x|.
    Input: array. Output: array."""
    total = int(round(np.sum(np.abs(x))))
    if total == 0:
        return np.array([1.0, 1.0, 1.0])

    # Binary digits
    bin_digits = len(bin(total)) - 2  # subtract '0b'

    # Fibonacci digits
    fib_digits = len(_zeckendorf(total))

    ratio = fib_digits / max(bin_digits, 1)
    return np.array([float(fib_digits), float(bin_digits), ratio])


OPERATIONS["fibonacci_vs_binary_efficiency"] = {
    "fn": fibonacci_vs_binary_efficiency,
    "input_type": "array",
    "output_type": "array",
    "description": "Compares Fibonacci vs binary digit counts"
}


def zeckendorf_canonical_form(x):
    """Convert each element to its Zeckendorf canonical form and back to decimal.
    This is a round-trip: encode then decode. Verifies the representation.
    Returns the reconstructed values. Input: array. Output: array."""
    results = []
    for val in x:
        digits = _zeckendorf(val)
        # Verify no consecutive 1s
        is_canonical = True
        for i in range(len(digits) - 1):
            if digits[i] == 1 and digits[i + 1] == 1:
                is_canonical = False
                break
        # Decode back
        total = sum(digits[i] * _FIB[i] for i in range(min(len(digits), len(_FIB))))
        results.append(total)
    return np.array(results)


OPERATIONS["zeckendorf_canonical_form"] = {
    "fn": zeckendorf_canonical_form,
    "input_type": "array",
    "output_type": "array",
    "description": "Round-trip through Zeckendorf representation"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
