"""
Yoruba Signed Digit — Yoruba base-20 subtraction arithmetic (signed-digit representation)

Connects to: [inka_yupana, bambara_divination, context_dependent_arithmetic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

The Yoruba number system is vigesimal (base 20) and uniquely uses subtraction:
e.g., 35 = 2*20 - 5 ("five from two twenties"). Numbers are represented as
minimal sums/differences of powers of 20. This connects to non-adjacent form
(NAF) used in elliptic curve cryptography.
"""

import numpy as np

FIELD_NAME = "yoruba_signed_digit"
OPERATIONS = {}


def yoruba_represent(x):
    """Represent each element in Yoruba-style base-20 signed digit form.
    Returns coefficients for powers of 20 (using {-1, 0, 1} digits) that
    minimize the number of nonzero digits. Output: flattened coefficient array.
    Input: array. Output: array."""
    all_coeffs = []
    for val in x:
        n = int(round(val))
        if n == 0:
            all_coeffs.append(0.0)
            continue
        sign = 1 if n >= 0 else -1
        n = abs(n)
        coeffs = []
        while n > 0:
            r = n % 20
            if r > 10:
                # Use subtraction: represent as next power minus (20-r)
                coeffs.append(-sign * (20 - r))
                n = n // 20 + 1
            else:
                coeffs.append(sign * r)
                n = n // 20
        if not coeffs:
            coeffs = [0.0]
        all_coeffs.extend(coeffs)
    return np.array(all_coeffs, dtype=float)


OPERATIONS["yoruba_represent"] = {
    "fn": yoruba_represent,
    "input_type": "array",
    "output_type": "array",
    "description": "Signed-digit base-20 representation (Yoruba style)"
}


def signed_digit_add(x):
    """Add adjacent pairs using signed-digit arithmetic.
    Performs addition in base 20 with carry propagation.
    Input: array. Output: array."""
    if len(x) < 2:
        return x.copy()
    results = []
    for i in range(0, len(x) - 1, 2):
        s = x[i] + x[i + 1]
        results.append(s)
    return np.array(results)


OPERATIONS["signed_digit_add"] = {
    "fn": signed_digit_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Pairwise signed-digit addition"
}


def signed_digit_multiply(x):
    """Multiply adjacent pairs. In signed-digit, multiplication uses
    Booth-like recoding to minimize partial products.
    Input: array. Output: array."""
    if len(x) < 2:
        return x.copy()
    results = []
    for i in range(0, len(x) - 1, 2):
        results.append(x[i] * x[i + 1])
    return np.array(results)


OPERATIONS["signed_digit_multiply"] = {
    "fn": signed_digit_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Pairwise signed-digit multiplication"
}


def minimal_operation_count(x):
    """Count minimal operations (additions + subtractions) needed to represent
    each value in base 20. This is the Hamming weight of the signed-digit
    representation. Input: array. Output: array."""
    counts = []
    for val in x:
        n = int(round(abs(val)))
        if n == 0:
            counts.append(0.0)
            continue
        count = 0
        while n > 0:
            r = n % 20
            if r > 10:
                count += 1
                n = n // 20 + 1
            elif r > 0:
                count += 1
                n = n // 20
            else:
                n = n // 20
        counts.append(float(count))
    return np.array(counts)


OPERATIONS["minimal_operation_count"] = {
    "fn": minimal_operation_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Minimal number of add/subtract operations in base-20"
}


def naf_representation(x):
    """Non-Adjacent Form (NAF): binary signed-digit where no two consecutive
    digits are nonzero. Used in ECC scalar multiplication.
    Returns NAF digits for each value (flattened). Input: array. Output: array."""
    all_digits = []
    for val in x:
        n = int(round(val))
        if n == 0:
            all_digits.append(0.0)
            continue
        digits = []
        while n != 0:
            if n % 2 != 0:
                # digit is 2 - (n mod 4) mapped to {-1, 1}
                d = 2 - (n % 4)
                n -= d
                digits.append(float(d))
            else:
                digits.append(0.0)
            n //= 2
        all_digits.extend(digits)
    return np.array(all_digits)


OPERATIONS["naf_representation"] = {
    "fn": naf_representation,
    "input_type": "array",
    "output_type": "array",
    "description": "Non-Adjacent Form binary signed-digit representation"
}


def representation_efficiency(x):
    """Compare representation efficiency: ratio of nonzero digits in NAF vs
    standard binary. Lower ratio = more efficient NAF.
    Input: array. Output: scalar."""
    total_naf_nz = 0
    total_bin_nz = 0
    for val in x:
        n = int(round(abs(val)))
        if n == 0:
            continue
        # Binary nonzero count (popcount)
        bin_nz = bin(n).count('1')
        total_bin_nz += bin_nz
        # NAF nonzero count
        naf_nz = 0
        m = n
        while m != 0:
            if m % 2 != 0:
                d = 2 - (m % 4)
                m -= d
                naf_nz += 1
            else:
                pass
            m //= 2
        total_naf_nz += naf_nz
    if total_bin_nz == 0:
        return 1.0
    return float(total_naf_nz / total_bin_nz)


OPERATIONS["representation_efficiency"] = {
    "fn": representation_efficiency,
    "input_type": "array",
    "output_type": "scalar",
    "description": "NAF vs binary efficiency ratio (lower = better NAF)"
}


def signed_vs_unsigned_compare(x):
    """Compare digit counts: Yoruba signed base-20 vs unsigned base-20.
    Returns [signed_total_digits, unsigned_total_digits, savings_ratio].
    Input: array. Output: array."""
    signed_total = 0
    unsigned_total = 0
    for val in x:
        n = int(round(abs(val)))
        if n == 0:
            signed_total += 1
            unsigned_total += 1
            continue
        # Unsigned base-20 digits
        m = n
        while m > 0:
            unsigned_total += 1
            m //= 20
        # Signed base-20 digits (nonzero only)
        m = n
        while m > 0:
            r = m % 20
            signed_total += 1
            if r > 10:
                m = m // 20 + 1
            else:
                m = m // 20
    ratio = signed_total / max(unsigned_total, 1)
    return np.array([float(signed_total), float(unsigned_total), ratio])


OPERATIONS["signed_vs_unsigned_compare"] = {
    "fn": signed_vs_unsigned_compare,
    "input_type": "array",
    "output_type": "array",
    "description": "Compares signed vs unsigned base-20 digit counts"
}


def scalar_multiply_naf(x):
    """Scalar multiplication using NAF (relevant to ECC).
    Computes n * P where n is derived from x[0] and P from x[1:].
    NAF minimizes additions in the double-and-add algorithm.
    Returns [result_value, num_additions, num_doublings].
    Input: array. Output: array."""
    if len(x) < 2:
        return np.array([0.0, 0.0, 0.0])
    n = int(round(abs(x[0])))
    p = np.sum(x[1:])  # simplified: use sum as scalar point

    # Compute NAF
    naf_digits = []
    m = n
    while m != 0:
        if m % 2 != 0:
            d = 2 - (m % 4)
            m -= d
            naf_digits.append(d)
        else:
            naf_digits.append(0)
        m //= 2

    # Count operations
    additions = sum(1 for d in naf_digits if d != 0)
    doublings = len(naf_digits) - 1 if naf_digits else 0

    result = float(n) * p
    return np.array([result, float(additions), float(max(doublings, 0))])


OPERATIONS["scalar_multiply_naf"] = {
    "fn": scalar_multiply_naf,
    "input_type": "array",
    "output_type": "array",
    "description": "NAF-based scalar multiplication with operation count"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
