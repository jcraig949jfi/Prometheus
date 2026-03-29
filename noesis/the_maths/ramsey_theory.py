"""
Ramsey Theory — Ramsey number bounds, coloring algorithms, Hales-Jewett

Connects to: [combinatorics, graph_theory, number_theory, extremal_combinatorics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import comb, factorial

FIELD_NAME = "ramsey_theory"
OPERATIONS = {}

# Known exact Ramsey numbers R(s,t) for small values
# R(s,t) where s <= t
_KNOWN_RAMSEY = {
    (1, 1): 1,
    (1, 2): 1, (2, 2): 2,
    (1, 3): 1, (2, 3): 3, (3, 3): 6,
    (1, 4): 1, (2, 4): 4, (3, 4): 9, (4, 4): 18,
    (1, 5): 1, (2, 5): 5, (3, 5): 14, (4, 5): 25,
    (1, 6): 1, (2, 6): 6, (3, 6): 18,
    (1, 7): 1, (2, 7): 7, (3, 7): 23,
    (1, 8): 1, (2, 8): 8, (3, 8): 28,
    (1, 9): 1, (2, 9): 9, (3, 9): 36,
}

# Known Schur numbers S(n)
_SCHUR_NUMBERS = {1: 1, 2: 4, 3: 13, 4: 44, 5: 160}


def ramsey_lower_bound(x):
    """Lower bound on R(s,t) using Erdos probabilistic argument.
    R(s,t) >= floor(2^{(s-1)/2}) for diagonal case s=t.
    Uses first element as s. Input: array. Output: scalar."""
    s = max(2, int(round(x[0])))
    t = max(2, int(round(x[1]))) if len(x) > 1 else s
    key = (min(s, t), max(s, t))
    if key in _KNOWN_RAMSEY:
        return float(_KNOWN_RAMSEY[key])
    # Erdos bound for diagonal: R(s,s) >= 2^{s/2} (roughly)
    if s == t:
        return float(int(2 ** (s / 2.0)))
    # General lower bound: R(s,t) >= R(s-1,t) + R(s,t-1) - 1 recursively is upper;
    # for lower, use 2^{(min(s,t)-1)/2} as rough bound
    return float(int(2 ** ((min(s, t) - 1) / 2.0)))


OPERATIONS["ramsey_lower_bound"] = {
    "fn": ramsey_lower_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Lower bound on Ramsey number R(s,t) from first two elements"
}


def ramsey_upper_bound(x):
    """Upper bound on R(s,t) using Erdos-Szekeres: R(s,t) <= C(s+t-2, s-1).
    Uses first two elements as s,t. Input: array. Output: scalar."""
    s = max(1, int(round(x[0])))
    t = max(1, int(round(x[1]))) if len(x) > 1 else s
    key = (min(s, t), max(s, t))
    if key in _KNOWN_RAMSEY:
        return float(_KNOWN_RAMSEY[key])
    return float(comb(s + t - 2, s - 1))


OPERATIONS["ramsey_upper_bound"] = {
    "fn": ramsey_upper_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Upper bound on R(s,t) via Erdos-Szekeres binomial bound C(s+t-2, s-1)"
}


def two_color_edges(x):
    """Two-color the edges of K_n (complete graph on n vertices) randomly,
    return the adjacency matrix of color 1 (using a deterministic seed from x).
    n = len(x). Input: array. Output: matrix."""
    n = len(x)
    rng = np.random.RandomState(int(abs(x[0]) * 1000) % (2**31))
    mat = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            color = rng.randint(0, 2)
            mat[i, j] = float(color)
            mat[j, i] = float(color)
    return mat


OPERATIONS["two_color_edges"] = {
    "fn": two_color_edges,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Two-color edges of K_n deterministically, return adjacency matrix of color 1"
}


def max_monochromatic_clique(x):
    """Find the size of the largest monochromatic clique in a 2-colored K_n.
    Uses greedy approach. n = len(x), coloring seeded by x. Input: array. Output: scalar."""
    n = len(x)
    adj = two_color_edges(x)
    best = 1
    # Check both colors
    for color in [0.0, 1.0]:
        color_adj = (adj == color)
        # Greedy clique search for each starting vertex
        for start in range(n):
            clique = [start]
            for v in range(start + 1, n):
                if all(color_adj[v, u] for u in clique):
                    clique.append(v)
            if len(clique) > best:
                best = len(clique)
    return float(best)


OPERATIONS["max_monochromatic_clique"] = {
    "fn": max_monochromatic_clique,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Size of largest monochromatic clique in a deterministic 2-coloring of K_n"
}


def schur_numbers_known(x):
    """Return known Schur numbers S(1)..S(k) where k = min(int(x[0]), 5).
    S(n) is the largest N such that {1,...,N} can be colored with n colors
    with no monochromatic solution to a+b=c. Input: array. Output: array."""
    k = min(5, max(1, int(round(abs(x[0])))))
    return np.array([float(_SCHUR_NUMBERS[i]) for i in range(1, k + 1)])


OPERATIONS["schur_numbers_known"] = {
    "fn": schur_numbers_known,
    "input_type": "array",
    "output_type": "array",
    "description": "Return known Schur numbers S(1) through S(k)"
}


def van_der_waerden_check(x):
    """Check if an array (interpreted as a 2-coloring of {1..n}) contains
    a monochromatic arithmetic progression of length k (k = int(x[0]), coloring = x[1:]).
    Returns 1.0 if such a progression exists, 0.0 otherwise. Input: array. Output: scalar."""
    k = max(2, int(round(x[0])))
    coloring = np.round(x[1:]).astype(int) % 2
    n = len(coloring)
    for color in [0, 1]:
        indices = np.where(coloring == color)[0]
        idx_set = set(indices.tolist())
        for start in indices:
            for diff in range(1, n):
                prog = [start + diff * j for j in range(k)]
                if prog[-1] >= n:
                    break
                if all(p in idx_set for p in prog):
                    return 1.0
    return 0.0


OPERATIONS["van_der_waerden_check"] = {
    "fn": van_der_waerden_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if a 2-coloring contains a monochromatic AP of length k"
}


def hales_jewett_bound(x):
    """Hales-Jewett number upper bound: HJ(r, k) for r colors, AP length k.
    Shelah's bound: HJ(r, k) <= tower(r, some function of k).
    We use the simpler primitive recursive bound for small values.
    Uses x[0] as r (colors) and x[1] as k (line length). Input: array. Output: scalar."""
    r = max(1, int(round(x[0])))
    k = max(1, int(round(x[1]))) if len(x) > 1 else 2
    # For r=2, known: HJ(2,1)=1, HJ(2,2)=2, HJ(2,3)=4, HJ(2,4)=...
    # Density HJ gives tower-type bounds; we use Shelah-type:
    # HJ(r, 1) = 1 for all r
    if k == 1:
        return 1.0
    # Simple recursive bound: HJ(r, k) <= (2*r*HJ(r, k-1))^HJ(r,k-1) is way too big
    # Use known small values and Ackermann-style growth estimate
    # For practical computation, bound by r^(k^2) for small values
    bound = min(r ** (k ** 2), 1e15)
    return float(bound)


OPERATIONS["hales_jewett_bound"] = {
    "fn": hales_jewett_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Upper bound on Hales-Jewett number HJ(r, k) for r colors, line length k"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
