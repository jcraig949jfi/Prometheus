"""
Numerical Semigroups -- Frobenius numbers, gap sets, Apery sets, genus

Connects to: [number_theory, combinatorics, commutative_algebra, algebraic_geometry]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import gcd
from functools import reduce

FIELD_NAME = "numerical_semigroups"
OPERATIONS = {}


def _make_generators(x):
    """Extract positive integer generators from input array, ensure gcd=1."""
    gens = sorted(set(int(abs(v)) for v in x if abs(v) >= 1))
    if not gens:
        gens = [2, 3]
    # Ensure gcd = 1 for a numerical semigroup
    g = reduce(gcd, gens)
    if g > 1:
        gens = [v // g for v in gens]
    gens = sorted(set(g for g in gens if g >= 1))
    if 1 in gens:
        gens = [1]  # trivial semigroup
    return gens


def _compute_semigroup(gens, limit=None):
    """Compute all elements of the numerical semigroup up to a limit."""
    m = min(gens)
    if m == 1:
        return set(range(0, 100))
    if limit is None:
        # Frobenius bound: for 2 generators a,b: ab - a - b
        # General bound: use m * max(gens) as safe upper bound
        limit = max(gens) * m
    membership = np.zeros(limit + 1, dtype=bool)
    membership[0] = True
    for g in gens:
        for n in range(g, limit + 1):
            if membership[n - g]:
                membership[n] = True
    return set(np.where(membership)[0])


def frobenius_number(x):
    """Frobenius number (largest non-representable integer) of numerical semigroup.
    Input: array (generators). Output: scalar."""
    gens = _make_generators(x)
    if len(gens) == 1 and gens[0] == 1:
        return -1.0  # convention: F(N) = -1 for N = N_0
    if len(gens) == 2:
        a, b = gens[0], gens[1]
        return float(a * b - a - b)
    # General case: compute semigroup
    S = _compute_semigroup(gens)
    limit = max(S) if S else 0
    gaps = [n for n in range(1, limit + 1) if n not in S]
    if gaps:
        return float(max(gaps))
    return -1.0

OPERATIONS["frobenius_number"] = {
    "fn": frobenius_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Frobenius number (largest gap) of numerical semigroup"
}


def gap_set(x):
    """Gap set (non-representable positive integers) of numerical semigroup.
    Input: array (generators). Output: array."""
    gens = _make_generators(x)
    if len(gens) == 1 and gens[0] == 1:
        return np.array([0.0])  # no gaps
    S = _compute_semigroup(gens)
    f = max(n for n in range(1, max(S) + 1) if n not in S) if len(S) > 1 else 0
    gaps = sorted(n for n in range(1, f + 1) if n not in S)
    return np.array(gaps, dtype=float) if gaps else np.array([0.0])

OPERATIONS["gap_set"] = {
    "fn": gap_set,
    "input_type": "array",
    "output_type": "array",
    "description": "Set of gaps (non-representable integers)"
}


def genus_numerical_semigroup(x):
    """Genus = number of gaps = |N_0 \\ S|.
    Input: array (generators). Output: scalar."""
    gens = _make_generators(x)
    if len(gens) == 1 and gens[0] == 1:
        return 0.0
    if len(gens) == 2:
        a, b = gens[0], gens[1]
        return float((a - 1) * (b - 1) / 2)
    S = _compute_semigroup(gens)
    f_val = max((n for n in range(1, max(S) + 1) if n not in S), default=0)
    gaps = [n for n in range(1, f_val + 1) if n not in S]
    return float(len(gaps))

OPERATIONS["genus_numerical_semigroup"] = {
    "fn": genus_numerical_semigroup,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Genus (number of gaps) of numerical semigroup"
}


def apery_set(x):
    """Apery set Ap(S, m) where m is the multiplicity (smallest nonzero generator).
    Ap(S,m) = {w in S : w - m not in S}, one element per residue class mod m.
    Input: array (generators). Output: array of m elements."""
    gens = _make_generators(x)
    m = min(gens)
    if m == 1:
        return np.array([0.0])
    S = _compute_semigroup(gens)
    apery = np.zeros(m)
    for r in range(m):
        # Find smallest s in S with s = r mod m
        candidates = sorted(s for s in S if s % m == r)
        if candidates:
            apery[r] = candidates[0]
        else:
            apery[r] = -1  # shouldn't happen for valid semigroup
    return apery

OPERATIONS["apery_set"] = {
    "fn": apery_set,
    "input_type": "array",
    "output_type": "array",
    "description": "Apery set with respect to the multiplicity"
}


def embedding_dimension(x):
    """Embedding dimension = number of minimal generators.
    Input: array (generators). Output: scalar."""
    gens = _make_generators(x)
    # Remove redundant generators
    minimal = []
    for g in sorted(gens):
        sub_gens = [h for h in minimal if h != g]
        if sub_gens:
            S_sub = _compute_semigroup(sub_gens, limit=g + 1)
            if g not in S_sub:
                minimal.append(g)
        else:
            minimal.append(g)
    return float(len(minimal))

OPERATIONS["embedding_dimension"] = {
    "fn": embedding_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Embedding dimension (number of minimal generators)"
}


def multiplicity(x):
    """Multiplicity = smallest nonzero element of the semigroup.
    Input: array (generators). Output: scalar."""
    gens = _make_generators(x)
    return float(min(gens))

OPERATIONS["multiplicity"] = {
    "fn": multiplicity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Multiplicity (smallest nonzero element)"
}


def conductor(x):
    """Conductor = Frobenius number + 1 = smallest c such that all n >= c are in S.
    Input: array (generators). Output: scalar."""
    f = frobenius_number(x)
    return f + 1.0

OPERATIONS["conductor"] = {
    "fn": conductor,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Conductor (Frobenius number + 1)"
}


def symmetric_check(x):
    """Check if numerical semigroup is symmetric.
    S is symmetric iff for all z in Z, z in S <=> F-z not in S.
    Equivalently, genus = (F+1)/2.
    Input: array (generators). Output: scalar (1.0 = symmetric, 0.0 = not)."""
    gens = _make_generators(x)
    if len(gens) == 1 and gens[0] == 1:
        return 1.0  # trivial is symmetric
    f = frobenius_number(x)
    g = genus_numerical_semigroup(x)
    # Symmetric iff genus = (F+1)/2
    if abs(g - (f + 1) / 2) < 0.01:
        return 1.0
    return 0.0

OPERATIONS["symmetric_check"] = {
    "fn": symmetric_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if semigroup is symmetric (1=yes, 0=no)"
}


def pseudo_frobenius(x):
    """Pseudo-Frobenius numbers: gaps g such that g + s in S for all s in S\\{0}.
    Input: array (generators). Output: array."""
    gens = _make_generators(x)
    if len(gens) == 1 and gens[0] == 1:
        return np.array([-1.0])
    S = _compute_semigroup(gens)
    f_val = max((n for n in range(1, max(S) + 1) if n not in S), default=0)
    gaps = [n for n in range(1, f_val + 1) if n not in S]
    non_zero_gens = [s for s in S if s > 0 and s <= f_val + max(gens)]
    pf = []
    for g in gaps:
        is_pf = True
        for s in gens:  # only need to check generators
            if (g + s) not in S:
                is_pf = False
                break
        if is_pf:
            pf.append(g)
    return np.array(pf, dtype=float) if pf else np.array([float(f_val)])

OPERATIONS["pseudo_frobenius"] = {
    "fn": pseudo_frobenius,
    "input_type": "array",
    "output_type": "array",
    "description": "Pseudo-Frobenius numbers (maximally large gaps)"
}


def type_numerical_semigroup(x):
    """Type of numerical semigroup = number of pseudo-Frobenius numbers.
    Input: array (generators). Output: scalar."""
    pf = pseudo_frobenius(x)
    if len(pf) == 1 and pf[0] == -1.0:
        return 0.0
    return float(len(pf))

OPERATIONS["type_numerical_semigroup"] = {
    "fn": type_numerical_semigroup,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Type of numerical semigroup (number of pseudo-Frobenius numbers)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
