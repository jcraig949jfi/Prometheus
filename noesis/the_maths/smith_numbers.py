"""
Smith Numbers — Base-dependent number properties: Smith, Niven/Harshad, repunits

Connects to: [digital_root, modular_arithmetic_exotic, p_adic_numbers, finite_fields]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "smith_numbers"
OPERATIONS = {}


def _to_digits_base_b(n, b=10):
    """Convert non-negative integer n to list of digits in base b."""
    n = int(abs(n))
    b = int(b)
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        digits.append(n % b)
        n //= b
    return digits[::-1]


def _digit_sum(n, b=10):
    """Sum of digits in base b."""
    return sum(_to_digits_base_b(n, b))


def _prime_factors_with_multiplicity(n):
    """Return list of prime factors with repetition."""
    n = int(abs(n))
    if n < 2:
        return []
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def is_smith_number(x):
    """Check if each value is a Smith number (digit sum = sum of digit sums of prime factors).
    Input: array (values; last=base). Output: array of 0/1."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        n = int(abs(v))
        if n < 2:
            results.append(0)
            continue
        factors = _prime_factors_with_multiplicity(n)
        # Smith numbers must be composite
        if len(factors) <= 1:
            results.append(0)
            continue
        ds = _digit_sum(n, b)
        factor_ds = sum(_digit_sum(f, b) for f in factors)
        results.append(1 if ds == factor_ds else 0)
    return np.array(results, dtype=float)


OPERATIONS["is_smith_number"] = {
    "fn": is_smith_number,
    "input_type": "array",
    "output_type": "array",
    "description": "Check if values are Smith numbers in given base"
}


def is_niven_harshad(x):
    """Check if each value is a Niven (Harshad) number: divisible by its digit sum.
    Input: array (values; last=base). Output: array of 0/1."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        n = int(abs(v))
        if n == 0:
            results.append(0)
            continue
        ds = _digit_sum(n, b)
        results.append(1 if ds > 0 and n % ds == 0 else 0)
    return np.array(results, dtype=float)


OPERATIONS["is_niven_harshad"] = {
    "fn": is_niven_harshad,
    "input_type": "array",
    "output_type": "array",
    "description": "Check if values are Niven/Harshad numbers in given base"
}


def digit_sum_equals_factor_digit_sum(x):
    """For each value, compute digit_sum(n) and sum of digit_sums of prime factors.
    Input: array (values; last=base). Output: array of differences."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        n = int(abs(v))
        if n < 2:
            results.append(0)
            continue
        ds = _digit_sum(n, b)
        factors = _prime_factors_with_multiplicity(n)
        factor_ds = sum(_digit_sum(f, b) for f in factors)
        results.append(ds - factor_ds)
    return np.array(results, dtype=float)


OPERATIONS["digit_sum_equals_factor_digit_sum"] = {
    "fn": digit_sum_equals_factor_digit_sum,
    "input_type": "array",
    "output_type": "array",
    "description": "Difference between digit sum and factor digit sum (0 = Smith)"
}


def repunit_value(x):
    """Compute repunit R_n in base b: (b^n - 1)/(b - 1).
    Input: array [n_values..., base]. Output: array of repunit values."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    b = max(b, 2)
    results = []
    for v in values:
        n = int(abs(v))
        if n <= 0:
            results.append(0)
        else:
            # R_n = (b^n - 1) / (b - 1)
            val = (b ** n - 1) // (b - 1)
            results.append(val)
    return np.array(results, dtype=float)


OPERATIONS["repunit_value"] = {
    "fn": repunit_value,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute repunit R_n = (b^n - 1)/(b - 1) in base b"
}


def repunit_primality_test(x):
    """Test if repunit R_n in base b is prime (trial division for small values).
    Input: array [n_values..., base]. Output: array of 0/1."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    b = max(b, 2)

    def _is_prime(n):
        if n < 2:
            return False
        if n < 4:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    results = []
    for v in values:
        n = int(abs(v))
        if n <= 0:
            results.append(0)
            continue
        rep = (b ** n - 1) // (b - 1)
        results.append(1 if _is_prime(rep) else 0)
    return np.array(results, dtype=float)


OPERATIONS["repunit_primality_test"] = {
    "fn": repunit_primality_test,
    "input_type": "array",
    "output_type": "array",
    "description": "Test if repunit R_n is prime in base b"
}


def smith_count_in_range(x):
    """Count Smith numbers in range [1, N] in base b.
    Input: array [N, base]. Output: scalar."""
    x = np.asarray(x, dtype=float)
    N = int(x[0]) if len(x) > 0 else 100
    b = int(x[1]) if len(x) > 1 else 10
    N = min(N, 10000)
    b = max(b, 2)
    count = 0
    for n in range(2, N + 1):
        factors = _prime_factors_with_multiplicity(n)
        if len(factors) <= 1:
            continue
        ds = _digit_sum(n, b)
        factor_ds = sum(_digit_sum(f, b) for f in factors)
        if ds == factor_ds:
            count += 1
    return np.float64(count)


OPERATIONS["smith_count_in_range"] = {
    "fn": smith_count_in_range,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count Smith numbers in range [1, N] in base b"
}


def base_dependent_palindrome(x):
    """Check if each value is a palindrome in base b.
    Input: array (values; last=base). Output: array of 0/1."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    b = max(b, 2)
    results = []
    for v in values:
        digits = _to_digits_base_b(int(abs(v)), b)
        results.append(1 if digits == digits[::-1] else 0)
    return np.array(results, dtype=float)


OPERATIONS["base_dependent_palindrome"] = {
    "fn": base_dependent_palindrome,
    "input_type": "array",
    "output_type": "array",
    "description": "Check if values are palindromes in base b"
}


def digital_invariant_base_b(x):
    """Find fixed point of iterated digit power sum (narcissistic/Armstrong iteration).
    For each value, iterate: n -> sum(d^p for d in digits(n, b)) where p=num_digits.
    Input: array (values; last=base). Output: array (fixed points or cycle lengths)."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    b = max(b, 2)
    results = []
    for v in values:
        n = int(abs(v))
        seen = {}
        step = 0
        while n not in seen and step < 200:
            seen[n] = step
            digits = _to_digits_base_b(n, b)
            p = len(digits)
            n = sum(d ** p for d in digits)
            step += 1
        if n in seen:
            cycle_len = step - seen[n]
            results.append(cycle_len)
        else:
            results.append(-1)
    return np.array(results, dtype=float)


OPERATIONS["digital_invariant_base_b"] = {
    "fn": digital_invariant_base_b,
    "input_type": "array",
    "output_type": "array",
    "description": "Cycle length of iterated digit power sum in base b"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
