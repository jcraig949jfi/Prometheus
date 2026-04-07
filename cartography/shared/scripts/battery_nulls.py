"""
Domain-Specific Null Generators for the Falsification Battery.
===============================================================
The overnight run (2026-04-05) showed that continuous random nulls are too
lenient for integer data: small integer ratios naturally match mathematical
constants (pi/3, sqrt(2), etc.) at rates far above what a continuous null
expects.  This module provides tighter null distributions that respect the
discrete/rational/structural constraints of real data.

Each generator returns an array of null hit counts (one per trial) that
can be compared directly to the observed test statistic from the battery.

Usage:
    from battery_nulls import auto_null, integer_null, fraction_null

    null_hits = integer_null(my_integer_data, n_trials=2000)
    p_value = np.mean(null_hits >= observed_hits)
"""

import numpy as np
from scipy import stats, sparse
from fractions import Fraction
from typing import Optional, Union


# ---------------------------------------------------------------------------
# 1. Integer Null
# ---------------------------------------------------------------------------

def integer_null(values: np.ndarray, n_trials: int = 1000,
                 seed: int = 42) -> np.ndarray:
    """Null distribution for integer-valued data.

    Generates random integers matching the distribution properties of the
    input: same range, same even/odd ratio, same approximate density (ratio
    of unique values to range span).

    Suitable for: knot determinants, conductors, space group numbers, ranks.

    Parameters
    ----------
    values : array-like
        Integer-valued observations.
    n_trials : int
        Number of null samples to generate.
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    null_hits : np.ndarray, shape (n_trials,)
        Count of "hits" (matches to mathematical constants) per trial.
        The caller defines what constitutes a hit; this returns the raw
        synthetic samples for external comparison.
    """
    values = np.asarray(values, dtype=int)
    rng = np.random.RandomState(seed)

    lo, hi = int(values.min()), int(values.max())
    n = len(values)

    # Distribution properties to preserve
    n_even = int(np.sum(values % 2 == 0))
    even_ratio = n_even / n if n > 0 else 0.5

    unique_vals = np.unique(values)
    span = hi - lo + 1
    density = len(unique_vals) / span if span > 0 else 1.0

    # Build the candidate pool: all integers in [lo, hi]
    all_ints = np.arange(lo, hi + 1)

    # If density is low, subsample the candidate pool to match
    if density < 0.8 and len(all_ints) > 1:
        pool_size = max(int(density * len(all_ints)), len(unique_vals))
        pool_size = min(pool_size, len(all_ints))
    else:
        pool_size = len(all_ints)

    null_samples = np.empty((n_trials, n), dtype=int)

    for t in range(n_trials):
        if pool_size < len(all_ints):
            pool = rng.choice(all_ints, size=pool_size, replace=False)
        else:
            pool = all_ints

        # Separate into even and odd candidates
        evens = pool[pool % 2 == 0]
        odds = pool[pool % 2 != 0]

        n_even_draw = int(round(even_ratio * n))
        n_odd_draw = n - n_even_draw

        # Draw with replacement from each parity pool
        drawn = np.empty(n, dtype=int)
        if len(evens) > 0 and n_even_draw > 0:
            drawn[:n_even_draw] = rng.choice(evens, size=n_even_draw, replace=True)
        elif n_even_draw > 0:
            drawn[:n_even_draw] = rng.choice(pool, size=n_even_draw, replace=True)

        if len(odds) > 0 and n_odd_draw > 0:
            drawn[n_even_draw:] = rng.choice(odds, size=n_odd_draw, replace=True)
        elif n_odd_draw > 0:
            drawn[n_even_draw:] = rng.choice(pool, size=n_odd_draw, replace=True)

        null_samples[t] = drawn

    return null_samples


# ---------------------------------------------------------------------------
# 2. Fraction Null
# ---------------------------------------------------------------------------

def fraction_null(values: np.ndarray, n_trials: int = 1000,
                  max_denom: int = 20, seed: int = 42) -> np.ndarray:
    """Null distribution for rational-valued data.

    Generates random fractions with small denominators (2 through max_denom),
    matching the range of the input values.

    Suitable for: ANTEDB exponent pairs, Fungrim constants, rational
    approximations to spectral data.

    Parameters
    ----------
    values : array-like
        Observed rational-valued data.
    n_trials : int
        Number of null samples to generate.
    max_denom : int
        Maximum denominator in generated fractions.
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    null_samples : np.ndarray, shape (n_trials, len(values))
        Synthetic rational samples per trial.
    """
    values = np.asarray(values, dtype=float)
    rng = np.random.RandomState(seed)

    lo, hi = float(values.min()), float(values.max())
    n = len(values)

    # Build pool of all fractions p/q in [lo, hi] with q in [2, max_denom]
    frac_pool = set()
    for q in range(2, max_denom + 1):
        p_lo = int(np.floor(lo * q))
        p_hi = int(np.ceil(hi * q))
        for p in range(p_lo, p_hi + 1):
            val = p / q
            if lo <= val <= hi:
                frac_pool.add(val)

    frac_pool = np.array(sorted(frac_pool))

    if len(frac_pool) == 0:
        # Fallback: uniform continuous in [lo, hi]
        return rng.uniform(lo, hi, size=(n_trials, n))

    null_samples = np.empty((n_trials, n), dtype=float)
    for t in range(n_trials):
        null_samples[t] = rng.choice(frac_pool, size=n, replace=True)

    return null_samples


# ---------------------------------------------------------------------------
# 3. Stoichiometric Null
# ---------------------------------------------------------------------------

def stoichiometric_null(S_matrix: np.ndarray, n_trials: int = 100,
                        seed: int = 42) -> np.ndarray:
    """Null distribution for metabolic stoichiometry matrices.

    Generates random matrices satisfying mass-balance constraints:
    - Same dimensions and sparsity as the input
    - Each column (reaction) has at least one positive and one negative entry
    - Non-zero entries drawn from the same magnitude distribution as input

    Returns null SVD spectra for comparison with the real matrix.

    Parameters
    ----------
    S_matrix : np.ndarray, shape (m, n)
        Real stoichiometry matrix (metabolites x reactions).
    n_trials : int
        Number of null matrices to generate.
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    null_spectra : np.ndarray, shape (n_trials, min(m, n))
        Singular values of each null matrix, for comparison with real SVD.
    """
    S = np.asarray(S_matrix, dtype=float)
    m, n = S.shape
    rng = np.random.RandomState(seed)

    # Analyze input structure
    nonzero_mask = S != 0
    density = np.sum(nonzero_mask) / S.size
    magnitudes = np.abs(S[nonzero_mask])

    # Per-column nonzero counts
    col_nnz = np.sum(nonzero_mask, axis=0)

    k = min(m, n)
    null_spectra = np.empty((n_trials, k), dtype=float)

    for t in range(n_trials):
        S_null = np.zeros((m, n), dtype=float)

        for j in range(n):
            nnz = max(int(col_nnz[j]), 2)  # at least 2 (one +, one -)
            rows = rng.choice(m, size=min(nnz, m), replace=False)

            # Assign random magnitudes from the empirical distribution
            mags = rng.choice(magnitudes, size=len(rows), replace=True)

            # Ensure at least one positive and one negative
            signs = np.ones(len(rows))
            signs[0] = 1.0
            signs[1] = -1.0
            if len(rows) > 2:
                signs[2:] = rng.choice([-1.0, 1.0], size=len(rows) - 2)
            rng.shuffle(signs)

            S_null[rows, j] = signs * mags

        # SVD
        try:
            sv = np.linalg.svd(S_null, compute_uv=False)
            null_spectra[t] = sv[:k]
        except np.linalg.LinAlgError:
            null_spectra[t] = np.nan

    return null_spectra


# ---------------------------------------------------------------------------
# 4. Graph Null (Configuration Model)
# ---------------------------------------------------------------------------

def graph_null(adjacency: np.ndarray, n_trials: int = 1000,
               seed: int = 42) -> np.ndarray:
    """Null distribution via configuration model: preserves degree sequence,
    randomizes edges.

    Returns null distributions of the leading eigenvalue (spectral radius)
    for comparison with the real graph.

    Parameters
    ----------
    adjacency : np.ndarray, shape (n, n)
        Adjacency matrix (symmetric for undirected, or asymmetric for directed).
    n_trials : int
        Number of null graphs to generate.
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    null_spectral_radii : np.ndarray, shape (n_trials,)
        Leading eigenvalue of each null graph.
    """
    A = np.asarray(adjacency, dtype=float)
    n = A.shape[0]
    rng = np.random.RandomState(seed)

    is_symmetric = np.allclose(A, A.T)

    if is_symmetric:
        # Undirected: degree = row sum
        degrees = np.sum(A > 0, axis=1).astype(int)
    else:
        # Directed: out-degree and in-degree
        out_deg = np.sum(A > 0, axis=1).astype(int)
        in_deg = np.sum(A > 0, axis=0).astype(int)

    null_radii = np.empty(n_trials, dtype=float)

    for t in range(n_trials):
        A_null = np.zeros((n, n), dtype=float)

        if is_symmetric:
            # Build stub list and pair randomly
            stubs = []
            for node, deg in enumerate(degrees):
                stubs.extend([node] * deg)
            stubs = np.array(stubs)
            rng.shuffle(stubs)

            # Pair stubs
            for i in range(0, len(stubs) - 1, 2):
                u, v = stubs[i], stubs[i + 1]
                if u != v:  # no self-loops
                    A_null[u, v] = 1.0
                    A_null[v, u] = 1.0
        else:
            # Directed: pair out-stubs with in-stubs
            out_stubs = []
            for node, deg in enumerate(out_deg):
                out_stubs.extend([node] * deg)
            in_stubs = []
            for node, deg in enumerate(in_deg):
                in_stubs.extend([node] * deg)

            out_stubs = np.array(out_stubs)
            in_stubs = np.array(in_stubs)
            rng.shuffle(in_stubs)

            n_edges = min(len(out_stubs), len(in_stubs))
            for i in range(n_edges):
                u, v = out_stubs[i], in_stubs[i]
                if u != v:
                    A_null[u, v] = 1.0

        # Leading eigenvalue
        try:
            if is_symmetric:
                eigvals = np.linalg.eigvalsh(A_null)
                null_radii[t] = np.max(np.abs(eigvals))
            else:
                eigvals = np.linalg.eigvals(A_null)
                null_radii[t] = np.max(np.abs(eigvals))
        except np.linalg.LinAlgError:
            null_radii[t] = np.nan

    return null_radii


# ---------------------------------------------------------------------------
# 5. Auto Null Selector
# ---------------------------------------------------------------------------

def _is_integer_data(values: np.ndarray, tol: float = 1e-10) -> bool:
    """Check if all values are (close to) integers."""
    return np.all(np.abs(values - np.round(values)) < tol)


def _is_fraction_data(values: np.ndarray, max_denom: int = 20,
                      tol: float = 1e-6) -> bool:
    """Check if all values are close to p/q for small q."""
    for v in values:
        matched = False
        for q in range(1, max_denom + 1):
            p = round(v * q)
            if abs(v - p / q) < tol:
                matched = True
                break
        if not matched:
            return False
    return True


def auto_null(values: np.ndarray, data_type: str = 'auto',
              n_trials: int = 1000, seed: int = 42) -> np.ndarray:
    """Automatically select the right null generator based on data properties.

    Parameters
    ----------
    values : array-like
        Observed data.
    data_type : str
        'auto' (detect), 'integer', 'fraction', or 'continuous'.
    n_trials : int
        Number of null trials.
    seed : int
        RNG seed.

    Returns
    -------
    null_samples : np.ndarray
        Shape depends on the selected generator.
    detected_type : str
        (Only when data_type='auto') The detected data type.
    """
    values = np.asarray(values, dtype=float)

    if data_type == 'auto':
        if _is_integer_data(values):
            data_type = 'integer'
        elif _is_fraction_data(values):
            data_type = 'fraction'
        else:
            data_type = 'continuous'

    if data_type == 'integer':
        samples = integer_null(values.astype(int), n_trials=n_trials, seed=seed)
    elif data_type == 'fraction':
        samples = fraction_null(values, n_trials=n_trials, seed=seed)
    elif data_type == 'continuous':
        # Standard continuous null: bootstrap from empirical distribution
        rng = np.random.RandomState(seed)
        n = len(values)
        lo, hi = float(values.min()), float(values.max())
        mu, sigma = float(np.mean(values)), float(np.std(values))
        if sigma < 1e-12:
            sigma = 1.0
        samples = rng.normal(mu, sigma, size=(n_trials, n))
    else:
        raise ValueError(f"Unknown data_type: {data_type!r}. "
                         f"Use 'auto', 'integer', 'fraction', or 'continuous'.")

    return samples


# ---------------------------------------------------------------------------
# Demo / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Battery Nulls — Domain-Specific Null Generator Demo")
    print("=" * 60)

    rng = np.random.RandomState(42)

    # --- 1. Integer null ---
    print("\n--- 1. Integer Null (simulated knot determinants) ---")
    knot_dets = np.array([1, 3, 5, 7, 5, 3, 9, 11, 13, 15, 7, 5, 3, 1, 9,
                          11, 7, 5, 13, 3, 15, 17, 19, 21, 23], dtype=int)
    int_samples = integer_null(knot_dets, n_trials=500)
    print(f"  Input: {len(knot_dets)} values, range [{knot_dets.min()}, {knot_dets.max()}]")
    print(f"  Even/odd ratio: {np.mean(knot_dets % 2 == 0):.2f}")
    print(f"  Null shape: {int_samples.shape}")
    print(f"  Null sample means: {np.mean(int_samples, axis=1)[:5].round(2)}")
    print(f"  Null even/odd ratios: {[np.mean(s % 2 == 0) for s in int_samples[:5]]}")

    # --- 2. Fraction null ---
    print("\n--- 2. Fraction Null (simulated exponent pairs) ---")
    exponents = np.array([1/2, 1/3, 2/3, 1/4, 3/4, 1/5, 2/5, 3/5, 4/5,
                          1/6, 5/6, 1/7, 2/7, 3/7])
    frac_samples = fraction_null(exponents, n_trials=500)
    print(f"  Input: {len(exponents)} values, range [{exponents.min():.4f}, {exponents.max():.4f}]")
    print(f"  Null shape: {frac_samples.shape}")
    print(f"  Sample null row: {frac_samples[0][:8].round(4)}")
    # Check that all null values are exact fractions
    all_rational = True
    for v in frac_samples[0]:
        f = Fraction(v).limit_denominator(20)
        if abs(float(f) - v) > 1e-10:
            all_rational = False
            break
    print(f"  All null values are small-denom fractions: {all_rational}")

    # --- 3. Stoichiometric null ---
    print("\n--- 3. Stoichiometric Null (random metabolic matrix) ---")
    S = np.zeros((8, 5))
    S[0, 0] = -1; S[1, 0] = 1  # reaction 0
    S[1, 1] = -1; S[2, 1] = 1; S[3, 1] = 1  # reaction 1
    S[2, 2] = -1; S[4, 2] = 2  # reaction 2
    S[3, 3] = -1; S[5, 3] = 1; S[6, 3] = -1  # reaction 3
    S[6, 4] = 1; S[7, 4] = -1  # reaction 4
    real_sv = np.linalg.svd(S, compute_uv=False)
    null_sv = stoichiometric_null(S, n_trials=200)
    print(f"  Input S: {S.shape}, density: {np.mean(S != 0):.2f}")
    print(f"  Real singular values: {real_sv[:5].round(3)}")
    print(f"  Null SV shape: {null_sv.shape}")
    print(f"  Null leading SV: mean={np.nanmean(null_sv[:, 0]):.3f}, "
          f"std={np.nanstd(null_sv[:, 0]):.3f}")
    real_rank = np.sum(real_sv > 1e-10)
    null_ranks = np.sum(null_sv > 1e-10, axis=1)
    print(f"  Real rank: {real_rank}, Null rank: mean={np.mean(null_ranks):.1f}")

    # --- 4. Graph null ---
    print("\n--- 4. Graph Null (configuration model) ---")
    n_nodes = 20
    A = np.zeros((n_nodes, n_nodes))
    for i in range(n_nodes - 1):
        A[i, i + 1] = 1; A[i + 1, i] = 1  # chain
    # Add a few random edges
    for _ in range(10):
        i, j = rng.randint(0, n_nodes, 2)
        if i != j:
            A[i, j] = 1; A[j, i] = 1
    real_eigvals = np.linalg.eigvalsh(A)
    real_radius = np.max(np.abs(real_eigvals))
    null_radii = graph_null(A, n_trials=500)
    print(f"  Graph: {n_nodes} nodes, {int(np.sum(A) / 2)} edges")
    print(f"  Real spectral radius: {real_radius:.3f}")
    print(f"  Null spectral radius: mean={np.nanmean(null_radii):.3f}, "
          f"std={np.nanstd(null_radii):.3f}")
    p_val = np.mean(null_radii >= real_radius)
    print(f"  p-value (null >= real): {p_val:.4f}")

    # --- 5. Auto null ---
    print("\n--- 5. Auto Null (type detection) ---")
    for label, data in [
        ("integers", np.array([1, 3, 5, 7, 9, 11, 13])),
        ("fractions", np.array([1/3, 2/5, 1/7, 3/4, 5/6])),
        ("continuous", np.array([1.41421356, 2.71828, 3.14159, 0.57721])),
    ]:
        detected = 'integer' if _is_integer_data(data) else (
            'fraction' if _is_fraction_data(data) else 'continuous')
        samples = auto_null(data, n_trials=100)
        print(f"  {label:12s} -> detected as '{detected}', "
              f"null shape: {samples.shape}")

    print("\nDone.")
