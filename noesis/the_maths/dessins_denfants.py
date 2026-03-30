"""
Dessins d'Enfants — Belyi maps as bipartite graphs on surfaces, Grothendieck's theory

Connects to: [polytope_combinatorics, sheaves_on_graphs, discrete_morse_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import gcd, factorial

FIELD_NAME = "dessins_denfants"
OPERATIONS = {}


def _permutation_from_array(x, offset=0):
    """Convert array values to a permutation of {0, ..., n-1}.
    Uses argsort to get a valid permutation."""
    n = len(x)
    shifted = x + offset * np.arange(n, dtype=float)
    return np.argsort(shifted).astype(int)


def _count_cycles(perm):
    """Count the number of cycles in a permutation."""
    n = len(perm)
    visited = np.zeros(n, dtype=bool)
    cycles = 0
    for i in range(n):
        if not visited[i]:
            cycles += 1
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
    return cycles


def _cycle_type(perm):
    """Return the cycle type (sorted cycle lengths) of a permutation."""
    n = len(perm)
    visited = np.zeros(n, dtype=bool)
    lengths = []
    for i in range(n):
        if not visited[i]:
            length = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
                length += 1
            lengths.append(length)
    return sorted(lengths, reverse=True)


def _compose_perm(p, q):
    """Compose two permutations: (p*q)(i) = p(q(i))."""
    return p[q]


def _inverse_perm(p):
    """Compute the inverse permutation."""
    n = len(p)
    inv = np.zeros(n, dtype=int)
    inv[p] = np.arange(n, dtype=int)
    return inv


def belyi_dessin_from_permutations(x):
    """Construct a dessin from two permutations sigma0, sigma1 derived from input.
    A dessin is defined by (sigma0, sigma1) acting on {0,...,n-1} (half-edges).
    Returns: array [n_black_vertices, n_white_vertices, n_edges, n_faces].
    Input: array. Output: array."""
    n = len(x)
    sigma0 = _permutation_from_array(x, offset=0)
    sigma1 = _permutation_from_array(x, offset=1)
    # sigma_inf = (sigma0 * sigma1)^{-1}
    sigma01 = _compose_perm(sigma0, sigma1)
    sigma_inf = _inverse_perm(sigma01)
    n_black = _count_cycles(sigma0)   # black vertices
    n_white = _count_cycles(sigma1)   # white vertices
    n_edges = n                        # half-edges = degree of permutations
    n_faces = _count_cycles(sigma_inf)
    return np.array([float(n_black), float(n_white), float(n_edges), float(n_faces)])


OPERATIONS["belyi_dessin_from_permutations"] = {
    "fn": belyi_dessin_from_permutations,
    "input_type": "array",
    "output_type": "array",
    "description": "Constructs a dessin d'enfant from permutation pair, returns [black, white, edges, faces]"
}


def dessin_genus(x):
    """Compute the genus of the surface on which the dessin is embedded.
    g = 1 - chi/2 where chi = V - E + F (V = black + white vertices).
    Input: array. Output: scalar."""
    info = belyi_dessin_from_permutations(x)
    n_black, n_white, n_edges, n_faces = info
    V = n_black + n_white
    E = n_edges
    F = n_faces
    chi = V - E + F
    g = (2.0 - chi) / 2.0
    return float(g)


OPERATIONS["dessin_genus"] = {
    "fn": dessin_genus,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes genus of the Riemann surface from the dessin"
}


def dessin_face_count(x):
    """Count faces (cycles of sigma_inf = (sigma0 * sigma1)^{-1}).
    Input: array. Output: scalar."""
    info = belyi_dessin_from_permutations(x)
    return float(info[3])


OPERATIONS["dessin_face_count"] = {
    "fn": dessin_face_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Counts faces of the dessin (cycles of sigma_infinity)"
}


def dessin_euler_characteristic(x):
    """Compute Euler characteristic chi = V - E + F of the dessin embedding.
    Input: array. Output: scalar."""
    info = belyi_dessin_from_permutations(x)
    n_black, n_white, n_edges, n_faces = info
    chi = (n_black + n_white) - n_edges + n_faces
    return float(chi)


OPERATIONS["dessin_euler_characteristic"] = {
    "fn": dessin_euler_characteristic,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes Euler characteristic chi = V - E + F"
}


def passport_from_permutations(x):
    """Compute the passport (triple of cycle types) of the dessin.
    Returns flattened array: [cycle_type(sigma0), cycle_type(sigma1), cycle_type(sigma_inf)],
    padded with zeros. Input: array. Output: array."""
    n = len(x)
    sigma0 = _permutation_from_array(x, offset=0)
    sigma1 = _permutation_from_array(x, offset=1)
    sigma01 = _compose_perm(sigma0, sigma1)
    sigma_inf = _inverse_perm(sigma01)
    ct0 = _cycle_type(sigma0)
    ct1 = _cycle_type(sigma1)
    ct_inf = _cycle_type(sigma_inf)
    # Pad each to length n and concatenate
    def pad(ct):
        padded = np.zeros(n)
        for i, v in enumerate(ct):
            padded[i] = float(v)
        return padded
    return np.concatenate([pad(ct0), pad(ct1), pad(ct_inf)])


OPERATIONS["passport_from_permutations"] = {
    "fn": passport_from_permutations,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes the passport (triple of cycle types) of the dessin"
}


def clean_dessin_construct(x):
    """Construct a 'clean' dessin where sigma1 is a fixed-point-free involution.
    For n even, pairs elements as (0,1)(2,3)...; for n odd, last is fixed.
    Returns the dessin info. Input: array. Output: array."""
    n = len(x)
    sigma0 = _permutation_from_array(x, offset=0)
    # Clean dessin: sigma1 is an involution (product of transpositions)
    sigma1 = np.arange(n, dtype=int)
    for i in range(0, n - 1, 2):
        sigma1[i] = i + 1
        sigma1[i + 1] = i
    sigma01 = _compose_perm(sigma0, sigma1)
    sigma_inf = _inverse_perm(sigma01)
    n_black = _count_cycles(sigma0)
    n_white = _count_cycles(sigma1)
    n_faces = _count_cycles(sigma_inf)
    return np.array([float(n_black), float(n_white), float(n), float(n_faces)])


OPERATIONS["clean_dessin_construct"] = {
    "fn": clean_dessin_construct,
    "input_type": "array",
    "output_type": "array",
    "description": "Constructs a clean dessin with sigma1 as involution"
}


def dessin_automorphism_count(x):
    """Estimate the automorphism group order of the dessin.
    |Aut| = n / |orbit of a half-edge under the monodromy group|.
    Input: array. Output: scalar."""
    n = len(x)
    sigma0 = _permutation_from_array(x, offset=0)
    sigma1 = _permutation_from_array(x, offset=1)
    # Compute orbit of element 0 under <sigma0, sigma1>
    orbit = set()
    stack = [0]
    while stack:
        el = stack.pop()
        if el in orbit:
            continue
        orbit.add(el)
        stack.append(sigma0[el])
        stack.append(sigma1[el])
    orbit_size = len(orbit)
    # |Aut| divides n; estimate as n / orbit_size (for transitive action, orbit=n, so |Aut|=1 generically)
    aut_order = n // orbit_size if orbit_size > 0 else n
    return float(aut_order)


OPERATIONS["dessin_automorphism_count"] = {
    "fn": dessin_automorphism_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates the automorphism group order of the dessin"
}


def ramification_profile(x):
    """Compute the ramification profile: degrees of the Belyi map at critical points.
    These are the cycle lengths of sigma0, sigma1, sigma_inf.
    Returns sorted concatenation of all cycle lengths.
    Input: array. Output: array."""
    n = len(x)
    sigma0 = _permutation_from_array(x, offset=0)
    sigma1 = _permutation_from_array(x, offset=1)
    sigma01 = _compose_perm(sigma0, sigma1)
    sigma_inf = _inverse_perm(sigma01)
    ct0 = _cycle_type(sigma0)
    ct1 = _cycle_type(sigma1)
    ct_inf = _cycle_type(sigma_inf)
    all_ramification = sorted(ct0 + ct1 + ct_inf, reverse=True)
    return np.array([float(v) for v in all_ramification])


OPERATIONS["ramification_profile"] = {
    "fn": ramification_profile,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes ramification profile (all cycle lengths) of the dessin"
}


def dessin_cartographic_group_order(x):
    """Compute (estimate) the order of the cartographic group <sigma0, sigma1>.
    For a transitive group on n elements, order is between n and n!.
    Uses orbit counting to estimate. Input: array. Output: scalar."""
    n = len(x)
    sigma0 = _permutation_from_array(x, offset=0)
    sigma1 = _permutation_from_array(x, offset=1)
    # Count orbits of <sigma0, sigma1> on pairs to estimate group order
    # Burnside: |orbits| = (1/|G|) sum |Fix(g)|
    # Instead, estimate via: if transitive on n points, |G| >= n
    # Check transitivity
    orbit = set()
    stack = [0]
    while stack:
        el = stack.pop()
        if el in orbit:
            continue
        orbit.add(el)
        stack.append(sigma0[el])
        stack.append(sigma1[el])
    n_orbits_on_points = 1 if len(orbit) == n else 0
    if not n_orbits_on_points:
        # Not transitive: product of smaller groups
        return float(len(orbit))
    # For transitive group, compute order via stabilizer chain (simplified)
    # Generate elements up to a limit
    seen = set()
    current_perms = [sigma0, sigma1, _inverse_perm(sigma0), _inverse_perm(sigma1)]
    for p in current_perms:
        seen.add(tuple(p))
    for _ in range(min(n * 10, 200)):
        new_perms = []
        for p in list(seen)[:20]:
            for q in current_perms:
                comp = _compose_perm(np.array(p), q)
                t = tuple(comp)
                if t not in seen:
                    seen.add(t)
                    new_perms.append(comp)
        if not new_perms:
            break
        current_perms = new_perms[:10]
    return float(len(seen))


OPERATIONS["dessin_cartographic_group_order"] = {
    "fn": dessin_cartographic_group_order,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates order of the cartographic (monodromy) group"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
