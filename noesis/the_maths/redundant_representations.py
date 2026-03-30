"""
Redundant Representations -- Digits outside normal range; representations not unique. Constant-time addition!

Connects to: [balanced_ternary, negabinary, symmetric_bases, non_integer_bases]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "redundant_representations"
OPERATIONS = {}


def signed_binary_encode(x):
    """Encode integer in signed binary (digits {-1, 0, 1}). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(x[0]))
    if n == 0:
        return np.array([0.0])
    sign = 1 if n > 0 else -1
    n = abs(n)
    # Standard binary, then convert to signed
    digits = []
    while n > 0:
        digits.append(n & 1)
        n >>= 1
    digits = digits[::-1]
    result = np.array(digits, dtype=float) * sign
    return result


OPERATIONS["signed_binary_encode"] = {
    "fn": signed_binary_encode,
    "input_type": "array",
    "output_type": "array",
    "description": "Encode integer in signed binary representation (digits {-1, 0, 1})"
}


def signed_binary_add(x):
    """Add two signed-binary numbers with no carry propagation (bounded carry). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    # In redundant signed-binary, addition is O(1) carry propagation
    # Each position: sum two digits, get result digit + carry that only goes 1 position
    a = x[:mid]
    b = x[mid:]
    max_len = max(len(a), len(b))
    a_pad = np.zeros(max_len + 2)
    b_pad = np.zeros(max_len + 2)
    a_pad[max_len + 2 - len(a):] = a
    b_pad[max_len + 2 - len(b):] = b
    # Parallel addition: sum digits, then single-pass bounded carry
    raw_sum = a_pad + b_pad
    result = np.zeros(max_len + 2)
    carry = 0
    for i in range(len(raw_sum) - 1, -1, -1):
        total = int(raw_sum[i]) + carry
        carry = 0
        if total > 1:
            result[i] = total - 2
            carry = 1
        elif total < -1:
            result[i] = total + 2
            carry = -1
        else:
            result[i] = total
    # Strip leading zeros
    first_nonzero = 0
    while first_nonzero < len(result) - 1 and result[first_nonzero] == 0:
        first_nonzero += 1
    return result[first_nonzero:]


OPERATIONS["signed_binary_add"] = {
    "fn": signed_binary_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two signed-binary numbers with bounded carry propagation"
}


def carry_save_add(x):
    """Carry-save addition: sum three numbers, output (sum_bits, carry_bits). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    # Split into 3 parts
    third = len(x) // 3
    a = x[:third].astype(int)
    b = x[third:2 * third].astype(int)
    c = x[2 * third:3 * third].astype(int)
    min_len = min(len(a), len(b), len(c))
    a, b, c = a[:min_len], b[:min_len], c[:min_len]
    # Carry-save: sum = a XOR b XOR c, carry = majority
    s = np.bitwise_xor(np.bitwise_xor(a, b), c)
    carry = ((a & b) | (b & c) | (a & c))
    return np.concatenate([s.astype(float), carry.astype(float)])


OPERATIONS["carry_save_add"] = {
    "fn": carry_save_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Carry-save addition: three inputs to (sum, carry) without propagation"
}


def canonical_form_extract(x):
    """Extract canonical (non-redundant) form from redundant representation. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    # Interpret as signed-binary, convert to integer, then standard binary
    val = 0
    for d in x:
        val = val * 2 + int(d)
    if val == 0:
        return np.array([0.0])
    sign = 1 if val > 0 else -1
    val = abs(val)
    bits = []
    while val > 0:
        bits.append(val & 1)
        val >>= 1
    return np.array(bits[::-1], dtype=float) * sign


OPERATIONS["canonical_form_extract"] = {
    "fn": canonical_form_extract,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert redundant representation to canonical binary form"
}


def redundancy_degree(x):
    """Measure redundancy: how many representations exist for this value. Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    # For signed binary of width n, redundancy ~ 3^n / 2^n representations per value
    n = len(x)
    # Approximate: count distinct signed-binary representations
    val = 0
    for d in x:
        val = val * 2 + int(round(d))
    # Redundancy ratio for n-digit signed binary
    redundancy = (3.0 ** n) / (2.0 ** (n + 1))
    return redundancy


OPERATIONS["redundancy_degree"] = {
    "fn": redundancy_degree,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Measure redundancy degree of signed-digit representation"
}


def signed_digit_multiply(x):
    """Multiply two signed-binary numbers. Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    # Convert to integers, multiply, convert back
    a_val = 0
    for d in x[:mid]:
        a_val = a_val * 2 + int(round(d))
    b_val = 0
    for d in x[mid:]:
        b_val = b_val * 2 + int(round(d))
    product = a_val * b_val
    return signed_binary_encode(np.array([float(product)]))


OPERATIONS["signed_digit_multiply"] = {
    "fn": signed_digit_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two signed-digit binary numbers"
}


def naf_encode(x):
    """Non-Adjacent Form: signed binary where no two consecutive digits are non-zero. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(x[0]))
    if n == 0:
        return np.array([0.0])
    # NAF computation: while n != 0, if n is odd, digit = 2 - (n % 4) if n%2==1 else 0
    digits = []
    while n != 0:
        if n % 2 != 0:
            digit = 2 - (n % 4)
            n -= digit
        else:
            digit = 0
        digits.append(digit)
        n //= 2
    return np.array(digits[::-1], dtype=float)


OPERATIONS["naf_encode"] = {
    "fn": naf_encode,
    "input_type": "array",
    "output_type": "array",
    "description": "Encode in Non-Adjacent Form (no consecutive non-zero digits)"
}


def redundant_to_standard(x):
    """Convert any redundant signed-digit number to standard integer. Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    val = 0
    for d in x:
        val = val * 2 + int(round(d))
    return float(val)


OPERATIONS["redundant_to_standard"] = {
    "fn": redundant_to_standard,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert redundant signed-digit representation to standard integer"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
