"""
Bambara Divination — West African binary mathematics in GF(2)^4

Connects to: [catuskoti_logic, yoruba_signed_digit, warlpiri_kinship]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

West African geomantic divination uses 16 figures, each a 4-bit binary vector.
Operations are performed in GF(2)^4 (the 4-dimensional vector space over the
field with 2 elements). Addition is XOR, and the 16 figures form a group
under this operation.
"""

import numpy as np

FIELD_NAME = "bambara_divination"
OPERATIONS = {}


def _to_gf2_4(val):
    """Convert a float to a 4-bit GF(2) vector."""
    n = int(round(abs(val))) % 16
    return np.array([(n >> i) & 1 for i in range(4)], dtype=float)


def _from_gf2_4(bits):
    """Convert a 4-bit GF(2) vector to an integer."""
    return float(sum(int(b) * (1 << i) for i, b in enumerate(bits[:4])))


def gf2_4_add(x):
    """XOR addition in GF(2)^4 for adjacent pairs. Input: array. Output: array."""
    if len(x) < 2:
        return x.copy()
    results = []
    for i in range(0, len(x) - 1, 2):
        a = _to_gf2_4(x[i])
        b = _to_gf2_4(x[i + 1])
        xor_result = (a + b) % 2
        results.append(_from_gf2_4(xor_result))
    return np.array(results)


OPERATIONS["gf2_4_add"] = {
    "fn": gf2_4_add,
    "input_type": "array",
    "output_type": "array",
    "description": "XOR addition in GF(2)^4 for adjacent pairs"
}


def gf2_4_multiply(x):
    """Multiplication in GF(2^4) with irreducible polynomial x^4 + x + 1.
    Multiplies adjacent pairs. Input: array. Output: array."""
    # GF(2^4) with primitive polynomial p(x) = x^4 + x + 1 (0b10011 = 19)
    def _gf_mult(a, b):
        a = int(round(abs(a))) % 16
        b = int(round(abs(b))) % 16
        result = 0
        for i in range(4):
            if (b >> i) & 1:
                result ^= (a << i)
        # Reduce modulo x^4 + x + 1
        for i in range(7, 3, -1):
            if (result >> i) & 1:
                result ^= (0b10011 << (i - 4))
        return float(result & 0xF)

    if len(x) < 2:
        return x.copy()
    results = []
    for i in range(0, len(x) - 1, 2):
        results.append(_gf_mult(x[i], x[i + 1]))
    return np.array(results)


OPERATIONS["gf2_4_multiply"] = {
    "fn": gf2_4_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiplication in GF(2^4) for adjacent pairs"
}


def figure_generate_random(x):
    """Generate geomantic figures using input as seed.
    Each element mod 16 gives a figure. Returns 4-bit expansions.
    Input: array. Output: array."""
    figures = []
    for val in x:
        bits = _to_gf2_4(val)
        figures.extend(bits)
    return np.array(figures)


OPERATIONS["figure_generate_random"] = {
    "fn": figure_generate_random,
    "input_type": "array",
    "output_type": "array",
    "description": "Generates geomantic figures as 4-bit vectors from input"
}


def figure_combine(x):
    """Combine all figures by successive XOR (the traditional method of
    generating daughter figures from mother figures).
    Input: array. Output: scalar."""
    result = _to_gf2_4(x[0]) if len(x) > 0 else np.zeros(4)
    for i in range(1, len(x)):
        b = _to_gf2_4(x[i])
        result = (result + b) % 2
    return _from_gf2_4(result)


OPERATIONS["figure_combine"] = {
    "fn": figure_combine,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Combines all figures by successive XOR"
}


def transformation_orbit(x):
    """Compute the orbit of x[0] under repeated XOR with x[1].
    Returns the orbit until it cycles back. Input: array. Output: array."""
    if len(x) < 2:
        return np.array([0.0])
    start = int(round(abs(x[0]))) % 16
    gen = int(round(abs(x[1]))) % 16
    if gen == 0:
        return np.array([float(start)])
    orbit = [float(start)]
    current = start
    for _ in range(16):
        current = current ^ gen
        if current == start:
            break
        orbit.append(float(current))
    return np.array(orbit)


OPERATIONS["transformation_orbit"] = {
    "fn": transformation_orbit,
    "input_type": "array",
    "output_type": "array",
    "description": "Orbit of figure under repeated XOR transformation"
}


def parity_classify(x):
    """Classify each figure by parity (popcount of 4-bit representation).
    Returns popcount for each element. Input: array. Output: array."""
    result = []
    for val in x:
        bits = _to_gf2_4(val)
        result.append(float(np.sum(bits)))
    return np.array(result)


OPERATIONS["parity_classify"] = {
    "fn": parity_classify,
    "input_type": "array",
    "output_type": "array",
    "description": "Popcount (parity) classification of each figure"
}


def gf2_4_basis(x):
    """Return the standard basis of GF(2)^4: {0001, 0010, 0100, 1000}.
    Input x is ignored. Input: array. Output: array."""
    basis = np.array([
        1, 0, 0, 0,  # e1 = 0001
        0, 1, 0, 0,  # e2 = 0010
        0, 0, 1, 0,  # e3 = 0100
        0, 0, 0, 1,  # e4 = 1000
    ], dtype=float)
    return basis


OPERATIONS["gf2_4_basis"] = {
    "fn": gf2_4_basis,
    "input_type": "array",
    "output_type": "array",
    "description": "Standard basis vectors of GF(2)^4"
}


def figure_complement(x):
    """Compute bitwise complement (XOR with 1111 = 15) of each figure.
    Input: array. Output: array."""
    result = []
    for val in x:
        n = int(round(abs(val))) % 16
        result.append(float(n ^ 15))
    return np.array(result)


OPERATIONS["figure_complement"] = {
    "fn": figure_complement,
    "input_type": "array",
    "output_type": "array",
    "description": "Bitwise complement of each geomantic figure"
}


def group_orbit_size(x):
    """Compute the size of the orbit/subgroup generated by the figures in x.
    Generates all elements reachable by XOR combinations.
    Input: array. Output: scalar."""
    elements = set()
    figures = [int(round(abs(v))) % 16 for v in x]
    # Start with all input figures
    elements.update(figures)
    elements.add(0)  # identity
    # Close under XOR
    changed = True
    while changed:
        changed = False
        new_elements = set()
        for a in elements:
            for b in elements:
                c = a ^ b
                if c not in elements:
                    new_elements.add(c)
                    changed = True
        elements.update(new_elements)
    return float(len(elements))


OPERATIONS["group_orbit_size"] = {
    "fn": group_orbit_size,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Size of subgroup generated by input figures under XOR"
}


def geomantic_correspondence_matrix(x):
    """Build the 16x16 XOR table (Cayley table for GF(2)^4 under addition).
    Input x is ignored. Input: array. Output: array."""
    table = np.zeros((16, 16))
    for i in range(16):
        for j in range(16):
            table[i, j] = float(i ^ j)
    return table.flatten()


OPERATIONS["geomantic_correspondence_matrix"] = {
    "fn": geomantic_correspondence_matrix,
    "input_type": "array",
    "output_type": "array",
    "description": "Complete 16x16 XOR Cayley table for GF(2)^4"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
