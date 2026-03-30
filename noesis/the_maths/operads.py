"""
Operads — composition operations, associahedra, little disks (simplified)

Connects to: [species_arithmetic, category_theory, topology, umbral_calculus]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import comb, factorial

FIELD_NAME = "operads"
OPERATIONS = {}


def _catalan(n):
    """Compute the nth Catalan number."""
    if n < 0:
        return 0
    return comb(2 * n, n) // (n + 1)


def operad_composition(x):
    """Operad composition: given arities (a1, a2, ..., ak) compose operation of
    arity k with operations of arities a_i. Result arity = sum(a_i).
    Returns array of composed arities at each level.
    Input: array. Output: array."""
    n = len(x)
    arities = np.maximum(np.round(np.abs(x)), 1).astype(int)
    # Compose: level 0 = arity n (top operation), level 1 = individual arities
    # Total arity at each composition step
    result = np.zeros(n)
    cumulative = 0
    for i in range(n):
        cumulative += arities[i]
        result[i] = cumulative
    return result


OPERATIONS["operad_composition"] = {
    "fn": operad_composition,
    "input_type": "array",
    "output_type": "array",
    "description": "Cumulative arity under operad composition"
}


def associahedron_vertices(x):
    """Number of vertices of the associahedron K_n (Stasheff polytope).
    K_n has C_{n-1} vertices (Catalan number) where n = each element.
    Input: array. Output: array."""
    result = np.zeros(len(x))
    for i, v in enumerate(x):
        n = max(2, int(round(abs(v))))
        result[i] = _catalan(n - 1)
    return result


OPERATIONS["associahedron_vertices"] = {
    "fn": associahedron_vertices,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of vertices of associahedron K_n (Catalan numbers)"
}


def associahedron_catalan(x):
    """Compute Catalan numbers C_0 through C_{n-1} where n=len(x).
    These count the vertices of associahedra / full bracketings.
    Input: array. Output: array."""
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        result[i] = _catalan(i)
    return result


OPERATIONS["associahedron_catalan"] = {
    "fn": associahedron_catalan,
    "input_type": "array",
    "output_type": "array",
    "description": "Sequence of Catalan numbers C_0 through C_{n-1}"
}


def little_disks_config(x):
    """Configuration space of n little 2-disks inside the unit disk.
    Returns a matrix of (center_x, center_y, radius) for n non-overlapping disks
    arranged symmetrically. n = len(x). Input: array. Output: matrix."""
    n = len(x)
    config = np.zeros((n, 3))
    if n == 1:
        config[0] = [0.0, 0.0, 0.5]
        return config
    r_small = 1.0 / (1.0 + 1.0 / np.sin(np.pi / n)) if n > 1 else 0.5
    r_orbit = 1.0 - r_small
    for i in range(n):
        angle = 2 * np.pi * i / n
        config[i, 0] = r_orbit * np.cos(angle)
        config[i, 1] = r_orbit * np.sin(angle)
        config[i, 2] = r_small * 0.9  # slight shrink to ensure non-overlap
    return config


OPERATIONS["little_disks_config"] = {
    "fn": little_disks_config,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Symmetric configuration of n little 2-disks in unit disk"
}


def operad_arity(x):
    """For a sequence of operations, compute the arity profile.
    An operation on n inputs has arity n. Returns histogram of arities.
    Input: array. Output: array."""
    arities = np.maximum(np.round(np.abs(x)), 0).astype(int)
    if len(arities) == 0:
        return np.array([0.0])
    max_arity = max(int(np.max(arities)), 0)
    hist = np.zeros(max_arity + 1)
    for a in arities:
        hist[a] += 1
    return hist


OPERATIONS["operad_arity"] = {
    "fn": operad_arity,
    "input_type": "array",
    "output_type": "array",
    "description": "Histogram of operation arities"
}


def symmetric_operad_action(x):
    """Apply symmetric group action to an operad element.
    For arity n, the symmetric group S_n acts by permuting inputs.
    Returns the orbit size |S_n / Stab| = n! / |stabilizer|.
    We approximate stabilizer as the automorphism group of the pattern in x.
    Input: array. Output: scalar."""
    n = len(x)
    total_perms = factorial(n)
    # Count symmetries: permutations that leave x unchanged
    # For efficiency, count duplicates
    vals, counts = np.unique(np.round(x, 10), return_counts=True)
    stab_size = 1
    for c in counts:
        stab_size *= factorial(int(c))
    orbit_size = total_perms // stab_size
    return float(orbit_size)


OPERATIONS["symmetric_operad_action"] = {
    "fn": symmetric_operad_action,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Orbit size under symmetric group action on operad element"
}


def planar_tree_count(x):
    """Count planar rooted trees with n internal nodes for each n in x.
    This equals the Catalan number C_n. Input: array. Output: array."""
    result = np.zeros(len(x))
    for i, v in enumerate(x):
        n = max(0, int(round(abs(v))))
        result[i] = _catalan(n)
    return result


OPERATIONS["planar_tree_count"] = {
    "fn": planar_tree_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of planar rooted trees (Catalan numbers)"
}


def operad_free_algebra_dim(x):
    """Dimension of the free algebra over the associative operad in degree n.
    For the associative operad, free algebra on k generators in degree n
    has dimension k^n * n!. Here k=len(x), compute for n=1..k.
    Input: array. Output: array."""
    k = len(x)
    result = np.zeros(k)
    for n in range(1, k + 1):
        # Free associative algebra: dim = k^n (just words of length n on k letters)
        # This is the standard: free algebra on k generators, degree n = k^n
        result[n - 1] = float(k ** n)
    return result


OPERATIONS["operad_free_algebra_dim"] = {
    "fn": operad_free_algebra_dim,
    "input_type": "array",
    "output_type": "array",
    "description": "Dimension of free algebra on k generators in degrees 1..k"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
