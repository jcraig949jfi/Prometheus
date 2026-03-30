"""
Digit Dynamics in Arbitrary Bases — Digital root and persistence in any base

Connects to: [digital_root, continued_fractions, p_adic_numbers, modular_arithmetic_exotic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "digit_dynamics_arbitrary_base"
OPERATIONS = {}


def _to_digits_base_b(n, b):
    """Convert non-negative integer n to list of digits in base b."""
    n = int(abs(n))
    b = int(b)
    if b < 2:
        raise ValueError("Base must be >= 2")
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        digits.append(n % b)
        n //= b
    return digits[::-1]


def digital_root_base_b(x):
    """Compute digital root in base b for each element. Input: array (values; last element=base). Output: array."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        n = int(abs(v))
        if n == 0:
            results.append(0)
        else:
            # Digital root in base b: 1 + ((n-1) % (b-1))
            results.append(1 + ((n - 1) % (b - 1)))
    return np.array(results)


OPERATIONS["digital_root_base_b"] = {
    "fn": digital_root_base_b,
    "input_type": "array",
    "output_type": "array",
    "description": "Digital root in base b (last element is base)"
}


def additive_persistence_base_b(x):
    """Count iterations of digit-sum until single digit. Input: array (values; last=base). Output: array."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        n = int(abs(v))
        count = 0
        while n >= b:
            n = sum(_to_digits_base_b(n, b))
            count += 1
        results.append(count)
    return np.array(results)


OPERATIONS["additive_persistence_base_b"] = {
    "fn": additive_persistence_base_b,
    "input_type": "array",
    "output_type": "array",
    "description": "Additive persistence in base b"
}


def multiplicative_persistence_base_b(x):
    """Count iterations of digit-product until single digit. Input: array (values; last=base). Output: array."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        n = int(abs(v))
        count = 0
        while n >= b:
            digits = _to_digits_base_b(n, b)
            product = 1
            for d in digits:
                product *= d
            n = product
            count += 1
            if count > 500:
                break
        results.append(count)
    return np.array(results)


OPERATIONS["multiplicative_persistence_base_b"] = {
    "fn": multiplicative_persistence_base_b,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiplicative persistence in base b"
}


def digit_sum_base_b(x):
    """Sum of digits in base b. Input: array (values; last=base). Output: array."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        results.append(sum(_to_digits_base_b(int(abs(v)), b)))
    return np.array(results, dtype=float)


OPERATIONS["digit_sum_base_b"] = {
    "fn": digit_sum_base_b,
    "input_type": "array",
    "output_type": "array",
    "description": "Sum of digits in base b"
}


def digit_product_base_b(x):
    """Product of digits in base b. Input: array (values; last=base). Output: array."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        digits = _to_digits_base_b(int(abs(v)), b)
        prod = 1
        for d in digits:
            prod *= d
        results.append(prod)
    return np.array(results, dtype=float)


OPERATIONS["digit_product_base_b"] = {
    "fn": digit_product_base_b,
    "input_type": "array",
    "output_type": "array",
    "description": "Product of digits in base b"
}


def persistence_landscape(x):
    """Additive persistence as a function of base (2..max_base) for a number. Input: array [number, max_base]. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(abs(x[0])) if len(x) > 0 else 99
    max_base = int(x[1]) if len(x) > 1 else 16
    results = []
    for b in range(2, max_base + 1):
        val = int(n)
        count = 0
        while val >= b:
            val = sum(_to_digits_base_b(val, b))
            count += 1
        results.append(count)
    return np.array(results, dtype=float)


OPERATIONS["persistence_landscape"] = {
    "fn": persistence_landscape,
    "input_type": "array",
    "output_type": "array",
    "description": "Additive persistence across bases 2..max_base for a given number"
}


def max_persistence_search(x):
    """Find number with max multiplicative persistence in range [1, N] in base b. Input: array [N, base]. Output: array [number, persistence]."""
    x = np.asarray(x, dtype=float)
    N = int(abs(x[0])) if len(x) > 0 else 100
    b = int(x[1]) if len(x) > 1 else 10
    N = min(N, 10000)  # cap for speed
    best_n = 0
    best_p = 0
    for n in range(1, N + 1):
        val = n
        count = 0
        while val >= b:
            digits = _to_digits_base_b(val, b)
            prod = 1
            for d in digits:
                prod *= d
            val = prod
            count += 1
            if count > 500:
                break
        if count > best_p:
            best_p = count
            best_n = n
    return np.array([best_n, best_p], dtype=float)


OPERATIONS["max_persistence_search"] = {
    "fn": max_persistence_search,
    "input_type": "array",
    "output_type": "array",
    "description": "Find number with max multiplicative persistence in range"
}


def persistence_record_holders(x):
    """Find first number achieving each persistence level 0..max_level in base b. Input: array [max_level, base]. Output: array."""
    x = np.asarray(x, dtype=float)
    max_level = int(x[0]) if len(x) > 0 else 4
    b = int(x[1]) if len(x) > 1 else 10
    max_level = min(max_level, 6)
    records = [-1] * (max_level + 1)
    records[0] = 0  # 0 has persistence 0
    found = 1
    for n in range(1, 100000):
        val = n
        count = 0
        while val >= b:
            digits = _to_digits_base_b(val, b)
            prod = 1
            for d in digits:
                prod *= d
            val = prod
            count += 1
            if count > max_level:
                break
        if count <= max_level and records[count] == -1:
            records[count] = n
            found += 1
            if found > max_level:
                break
    return np.array(records, dtype=float)


OPERATIONS["persistence_record_holders"] = {
    "fn": persistence_record_holders,
    "input_type": "array",
    "output_type": "array",
    "description": "First number achieving each multiplicative persistence level"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
