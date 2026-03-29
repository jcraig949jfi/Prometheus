"""
Context-Dependent Arithmetic — Proto-Elamite style: the radix changes based on semantic domain

Connects to: [yoruba_signed_digit, inka_yupana, jain_combinatorics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

In Proto-Elamite notation, the base of the number system varied by context:
grain was counted in a different base than livestock or land. This models
arithmetic where the radix is a function of a domain tag, creating
ambiguity when domain is unknown and requiring explicit conversion
for cross-domain operations.

Domain tags and their radices:
  0: grain (base 6, with sub-base 10 for large amounts: sexagesimal-like)
  1: livestock (base 10)
  2: land (base 18)
  3: labor (base 12)
  4: trade goods (base 20, vigesimal)
"""

import numpy as np

FIELD_NAME = "context_dependent_arithmetic"
OPERATIONS = {}

DOMAIN_RADICES = {
    0: 6,    # grain
    1: 10,   # livestock
    2: 18,   # land
    3: 12,   # labor
    4: 20,   # trade goods
}

DOMAIN_NAMES = {0: "grain", 1: "livestock", 2: "land", 3: "labor", 4: "trade"}


def _encode_in_base(n, base, max_digits=20):
    """Encode integer n in given base, return digits (least significant first)."""
    n = int(round(abs(n)))
    if n == 0:
        return [0]
    digits = []
    while n > 0 and len(digits) < max_digits:
        digits.append(n % base)
        n //= base
    return digits


def _decode_from_base(digits, base):
    """Decode digits in given base back to integer."""
    total = 0
    for i, d in enumerate(digits):
        total += int(d) * (base ** i)
    return total


def context_radix_encode(x):
    """Encode values using domain-dependent radix. x[0] is the domain tag (0-4),
    remaining elements are values to encode. Returns digits flattened.
    Input: array. Output: array."""
    domain = int(round(x[0])) % 5 if len(x) > 0 else 0
    base = DOMAIN_RADICES[domain]
    all_digits = []
    for val in x[1:]:
        digits = _encode_in_base(val, base)
        all_digits.extend([float(d) for d in digits])
        all_digits.append(-1.0)  # separator
    if all_digits and all_digits[-1] == -1.0:
        all_digits.pop()
    if not all_digits:
        all_digits = [0.0]
    return np.array(all_digits)


OPERATIONS["context_radix_encode"] = {
    "fn": context_radix_encode,
    "input_type": "array",
    "output_type": "array",
    "description": "Encode values in domain-dependent base (x[0]=domain tag)"
}


def context_radix_decode(x):
    """Decode domain-tagged digits back to values. x[0] is domain tag,
    remaining are digits (separated by -1). Input: array. Output: array."""
    domain = int(round(x[0])) % 5 if len(x) > 0 else 0
    base = DOMAIN_RADICES[domain]
    # Split by separator -1
    current_digits = []
    values = []
    for val in x[1:]:
        if val < 0:
            if current_digits:
                values.append(float(_decode_from_base(current_digits, base)))
                current_digits = []
        else:
            current_digits.append(int(round(val)))
    if current_digits:
        values.append(float(_decode_from_base(current_digits, base)))
    if not values:
        values = [0.0]
    return np.array(values)


OPERATIONS["context_radix_decode"] = {
    "fn": context_radix_decode,
    "input_type": "array",
    "output_type": "array",
    "description": "Decode domain-tagged digits back to decimal values"
}


def multi_system_add(x):
    """Cross-domain addition: x[0]=domain_a, x[1]=value_a, x[2]=domain_b, x[3]=value_b.
    Converts both to decimal, adds, returns result in domain_a's base.
    Input: array. Output: array."""
    if len(x) < 4:
        return np.array([0.0])
    domain_a = int(round(x[0])) % 5
    val_a = abs(x[1])
    domain_b = int(round(x[2])) % 5
    val_b = abs(x[3])
    # Both are already in decimal (the values), just add
    total = val_a + val_b
    base_a = DOMAIN_RADICES[domain_a]
    digits = _encode_in_base(total, base_a)
    return np.array([float(d) for d in digits])


OPERATIONS["multi_system_add"] = {
    "fn": multi_system_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Cross-domain addition with conversion to domain_a's base"
}


def cross_system_consistency_check(x):
    """Check if a value encoded in one domain decodes consistently in another.
    x[0]=source domain, x[1]=target domain, x[2:]=digits.
    Returns 1.0 if round-trip is exact, 0.0 otherwise.
    Input: array. Output: scalar."""
    if len(x) < 3:
        return 0.0
    src_domain = int(round(x[0])) % 5
    tgt_domain = int(round(x[1])) % 5
    digits = [int(round(d)) for d in x[2:]]
    src_base = DOMAIN_RADICES[src_domain]
    tgt_base = DOMAIN_RADICES[tgt_domain]
    # Decode in source base
    value = _decode_from_base(digits, src_base)
    # Re-encode in target, then decode back in target
    tgt_digits = _encode_in_base(value, tgt_base)
    reconstructed = _decode_from_base(tgt_digits, tgt_base)
    return 1.0 if reconstructed == value else 0.0


OPERATIONS["cross_system_consistency_check"] = {
    "fn": cross_system_consistency_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Checks round-trip consistency across domain encodings"
}


def context_switch_cost(x):
    """Compute the cost of switching between domains: the number of extra
    digits needed when re-encoding. x[0]=source domain, x[1]=target domain,
    x[2]=value. Input: array. Output: scalar."""
    if len(x) < 3:
        return 0.0
    src_domain = int(round(x[0])) % 5
    tgt_domain = int(round(x[1])) % 5
    value = int(round(abs(x[2])))
    src_digits = len(_encode_in_base(value, DOMAIN_RADICES[src_domain]))
    tgt_digits = len(_encode_in_base(value, DOMAIN_RADICES[tgt_domain]))
    return float(abs(tgt_digits - src_digits))


OPERATIONS["context_switch_cost"] = {
    "fn": context_switch_cost,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Extra digits needed when re-encoding across domains"
}


def domain_detect_from_digits(x):
    """Given digits, detect which domain is most likely based on max digit value.
    If max digit < 6: grain(base 6). < 10: livestock. < 12: labor.
    < 18: land. else: trade(base 20). Input: array. Output: scalar."""
    max_digit = int(np.max(np.abs(x))) if len(x) > 0 else 0
    if max_digit < 6:
        return 0.0  # grain
    elif max_digit < 10:
        return 1.0  # livestock
    elif max_digit < 12:
        return 3.0  # labor
    elif max_digit < 18:
        return 2.0  # land
    else:
        return 4.0  # trade


OPERATIONS["domain_detect_from_digits"] = {
    "fn": domain_detect_from_digits,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Detects most likely domain from digit values"
}


def mixed_domain_checksum(x):
    """Compute a domain-aware checksum: sum of (digit * position * radix) mod 997.
    x[0]=domain tag, x[1:]=values. Input: array. Output: scalar."""
    domain = int(round(x[0])) % 5 if len(x) > 0 else 0
    base = DOMAIN_RADICES[domain]
    checksum = 0
    for i, val in enumerate(x[1:]):
        checksum = (checksum + int(round(abs(val))) * (i + 1) * base) % 997
    return float(checksum)


OPERATIONS["mixed_domain_checksum"] = {
    "fn": mixed_domain_checksum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Domain-aware positional checksum mod 997"
}


def radix_ambiguity_count(x):
    """Count how many domains could validly interpret the given digits.
    A digit sequence is valid in base B if all digits < B.
    Input: array. Output: scalar."""
    if len(x) == 0:
        return 5.0  # empty sequence valid everywhere
    max_digit = int(np.max(np.abs(x)))
    count = 0
    for domain, base in DOMAIN_RADICES.items():
        if max_digit < base:
            count += 1
    return float(count)


OPERATIONS["radix_ambiguity_count"] = {
    "fn": radix_ambiguity_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of domains that could validly interpret the digits"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
