"""Rank-ceiling null model.

For each candidate rank profile r = (r_1, ..., r_{d-1}), compute the
expected relative L2 error of a TT-SVD truncation at that profile when
applied to an i.i.d. Gaussian tensor of the same shape. This is the
"no structure" ceiling: any elite in the archive that sits at the null
ceiling has compressibility that is statistically indistinguishable from
random structure at that rank budget.

Usage: overlay the null error curve (params -> error) on the Pareto
plot. Any Pareto point AT or ABOVE the null ceiling is a rank-ceiling-
trivial elite; any point BELOW it encodes actual function structure.

Implementation: Monte Carlo. We sample n_trials Gaussian tensors, run
TT-SVD at the given rank profile, and average the relative error. For
large tensors this is expensive; we only compute the null at a modest
set of reference profiles.
"""
from __future__ import annotations
import numpy as np

from ..tt.core import tt_svd, relative_l2_error, max_possible_ranks


def null_error_at_rank(shape: tuple[int, ...], ranks: tuple[int, ...],
                       n_trials: int = 3, seed: int = 20260424) -> dict:
    """Mean relative L2 error for TT-SVD at `ranks` on i.i.d. Gaussian
    tensors of shape `shape`."""
    rng = np.random.default_rng(seed)
    errs = []
    n_params_list = []
    for _ in range(n_trials):
        T = rng.standard_normal(shape)
        tt = tt_svd(T, max_ranks=ranks)
        recon = tt.reconstruct()
        errs.append(relative_l2_error(T, recon))
        n_params_list.append(tt.n_params)
    return {
        "ranks": list(ranks),
        "mean_error": float(np.mean(errs)),
        "std_error": float(np.std(errs)),
        "n_params": int(np.median(n_params_list)),
        "n_trials": n_trials,
    }


def null_curve(shape: tuple[int, ...], rank_levels: list[int] | None = None,
               n_trials: int = 2, seed: int = 20260424,
               max_bond: int = 16) -> list[dict]:
    """Build the null (n_params, mean_error) curve for uniform-rank
    profiles at levels r = 1, 2, 3, ..., max_bond capped at ceiling.
    """
    ceiling = max_possible_ranks(shape)
    d_minus_1 = len(ceiling)
    if rank_levels is None:
        rank_levels = list(range(1, max_bond + 1))
    curve = []
    for r in rank_levels:
        ranks = tuple(min(r, ceiling[k], max_bond) for k in range(d_minus_1))
        rec = null_error_at_rank(shape, ranks, n_trials=n_trials, seed=seed + r)
        curve.append(rec)
    return curve
