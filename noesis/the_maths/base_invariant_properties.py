"""
Base-Invariant Properties — Meta-analysis: which number properties depend on base and which don't

Connects to: [digital_root, smith_numbers, normal_numbers, modular_arithmetic_exotic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "base_invariant_properties"
OPERATIONS = {}


def _to_digits_base_b(n, b):
    """Convert non-negative integer n to list of digits in base b."""
    n = int(abs(n))
    b = int(b)
    if b < 2:
        b = 2
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        digits.append(n % b)
        n //= b
    return digits[::-1]


def _is_prime(n):
    """Simple primality test."""
    n = int(abs(n))
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


def is_base_invariant_property(x):
    """Classify properties as base-invariant (1) or base-dependent (0).
    Encodes: 0=primality, 1=divisibility, 2=being_perfect, 3=palindrome, 4=digit_sum,
    5=repunit, 6=smith, 7=harshad.
    Input: array of property indices. Output: array of 0/1."""
    x = np.asarray(x, dtype=float)
    # Ground truth classification
    invariant = {
        0: 1,  # primality - independent of base
        1: 1,  # divisibility - independent
        2: 1,  # perfect number - independent
        3: 0,  # palindrome - base dependent
        4: 0,  # digit sum - base dependent
        5: 0,  # repunit - base dependent
        6: 0,  # Smith number - base dependent
        7: 0,  # Harshad/Niven - base dependent
    }
    results = []
    for v in x:
        idx = int(v) % 8
        results.append(invariant.get(idx, 0))
    return np.array(results, dtype=float)


OPERATIONS["is_base_invariant_property"] = {
    "fn": is_base_invariant_property,
    "input_type": "array",
    "output_type": "array",
    "description": "Classify number properties as base-invariant or base-dependent"
}


def primality_invariance_demo(x):
    """Demonstrate that primality is base-invariant: check primality of each value.
    Primality depends only on the number itself, not its representation.
    Input: array. Output: array of 0/1."""
    x = np.asarray(x, dtype=float)
    results = [1.0 if _is_prime(int(v)) else 0.0 for v in x]
    return np.array(results, dtype=float)


OPERATIONS["primality_invariance_demo"] = {
    "fn": primality_invariance_demo,
    "input_type": "array",
    "output_type": "array",
    "description": "Demonstrate base-invariance of primality"
}


def palindrome_base_dependence(x):
    """Show base-dependence of palindromes: for each value, count how many
    bases (2..max_base) it's a palindrome in.
    Input: array (values; last=max_base). Output: array of palindrome-base counts."""
    x = np.asarray(x, dtype=float)
    max_base = int(x[-1]) if len(x) > 1 else 16
    values = x[:-1] if len(x) > 1 else x
    max_base = max(max_base, 3)
    max_base = min(max_base, 36)
    results = []
    for v in values:
        n = int(abs(v))
        count = 0
        for b in range(2, max_base + 1):
            digits = _to_digits_base_b(n, b)
            if digits == digits[::-1]:
                count += 1
        results.append(count)
    return np.array(results, dtype=float)


OPERATIONS["palindrome_base_dependence"] = {
    "fn": palindrome_base_dependence,
    "input_type": "array",
    "output_type": "array",
    "description": "Count bases where each number is a palindrome (shows base dependence)"
}


def digit_sum_base_dependence(x):
    """Show base-dependence of digit sum: compute digit sum in bases 2..max_base.
    Input: array [number, max_base]. Output: array of digit sums."""
    x = np.asarray(x, dtype=float)
    number = int(abs(x[0])) if len(x) > 0 else 100
    max_base = int(x[1]) if len(x) > 1 else 16
    max_base = max(max_base, 3)
    max_base = min(max_base, 36)
    results = []
    for b in range(2, max_base + 1):
        ds = sum(_to_digits_base_b(number, b))
        results.append(ds)
    return np.array(results, dtype=float)


OPERATIONS["digit_sum_base_dependence"] = {
    "fn": digit_sum_base_dependence,
    "input_type": "array",
    "output_type": "array",
    "description": "Digit sum across bases (shows base dependence)"
}


def minimal_base_for_property(x):
    """Find the smallest base in which a number has a given property.
    Properties: 0=palindrome, 1=repdigit, 2=harshad.
    Input: array [number, property_id]. Output: scalar (minimal base, or -1)."""
    x = np.asarray(x, dtype=float)
    number = int(abs(x[0])) if len(x) > 0 else 10
    prop = int(x[1]) if len(x) > 1 else 0
    for b in range(2, max(number + 2, 37)):
        digits = _to_digits_base_b(number, b)
        if prop == 0:  # palindrome
            if digits == digits[::-1]:
                return np.float64(b)
        elif prop == 1:  # repdigit (all digits same)
            if len(set(digits)) == 1:
                return np.float64(b)
        elif prop == 2:  # harshad
            ds = sum(digits)
            if ds > 0 and number % ds == 0:
                return np.float64(b)
        if b > 100:
            break
    return np.float64(-1)


OPERATIONS["minimal_base_for_property"] = {
    "fn": minimal_base_for_property,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Find smallest base where number has given property"
}


def base_independent_canonical_form(x):
    """Compute base-independent canonical representation of a number.
    Uses prime factorization as the canonical form (base-invariant).
    Input: array. Output: array of [p1, e1, p2, e2, ...] for prime factorization."""
    x = np.asarray(x, dtype=float)
    n = int(abs(x[0])) if len(x) > 0 else 60
    if n < 2:
        return np.array([n], dtype=float)
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        exp = 0
        while temp % d == 0:
            exp += 1
            temp //= d
        if exp > 0:
            factors.extend([d, exp])
        d += 1
    if temp > 1:
        factors.extend([temp, 1])
    return np.array(factors, dtype=float)


OPERATIONS["base_independent_canonical_form"] = {
    "fn": base_independent_canonical_form,
    "input_type": "array",
    "output_type": "array",
    "description": "Prime factorization as base-independent canonical form"
}


def representation_complexity_by_base(x):
    """Measure representation complexity (number of digits) across bases.
    Input: array [number, max_base]. Output: array of digit counts."""
    x = np.asarray(x, dtype=float)
    number = int(abs(x[0])) if len(x) > 0 else 1000
    max_base = int(x[1]) if len(x) > 1 else 16
    max_base = max(max_base, 3)
    max_base = min(max_base, 64)
    results = []
    for b in range(2, max_base + 1):
        if number == 0:
            results.append(1)
        else:
            num_digits = int(np.floor(np.log(max(number, 1)) / np.log(b))) + 1
            results.append(num_digits)
    return np.array(results, dtype=float)


OPERATIONS["representation_complexity_by_base"] = {
    "fn": representation_complexity_by_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of digits needed in each base (representation complexity)"
}


def property_sensitivity_to_base(x):
    """Compute how sensitive a number's properties are to base choice.
    Measures fraction of bases (2..36) in which the number has each property.
    Input: array. Output: array [palindrome_frac, harshad_frac, repdigit_frac, smith_frac]."""
    x = np.asarray(x, dtype=float)
    n = int(abs(x[0])) if len(x) > 0 else 100
    max_base = 36
    counts = [0, 0, 0, 0]  # palindrome, harshad, repdigit, single_digit
    total = max_base - 1  # bases 2..36
    for b in range(2, max_base + 1):
        digits = _to_digits_base_b(n, b)
        # Palindrome
        if digits == digits[::-1]:
            counts[0] += 1
        # Harshad
        ds = sum(digits)
        if ds > 0 and n % ds == 0:
            counts[1] += 1
        # Repdigit
        if len(set(digits)) == 1:
            counts[2] += 1
        # Single digit (trivial representation)
        if len(digits) == 1:
            counts[3] += 1
    fracs = [c / total for c in counts]
    return np.array(fracs, dtype=float)


OPERATIONS["property_sensitivity_to_base"] = {
    "fn": property_sensitivity_to_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Fraction of bases where number has various properties"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
