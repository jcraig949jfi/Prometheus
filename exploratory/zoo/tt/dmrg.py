"""Two-site DMRG refinement for tensor trains.

Core distinction from one-site ALS: the rank at each bond is allowed to
ADAPT during the sweep. After merging cores k and k+1 into a supercore
W_{k,k+1}, we optimize W against the target, SVD it, and re-split with
truncation chosen by relative-tolerance threshold (bounded by max_bond).

This removes the artificial cap on refinement_gain that one-site ALS
imposed: under one-site, the rank profile never changes and "refinement
gain" measures only core-entry optimization. Under two-site, refinement
can discover that the requested rank was too high (truncate) or that a
different rank distribution across bonds fits the target better.

Two-site DMRG produces OUTPUT ranks that may differ from the INPUT
rank request. Callers must use the output TT's actual .ranks attribute
for reporting (n_params, rank_entropy, etc.) — not the requested profile.
"""
from __future__ import annotations
import numpy as np

from .core import TTDecomposition, tt_svd, relative_l2_error
from .als import _left_environment, _right_environment


def _supercore_ls(L: np.ndarray, R: np.ndarray, T3: np.ndarray,
                  r_prev: int, n_k: int, n_kp1: int, r_next: int) -> np.ndarray:
    """Closed-form least-squares solve for the two-site supercore.

    T3 has shape (left_size, n_k * n_{k+1}, right_size) after reshape of
    the target slice. We want W of shape (r_prev, n_k, n_{k+1}, r_next)
    such that T3[:, i_k * n_{k+1} + i_{k+1}, :] = L @ W[:, i_k, i_{k+1}, :] @ R.

    Closed form: W[:, i_k, i_{k+1}, :] = pinv(L) @ T3_slice @ pinv(R).
    """
    L_pinv = np.linalg.pinv(L)      # (r_prev, left_size)
    R_pinv = np.linalg.pinv(R)      # (right_size, r_next)
    W = np.empty((r_prev, n_k, n_kp1, r_next))
    for i in range(n_k):
        for j in range(n_kp1):
            slice_idx = i * n_kp1 + j
            W[:, i, j, :] = L_pinv @ T3[:, slice_idx, :] @ R_pinv
    return W


def _two_site_update(cores: list[np.ndarray], target: np.ndarray, k: int,
                     rel_tol: float, max_bond: int) -> None:
    """Update cores[k] and cores[k+1] via two-site DMRG. Rank at the
    (k, k+1) bond may change (adaptive)."""
    d = len(cores)
    shape = target.shape

    r_prev = cores[k].shape[0]
    n_k = cores[k].shape[1]
    n_kp1 = cores[k + 1].shape[1]
    r_next = cores[k + 1].shape[2]

    # Environments (left of k, right of k+1)
    L = _left_environment(cores, k)
    R = _right_environment(cores, k + 1)

    left_size = L.shape[0]
    right_size = R.shape[1]

    # Reshape target
    T3 = target.reshape(left_size, n_k * n_kp1, right_size)

    W = _supercore_ls(L, R, T3, r_prev, n_k, n_kp1, r_next)

    # SVD the supercore reshaped as (r_prev * n_k) x (n_{k+1} * r_next)
    W_mat = W.reshape(r_prev * n_k, n_kp1 * r_next)
    U, S, Vt = np.linalg.svd(W_mat, full_matrices=False)

    # Rank truncation: relative tolerance OR max_bond, whichever binds first
    if S[0] > 0:
        keep = int(np.sum(S / S[0] >= rel_tol))
    else:
        keep = 1
    ceiling = min(r_prev * n_k, n_kp1 * r_next)
    keep = max(1, min(keep, max_bond, ceiling))

    U_k = U[:, :keep]
    S_k = S[:keep]
    Vt_k = Vt[:keep, :]

    cores[k] = U_k.reshape(r_prev, n_k, keep)
    cores[k + 1] = (np.diag(S_k) @ Vt_k).reshape(keep, n_kp1, r_next)


def tt_dmrg_refine(tt: TTDecomposition, target: np.ndarray, n_sweeps: int = 1,
                   rel_tol: float = 1e-10, max_bond: int = 16) -> TTDecomposition:
    """Two-site DMRG with adaptive rank. One full sweep = left-to-right
    traversal + right-to-left traversal of the d-1 bonds.

    rel_tol controls rank truncation: singular values below
    sigma_max * rel_tol are discarded.
    """
    cores = [c.copy() for c in tt.cores]
    d = len(cores)
    for _ in range(n_sweeps):
        for k in range(d - 1):
            _two_site_update(cores, target, k, rel_tol, max_bond)
        for k in range(d - 2, -1, -1):
            _two_site_update(cores, target, k, rel_tol, max_bond)
    return TTDecomposition(cores=cores)


def tt_evaluate_with_dmrg(target: np.ndarray, ranks: tuple[int, ...],
                          n_sweeps: int = 1, rel_tol: float = 1e-10,
                          max_bond: int = 16) -> tuple[TTDecomposition, float, float]:
    """TT-SVD at `ranks`, then two-site DMRG refinement.

    Returns (refined_tt, err_before, err_after). The refined TT's actual
    ranks may differ from the input `ranks` because DMRG rank-adapts.
    Callers should use refined_tt.ranks for downstream descriptor
    computation (n_params, rank_entropy, rank_concentration).
    """
    tt0 = tt_svd(target, max_ranks=ranks)
    err_before = relative_l2_error(target, tt0.reconstruct())
    if n_sweeps <= 0:
        return tt0, err_before, err_before
    tt1 = tt_dmrg_refine(tt0, target, n_sweeps=n_sweeps, rel_tol=rel_tol,
                         max_bond=max_bond)
    err_after = relative_l2_error(target, tt1.reconstruct())
    if err_after > err_before * 1.001:
        return tt0, err_before, err_before
    return tt1, err_before, err_after
