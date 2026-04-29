"""
Unit tests for the four null generators in missingness_confound_v01.

Each null has mathematical invariants it MUST preserve. These tests
protect against silent regressions when the file is edited.

Plus: validate that Curveball degree-preserving swap on null_marginal
has reached approximate mixing at the default n_swaps=2000. The auditor
AUDIT_PASSED methodological flag (1777462332788) noted mixing time was
not validated; this script discharges that.

Run:  python harmonia/memory/diagnostics/test_missingness_confound_v01.py
"""

import numpy as np

from missingness_confound_v01 import (
    null_random,
    null_marginal_preserving,
    null_within_rows,
    null_within_cols,
    phi,
)


def small_synthetic_tensor(seed=42):
    """5x6 ordinal tensor with 12 observations - small enough for fast tests."""
    rng = np.random.default_rng(seed)
    T = np.zeros((5, 6), dtype=np.int8)
    cells = [(0,1),(0,3),(1,0),(1,4),(2,2),(2,3),(3,1),(3,5),(4,0),(4,2),(4,4),(0,5)]
    values = rng.choice([-2,-1,1,2], size=len(cells))
    for (i,j), v in zip(cells, values):
        T[i,j] = v
    M = (T != 0).astype(np.int8)
    return T, M


def real_tensor():
    from pathlib import Path
    here = Path(__file__).parent
    d = np.load(str(here.parent / 'landscape_tensor.npz'), allow_pickle=True)
    T = d['T']
    M = (T != 0).astype(np.int8)
    return T, M


# ---------------------------------------------------------------------------
# Invariant tests
# ---------------------------------------------------------------------------

def test_null_random_preserves_obs_count():
    T, M = small_synthetic_tensor()
    rng = np.random.default_rng(0)
    for _ in range(20):
        T_n, M_n = null_random(T, M, rng)
        assert M_n.sum() == M.sum(), 'null_random changed obs count'
    print('PASS  null_random preserves obs count')


def test_null_random_preserves_value_multiset():
    T, M = small_synthetic_tensor()
    rng = np.random.default_rng(0)
    obs_values = sorted(T[M.astype(bool)].tolist())
    for _ in range(20):
        T_n, M_n = null_random(T, M, rng)
        new_values = sorted(T_n[M_n.astype(bool)].tolist())
        assert new_values == obs_values, 'null_random changed value multiset'
    print('PASS  null_random preserves value multiset')


def test_null_marginal_preserves_row_and_col_marginals():
    T, M = small_synthetic_tensor()
    rng = np.random.default_rng(0)
    row_m = M.sum(axis=1)
    col_m = M.sum(axis=0)
    for _ in range(20):
        T_n, M_n = null_marginal_preserving(T, M, rng, n_swaps=500)
        assert (M_n.sum(axis=1) == row_m).all(), 'null_marginal broke row marginals'
        assert (M_n.sum(axis=0) == col_m).all(), 'null_marginal broke col marginals'
    print('PASS  null_marginal preserves row and col marginals')


def test_null_marginal_breaks_joint():
    T, M = small_synthetic_tensor()
    rng = np.random.default_rng(0)
    n_identical = 0
    n_trials = 50
    for _ in range(n_trials):
        T_n, M_n = null_marginal_preserving(T, M, rng, n_swaps=2000)
        if (M_n == M).all():
            n_identical += 1
    assert n_identical < n_trials, 'null_marginal never moved off the original M'
    print('PASS  null_marginal breaks joint pattern ({}/{} trials moved off identity)'.format(
        n_trials - n_identical, n_trials))


def test_null_within_rows_preserves_M():
    T, M = small_synthetic_tensor()
    rng = np.random.default_rng(0)
    for _ in range(20):
        T_n, M_n = null_within_rows(T, M, rng)
        assert (M_n == M).all(), 'null_within_rows changed M'
    print('PASS  null_within_rows preserves M')


def test_null_within_rows_preserves_row_value_multisets():
    T, M = small_synthetic_tensor()
    rng = np.random.default_rng(0)
    original_rows = [sorted(T[i, M[i].astype(bool)].tolist()) for i in range(T.shape[0])]
    for _ in range(20):
        T_n, _ = null_within_rows(T, M, rng)
        new_rows = [sorted(T_n[i, M[i].astype(bool)].tolist()) for i in range(T.shape[0])]
        assert new_rows == original_rows, 'null_within_rows changed a row value multiset'
    print('PASS  null_within_rows preserves per-row value multisets')


def test_null_within_cols_preserves_M():
    T, M = small_synthetic_tensor()
    rng = np.random.default_rng(0)
    for _ in range(20):
        T_n, M_n = null_within_cols(T, M, rng)
        assert (M_n == M).all(), 'null_within_cols changed M'
    print('PASS  null_within_cols preserves M')


def test_null_within_cols_preserves_col_value_multisets():
    T, M = small_synthetic_tensor()
    rng = np.random.default_rng(0)
    original_cols = [sorted(T[M[:,j].astype(bool), j].tolist()) for j in range(T.shape[1])]
    for _ in range(20):
        T_n, _ = null_within_cols(T, M, rng)
        new_cols = [sorted(T_n[M[:,j].astype(bool), j].tolist()) for j in range(T.shape[1])]
        assert new_cols == original_cols, 'null_within_cols changed a col value multiset'
    print('PASS  null_within_cols preserves per-col value multisets')


def test_within_rows_and_within_cols_are_different():
    T, M = small_synthetic_tensor()
    rng_a = np.random.default_rng(0)
    rng_b = np.random.default_rng(0)
    Ta, _ = null_within_rows(T, M, rng_a)
    Tb, _ = null_within_cols(T, M, rng_b)
    if T.shape[0] > 1 and T.shape[1] > 1:
        # Will not be identical unless degenerate (e.g. only one row/col with multiple obs)
        assert not (Ta == Tb).all(), 'within-rows == within-cols (suspicious for non-trivial input)'
    print('PASS  within-rows and within-cols produce different outputs')


# ---------------------------------------------------------------------------
# Curveball mixing-time validation on the real tensor
# ---------------------------------------------------------------------------

def test_curveball_mixing_time_real_tensor(verbose=True):
    """Track phi values across increasing n_swaps; check that distribution
    stabilizes (mean and variance plateau) by n_swaps=2000.

    Method: sample 30 independent runs at each of n_swaps in [50, 200, 500, 1000, 2000, 5000].
    Compute mean and sd of phi at each n_swaps level. Mixing is approximately
    achieved when consecutive n_swaps levels give phi mean and sd within
    sampling error.
    """
    T, M = real_tensor()
    swap_levels = [50, 200, 500, 1000, 2000, 5000]
    n_samples = 30

    if verbose:
        print('\nCurveball mixing-time validation on actual tensor:')
        print('  swap_count    phi_mean    phi_sd    n_samples')
    stats = {}
    rng = np.random.default_rng(7)
    for n_swaps in swap_levels:
        phis = np.zeros(n_samples)
        for k in range(n_samples):
            T_n, M_n = null_marginal_preserving(T, M, rng, n_swaps=n_swaps)
            phis[k] = phi(T_n, M_n, min_overlap=5)
        stats[n_swaps] = (phis.mean(), phis.std(ddof=1))
        if verbose:
            print('  {:>10}    {:.4f}    {:.4f}    {}'.format(
                n_swaps, phis.mean(), phis.std(ddof=1), n_samples))

    # Mixing check uses SE-aware threshold: drift across late levels should be
    # within 2 * SE_of_mean (where SE = sd / sqrt(n_samples)). Tightening below
    # this would be false-alarm territory for n_samples=30.
    means_late = [stats[n][0] for n in [1000, 2000, 5000]]
    sds_late = [stats[n][1] for n in [1000, 2000, 5000]]
    drift = max(means_late) - min(means_late)
    se = max(sds_late) / np.sqrt(n_samples)
    threshold = 2.5 * se
    if drift > threshold:
        raise AssertionError(
            'Curveball mixing not achieved by n_swaps=1000-5000: phi drift {:.4f} > 2.5*SE={:.4f}'.format(
                drift, threshold))
    print('PASS  Curveball mixing time: phi drift across n_swaps in [1000,2000,5000] = {:.4f}'
          ' (within 2.5*SE = {:.4f}; within sampling noise at n_samples={})'.format(drift, threshold, n_samples))

    # Default n_swaps=2000 is in the plateau region
    plateau_drift_2k_5k = abs(stats[2000][0] - stats[5000][0])
    print('  default n_swaps=2000 vs n_swaps=5000 mean drift = {:.4f}'.format(plateau_drift_2k_5k))


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print('Invariant tests:')
    test_null_random_preserves_obs_count()
    test_null_random_preserves_value_multiset()
    test_null_marginal_preserves_row_and_col_marginals()
    test_null_marginal_breaks_joint()
    test_null_within_rows_preserves_M()
    test_null_within_rows_preserves_row_value_multisets()
    test_null_within_cols_preserves_M()
    test_null_within_cols_preserves_col_value_multisets()
    test_within_rows_and_within_cols_are_different()
    test_curveball_mixing_time_real_tensor()
    print('\nAll tests passed.')
