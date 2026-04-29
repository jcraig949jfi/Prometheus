"""prometheus_math.algebra_lie_algebras — root systems & Weyl groups.

Phase-1 of project #88: classical and exceptional finite-dimensional
complex semisimple Lie algebras, in their root-system / Weyl-group
incarnation. Phase 2 (representations + characters) and Phase 3 (real
forms + Cartan involutions) are deferred.

Conventions follow Humphreys, "Introduction to Lie Algebras and
Representation Theory" (GTM 9) and Bourbaki "Groupes et Algebres de
Lie", chapters IV-VI (Plates I-IX). Where conventions differ between
authors, we follow Bourbaki.

Public API
----------
- ``cartan_matrix(type_, rank)``       — n x n integer Cartan matrix
- ``simple_roots(type_, rank)``        — rank x dim float array
- ``positive_roots(type_, rank)``      — |Phi^+| x dim
- ``all_roots(type_, rank)``           — 2|Phi^+| x dim
- ``fundamental_weights(type_, rank)`` — rank x dim, dual basis
- ``weyl_group_order(type_, rank)``    — |W|
- ``weyl_group_generators(type_, rank)`` — list of reflection matrices
  acting on the ambient Euclidean space
- ``weyl_dim_formula(type_, rank, hw)`` — dim V(lambda) by Weyl
- ``dynkin_diagram_string(type_, rank)`` — ASCII-art Dynkin diagram
- ``is_dominant_weight(weight, type_, rank)`` — dominance check (in
  the fundamental-weight basis, equivalently Dynkin labels)
- ``longest_weyl_element(type_, rank)`` — w_0 as a matrix
- ``root_height(root, simple_roots)``  — sum of coefficients in the
  simple-root expansion

References:
- Humphreys, J. E., "Introduction to Lie Algebras and Representation
  Theory", Springer GTM 9 (1972).
- Bourbaki, "Groupes et Algebres de Lie", Chapitres IV-VI (Plates I-IX
  list root systems and Cartan matrices for every irreducible type).
- Fulton & Harris, "Representation Theory" (1991), Chapters 21-25.
"""
from __future__ import annotations

from fractions import Fraction
from math import factorial
from typing import Iterable, List, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


_VALID_TYPES = ("A", "B", "C", "D", "E", "F", "G")


def _validate(type_: str, rank: int) -> None:
    """Validate (type, rank) lies in the Cartan-Killing classification.

    Raises ValueError otherwise.
    """
    if not isinstance(type_, str) or len(type_) != 1 or type_ not in _VALID_TYPES:
        raise ValueError(
            f"unknown root-system type {type_!r}; expected one of "
            f"{_VALID_TYPES}"
        )
    if not isinstance(rank, (int, np.integer)) or rank < 1:
        raise ValueError(f"rank must be a positive integer, got {rank!r}")
    if type_ == "A" and rank < 1:
        raise ValueError("A_n requires n >= 1")
    if type_ in ("B", "C") and rank < 2:
        raise ValueError(f"{type_}_n requires n >= 2 (rank=1 collapses to A_1)")
    if type_ == "D" and rank < 3:
        raise ValueError(
            "D_n requires n >= 3 (D_1 is trivial, D_2 = A_1 x A_1 is reducible)"
        )
    if type_ == "E" and rank not in (6, 7, 8):
        raise ValueError(f"E_n only exists for n in (6, 7, 8); got n={rank}")
    if type_ == "F" and rank != 4:
        raise ValueError(f"F_n only exists for n=4; got n={rank}")
    if type_ == "G" and rank != 2:
        raise ValueError(f"G_n only exists for n=2; got n={rank}")


# ---------------------------------------------------------------------------
# Simple roots in standard Euclidean coordinates
# ---------------------------------------------------------------------------
#
# We follow the standard embeddings:
#  * A_n: simple roots e_i - e_{i+1} in R^{n+1}
#  * B_n: e_i - e_{i+1} (long, i < n) and e_n (short)
#  * C_n: e_i - e_{i+1} and 2 e_n
#  * D_n: e_i - e_{i+1} (i<n) and e_{n-1} + e_n
#  * E_8: standard basis as in Humphreys 12.2 / Bourbaki Plate VII.
#         alpha_1 = (1/2)(e_1 - e_2 - ... - e_7 + e_8)
#         alpha_2 = e_1 + e_2
#         alpha_i = e_{i-1} - e_{i-2} for i = 3,...,8
#  * E_7, E_6: span{alpha_1,...,alpha_7} resp {alpha_1,...,alpha_6} of E_8
#  * F_4: simple roots from Bourbaki Plate VIII.
#  * G_2: simple roots from Bourbaki Plate IX.


def _simple_roots_matrix(type_: str, rank: int) -> np.ndarray:
    """Build simple roots as rows of a float matrix.

    Returns shape (rank, dim) where dim is the ambient Euclidean
    dimension carrying the root system.
    """
    if type_ == "A":
        n = rank
        # alpha_i = e_i - e_{i+1} in R^{n+1}
        alpha = np.zeros((n, n + 1), dtype=float)
        for i in range(n):
            alpha[i, i] = 1.0
            alpha[i, i + 1] = -1.0
        return alpha

    if type_ == "B":
        n = rank
        alpha = np.zeros((n, n), dtype=float)
        for i in range(n - 1):
            alpha[i, i] = 1.0
            alpha[i, i + 1] = -1.0
        alpha[n - 1, n - 1] = 1.0  # short
        return alpha

    if type_ == "C":
        n = rank
        alpha = np.zeros((n, n), dtype=float)
        for i in range(n - 1):
            alpha[i, i] = 1.0
            alpha[i, i + 1] = -1.0
        alpha[n - 1, n - 1] = 2.0  # long
        return alpha

    if type_ == "D":
        n = rank
        alpha = np.zeros((n, n), dtype=float)
        for i in range(n - 1):
            alpha[i, i] = 1.0
            alpha[i, i + 1] = -1.0
        alpha[n - 1, n - 2] = 1.0
        alpha[n - 1, n - 1] = 1.0
        return alpha

    if type_ == "E":
        # Bourbaki Plate VII labelling (E_8). For E_6, E_7 we restrict.
        n = rank
        alpha = np.zeros((8, 8), dtype=float)
        # alpha_1 = (1/2)(e_1 - e_2 - e_3 - e_4 - e_5 - e_6 - e_7 + e_8)
        alpha[0, 0] = 0.5
        for k in range(1, 7):
            alpha[0, k] = -0.5
        alpha[0, 7] = 0.5
        # alpha_2 = e_1 + e_2
        alpha[1, 0] = 1.0
        alpha[1, 1] = 1.0
        # alpha_i = e_{i-1} - e_{i-2} for i = 3,...,8
        for i in range(3, 9):
            alpha[i - 1, i - 2] = 1.0
            alpha[i - 1, i - 3] = -1.0
        return alpha[:n]  # take first n simple roots for E_n, n in {6,7,8}

    if type_ == "F":
        # Bourbaki Plate VIII: F_4 simple roots in R^4
        # alpha_1 = e_2 - e_3,   alpha_2 = e_3 - e_4 (long)
        # alpha_3 = e_4         (short)
        # alpha_4 = (1/2)(e_1 - e_2 - e_3 - e_4)  (short)
        alpha = np.zeros((4, 4), dtype=float)
        alpha[0, 1] = 1.0; alpha[0, 2] = -1.0
        alpha[1, 2] = 1.0; alpha[1, 3] = -1.0
        alpha[2, 3] = 1.0
        alpha[3, 0] = 0.5; alpha[3, 1] = -0.5
        alpha[3, 2] = -0.5; alpha[3, 3] = -0.5
        return alpha

    if type_ == "G":
        # Bourbaki Plate IX: G_2 simple roots in the hyperplane
        # x_1+x_2+x_3=0 of R^3. We embed in R^3.
        # alpha_1 = e_1 - e_2 (short)
        # alpha_2 = -2 e_1 + e_2 + e_3 (long)
        alpha = np.zeros((2, 3), dtype=float)
        alpha[0, 0] = 1.0; alpha[0, 1] = -1.0
        alpha[1, 0] = -2.0; alpha[1, 1] = 1.0; alpha[1, 2] = 1.0
        return alpha

    raise ValueError(f"unknown type {type_!r}")  # pragma: no cover


def simple_roots(type_: str, rank: int) -> np.ndarray:
    """Simple roots as rows in standard Euclidean coordinates.

    Reference: Bourbaki Lie IV-VI Plates I-IX.
    """
    _validate(type_, rank)
    return _simple_roots_matrix(type_, rank).copy()


# ---------------------------------------------------------------------------
# Cartan matrix
# ---------------------------------------------------------------------------


def cartan_matrix(type_: str, rank: int) -> np.ndarray:
    """Return the Cartan matrix C with C[i,j] = 2*(alpha_i, alpha_j) /
    (alpha_j, alpha_j).

    Reference: Humphreys 9.4, Bourbaki Lie IV-VI Plates I-IX.
    """
    _validate(type_, rank)
    alpha = _simple_roots_matrix(type_, rank)
    n = alpha.shape[0]
    C = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            num = 2 * float(np.dot(alpha[i], alpha[j]))
            den = float(np.dot(alpha[j], alpha[j]))
            val = num / den
            C[i, j] = int(round(val))
            if abs(val - C[i, j]) > 1e-8:
                raise RuntimeError(
                    f"non-integer Cartan entry at {type_}_{rank}[{i},{j}]: {val}"
                )
    return C


# ---------------------------------------------------------------------------
# Positive roots: build by closure under simple reflections
# ---------------------------------------------------------------------------


def _reflect(v: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """s_alpha(v) = v - 2 (v,alpha)/(alpha,alpha) alpha."""
    coeff = 2.0 * np.dot(v, alpha) / np.dot(alpha, alpha)
    return v - coeff * alpha


def _round_vec(v: np.ndarray) -> Tuple[float, ...]:
    """Round to 8 decimals, used as dict key for set membership."""
    return tuple(round(float(x), 8) for x in v)


def _all_roots_closure(simple: np.ndarray) -> List[np.ndarray]:
    """Compute all roots by closing simple roots under simple reflections.

    Returns the full set Phi (positive + negative) as a list of
    numpy vectors.
    """
    n_simple = simple.shape[0]
    seen = {_round_vec(a): a.copy() for a in simple}
    # Also include negatives of simple roots for completeness of closure.
    for a in simple:
        na = -a
        seen[_round_vec(na)] = na.copy()
    queue: List[np.ndarray] = [a.copy() for a in simple] + [-a.copy() for a in simple]
    while queue:
        v = queue.pop()
        for i in range(n_simple):
            w = _reflect(v, simple[i])
            key = _round_vec(w)
            if key not in seen:
                # Skip zero (not a root)
                if np.linalg.norm(w) < 1e-9:
                    continue
                seen[key] = w
                queue.append(w)
    return list(seen.values())


def _expand_in_simple(v: np.ndarray, simple: np.ndarray) -> np.ndarray:
    """Express v as a linear combination of simple roots (rows).

    Solves the (overdetermined) linear system; expects an integer
    combination (returns the rounded integer coefficients).
    """
    # Solve simple^T @ c = v in least-squares sense, then round.
    sol, *_ = np.linalg.lstsq(simple.T, v, rcond=None)
    return sol


def all_roots(type_: str, rank: int) -> np.ndarray:
    """All roots of the root system, as rows in standard coordinates.

    Reference: Humphreys 10.1.
    """
    _validate(type_, rank)
    simple = _simple_roots_matrix(type_, rank)
    roots = _all_roots_closure(simple)
    return np.array(roots, dtype=float)


def positive_roots(type_: str, rank: int) -> np.ndarray:
    """Positive roots: those with non-negative integer expansion in
    simple roots.

    Reference: Humphreys 10.1.
    """
    _validate(type_, rank)
    simple = _simple_roots_matrix(type_, rank)
    roots = _all_roots_closure(simple)
    pos: List[np.ndarray] = []
    for r in roots:
        coeffs = _expand_in_simple(r, simple)
        # Round to nearest integer; check sign of first non-zero coefficient.
        rounded = np.round(coeffs).astype(int)
        # Sanity: residual must be small.
        residual = simple.T @ rounded.astype(float) - r
        if np.linalg.norm(residual) > 1e-6:
            # Not integer combination — shouldn't happen for a valid root.
            continue
        # All coefficients have the same sign (root system property).
        nonzero = rounded[rounded != 0]
        if len(nonzero) == 0:
            continue
        if (nonzero > 0).all():
            pos.append(r)
    return np.array(pos, dtype=float)


# ---------------------------------------------------------------------------
# Fundamental weights
# ---------------------------------------------------------------------------


def fundamental_weights(type_: str, rank: int) -> np.ndarray:
    """Fundamental weights ω_i in standard coordinates.

    The defining duality: 2(ω_i, alpha_j)/(alpha_j, alpha_j) = δ_ij.

    Reference: Humphreys 13.1.
    """
    _validate(type_, rank)
    alpha = _simple_roots_matrix(type_, rank)
    n = alpha.shape[0]
    dim = alpha.shape[1]
    # We seek ω_i in span(alpha_1, ..., alpha_n) (= V) such that
    # 2 (ω_i, alpha_j) / (alpha_j, alpha_j) = δ_ij.
    # Write ω_i = sum_k x_{ik} alpha_k. Then the system in x is
    # M_{jk} := 2(alpha_k, alpha_j)/(alpha_j, alpha_j) ; M^T x_i = e_i.
    # M is the Cartan matrix C; so x = (C^{-1})^T applied... Actually
    # M_{jk} = C[k, j] (note transpose), so M = C^T. Then x_i^T = e_i^T (C^T)^{-1}
    # i.e. x_i is the i-th row of (C^T)^{-1}, equivalently the i-th
    # column of C^{-1}.
    C = cartan_matrix(type_, rank).astype(float)
    Cinv = np.linalg.inv(C)
    # ω_i = sum_k Cinv[i, k] alpha_k  (rows of Cinv give expansion)
    weights = Cinv @ alpha  # shape (n, dim)
    return weights


# ---------------------------------------------------------------------------
# Weyl group order
# ---------------------------------------------------------------------------


# Tabulated orders (Bourbaki Lie IV-VI Plates I-IX).
_EXCEPTIONAL_W = {
    ("E", 6): 51840,
    ("E", 7): 2903040,
    ("E", 8): 696729600,
    ("F", 4): 1152,
    ("G", 2): 12,
}


def weyl_group_order(type_: str, rank: int) -> int:
    """Order of the Weyl group W.

    Reference: Humphreys 2.10, Bourbaki Lie IV-VI Plates.
    """
    _validate(type_, rank)
    n = rank
    if type_ == "A":
        return factorial(n + 1)
    if type_ in ("B", "C"):
        return (2 ** n) * factorial(n)
    if type_ == "D":
        return (2 ** (n - 1)) * factorial(n)
    return _EXCEPTIONAL_W[(type_, rank)]


# ---------------------------------------------------------------------------
# Weyl group generators (simple reflections)
# ---------------------------------------------------------------------------


def weyl_group_generators(type_: str, rank: int) -> List[np.ndarray]:
    """Simple reflections s_i as matrices acting on the ambient
    Euclidean space.

    Reference: Humphreys 1.1, definition of reflection.
    """
    _validate(type_, rank)
    alpha = _simple_roots_matrix(type_, rank)
    dim = alpha.shape[1]
    gens: List[np.ndarray] = []
    for i in range(alpha.shape[0]):
        a = alpha[i]
        norm_sq = float(np.dot(a, a))
        # s(v) = v - 2 (v, a)/(a, a) * a
        # In matrix form: s = I - (2/(a,a)) * a a^T
        S = np.eye(dim) - (2.0 / norm_sq) * np.outer(a, a)
        gens.append(S)
    return gens


# ---------------------------------------------------------------------------
# Dimensions of fundamental invariants — used by Weyl dim formula
# ---------------------------------------------------------------------------


def _coxeter_number(type_: str, rank: int) -> int:
    """Coxeter number h.

    Reference: Humphreys 12.2 / Bourbaki Plates.
    """
    n = rank
    if type_ == "A":
        return n + 1
    if type_ in ("B", "C"):
        return 2 * n
    if type_ == "D":
        return 2 * n - 2
    if type_ == "E":
        return {6: 12, 7: 18, 8: 30}[n]
    if type_ == "F":
        return 12
    if type_ == "G":
        return 6
    raise ValueError(type_)  # pragma: no cover


# ---------------------------------------------------------------------------
# Dynkin diagram (ASCII art)
# ---------------------------------------------------------------------------


def dynkin_diagram_string(type_: str, rank: int) -> str:
    """ASCII Dynkin diagram for the irreducible type.

    Each ``o`` is a node, each ``-`` a single bond, ``=>`` and ``<=`` are
    double bonds with arrows pointing toward the short root, ``=>=`` is
    the triple bond used for G_2.

    Reference: Humphreys 11.4, Bourbaki Plates.
    """
    _validate(type_, rank)
    n = rank
    if type_ == "A":
        nodes = "---".join(["o"] * n)
        return f"A_{n}: " + nodes
    if type_ == "B":
        # o---o---...---o=>=o (last two with arrow toward short root)
        if n == 1:
            return f"B_1: o"  # pragma: no cover (validated out)
        prefix = "---".join(["o"] * (n - 1))
        return f"B_{n}: {prefix}=>=o"
    if type_ == "C":
        prefix = "---".join(["o"] * (n - 1))
        return f"C_{n}: {prefix}=<=o"
    if type_ == "D":
        if n < 3:
            return f"D_{n}: o"  # pragma: no cover
        # D_n: chain of n-2 nodes branching to two on the right
        chain = "---".join(["o"] * (n - 2))
        return f"D_{n}: {chain}---o\n          \\\n           o"
    if type_ == "E":
        # E_n: chain o-o-o-... with a branch at the third node
        if n == 6:
            return "E_6: o---o---o---o---o\n             |\n             o"
        if n == 7:
            return "E_7: o---o---o---o---o---o\n             |\n             o"
        if n == 8:
            return "E_8: o---o---o---o---o---o---o\n             |\n             o"
    if type_ == "F":
        return "F_4: o---o=>=o---o"
    if type_ == "G":
        return "G_2: o#=#o"  # triple bond
    raise ValueError(type_)  # pragma: no cover


# ---------------------------------------------------------------------------
# is_dominant_weight, longest_weyl_element, root_height
# ---------------------------------------------------------------------------


def is_dominant_weight(weight: Sequence[int], type_: str, rank: int) -> bool:
    """A weight given by its Dynkin labels (coefficients in the
    fundamental-weight basis) is dominant iff all labels are >= 0.

    Reference: Humphreys 13.1.

    Edge: empty or wrong-length input -> ValueError.
    """
    _validate(type_, rank)
    if not isinstance(weight, (list, tuple, np.ndarray)) or len(weight) == 0:
        raise ValueError("weight must be a non-empty sequence")
    if len(weight) != rank:
        raise ValueError(
            f"weight has {len(weight)} components; expected {rank}"
        )
    return all(int(w) >= 0 for w in weight)


def longest_weyl_element(type_: str, rank: int) -> np.ndarray:
    """The longest element w_0 of the Weyl group, as a matrix on the
    ambient Euclidean space.

    Construction: enumerate orbit of rho under simple reflections, find
    the element sending rho to -rho (or, equivalently, take the matrix
    whose action on positive roots is a permutation onto negative roots).

    Reference: Humphreys 1.8 / Bourbaki Lie IV.
    """
    _validate(type_, rank)
    gens = weyl_group_generators(type_, rank)
    weights = fundamental_weights(type_, rank)
    rho = weights.sum(axis=0)
    target = -rho
    dim = rho.shape[0]
    # BFS on group elements until we send rho -> -rho.
    start = np.eye(dim)
    seen: dict = {_round_vec(start.flatten()): start}
    queue = [start]
    while queue:
        next_queue = []
        for g in queue:
            for s in gens:
                h = s @ g
                key = _round_vec(h.flatten())
                if key in seen:
                    continue
                seen[key] = h
                v = h @ rho
                if np.allclose(v, target, atol=1e-8):
                    return h
                next_queue.append(h)
        queue = next_queue
    # If BFS exhausts without finding (shouldn't happen for finite Weyl
    # group), return identity. We add a safety bound: BFS will stop
    # naturally because the group is finite.
    raise RuntimeError(  # pragma: no cover
        f"longest element not found for {type_}_{rank}"
    )


def root_height(root: Sequence[float], simple: np.ndarray) -> int:
    """Height of a root: sum of coefficients in its expansion in the
    simple roots.

    Reference: Humphreys 10.1.
    """
    root = np.asarray(root, dtype=float)
    coeffs = _expand_in_simple(root, simple)
    rounded = np.round(coeffs).astype(int)
    residual = simple.T @ rounded.astype(float) - root
    if np.linalg.norm(residual) > 1e-6:
        raise ValueError(
            "input vector is not an integer combination of the given simple roots"
        )
    return int(rounded.sum())


# ---------------------------------------------------------------------------
# Weyl dimension formula
# ---------------------------------------------------------------------------


def weyl_dim_formula(
    type_: str,
    rank: int,
    highest_weight: Sequence[int],
) -> int:
    """Dimension of the irreducible representation V(λ) by Weyl's
    dimension formula:

        dim V(λ) = prod_{α in Phi^+} (λ + ρ, α) / (ρ, α)

    where ρ = sum of fundamental weights, λ is given by its Dynkin
    labels (coefficients in the fundamental-weight basis).

    Reference: Humphreys 24.3, Theorem.
    """
    _validate(type_, rank)
    if not isinstance(highest_weight, (list, tuple, np.ndarray)) or len(highest_weight) == 0:
        raise ValueError("highest_weight must be a non-empty sequence")
    if len(highest_weight) != rank:
        raise ValueError(
            f"highest_weight has {len(highest_weight)} components; expected {rank}"
        )

    weights = fundamental_weights(type_, rank)
    rho = weights.sum(axis=0)
    lam = np.zeros_like(rho)
    for i, c in enumerate(highest_weight):
        lam = lam + float(c) * weights[i]

    pos = positive_roots(type_, rank)
    num = Fraction(1)
    den = Fraction(1)
    for a in pos:
        # Use rationalisation: inner products are rationals (scaled by 4
        # for E_8 because of the 1/2 factors; we keep float and round
        # at the end).
        n_val = float(np.dot(lam + rho, a))
        d_val = float(np.dot(rho, a))
        num = num * Fraction(n_val).limit_denominator(10**12)
        den = den * Fraction(d_val).limit_denominator(10**12)

    result = num / den
    # dim is a positive integer
    if result.denominator != 1:
        # Allow tiny floating slack: round if very close to integer.
        approx = float(result)
        nearest = int(round(approx))
        if abs(approx - nearest) < 1e-6:
            return nearest
        raise RuntimeError(
            f"non-integer dimension {result} for {type_}_{rank} hw={list(highest_weight)}"
        )
    return int(result.numerator)


__all__ = [
    "cartan_matrix",
    "simple_roots",
    "positive_roots",
    "all_roots",
    "fundamental_weights",
    "weyl_group_order",
    "weyl_group_generators",
    "weyl_dim_formula",
    "dynkin_diagram_string",
    "is_dominant_weight",
    "longest_weyl_element",
    "root_height",
]
