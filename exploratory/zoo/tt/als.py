"""TT-ALS refinement (one-site).

Constrained per James 2026-04-24: applied as a finishing step on each TT-SVD
output with a fixed small sweep budget. Does NOT change the rank profile —
only the core entries. So `n_params` is preserved; `rel_l2_error` may improve.

Diversity-collapse risk: if budget is too high, every cell's elite gets
near-optimal at its rank, and the archive measures "rank ladder" rather
than "evolutionary exploration." Default budget is 1 sweep total.

One-site update closed form: with all cores except k held fixed,
T(i_1,...,i_d) = L[i_1...i_{k-1}, :] @ G_k[:, i_k, :] @ R[:, i_{k+1}...i_d]
The least-squares solution is G_k[:, i_k, :] = pinv(L) @ T_slice @ pinv(R).
Cheap because L and R are tall-skinny (huge x rank).
"""
from __future__ import annotations
import numpy as np

from .core import TTDecomposition, relative_l2_error


def _left_environment(cores: list[np.ndarray], k: int) -> np.ndarray:
    """Contract cores[0..k-1] to a (prod(n_0..n_{k-1}), r_{k-1}) matrix."""
    if k == 0:
        return np.array([[1.0]])
    g = cores[0]                                  # (1, n_0, r_0)
    out = g.reshape(g.shape[1], g.shape[2])       # (n_0, r_0)
    for j in range(1, k):
        rp, nj, rn = cores[j].shape
        out = out @ cores[j].reshape(rp, nj * rn)  # (left_so_far, n_j * r_j)
        out = out.reshape(-1, rn)
    return out


def _right_environment(cores: list[np.ndarray], k: int) -> np.ndarray:
    """Contract cores[k+1..d-1] to a (r_k, prod(n_{k+1}..n_{d-1})) matrix."""
    d = len(cores)
    if k == d - 1:
        return np.array([[1.0]])
    g = cores[d - 1]                                          # (r_{d-1}, n_{d-1}, 1)
    out = g.reshape(g.shape[0], g.shape[1])                   # (r_{d-1}, n_{d-1})
    for j in range(d - 2, k, -1):
        rp, nj, rn = cores[j].shape
        out = cores[j].reshape(rp * nj, rn) @ out.reshape(rn, -1)  # (r_{j-1} * n_j, right_so_far)
        out = out.reshape(rp, -1)
    return out


def tt_als_refine(tt: TTDecomposition, target: np.ndarray,
                  n_sweeps: int = 1) -> TTDecomposition:
    """One-site ALS sweep(s). Updates core k assuming all others fixed using
    the closed-form pseudoinverse solution. Default budget: 1 sweep
    (left-to-right + right-to-left = 2 traversals).

    Cores are updated in place on a copied list. Rank profile is preserved.
    """
    cores = [c.copy() for c in tt.cores]
    d = len(cores)
    shape = target.shape

    for _sweep in range(n_sweeps):
        for direction in ("ltr", "rtl"):
            order = range(d) if direction == "ltr" else range(d - 1, -1, -1)
            for k in order:
                r_prev, n_k, r_next = cores[k].shape
                L = _left_environment(cores, k)         # (left_size, r_prev)
                R = _right_environment(cores, k)        # (r_next, right_size)
                left_size = L.shape[0]
                right_size = R.shape[1]
                T3 = target.reshape(left_size, n_k, right_size)

                # Pseudoinverses (small in the rank dimension; cheap)
                L_pinv = np.linalg.pinv(L)              # (r_prev, left_size)
                R_pinv = np.linalg.pinv(R)              # (right_size, r_next)
                new_core = np.empty_like(cores[k])
                for ik in range(n_k):
                    new_core[:, ik, :] = L_pinv @ T3[:, ik, :] @ R_pinv
                cores[k] = new_core

    return TTDecomposition(cores=cores)


def tt_evaluate_with_refinement(target: np.ndarray, ranks: tuple[int, ...],
                                n_sweeps: int = 1) -> tuple[TTDecomposition, float, float]:
    """Run TT-SVD at the given ranks, then refine with n_sweeps ALS sweeps.

    Returns (refined_tt, error_before_refine, error_after_refine).
    error_before_refine is what TT-SVD alone produced; error_after_refine is
    what gets reported to the archive. The pair lets us audit how much
    refinement is doing.
    """
    from .core import tt_svd
    tt0 = tt_svd(target, max_ranks=ranks)
    err_before = relative_l2_error(target, tt0.reconstruct())
    if n_sweeps <= 0:
        return tt0, err_before, err_before
    tt1 = tt_als_refine(tt0, target, n_sweeps=n_sweeps)
    err_after = relative_l2_error(target, tt1.reconstruct())
    # Refinement should never make error worse (LS is non-increasing). Guard anyway.
    if err_after > err_before * 1.001:
        return tt0, err_before, err_before
    return tt1, err_before, err_after
