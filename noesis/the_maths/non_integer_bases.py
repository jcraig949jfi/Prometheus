"""
Non-Integer Bases -- Base phi (golden ratio), base e, base pi.

Connects to: [fibonacci_base, balanced_ternary, complex_bases, p_adic_expansions]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "non_integer_bases"
OPERATIONS = {}

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ~ 1.618


def to_base_phi(x):
    """Convert non-negative integer to base phi representation. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0])))
    if n == 0:
        return np.array([0.0])
    # Use greedy algorithm with powers of phi
    max_power = int(np.ceil(np.log(n + 1) / np.log(PHI))) + 2
    powers = [PHI ** i for i in range(max_power, -max_power - 1, -1)]
    digits = []
    remaining = float(n)
    for p in powers:
        if remaining >= p - 1e-9:
            digits.append(1.0)
            remaining -= p
        else:
            digits.append(0.0)
    # Strip leading zeros
    result = np.array(digits)
    first_one = 0
    while first_one < len(result) - 1 and result[first_one] == 0:
        first_one += 1
    return result[first_one:]


OPERATIONS["to_base_phi"] = {
    "fn": to_base_phi,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert integer to base-phi (golden ratio) representation"
}


def from_base_phi(digits):
    """Convert base-phi digits to value. Input: array (digits, with index 0 = phi^(n-1)). Output: scalar."""
    digits = np.asarray(digits, dtype=float)
    n = len(digits)
    result = 0.0
    for i, d in enumerate(digits):
        power = n - 1 - i
        result += d * (PHI ** power)
    return result


OPERATIONS["from_base_phi"] = {
    "fn": from_base_phi,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert base-phi digits back to numeric value"
}


def base_phi_add(x):
    """Add two base-phi numbers (by value, re-encode). Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    a = from_base_phi(x[:mid])
    b = from_base_phi(x[mid:])
    total = a + b
    return to_base_phi(np.array([total]))


OPERATIONS["base_phi_add"] = {
    "fn": base_phi_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two base-phi numbers"
}


def base_phi_normalize(x):
    """Normalize base-phi: apply carry rule phi^2 = phi + 1 (replace 011 with 100). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    digits = list(x.copy())
    # Repeatedly apply: if digits[i] and digits[i+1] are both 1, replace with carry
    # 11 at positions i,i+1 means phi^a + phi^(a-1) = phi^(a+1), so carry up
    changed = True
    max_iter = 100
    while changed and max_iter > 0:
        changed = False
        max_iter -= 1
        for i in range(len(digits) - 1):
            if digits[i] >= 1 and digits[i + 1] >= 1:
                # phi^k + phi^(k-1) = phi^(k+1)
                digits[i] -= 1
                digits[i + 1] -= 1
                if i > 0:
                    digits[i - 1] += 1
                else:
                    digits.insert(0, 1)
                changed = True
                break
        # Also handle digits >= 2: phi^k * 2 = phi^(k+1) + phi^(k-2) if possible
        for i in range(len(digits)):
            if digits[i] >= 2:
                digits[i] -= 2
                if i > 0:
                    digits[i - 1] += 1
                else:
                    digits.insert(0, 1)
                    i += 1
                if i + 2 < len(digits):
                    digits[i + 2] += 1
                else:
                    while len(digits) <= i + 2:
                        digits.append(0)
                    digits[i + 2] += 1
                changed = True
                break
    return np.array(digits, dtype=float)


OPERATIONS["base_phi_normalize"] = {
    "fn": base_phi_normalize,
    "input_type": "array",
    "output_type": "array",
    "description": "Normalize base-phi using carry rule phi^2 = phi + 1"
}


def base_e_representation(x):
    """Represent integer in base e (Euler's number). Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    val = abs(x[0])
    if val < 1e-10:
        return np.array([0.0])
    e = np.e
    # Greedy algorithm: find powers of e
    max_power = int(np.ceil(np.log(val + 1) / np.log(e))) + 1
    digits = []
    remaining = val
    for p in range(max_power, -1, -1):
        ep = e ** p
        d = int(remaining / ep)
        d = min(d, 2)  # In base e, digits are typically 0, 1, or 2
        digits.append(float(d))
        remaining -= d * ep
    return np.array(digits)


OPERATIONS["base_e_representation"] = {
    "fn": base_e_representation,
    "input_type": "array",
    "output_type": "array",
    "description": "Represent number in base e (greedy algorithm, digits 0-2)"
}


def base_pi_representation(x):
    """Represent integer in base pi. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    val = abs(x[0])
    if val < 1e-10:
        return np.array([0.0])
    pi = np.pi
    max_power = int(np.ceil(np.log(val + 1) / np.log(pi))) + 1
    digits = []
    remaining = val
    for p in range(max_power, -1, -1):
        pp = pi ** p
        d = int(remaining / pp)
        d = min(d, 3)  # In base pi, digits 0-3
        digits.append(float(d))
        remaining -= d * pp
    return np.array(digits)


OPERATIONS["base_pi_representation"] = {
    "fn": base_pi_representation,
    "input_type": "array",
    "output_type": "array",
    "description": "Represent number in base pi (greedy algorithm, digits 0-3)"
}


def non_integer_base_efficiency(x):
    """Compare efficiency of bases phi, e, pi, 2, 10. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    val = max(2, abs(x[0]))
    bases = [PHI, np.e, np.pi, 2.0, 10.0]
    names_encoded = [1.618, 2.718, 3.14159, 2.0, 10.0]  # encode base as value
    results = []
    for b in bases:
        digits = np.ceil(np.log(val + 1) / np.log(b))
        economy = b * digits  # radix economy
        results.append(economy)
    return np.array(results)


OPERATIONS["non_integer_base_efficiency"] = {
    "fn": non_integer_base_efficiency,
    "input_type": "array",
    "output_type": "array",
    "description": "Compare radix economy across phi, e, pi, 2, 10"
}


def golden_string_generate(x):
    """Generate golden string (Fibonacci word). Input: array (length from first elem). Output: array."""
    x = np.asarray(x, dtype=float)
    n = max(1, min(int(round(abs(x[0]))), 100))
    # Fibonacci word: limit of S(n) where S(0)=0, S(1)=01, S(n)=S(n-1)+S(n-2)
    a = [1.0]
    b = [1.0, 0.0]
    while len(b) < n:
        a, b = b, list(b) + list(a)
    return np.array(b[:n])


OPERATIONS["golden_string_generate"] = {
    "fn": golden_string_generate,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate golden string (infinite Fibonacci word) up to given length"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
