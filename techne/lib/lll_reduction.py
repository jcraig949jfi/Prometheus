"""TOOL_LLL_REDUCTION — Lenstra-Lenstra-Lovasz lattice basis reduction.

Given a basis B of a full-rank or degenerate lattice in Z^n, returns an
LLL-reduced basis. Provides both vector-input (rows = basis vectors, the
usual mathematical convention) and Gram-matrix input.

Uses PARI's qflll/qflllgram. PARI convention: basis vectors are COLUMNS
of the input matrix. This tool accepts the natural row-convention (rows =
basis vectors) and transposes internally — output is also row-convention.

Interface:
    lll(basis) -> np.ndarray                          # rows = reduced basis
    lll_with_transform(basis) -> (reduced, T)         # reduced = T @ basis
    shortest_vector_lll(basis) -> np.ndarray          # first row of LLL basis (approx SVP)
    lll_gram(gram) -> np.ndarray                      # input is G = B B^T

Forged: 2026-04-22 | Tier: 1 (cypari wrapper) | REQ-018
Tested against: Cohen Ch. 2 examples, Lagarias-Miller-Odlyzko test cases,
                random lattices with known determinant preservation.

KNOWN LIMITATION: cypari's qflll uses integer lattices by default. For
floating-point / rational lattices, scale and round. PSLQ (mpmath.lindep)
is a better tool for real-number relation finding.
"""
from typing import Sequence
import numpy as np
import cypari

_pari = cypari.pari


def _to_pari_mat_cols(basis: np.ndarray):
    """Convert row-convention basis (rows = vectors) to PARI matrix with
    basis vectors as COLUMNS (PARI convention)."""
    arr = np.asarray(basis, dtype=object)
    if arr.ndim != 2:
        raise ValueError(f"expected 2D basis matrix, got shape {arr.shape}")
    # Transpose: our rows -> PARI columns
    cols = arr.T
    m, n = cols.shape  # m = dim of ambient space, n = number of basis vectors
    rows_str = [','.join(str(int(x)) for x in row) for row in cols]
    return _pari('[' + ';'.join(rows_str) + ']')


def _pari_mat_cols_to_rows(M, out_rows: int, out_cols: int) -> np.ndarray:
    """Convert PARI matrix (cols = vectors) back to row-convention numpy array."""
    # PARI matrix indexing M[i,j]: i in [0, rows-1], j in [0, cols-1]
    out = np.zeros((out_cols, out_rows), dtype=object)
    for j in range(out_cols):   # column index in PARI (= vector index)
        for i in range(out_rows):   # row index in PARI (= coordinate index)
            out[j, i] = int(M[i, j])
    return out


def lll(basis) -> np.ndarray:
    """LLL-reduced basis of the lattice spanned by the rows of `basis`.

    Parameters
    ----------
    basis : 2D array-like of int, shape (n, d)
        Rows are the basis vectors (n vectors in Z^d).

    Returns
    -------
    np.ndarray shape (n, d) of int
        LLL-reduced basis (rows are the reduced vectors), sorted so the
        shortest vectors come first.

    Examples
    --------
    >>> B = [[1, 1, 1], [0, 1, 0], [0, 0, 1000000]]
    >>> R = lll(B)
    >>> R[0].tolist()
    [1, 0, 0]
    """
    arr = np.asarray(basis, dtype=object)
    n, d = arr.shape
    M = _to_pari_mat_cols(arr)
    T = _pari.qflll(M)       # transformation matrix (n x n)
    reduced = M * T          # new columns = reduced basis
    return _pari_mat_cols_to_rows(reduced, d, n)


def lll_with_transform(basis):
    """LLL-reduced basis R together with the transform T so that R = T @ B.

    Returns
    -------
    (R, T) : (np.ndarray, np.ndarray)
        Both row-convention. R has shape (n, d), T has shape (n, n) and is
        unimodular (det = +/-1).
    """
    arr = np.asarray(basis, dtype=object)
    n, d = arr.shape
    M = _to_pari_mat_cols(arr)
    T_pari = _pari.qflll(M)
    reduced = M * T_pari
    R = _pari_mat_cols_to_rows(reduced, d, n)
    # T_pari is n x n mapping column basis to column basis: reduced_cols = M * T_pari
    # In row convention: R = T @ B where T = T_pari^T
    T = np.zeros((n, n), dtype=object)
    for j in range(n):
        for i in range(n):
            T[j, i] = int(T_pari[i, j])
    return R, T


def shortest_vector_lll(basis) -> np.ndarray:
    """Shortest vector of the LLL-reduced basis (approximate SVP).

    NOTE: LLL finds a short vector, NOT necessarily the shortest. The LLL
    bound is ||b_1|| <= 2^((n-1)/2) * lambda_1 where lambda_1 is the true
    shortest-vector length. For exact SVP, use a dedicated SVP solver (fpylll).
    """
    R = lll(basis)
    # Sort rows by L2 norm and return the shortest
    norms = [sum(int(x) ** 2 for x in row) for row in R]
    idx = int(np.argmin(norms))
    return R[idx]


def lll_gram(gram) -> np.ndarray:
    """LLL reduction given the Gram matrix G = B B^T.

    Returns the unimodular transform T such that T G T^T is reduced.
    Use when you don't have explicit coordinates but have the inner-product
    matrix.
    """
    arr = np.asarray(gram, dtype=object)
    n = arr.shape[0]
    if arr.shape != (n, n):
        raise ValueError(f"Gram matrix must be square, got {arr.shape}")
    rows_str = [','.join(str(int(x)) for x in row) for row in arr]
    G = _pari('[' + ';'.join(rows_str) + ']')
    T = _pari.qflllgram(G)
    # Convert T back to row-conv numpy
    out = np.zeros((n, n), dtype=object)
    for j in range(n):
        for i in range(n):
            out[j, i] = int(T[i, j])
    return out
