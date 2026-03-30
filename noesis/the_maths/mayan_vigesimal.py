"""
Mayan Vigesimal — Mixed-radix base-20 with 18x20 calendrical irregularity

Connects to: [babylonian_sexagesimal, inca_quipu, rod_calculus]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import gcd

FIELD_NAME = "mayan_vigesimal"
OPERATIONS = {}


def to_mayan_vigesimal(x):
    """Convert decimal to pure base-20 (vigesimal) digits. Input: array. Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    max_digits = 6
    result = np.zeros((len(arr), max_digits), dtype=np.float64)
    for i, val in enumerate(arr):
        n = int(abs(val))
        for j in range(max_digits - 1, -1, -1):
            result[i, j] = n % 20
            n //= 20
    return result


OPERATIONS["to_mayan_vigesimal"] = {
    "fn": to_mayan_vigesimal,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Convert decimal numbers to base-20 digit arrays"
}


def from_mayan_vigesimal(x):
    """Convert base-20 digit array to decimal. Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    result = 0.0
    for d in arr:
        result = result * 20.0 + d
    return float(result)


OPERATIONS["from_mayan_vigesimal"] = {
    "fn": from_mayan_vigesimal,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert base-20 digit array to decimal number"
}


def mayan_add(x):
    """Add two vigesimal numbers (first/second half of array). Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = len(arr) // 2
    a = arr[:n]
    b = arr[n:2 * n]
    val_a = from_mayan_vigesimal(a)
    val_b = from_mayan_vigesimal(b)
    total = int(val_a + val_b)
    # Convert back to vigesimal
    digits = []
    if total == 0:
        digits = [0]
    else:
        while total > 0:
            digits.append(total % 20)
            total //= 20
        digits.reverse()
    return np.array(digits, dtype=np.float64)


OPERATIONS["mayan_add"] = {
    "fn": mayan_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two vigesimal numbers (array split in half)"
}


def mayan_multiply(x):
    """Multiply two vigesimal numbers (first/second half of array). Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = len(arr) // 2
    a = arr[:n]
    b = arr[n:2 * n]
    val_a = from_mayan_vigesimal(a)
    val_b = from_mayan_vigesimal(b)
    total = int(val_a * val_b)
    digits = []
    if total == 0:
        digits = [0]
    else:
        while total > 0:
            digits.append(total % 20)
            total //= 20
        digits.reverse()
    return np.array(digits, dtype=np.float64)


OPERATIONS["mayan_multiply"] = {
    "fn": mayan_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two vigesimal numbers (array split in half)"
}


def long_count_to_days(x):
    """Convert Mayan Long Count [baktun, katun, tun, uinal, kin] to days.
    Mixed radix: 20, 20, 18, 20 (uinal has 18 tuns). Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    # Pad to 5 elements
    lc = np.zeros(5)
    lc[:min(len(arr), 5)] = arr[:min(len(arr), 5)]
    # Long Count: baktun*144000 + katun*7200 + tun*360 + uinal*20 + kin
    # 1 kin = 1 day, 1 uinal = 20 kin, 1 tun = 360 kin (18 uinal),
    # 1 katun = 7200 kin (20 tun), 1 baktun = 144000 kin (20 katun)
    multipliers = [144000, 7200, 360, 20, 1]
    days = sum(lc[i] * multipliers[i] for i in range(5))
    return float(days)


OPERATIONS["long_count_to_days"] = {
    "fn": long_count_to_days,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert Mayan Long Count date to total days"
}


def calendar_round_cycle(x):
    """Compute the Calendar Round cycle length: LCM(260, 365). Input: any. Output: scalar."""
    # Tzolkin = 260 days, Haab = 365 days
    # Calendar Round = LCM(260, 365)
    a, b = 260, 365
    lcm = a * b // gcd(a, b)
    return float(lcm)  # = 18980 days = 52 Haab years


OPERATIONS["calendar_round_cycle"] = {
    "fn": calendar_round_cycle,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Calendar Round cycle length: LCM of Tzolkin (260) and Haab (365)"
}


def haab_position(x):
    """Compute Haab calendar position (month 0-17, day 0-19 + Wayeb 0-4). Input: array (days). Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for days in arr:
        d = int(days) % 365
        month = d // 20
        day = d % 20
        results.append([month, day])
    return np.array(results, dtype=np.float64)


OPERATIONS["haab_position"] = {
    "fn": haab_position,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Compute Haab calendar position [month, day] from day count"
}


def tzolkin_position(x):
    """Compute Tzolkin calendar position (number 1-13, day sign 0-19). Input: array (days). Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for days in arr:
        d = int(days)
        number = (d % 13) + 1  # 1-13
        day_sign = d % 20       # 0-19
        results.append([number, day_sign])
    return np.array(results, dtype=np.float64)


OPERATIONS["tzolkin_position"] = {
    "fn": tzolkin_position,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Compute Tzolkin calendar position [number, day_sign] from day count"
}


def mixed_radix_carry(x):
    """Perform carry propagation in Mayan mixed-radix system. Input: array. Output: array.
    Radices from least significant: 20, 18, 20, 20, 20, ..."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    digits = list(arr[::-1])  # reverse to least significant first
    radices = [20, 18, 20, 20, 20, 20, 20, 20]
    # Extend if needed
    while len(digits) < len(radices):
        digits.append(0)
    # Carry propagation
    for i in range(len(digits) - 1):
        r = radices[i] if i < len(radices) else 20
        if digits[i] >= r:
            carry = int(digits[i]) // r
            digits[i] = int(digits[i]) % r
            digits[i + 1] += carry
        while digits[i] < 0 and i + 1 < len(digits):
            digits[i] += r
            digits[i + 1] -= 1
    # Remove trailing zeros
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
    return np.array(digits[::-1], dtype=np.float64)


OPERATIONS["mixed_radix_carry"] = {
    "fn": mixed_radix_carry,
    "input_type": "array",
    "output_type": "array",
    "description": "Carry propagation in Mayan mixed-radix (20, 18, 20, ...) system"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
