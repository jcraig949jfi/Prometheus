"""
Reversible Computing — Toffoli gates, Fredkin gates, reversible circuit synthesis, bijective computation

Connects to: [formal_logic_systems, proof_complexity, automata_infinite_words]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "reversible_computing"
OPERATIONS = {}


def toffoli_gate(x):
    """Apply Toffoli (CCNOT) gate to 3-bit groups in the array.
    Toffoli: if first two bits are 1, flip the third. Bits: x > 0.5.
    Input: array. Output: array."""
    bits = (x > 0.5).astype(float)
    result = bits.copy()
    n = len(bits)
    for i in range(0, n - 2, 3):
        if bits[i] == 1.0 and bits[i + 1] == 1.0:
            result[i + 2] = 1.0 - bits[i + 2]
    return result


OPERATIONS["toffoli_gate"] = {
    "fn": toffoli_gate,
    "input_type": "array",
    "output_type": "array",
    "description": "Apply Toffoli (CCNOT) gate to each 3-bit group"
}


def fredkin_gate(x):
    """Apply Fredkin (CSWAP) gate to 3-bit groups.
    Fredkin: if first bit is 1, swap the other two.
    Input: array. Output: array."""
    bits = (x > 0.5).astype(float)
    result = bits.copy()
    n = len(bits)
    for i in range(0, n - 2, 3):
        if bits[i] == 1.0:
            result[i + 1], result[i + 2] = bits[i + 2], bits[i + 1]
    return result


OPERATIONS["fredkin_gate"] = {
    "fn": fredkin_gate,
    "input_type": "array",
    "output_type": "array",
    "description": "Apply Fredkin (CSWAP) gate to each 3-bit group"
}


def cnot_gate(x):
    """Apply CNOT gate to pairs: if control (even index) is 1, flip target (odd index).
    Input: array. Output: array."""
    bits = (x > 0.5).astype(float)
    result = bits.copy()
    for i in range(0, len(bits) - 1, 2):
        if bits[i] == 1.0:
            result[i + 1] = 1.0 - bits[i + 1]
    return result


OPERATIONS["cnot_gate"] = {
    "fn": cnot_gate,
    "input_type": "array",
    "output_type": "array",
    "description": "Apply CNOT to pairs: flip target if control is 1"
}


def swap_gate(x):
    """Apply SWAP gate to adjacent pairs. Input: array. Output: array."""
    result = x.copy()
    for i in range(0, len(result) - 1, 2):
        result[i], result[i + 1] = x[i + 1], x[i]
    return result


OPERATIONS["swap_gate"] = {
    "fn": swap_gate,
    "input_type": "array",
    "output_type": "array",
    "description": "Swap adjacent pairs of elements"
}


def reversible_not(x):
    """Apply NOT (bit flip) to all bits. This is its own inverse. Input: array. Output: array."""
    bits = (x > 0.5).astype(float)
    return 1.0 - bits


OPERATIONS["reversible_not"] = {
    "fn": reversible_not,
    "input_type": "array",
    "output_type": "array",
    "description": "Flip all bits (reversible NOT, self-inverse)"
}


def reversible_circuit_compose(x):
    """Compose a sequence of reversible gates: NOT -> CNOT -> Toffoli.
    Input: array. Output: array."""
    step1 = reversible_not(x)
    step2 = cnot_gate(step1)
    step3 = toffoli_gate(step2)
    return step3


OPERATIONS["reversible_circuit_compose"] = {
    "fn": reversible_circuit_compose,
    "input_type": "array",
    "output_type": "array",
    "description": "Compose NOT -> CNOT -> Toffoli as a reversible circuit"
}


def circuit_inverse(x):
    """Compute the inverse circuit of NOT -> CNOT -> Toffoli (reverse order, each self-inverse).
    Toffoli, CNOT, NOT are each self-inverse, so inverse = Toffoli -> CNOT -> NOT.
    Input: array. Output: array."""
    step1 = toffoli_gate(x)
    step2 = cnot_gate(step1)
    step3 = reversible_not(step2)
    return step3


OPERATIONS["circuit_inverse"] = {
    "fn": circuit_inverse,
    "input_type": "array",
    "output_type": "array",
    "description": "Inverse of composed circuit (Toffoli -> CNOT -> NOT)"
}


def reversible_add_modular(x):
    """Reversible modular addition: interpret array as two n/2-bit numbers, add mod 2^(n/2).
    Input: array. Output: array (first half = a, second half = a+b mod 2^k)."""
    bits = (x > 0.5).astype(int)
    n = len(bits)
    k = n // 2
    if k == 0:
        return x.copy().astype(float)
    # Convert halves to integers
    a = 0
    for i in range(k):
        a = (a << 1) | bits[i]
    b = 0
    for i in range(k, 2 * k):
        b = (b << 1) | bits[i]
    s = (a + b) % (2 ** k)
    # Encode result: first half unchanged, second half = sum
    result = np.zeros(n)
    for i in range(k):
        result[i] = float(bits[i])
    for i in range(k):
        result[k + i] = float((s >> (k - 1 - i)) & 1)
    return result


OPERATIONS["reversible_add_modular"] = {
    "fn": reversible_add_modular,
    "input_type": "array",
    "output_type": "array",
    "description": "Reversible modular addition of two bit-halves"
}


def bijection_verify(x):
    """Verify that a function (given by mapping) is a bijection.
    Interpret x as a permutation (indices). Round, take mod n, check if it's a valid permutation.
    Input: array. Output: scalar (1 if bijection, 0 if not)."""
    n = len(x)
    indices = np.round(np.abs(x)).astype(int) % n
    return float(len(set(indices)) == n)


OPERATIONS["bijection_verify"] = {
    "fn": bijection_verify,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if rounded array values form a bijection (permutation)"
}


def circuit_gate_count(x):
    """Estimate gate count for a reversible circuit implementing an arbitrary permutation on n bits.
    Upper bound: O(n * 2^n) Toffoli gates for n-bit reversible function.
    Return log2 of estimated gate count. Input: array (len = n bits). Output: scalar."""
    n = len(x)
    # Upper bound for arbitrary n-bit reversible function: O(n * 2^n) Toffoli gates
    gate_count_log2 = np.log2(max(n, 1)) + n
    return float(gate_count_log2)


OPERATIONS["circuit_gate_count"] = {
    "fn": circuit_gate_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Log2 of estimated Toffoli gate count for n-bit reversible function"
}


def landauer_erasure_bound(x):
    """Compute Landauer's erasure energy bound: E = n * k_B * T * ln(2) per erased bit.
    Returns energy in units of k_B*T for erasing len(x) bits at temperature derived from mean(x).
    Input: array. Output: scalar."""
    n_bits = len(x)
    # Temperature factor from array (normalized)
    T_factor = max(np.mean(np.abs(x)), 0.01)
    # Landauer bound: n * kT * ln(2)
    energy = n_bits * T_factor * np.log(2)
    return float(energy)


OPERATIONS["landauer_erasure_bound"] = {
    "fn": landauer_erasure_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Landauer erasure energy bound: n_bits * kT * ln(2)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
