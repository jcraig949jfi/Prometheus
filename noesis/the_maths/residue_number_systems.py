"""
Residue Number Systems — Represent integers by remainders mod coprime moduli. Parallel carry-free arithmetic.

Connects to: [modular_arithmetic_exotic, finite_fields, coding_theory, computational_algebra]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "residue_number_systems"
OPERATIONS = {}


def _default_moduli():
    """Default coprime moduli for RNS."""
    return np.array([3, 5, 7, 11, 13])


def _extended_gcd(a, b):
    """Extended Euclidean algorithm. Returns (g, x, y) where a*x + b*y = g."""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def _crt(residues, moduli):
    """Chinese Remainder Theorem: reconstruct integer from residues mod moduli."""
    M = 1
    for m in moduli:
        M *= int(m)
    result = 0
    for r, m in zip(residues, moduli):
        m = int(m)
        Mi = M // m
        _, x, _ = _extended_gcd(Mi % m, m)
        result += int(r) * Mi * x
    return result % M


def rns_encode(x):
    """Encode integers into RNS representation.
    Input: array [values..., then moduli count, then moduli].
    Simple mode: just values, uses default moduli.
    Output: flattened residue matrix."""
    x = np.asarray(x, dtype=float)
    moduli = _default_moduli()
    values = x
    results = []
    for v in values:
        n = int(v)
        residues = [n % int(m) for m in moduli]
        results.extend(residues)
    return np.array(results, dtype=float)


OPERATIONS["rns_encode"] = {
    "fn": rns_encode,
    "input_type": "array",
    "output_type": "array",
    "description": "Encode integers into RNS using default coprime moduli {3,5,7,11,13}"
}


def rns_decode(x):
    """Decode RNS residues back to integers using CRT.
    Input: array of residues (groups of 5 for default moduli). Output: array of integers."""
    x = np.asarray(x, dtype=float)
    moduli = _default_moduli()
    k = len(moduli)
    num_values = len(x) // k
    results = []
    for i in range(max(num_values, 1)):
        residues = x[i * k:(i + 1) * k]
        if len(residues) < k:
            residues = np.pad(residues, (0, k - len(residues)))
        val = _crt(residues.astype(int), moduli)
        results.append(val)
    return np.array(results, dtype=float)


OPERATIONS["rns_decode"] = {
    "fn": rns_decode,
    "input_type": "array",
    "output_type": "array",
    "description": "Decode RNS residues to integers via Chinese Remainder Theorem"
}


def rns_add(x):
    """Parallel carry-free addition in RNS.
    Input: array [a_residues (5), b_residues (5)]. Output: array of sum residues."""
    x = np.asarray(x, dtype=float)
    moduli = _default_moduli()
    k = len(moduli)
    a_res = x[:k] if len(x) >= k else np.pad(x, (0, k - len(x)))
    b_res = x[k:2*k] if len(x) >= 2*k else np.zeros(k)
    # Addition is just componentwise mod - NO CARRY needed!
    result = np.array([(int(a_res[i]) + int(b_res[i])) % int(moduli[i]) for i in range(k)], dtype=float)
    return result


OPERATIONS["rns_add"] = {
    "fn": rns_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Parallel carry-free RNS addition (componentwise mod)"
}


def rns_multiply(x):
    """Parallel carry-free multiplication in RNS.
    Input: array [a_residues (5), b_residues (5)]. Output: array of product residues."""
    x = np.asarray(x, dtype=float)
    moduli = _default_moduli()
    k = len(moduli)
    a_res = x[:k] if len(x) >= k else np.pad(x, (0, k - len(x)))
    b_res = x[k:2*k] if len(x) >= 2*k else np.ones(k)
    # Multiplication is componentwise mod - NO CARRY needed!
    result = np.array([(int(a_res[i]) * int(b_res[i])) % int(moduli[i]) for i in range(k)], dtype=float)
    return result


OPERATIONS["rns_multiply"] = {
    "fn": rns_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Parallel carry-free RNS multiplication (componentwise mod)"
}


def rns_overflow_detect(x):
    """Detect if an RNS value exceeds the dynamic range M = product of moduli.
    Since RNS wraps around, this checks if operations produced overflow.
    Uses approximate magnitude estimation via mixed-radix conversion.
    Input: array of residues. Output: scalar (estimated magnitude / M)."""
    x = np.asarray(x, dtype=float)
    moduli = _default_moduli()
    k = len(moduli)
    residues = x[:k] if len(x) >= k else np.pad(x, (0, k - len(x)))
    M = 1
    for m in moduli:
        M *= int(m)
    # Decode and check
    val = _crt(residues.astype(int), moduli)
    return np.float64(val / M)


OPERATIONS["rns_overflow_detect"] = {
    "fn": rns_overflow_detect,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Detect RNS overflow (value / dynamic range M)"
}


def rns_base_extension(x):
    """Extend RNS representation to include additional moduli.
    Given residues mod {m1,...,mk}, compute residues mod {mk+1,...} using CRT.
    Input: array [residues..., new_modulus]. Output: array [original residues, new residue]."""
    x = np.asarray(x, dtype=float)
    moduli = _default_moduli()
    k = len(moduli)
    residues = x[:k] if len(x) >= k else np.pad(x, (0, k - len(x)))
    new_mod = int(x[k]) if len(x) > k else 17
    # Reconstruct value via CRT
    val = _crt(residues.astype(int), moduli)
    # Compute new residue
    new_res = val % new_mod
    return np.append(residues, new_res)


OPERATIONS["rns_base_extension"] = {
    "fn": rns_base_extension,
    "input_type": "array",
    "output_type": "array",
    "description": "Extend RNS to additional modulus via CRT reconstruction"
}


def rns_comparison(x):
    """Compare two RNS numbers (the hard operation in RNS - no simple parallel method).
    Uses mixed-radix conversion for comparison.
    Input: array [a_residues (5), b_residues (5)]. Output: scalar (-1, 0, or 1)."""
    x = np.asarray(x, dtype=float)
    moduli = _default_moduli()
    k = len(moduli)
    a_res = x[:k] if len(x) >= k else np.pad(x, (0, k - len(x)))
    b_res = x[k:2*k] if len(x) >= 2*k else np.zeros(k)
    # Must reconstruct to compare - this is why comparison is expensive in RNS
    a_val = _crt(a_res.astype(int), moduli)
    b_val = _crt(b_res.astype(int), moduli)
    if a_val < b_val:
        return np.float64(-1)
    elif a_val > b_val:
        return np.float64(1)
    else:
        return np.float64(0)


OPERATIONS["rns_comparison"] = {
    "fn": rns_comparison,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Compare two RNS numbers (requires CRT reconstruction - the hard part)"
}


def rns_mixed_radix_convert(x):
    """Convert RNS to mixed-radix representation for magnitude estimation.
    Mixed-radix digits v_i satisfy: X = v_1 + v_2*m_1 + v_3*m_1*m_2 + ...
    Input: array of residues. Output: array of mixed-radix digits."""
    x = np.asarray(x, dtype=float)
    moduli = _default_moduli()
    k = len(moduli)
    residues = x[:k].astype(int) if len(x) >= k else np.pad(x, (0, k - len(x))).astype(int)
    # Garner's algorithm for mixed-radix conversion
    v = np.zeros(k, dtype=int)
    v[0] = int(residues[0]) % int(moduli[0])
    for i in range(1, k):
        # v[i] = (residues[i] - v[0] - v[1]*m[0] - ...) * (m[0]*m[1]*...*m[i-1])^{-1} mod m[i]
        val = int(residues[i])
        product = 1
        for j in range(i):
            val = val - int(v[j]) * product
            product *= int(moduli[j])
        # Compute inverse of product mod moduli[i]
        mi = int(moduli[i])
        _, inv, _ = _extended_gcd(product % mi, mi)
        v[i] = (val * inv) % mi
    return np.array(v, dtype=float)


OPERATIONS["rns_mixed_radix_convert"] = {
    "fn": rns_mixed_radix_convert,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert RNS to mixed-radix via Garner's algorithm"
}


def rns_moduli_selection(x):
    """Select optimal coprime moduli for RNS with given dynamic range.
    Chooses consecutive primes to maximize range while minimizing modulus size.
    Input: array [min_range, num_moduli]. Output: array of selected moduli."""
    x = np.asarray(x, dtype=float)
    min_range = int(x[0]) if len(x) > 0 else 1000
    num_moduli = int(x[1]) if len(x) > 1 else 5
    num_moduli = max(num_moduli, 2)
    num_moduli = min(num_moduli, 20)
    # Sieve for primes
    limit = max(200, num_moduli * 20)
    sieve = np.ones(limit, dtype=bool)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = False
    primes = np.where(sieve)[0]
    # Select smallest primes that give sufficient range
    selected = []
    product = 1
    for p in primes:
        selected.append(int(p))
        product *= int(p)
        if len(selected) >= num_moduli and product >= min_range:
            break
    # Ensure we have enough moduli
    while len(selected) < num_moduli:
        selected.append(int(primes[len(selected)]))
    return np.array(selected[:num_moduli], dtype=float)


OPERATIONS["rns_moduli_selection"] = {
    "fn": rns_moduli_selection,
    "input_type": "array",
    "output_type": "array",
    "description": "Select optimal coprime moduli for given dynamic range"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
