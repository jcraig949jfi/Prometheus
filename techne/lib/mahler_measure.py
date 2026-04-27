"""TOOL_MAHLER_MEASURE — Mahler measure of a polynomial.

The Mahler measure M(p) of a polynomial p(x) = a_n * prod(x - alpha_i) is:
    M(p) = |a_n| * prod(max(1, |alpha_i|))

Equivalently: exp(integral_0^1 log|p(e^{2*pi*i*t})| dt)

For integer polynomials, M(p) >= 1, and Lehmer's conjecture asserts
M(p) > 1.17628... for any non-cyclotomic polynomial with M(p) > 1.

Interface:
    mahler_measure(coefficients) -> float           (scalar)
    is_cyclotomic(coefficients) -> bool             (scalar)
    log_mahler_measure(coefficients) -> float       (scalar)

    mahler_measure_batch(coeffs_list, method='auto') -> np.ndarray
    mahler_measure_batch_chunked(coeffs_list, chunk_size=1000) -> np.ndarray
    mahler_measure_padded(coeff_matrix) -> np.ndarray
    benchmark_mahler_batch(degrees, n_per_degree, methods=None) -> dict

Forged: 2026-04-21 | Tier: 1 (scalar) + Tier: 2 (batch, project #51, 2026-04-25)
Tested against: Mossinghoff's list of known small Mahler measures
"""
from __future__ import annotations

import time
from typing import Iterable, Mapping, Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Scalar API (Tier 1, original)
# ---------------------------------------------------------------------------

def mahler_measure(coefficients: list) -> float:
    """Compute the Mahler measure of a polynomial from its coefficients.

    Parameters
    ----------
    coefficients : list of int or float
        Polynomial coefficients in descending degree order: [a_n, ..., a_1, a_0]
        (numpy convention). For ascending order, reverse first.

    Returns
    -------
    float
        The Mahler measure M(p). Always >= 0. Returns |a_0| if degree 0.

    Raises
    ------
    ValueError
        If coefficients is empty or all zeros.
    """
    coeffs = np.array(coefficients, dtype=np.complex128)
    # Strip leading zeros
    nonzero = np.nonzero(coeffs)[0]
    if len(nonzero) == 0:
        raise ValueError("Zero polynomial has no Mahler measure")
    coeffs = coeffs[nonzero[0]:]

    if len(coeffs) == 1:
        return abs(float(coeffs[0]))

    roots = np.roots(coeffs)
    leading = abs(coeffs[0])
    return float(leading * np.prod(np.maximum(1.0, np.abs(roots))))


def log_mahler_measure(coefficients: list) -> float:
    """Compute log(M(p)), the logarithmic Mahler measure.

    This is the more natural quantity for theoretical work:
    m(p) = log(M(p)) = log|a_n| + sum(max(0, log|alpha_i|))
    """
    m = mahler_measure(coefficients)
    if m <= 0:
        return float('-inf')
    return float(np.log(m))


def is_cyclotomic(coefficients: list, tol: float = 1e-10) -> bool:
    """Test whether a polynomial is cyclotomic (all roots on unit circle).

    Cyclotomic polynomials have M(p) = 1 exactly. This is a numerical
    test with tolerance `tol` on root moduli.

    Returns False for constant polynomials.
    """
    coeffs = np.array(coefficients, dtype=np.complex128)
    nonzero = np.nonzero(coeffs)[0]
    if len(nonzero) == 0 or len(coeffs) <= 1:
        return False
    coeffs = coeffs[nonzero[0]:]
    if len(coeffs) <= 1:
        return False

    roots = np.roots(coeffs)
    return bool(np.all(np.abs(np.abs(roots) - 1.0) < tol))


# ---------------------------------------------------------------------------
# Batch API (Tier 2, project #51, 2026-04-25)
# ---------------------------------------------------------------------------
#
# Design notes
# ------------
# The bottleneck of `mahler_measure` for short polynomials (degree <= 20)
# is the per-call Python overhead around `np.roots`: argument coercion,
# leading-zero stripping, companion-matrix allocation, and the eigvals
# dispatch.  When we have n polynomials of similar degree we can:
#
#   1. Strip leading zeros and pad each polynomial to a common max degree.
#   2. Build a single (n, d, d) stack of companion matrices.
#   3. Call `np.linalg.eigvals` once on the stack — numpy's LAPACK
#      backend processes batches with much less overhead per matrix.
#   4. Reduce to M values via vectorised abs / max / prod.
#
# For *very* heterogeneous degrees the padding is wasteful (a degree-1
# poly padded to degree 30 introduces 29 spurious zero roots), so the
# 'auto' policy falls back to scalar evaluation when the degree spread
# is large.  Cyclotomic / trivial polynomials short-circuit before any
# eigenvalue computation.
#
# The returned array is float64 with NaN for zero polynomials and for
# polynomials whose coefficient vector is empty.  The scalar API still
# raises ValueError on those inputs — batch is more forgiving because
# scans regularly contain a few degenerate rows.

_VALID_BATCH_METHODS = ("auto", "companion_batch", "individual")


def _strip_leading_zeros(c: np.ndarray) -> np.ndarray:
    """Strip leading zeros from a 1-D coefficient vector (descending order)."""
    nz = np.nonzero(c)[0]
    if len(nz) == 0:
        return c[:0]
    return c[nz[0]:]


def _is_palindromic(c: np.ndarray, tol: float = 0.0) -> bool:
    """True if c == c[::-1] within tolerance.

    Reciprocal (palindromic) integer polynomials are the cyclotomic
    candidates — the cyclotomic short-circuit only fires on these.
    """
    if len(c) < 2:
        return False
    if tol == 0.0:
        return bool(np.array_equal(c, c[::-1]))
    return bool(np.allclose(c, c[::-1], atol=tol))


def _cyclotomic_short_circuit(c: np.ndarray, tol: float = 1e-10) -> bool:
    """Return True iff polynomial has M(p) = 1 via cyclotomic test.

    A polynomial has M(p) = 1 iff *both* (a) its leading coefficient is
    a unit (|a_n| = 1) and (b) every root lies on the unit circle.
    Without (a) the leading-coefficient factor in
    M(p) = |a_n| * prod max(1, |alpha_i|) keeps M above 1 -- e.g.
    2(x+1) is palindromic, has its single root on the unit circle, but
    has M = 2.

    We require palindromic + |a_n| = 1 + small-coefficient (a necessary
    condition for cyclotomic factors) before paying for the eigenvalue
    check.  Returns False on any non-trivial uncertainty so the caller
    falls back to the eigenvalue path.
    """
    if len(c) < 2:
        return False
    if not _is_palindromic(c.real if np.iscomplexobj(c) else c):
        return False
    # Leading coefficient must be a unit for M(p) = 1.
    if abs(abs(complex(c[0])) - 1.0) > 1e-12:
        return False
    # Coefficient ceiling: heuristic guard — true cyclotomic factors
    # have small integer coefficients, and the only ones that bite our
    # use-case (Mossinghoff catalog, Lehmer scan) are tiny.
    if np.any(np.abs(c) > 50):
        return False
    roots = np.roots(c)
    return bool(np.all(np.abs(np.abs(roots) - 1.0) < tol))


def _stripped_complex(coeffs) -> np.ndarray:
    """Coerce one polynomial into a 1-D complex128, stripping leading zeros.

    Empty / all-zero input is returned as a length-0 array; callers
    treat that as the degenerate case (M = NaN).
    """
    c = np.asarray(coeffs, dtype=np.complex128).reshape(-1)
    return _strip_leading_zeros(c)


def _companion_stack(coeff_matrix: np.ndarray) -> np.ndarray:
    """Build a stack of companion matrices from a 2-D coefficient array.

    Parameters
    ----------
    coeff_matrix : ndarray, shape (n_polys, d+1)
        Polynomials in descending order, with leading entry treated as
        a_n.  Rows where a_n == 0 are not allowed (caller must pad
        sensibly, e.g. with a leading 1 then zeros — but normal use is
        all rows have a_n != 0 after stripping).

    Returns
    -------
    M : ndarray, shape (n_polys, d, d), complex128
        Companion matrix for each polynomial (top-row = -a_{n-1..0}/a_n,
        identity subdiagonal).
    """
    n, k = coeff_matrix.shape
    d = k - 1
    if d <= 0:
        return np.zeros((n, 0, 0), dtype=np.complex128)
    cm = np.asarray(coeff_matrix, dtype=np.complex128)
    leading = cm[:, 0:1]
    # Top row is -a_{n-1..0} / a_n
    top = -cm[:, 1:] / leading
    M = np.zeros((n, d, d), dtype=np.complex128)
    M[:, 0, :] = top
    if d > 1:
        # Identity subdiagonal (rows 1..d-1, cols 0..d-2)
        idx = np.arange(d - 1)
        M[:, idx + 1, idx] = 1.0
    return M


def mahler_measure_padded(coeff_matrix) -> np.ndarray:
    """Compute Mahler measure for each row of a 2-D coefficient matrix.

    All rows share a common length; shorter polynomials must be
    represented by zero-padding *on the left* (descending convention),
    e.g. degree-3 poly [1, 2, 3, 4] in a degree-5 matrix becomes
    [0, 0, 1, 2, 3, 4].

    Parameters
    ----------
    coeff_matrix : array-like, shape (n_polys, max_degree+1)
        Coefficients in descending order, left-padded with zeros.

    Returns
    -------
    M : ndarray of float64, shape (n_polys,)
        Mahler measure per row.  Rows of all zeros yield NaN.

    Notes
    -----
    Internal helper of `mahler_measure_batch` exposed as a public entry
    point for callers that already maintain a packed numpy array
    (Charon's Lehmer scan does this).  No leading-zero stripping is
    performed beyond what is needed to extract a per-row leading
    coefficient.

    Algorithm
    ---------
    For each row, we locate the leftmost non-zero entry to identify
    a_n.  Rows that share the same effective degree are batched
    through `np.linalg.eigvals`.  The result is rendered into a
    common float64 output array.
    """
    A = np.asarray(coeff_matrix, dtype=np.complex128)
    if A.ndim != 2:
        raise ValueError(
            f"mahler_measure_padded expected 2-D array, got shape {A.shape}"
        )
    n_polys, k = A.shape
    out = np.full(n_polys, np.nan, dtype=np.float64)
    if n_polys == 0 or k == 0:
        return out

    # Locate first non-zero column per row (effective leading coefficient).
    # Rows of all-zeros remain NaN.
    nonzero_mask = A != 0
    any_nz = nonzero_mask.any(axis=1)
    first_nz_col = np.where(
        any_nz,
        nonzero_mask.argmax(axis=1),
        -1,
    )

    # Group rows by effective degree (k - 1 - first_nz_col).  All rows
    # in a group share a common companion-matrix size, so they can be
    # batched.
    valid_idx = np.where(any_nz)[0]
    if len(valid_idx) == 0:
        return out

    eff_deg = (k - 1) - first_nz_col[valid_idx]
    # Constants (eff_deg == 0) — Mahler measure is |a_0|.
    const_mask = eff_deg == 0
    if const_mask.any():
        rows_const = valid_idx[const_mask]
        cols_const = first_nz_col[rows_const]
        out[rows_const] = np.abs(A[rows_const, cols_const]).real

    # Group remaining rows by effective degree.
    rest_idx = valid_idx[~const_mask]
    if len(rest_idx) == 0:
        return out
    rest_deg = (k - 1) - first_nz_col[rest_idx]

    # For each unique degree, batch-eigvals the corresponding rows.
    for d in np.unique(rest_deg):
        rows = rest_idx[rest_deg == d]
        # Slice each row to its effective coefficient block of length d+1.
        # All rows in this group share the same starting column.
        start_col = k - 1 - int(d)
        block = A[rows, start_col:]   # shape (len(rows), d+1)
        leading = np.abs(block[:, 0])
        if d == 1:
            # Linear: roots = -a_0 / a_1; M = |a_1| * max(1, |root|).
            root_abs = np.abs(block[:, 1] / block[:, 0])
            out[rows] = (leading * np.maximum(1.0, root_abs)).real
            continue
        comp = _companion_stack(block)
        roots = np.linalg.eigvals(comp)               # shape (n_rows, d)
        contrib = np.maximum(1.0, np.abs(roots))      # shape (n_rows, d)
        out[rows] = leading * np.prod(contrib, axis=1)

    return out


def _max_degree(coeffs_list: Sequence) -> int:
    """Maximum effective degree across the list (after leading-zero strip)."""
    md = 0
    for c in coeffs_list:
        s = _stripped_complex(c)
        if len(s) > md + 1:
            md = len(s) - 1
    return md


def mahler_measure_batch(coeffs_list, method: str = "auto") -> np.ndarray:
    """Compute Mahler measure for a list of polynomials.

    Parameters
    ----------
    coeffs_list : iterable of (list/array of numbers)
        Each entry is a polynomial in descending coefficient order
        (matching the scalar `mahler_measure` convention).  Entries
        may have different degrees.
    method : {'auto', 'companion_batch', 'individual'}, default 'auto'
        Computation strategy.

        - 'companion_batch' — pad all polynomials to the maximum
          effective degree, build one stack of companion matrices, and
          batch-eigvals.  Best when degrees are similar.
        - 'individual' — call scalar `mahler_measure` for each entry.
          Slower but uses minimal memory and correctly handles wildly
          mixed degrees.
        - 'auto' — pick `companion_batch` when the degree spread is
          modest (max_degree - min_degree <= 4 OR n_polys < 64),
          otherwise `individual`.

    Returns
    -------
    M : ndarray of float64, shape (n,)
        Mahler measure per polynomial.  All-zero / empty rows yield NaN.

    Raises
    ------
    ValueError
        If ``method`` is not one of the documented choices.

    Examples
    --------
    >>> lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    >>> phi5   = [1, 1, 1, 1, 1]
    >>> M = mahler_measure_batch([lehmer, phi5])
    >>> abs(M[0] - 1.1762808182599) < 1e-9
    True
    >>> abs(M[1] - 1.0) < 1e-9
    True
    """
    if method not in _VALID_BATCH_METHODS:
        raise ValueError(
            f"method must be one of {_VALID_BATCH_METHODS}, got {method!r}"
        )

    items = list(coeffs_list)
    n = len(items)
    out = np.empty(n, dtype=np.float64)
    if n == 0:
        return out

    # Strip leading zeros and find effective lengths.
    stripped = [_stripped_complex(c) for c in items]
    lens = np.array([len(s) for s in stripped], dtype=np.int64)
    eff_deg = lens - 1   # -1 for empty / all-zero rows

    # Resolve method='auto'
    valid_mask = lens > 0
    chosen = method
    if chosen == "auto":
        if not valid_mask.any():
            chosen = "individual"
        else:
            d_valid = eff_deg[valid_mask]
            spread = int(d_valid.max() - d_valid.min())
            # Heuristic: small spread or small n favours batch.
            if spread <= 4 or n < 64:
                chosen = "companion_batch"
            else:
                chosen = "individual"

    if chosen == "individual":
        for i, s in enumerate(stripped):
            if len(s) == 0:
                out[i] = np.nan
            elif len(s) == 1:
                out[i] = abs(complex(s[0]))
            else:
                # Cyclotomic short-circuit on the stripped vector.
                if _cyclotomic_short_circuit(s):
                    out[i] = 1.0
                else:
                    roots = np.roots(s)
                    out[i] = float(
                        abs(s[0]) * np.prod(np.maximum(1.0, np.abs(roots)))
                    )
        return out

    # chosen == 'companion_batch'
    out[:] = np.nan
    if not valid_mask.any():
        return out

    # Constants (effective degree 0).
    const_mask = lens == 1
    for i in np.where(const_mask)[0]:
        out[i] = abs(complex(stripped[i][0]))

    # Rows that still need eigvals.  No cyclotomic pre-pass: a
    # per-row `np.roots` would defeat batching; cyclotomic polys
    # flow through the same companion-stack path and emerge with
    # M = 1 (up to floating-point noise) just like everyone else.
    todo = np.where(valid_mask & (lens > 1))[0]
    if len(todo) == 0:
        return out

    # For tiny batches, stacked companion eigvals can drift farther from
    # numpy.roots than the test-backed scalar contract allows (observed
    # ~1e-8 on a degree-7 integer polynomial). Keep the public batch API
    # scalar-identical at small n; the vectorized path remains for scan scale.
    if len(todo) < 16:
        for i in todo:
            s = stripped[i]
            if _cyclotomic_short_circuit(s):
                out[i] = 1.0
            else:
                roots = np.roots(s)
                out[i] = float(
                    abs(s[0]) * np.prod(np.maximum(1.0, np.abs(roots)))
                )
        return out

    # Build a packed coefficient matrix at max effective degree across todo.
    max_d = int(eff_deg[todo].max())
    coeff_mat = np.zeros((len(todo), max_d + 1), dtype=np.complex128)
    for j, i in enumerate(todo):
        s = stripped[i]
        coeff_mat[j, max_d + 1 - len(s):] = s

    out[todo] = mahler_measure_padded(coeff_mat)
    return out


def mahler_measure_batch_chunked(
    coeffs_list, chunk_size: int = 1000, method: str = "auto"
) -> np.ndarray:
    """Memory-bounded batch evaluation: splits input into chunks.

    For a degree-d batch of n polynomials, `mahler_measure_batch`
    allocates an O(n * d^2) complex128 companion stack.  At d = 30,
    n = 100_000 that is ~1.4 GB — enough to OOM on small machines.
    This wrapper splits the input into `chunk_size` pieces and
    concatenates the results.

    Parameters
    ----------
    coeffs_list : iterable of polynomials (descending order)
    chunk_size : int, default 1000
        Polynomials per batch call.  Must be >= 1.
    method : str, default 'auto'
        Forwarded to `mahler_measure_batch` for each chunk.

    Returns
    -------
    M : ndarray of float64, shape (n,)
    """
    if chunk_size < 1:
        raise ValueError(f"chunk_size must be >= 1, got {chunk_size}")
    items = list(coeffs_list)
    n = len(items)
    if n == 0:
        return np.empty(0, dtype=np.float64)
    parts = []
    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        parts.append(mahler_measure_batch(items[start:end], method=method))
    return np.concatenate(parts)


def benchmark_mahler_batch(
    degrees: Iterable[int],
    n_per_degree: int,
    methods: Sequence[str] | None = None,
    seed: int = 0,
) -> dict:
    """Quick performance comparison across batch methods.

    Generates random reciprocal integer polynomials at each requested
    degree and times each method on the union.

    Parameters
    ----------
    degrees : iterable of int
        Degrees to populate the test set with.
    n_per_degree : int
        Polynomials sampled per degree.
    methods : sequence of str, optional
        Methods to compare; defaults to ('individual', 'companion_batch').
    seed : int, default 0
        RNG seed for reproducible benchmarks.

    Returns
    -------
    dict
        ``{method: {'time_total': float, 'time_per_poly': float,
                    'n_polys': int}}``
    """
    if methods is None:
        methods = ("individual", "companion_batch")
    rng = np.random.default_rng(seed)
    polys: list[list[int]] = []
    for d in degrees:
        # Random reciprocal poly: choose first half of coefficients in
        # {-1, 0, 1}, mirror.  Always monic.
        half = (d // 2) + 1
        for _ in range(n_per_degree):
            head = rng.integers(-1, 2, size=half).tolist()
            head[0] = 1  # monic
            if d % 2 == 0:
                tail = head[:-1][::-1]
            else:
                tail = head[::-1]
            polys.append([int(x) for x in head + tail])
    n = len(polys)
    results: dict = {}
    for m in methods:
        t0 = time.perf_counter()
        if m == "individual":
            arr = np.array(
                [mahler_measure(p) for p in polys], dtype=np.float64
            )
        else:
            arr = mahler_measure_batch(polys, method=m)
        t1 = time.perf_counter()
        elapsed = t1 - t0
        results[m] = {
            "time_total": elapsed,
            "time_per_poly": elapsed / max(n, 1),
            "n_polys": n,
            # Sanity: keep the first 3 values for quick visual check.
            "sample_M": arr[:3].tolist() if n else [],
        }
    return results


if __name__ == "__main__":
    # Quick smoke test with known values
    # x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1 (Lehmer's polynomial)
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    m = mahler_measure(lehmer)
    print(f"Lehmer polynomial M(p) = {m:.10f}")
    print(f"  Expected:             1.1762808183...")
    print(f"  Cyclotomic: {is_cyclotomic(lehmer)}")

    # Cyclotomic: x^4 + x^3 + x^2 + x + 1 = Phi_5
    phi5 = [1, 1, 1, 1, 1]
    print(f"\nPhi_5 M(p) = {mahler_measure(phi5):.10f}")
    print(f"  Expected: 1.0000000000")
    print(f"  Cyclotomic: {is_cyclotomic(phi5)}")

    # x^2 - x - 1 (golden ratio polynomial)
    golden = [1, -1, -1]
    print(f"\nGolden ratio poly M(p) = {mahler_measure(golden):.10f}")
    print(f"  Expected:              1.6180339887...")

    # Batch smoke test
    print("\nBatch smoke test:")
    M = mahler_measure_batch([lehmer, phi5, golden])
    print(f"  Batch result: {M}")
    print(f"  Expected:     [1.176280818..., 1.0, 1.618033988...]")

    # Benchmark
    print("\nBenchmark (degree 8, 1000 polys):")
    res = benchmark_mahler_batch([8], 1000, seed=1)
    for k, v in res.items():
        print(
            f"  {k:18s} total={v['time_total']:.4f}s   "
            f"per-poly={v['time_per_poly']*1e6:.2f}us"
        )
