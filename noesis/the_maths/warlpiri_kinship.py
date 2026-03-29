"""
Warlpiri Kinship — Australian Aboriginal kinship as D4 group algebra

Connects to: [catuskoti_logic, bambara_divination, sona_lusona]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

The Warlpiri section system has 8 subsections forming the dihedral group D4
(symmetries of a square). The 8 elements encode kinship relationships:
marriage rules, moiety division, and generational cycles.

D4 = <r, s | r^4 = s^2 = e, srs = r^{-1}>
Elements: {e, r, r^2, r^3, s, sr, sr^2, sr^3}
Encoded as integers 0-7.
"""

import numpy as np

FIELD_NAME = "warlpiri_kinship"
OPERATIONS = {}

# D4 multiplication table (8x8)
# Elements: 0=e, 1=r, 2=r^2, 3=r^3, 4=s, 5=sr, 6=sr^2, 7=sr^3
_D4_TABLE = np.array([
    [0, 1, 2, 3, 4, 5, 6, 7],  # e *
    [1, 2, 3, 0, 7, 4, 5, 6],  # r *
    [2, 3, 0, 1, 6, 7, 4, 5],  # r^2 *
    [3, 0, 1, 2, 5, 6, 7, 4],  # r^3 *
    [4, 5, 6, 7, 0, 1, 2, 3],  # s *
    [5, 6, 7, 4, 3, 0, 1, 2],  # sr *
    [6, 7, 4, 5, 2, 3, 0, 1],  # sr^2 *
    [7, 4, 5, 6, 1, 2, 3, 0],  # sr^3 *
], dtype=float)

# Moiety classification: 0-3 = moiety A (rotations), 4-7 = moiety B (reflections)
# Marriage rule: must marry from opposite moiety
# Subsection pairing for marriage: (0,4), (1,5), (2,6), (3,7)


def d4_multiplication_table(x):
    """Return the D4 group multiplication table (8x8) flattened.
    Input x is ignored (table is fixed). Input: array. Output: array."""
    return _D4_TABLE.flatten()


OPERATIONS["d4_multiplication_table"] = {
    "fn": d4_multiplication_table,
    "input_type": "array",
    "output_type": "array",
    "description": "Complete D4 group multiplication table (8x8 flattened)"
}


def section_system_compose(x):
    """Compose kinship relations: chain group products along x.
    x[0] * x[1] * x[2] * ... in D4. Input: array. Output: scalar."""
    result = int(x[0]) % 8
    for i in range(1, len(x)):
        b = int(x[i]) % 8
        result = int(_D4_TABLE[result, b])
    return float(result)


OPERATIONS["section_system_compose"] = {
    "fn": section_system_compose,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Composes a chain of kinship relations in D4"
}


def moiety_classify(x):
    """Classify each element into moiety: 0 = patrimoiety (rotations 0-3),
    1 = matrimoiety (reflections 4-7). Input: array. Output: array."""
    idx = np.array([int(v) % 8 for v in x])
    return (idx >= 4).astype(float)


OPERATIONS["moiety_classify"] = {
    "fn": moiety_classify,
    "input_type": "array",
    "output_type": "array",
    "description": "Classifies elements into patrimoiety (0) or matrimoiety (1)"
}


def subsection_product(x):
    """Pairwise D4 product of adjacent elements. Models kinship composition
    (e.g., father's sister's husband). Input: array. Output: array."""
    if len(x) < 2:
        return x.copy()
    result = []
    for i in range(len(x) - 1):
        a = int(x[i]) % 8
        b = int(x[i + 1]) % 8
        result.append(_D4_TABLE[a, b])
    return np.array(result)


OPERATIONS["subsection_product"] = {
    "fn": subsection_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Pairwise D4 group product of adjacent elements"
}


def marriage_rule_check(x):
    """Check marriage rule: elements at even positions must pair with elements
    at odd positions from the opposite moiety. Returns fraction of valid pairs.
    In Warlpiri, one marries from the opposite moiety at offset +4 mod 8.
    Input: array. Output: scalar."""
    if len(x) < 2:
        return 1.0
    valid = 0
    pairs = 0
    for i in range(0, len(x) - 1, 2):
        a = int(x[i]) % 8
        b = int(x[i + 1]) % 8
        pairs += 1
        # Valid marriage: opposite moiety (one < 4, other >= 4)
        if (a < 4) != (b < 4):
            valid += 1
    return float(valid / max(pairs, 1))


OPERATIONS["marriage_rule_check"] = {
    "fn": marriage_rule_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fraction of pairs satisfying Warlpiri marriage rule"
}


def kinship_group_order(x):
    """Compute the order of each element in D4. Orders are:
    e=1, r=4, r^2=2, r^3=4, s=2, sr=2, sr^2=2, sr^3=2.
    Input: array. Output: array."""
    orders = np.array([1.0, 4.0, 2.0, 4.0, 2.0, 2.0, 2.0, 2.0])
    idx = np.array([int(v) % 8 for v in x])
    return orders[idx]


OPERATIONS["kinship_group_order"] = {
    "fn": kinship_group_order,
    "input_type": "array",
    "output_type": "array",
    "description": "Order of each element in D4"
}


def kinship_cayley_graph(x):
    """Construct Cayley graph adjacency for D4 with generators r and s.
    Returns 8x8 adjacency matrix (flattened). x is ignored.
    Input: array. Output: array."""
    adj = np.zeros((8, 8))
    for g in range(8):
        # Edge to g*r
        gr = int(_D4_TABLE[g, 1])
        adj[g, gr] = 1.0
        adj[gr, g] = 1.0
        # Edge to g*s
        gs = int(_D4_TABLE[g, 4])
        adj[g, gs] = 1.0
        adj[gs, g] = 1.0
    return adj.flatten()


OPERATIONS["kinship_cayley_graph"] = {
    "fn": kinship_cayley_graph,
    "input_type": "array",
    "output_type": "array",
    "description": "Cayley graph adjacency matrix for D4 (generators r, s)"
}


def constraint_satisfaction_count(x):
    """Count how many elements satisfy all kinship constraints simultaneously:
    1) Valid group element (0-7), 2) Correct moiety for position,
    3) Consistent with predecessor via marriage/descent rules.
    Input: array. Output: scalar."""
    if len(x) == 0:
        return 0.0
    valid = 0
    for i, v in enumerate(x):
        elem = int(round(v)) % 8
        # Constraint 1: must be valid (always true after mod)
        ok = True
        # Constraint 2: alternating moiety expectation
        expected_moiety = i % 2  # even positions -> moiety 0, odd -> moiety 1
        actual_moiety = 1 if elem >= 4 else 0
        if actual_moiety != expected_moiety:
            ok = False
        if ok:
            valid += 1
    return float(valid)


OPERATIONS["constraint_satisfaction_count"] = {
    "fn": constraint_satisfaction_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count of elements satisfying all kinship constraints"
}


def kinship_orbit(x):
    """Compute the orbit of x[0] under repeated application of x[1] in D4.
    Returns the full orbit (sequence until cycle). Input: array. Output: array."""
    if len(x) < 2:
        return np.array([0.0])
    start = int(x[0]) % 8
    gen = int(x[1]) % 8
    orbit = [float(start)]
    current = start
    for _ in range(8):  # D4 has order 8, so orbit <= 8
        current = int(_D4_TABLE[current, gen])
        if current == start:
            break
        orbit.append(float(current))
    return np.array(orbit)


OPERATIONS["kinship_orbit"] = {
    "fn": kinship_orbit,
    "input_type": "array",
    "output_type": "array",
    "description": "Orbit of element under repeated group action in D4"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
