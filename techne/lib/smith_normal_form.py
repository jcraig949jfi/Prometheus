"""TOOL_SMITH_NORMAL_FORM — Smith normal form of an integer matrix.

For an m x n integer matrix A, computes diagonal D = P A Q where P in GL_m(Z),
Q in GL_n(Z) are unimodular, and D has diagonal entries d_1 | d_2 | ... | d_r
(the invariant factors, r = rank of A).

Applications: computing integer homology of chain complexes (invariant factors
of the boundary map give the torsion part), testing for isomorphism of
finitely generated abelian groups, integer linear systems.

Interface:
    smith_normal_form(M) -> np.ndarray       # diagonal matrix, same shape
    invariant_factors(M) -> list[int]        # ascending d_1 | d_2 | ... (zeros dropped)
    abelian_group_structure(M) -> dict       # torsion + free rank decomposition

Forged: 2026-04-22 | Tier: 1 (sympy wrapper) | REQ-015
Backend: sympy.matrices.normalforms.smith_normal_form.
For matrices >~ 30x30 this is slow; PARI matsnf backend deferred to Tier 2.
"""
from typing import Sequence, Union
import numpy as np
from sympy import Matrix
from sympy.matrices.normalforms import smith_normal_form as _sym_snf


ArrayLike = Union[np.ndarray, Sequence[Sequence[int]]]


def _to_sym(M: ArrayLike) -> Matrix:
    if isinstance(M, Matrix):
        return M
    arr = np.asarray(M, dtype=object)
    if arr.ndim != 2:
        raise ValueError(f"expected 2D matrix, got shape {arr.shape}")
    return Matrix(arr.tolist())


def smith_normal_form(M: ArrayLike) -> np.ndarray:
    """Smith normal form of an integer matrix.

    Parameters
    ----------
    M : 2D array-like of int
        The input matrix (shape m x n).

    Returns
    -------
    np.ndarray of shape (m, n), dtype=object
        Diagonal matrix D with D[i,i] = d_i (invariant factors) and d_i | d_{i+1}.
        Entries are Python ints (via dtype=object) to support arbitrary precision.

    Examples
    --------
    >>> D = smith_normal_form([[2, 4, 4], [-6, 6, 12], [10, -4, -16]])
    >>> [int(D[i, i]) for i in range(3)]
    [2, 6, 12]
    """
    sym = _to_sym(M)
    S = _sym_snf(sym)
    return np.array(S.tolist(), dtype=object)


def invariant_factors(M: ArrayLike) -> list:
    """Non-zero invariant factors d_1 | d_2 | ... of the integer matrix M.

    Returns the ascending sequence of non-trivial invariant factors (zeros
    dropped — zeros encode the kernel dimension, use abelian_group_structure
    if you want that).

    Examples
    --------
    >>> invariant_factors([[2, 4, 4], [-6, 6, 12], [10, -4, -16]])
    [2, 6, 12]
    >>> invariant_factors([[2, 0], [0, 0]])
    [2]
    """
    D = smith_normal_form(M)
    r = min(D.shape)
    diag = [int(D[i, i]) for i in range(r)]
    return [d for d in diag if d != 0]


def abelian_group_structure(M: ArrayLike) -> dict:
    """Decompose Z^m / A Z^n as torsion x free.

    Given an m x n integer matrix A treated as a presentation matrix:
    columns span a subgroup of Z^m, and the quotient Z^m / im(A) has
    structure Z/d_1 x Z/d_2 x ... x Z^k where:
        d_1 | d_2 | ... | d_s are the invariant factors > 1
        k = m - (number of nonzero invariant factors)

    Returns
    -------
    dict with keys:
        torsion : list[int]  — invariant factors > 1 in ascending order
        free_rank : int      — rank of the Z^k summand
        trivial_factors : int — number of invariant factors equal to 1 (absorbed)
        presentation_shape : (m, n)

    Examples
    --------
    >>> # Z^2 / <(2,0), (0,6)> = Z/2 x Z/6
    >>> abelian_group_structure([[2, 0], [0, 6]])['torsion']
    [2, 6]
    >>> # Z^3 / <(1,0,0), (0,1,0)> = Z  (two trivial factors absorbed)
    >>> abelian_group_structure([[1, 0], [0, 1], [0, 0]])['free_rank']
    1
    """
    arr = np.asarray(M, dtype=object)
    if arr.ndim != 2:
        raise ValueError(f"expected 2D matrix, got shape {arr.shape}")
    m, n = arr.shape
    D = smith_normal_form(M)
    r = min(D.shape)
    diag = [int(D[i, i]) for i in range(r)]
    torsion = [d for d in diag if d > 1]
    trivial = sum(1 for d in diag if d == 1)
    nonzero = sum(1 for d in diag if d != 0)
    free_rank = m - nonzero
    return {
        'torsion': torsion,
        'free_rank': free_rank,
        'trivial_factors': trivial,
        'presentation_shape': (m, n),
    }
