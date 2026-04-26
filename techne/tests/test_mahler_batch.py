"""Test TOOL_MAHLER_MEASURE batch API (project #51).

Math-TDD coverage:
    Authority    : Mossinghoff snapshot (178 entries),
                   Lehmer polynomial,
                   cyclotomic polynomials Phi_n,
                   100-poly padded matrix.
    Property     : batch == [scalar(c) for c in batch],
                   shape == (n,),
                   M >= 1 - eps for integer polys (or NaN),
                   order-preserving under permutation.
    Edge         : empty list, singleton, all-zero polynomial,
                   mixed-degree input, unknown method,
                   chunk_size validation.
    Composition  : batch + sort matches sorted scalar values,
                   batch + filter_below_M matches scalar pipeline.

The batch API must agree with `mahler_measure(c)` to within 1e-9 for any
input (companion-matrix eigenvalue noise floor is ~1e-13).
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

# Add techne/ to path so `from lib.mahler_measure import ...` works.
HERE = os.path.dirname(os.path.abspath(__file__))
TECHNE_ROOT = os.path.dirname(HERE)
sys.path.insert(0, TECHNE_ROOT)
# And add the prometheus repo root so we can import prometheus_math for
# the composition test against `lehmer.filter_below_M`.
REPO_ROOT = os.path.dirname(TECHNE_ROOT)
sys.path.insert(0, REPO_ROOT)

from lib.mahler_measure import (   # noqa: E402
    benchmark_mahler_batch,
    mahler_measure,
    mahler_measure_batch,
    mahler_measure_batch_chunked,
    mahler_measure_padded,
)


# ---------------------------------------------------------------------------
# Reference fixtures
# ---------------------------------------------------------------------------

# Lehmer's polynomial in *descending* order (numpy convention),
# x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1.
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.17628081825991750  # Lehmer 1933; reproduced everywhere.

# Cyclotomic polynomials Phi_n have M(Phi_n) = 1 exactly.
PHI_2 = [1, 1]                    # Phi_2 = x + 1
PHI_3 = [1, 1, 1]                 # Phi_3 = x^2 + x + 1
PHI_5 = [1, 1, 1, 1, 1]           # Phi_5 = x^4 + x^3 + x^2 + x + 1
PHI_6 = [1, -1, 1]                # Phi_6 = x^2 - x + 1


def _load_mossinghoff_snapshot():
    """Return list of (coeffs_desc, M_stored) from MAHLER_TABLE.

    The snapshot stores coefficients in *ascending* order; the scalar
    `mahler_measure` consumes *descending* order, so reverse here.
    """
    try:
        from prometheus_math.databases._mahler_data import MAHLER_TABLE
    except Exception:                                        # pragma: no cover
        pytest.skip("prometheus_math.databases._mahler_data unavailable")
    return [
        (list(reversed(e["coeffs"])), float(e["mahler_measure"]))
        for e in MAHLER_TABLE
    ]


# ---------------------------------------------------------------------------
# 1. Authority-based tests (>= 2 required)
# ---------------------------------------------------------------------------

def test_authority_mossinghoff_snapshot_178_entries():
    """Batch agrees with stored Mahler measures across the catalog.

    Reference: prometheus_math.databases._mahler_data.MAHLER_TABLE,
    which is itself a curated snapshot of Mossinghoff's small-Mahler
    tables (Davidson, Wayback Machine), cross-checked against Lehmer
    1933, Smyth 1971, Boyd 1980, Mossinghoff 1998.

    The batch result must agree with the *scalar* mahler_measure to
    1e-10 (the same floor that `_mahler_data` validates against).
    """
    snap = _load_mossinghoff_snapshot()
    polys = [c for c, _ in snap]
    stored = np.array([m for _, m in snap])
    M_batch = mahler_measure_batch(polys)
    M_indiv = np.array([mahler_measure(p) for p in polys])
    assert np.max(np.abs(M_batch - M_indiv)) < 1e-10
    assert np.max(np.abs(M_batch - stored)) < 1e-9


def test_authority_lehmer_polynomial():
    """Lehmer's polynomial M(p) = 1.176280818... (Lehmer 1933).

    Reference: D.H. Lehmer, "Factorization of certain cyclotomic
    functions," Annals of Math. 34 (1933), 461-479.  The Lehmer
    polynomial is the conjectured infimum of M(p) > 1 for non-cyclotomic
    integer polynomials.
    """
    M = mahler_measure_batch([LEHMER])
    assert M.shape == (1,)
    assert abs(M[0] - LEHMER_M) < 1e-10


def test_authority_cyclotomic_polynomials_M_equals_1():
    """Phi_n cyclotomic polynomials all have M = 1 exactly.

    Reference: Kronecker's theorem.  M(Phi_n) = 1 because all roots
    are roots of unity and lie on the unit circle.  Numerical
    eigenvalue computation introduces noise on the order of 1e-13.
    """
    M = mahler_measure_batch([PHI_2, PHI_3, PHI_5, PHI_6])
    assert M.shape == (4,)
    assert np.allclose(M, 1.0, atol=1e-9)


def test_authority_padded_matrix_matches_scalar_for_100_polys():
    """`mahler_measure_padded` agrees with scalar over 100 random polys.

    Reference: scalar `mahler_measure` is the existing gold standard
    forged 2026-04-21 and authority-tested against Mossinghoff.
    Padded version must reproduce it to 1e-10.
    """
    rng = np.random.default_rng(42)
    polys = []
    for _ in range(100):
        d = int(rng.integers(2, 12))
        # Reciprocal random poly with coefficients in {-1, 0, 1}.
        half = (d // 2) + 1
        head = rng.integers(-1, 2, size=half).tolist()
        head[0] = 1
        tail = head[:-1][::-1] if d % 2 == 0 else head[::-1]
        polys.append([int(x) for x in head + tail])

    max_d = max(len(p) for p in polys)
    M = np.zeros((len(polys), max_d), dtype=np.complex128)
    for i, p in enumerate(polys):
        M[i, max_d - len(p):] = p
    out_padded = mahler_measure_padded(M)
    out_scalar = np.array([mahler_measure(p) for p in polys])
    assert np.max(np.abs(out_padded - out_scalar)) < 1e-10


# ---------------------------------------------------------------------------
# 2. Property-based tests (>= 2 required)
# ---------------------------------------------------------------------------

# Strategy: integer coefficient lists, leading entry guaranteed non-zero
# so the Mahler measure is well-defined.
_int_coeffs = st.lists(
    st.integers(min_value=-3, max_value=3),
    min_size=1,
    max_size=10,
).filter(lambda lst: lst[0] != 0)


@given(st.lists(_int_coeffs, min_size=1, max_size=8))
@settings(max_examples=40, deadline=2000)
def test_property_batch_equals_scalar(coeffs_list):
    """For any list of valid polynomials, batch == per-poly scalar.

    Both methods are hit (companion_batch + individual) to make sure
    they stay equivalent.  Tolerance 1e-9 accommodates LAPACK eigvals
    drift; coefficient magnitudes are clamped (|c| <= 3) to keep M well
    below 1e6 where double precision tightly tracks log M.
    """
    expected = np.array([mahler_measure(c) for c in coeffs_list])
    for method in ("auto", "companion_batch", "individual"):
        out = mahler_measure_batch(coeffs_list, method=method)
        assert out.shape == (len(coeffs_list),)
        assert np.allclose(out, expected, atol=1e-9, rtol=1e-9)


@given(st.lists(_int_coeffs, min_size=0, max_size=20))
@settings(max_examples=30, deadline=2000)
def test_property_shape_and_dtype(coeffs_list):
    """Output shape == (len(input),) and dtype == float64."""
    out = mahler_measure_batch(coeffs_list)
    assert out.shape == (len(coeffs_list),)
    assert out.dtype == np.float64


@given(st.lists(_int_coeffs, min_size=1, max_size=10))
@settings(max_examples=30, deadline=2000)
def test_property_integer_polys_M_at_least_one(coeffs_list):
    """For any non-zero integer poly, M(p) >= 1 (Kronecker / trivial bound).

    The batch routine produces float64 output with O(1e-13) eigenvalue
    noise, so we use a 1e-9 tolerance below 1.0.  Trivial polynomials
    are filtered upstream by the `_int_coeffs` strategy.
    """
    out = mahler_measure_batch(coeffs_list)
    finite = ~np.isnan(out)
    assert np.all(out[finite] >= 1.0 - 1e-9)


@given(
    st.lists(_int_coeffs, min_size=2, max_size=12),
    st.integers(min_value=0, max_value=2**30),
)
@settings(max_examples=20, deadline=2000)
def test_property_order_preserving(coeffs_list, seed):
    """Permuting input coords corresponds to permuting output coords.

    This catches ordering-dependent bugs in the per-degree grouping
    inside `mahler_measure_padded` (rows in different degree groups
    must end up at their original positions).
    """
    n = len(coeffs_list)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    M_orig = mahler_measure_batch(coeffs_list)
    shuffled = [coeffs_list[i] for i in perm]
    M_shuf = mahler_measure_batch(shuffled)
    # M_shuf[k] should equal M_orig[perm[k]].
    assert np.allclose(M_shuf, M_orig[perm], atol=1e-9, rtol=1e-9)


# ---------------------------------------------------------------------------
# 3. Edge-case tests (>= 2 required)
# ---------------------------------------------------------------------------

def test_edge_empty_list_returns_empty_array():
    """Empty input -> empty float64 array, no eigvals call."""
    out = mahler_measure_batch([])
    assert out.shape == (0,)
    assert out.dtype == np.float64


def test_edge_singleton_input_returns_length_one_array():
    """Length-1 input -> shape (1,) result with the right value."""
    out = mahler_measure_batch([LEHMER])
    assert out.shape == (1,)
    assert abs(out[0] - LEHMER_M) < 1e-10


def test_edge_zero_polynomial_yields_nan():
    """All-zero polynomial in a batch -> NaN, no exception.

    The scalar `mahler_measure` raises ValueError on a zero poly, but
    in a research scan a single bad row should not poison the whole
    batch — surface NaN instead.
    """
    out = mahler_measure_batch([[0, 0, 0], LEHMER])
    assert np.isnan(out[0])
    assert abs(out[1] - LEHMER_M) < 1e-10


def test_edge_mixed_degree_input_handles_padding():
    """Mixed-degree inputs go through padded companion stack correctly.

    The internal grouping in `mahler_measure_padded` slices rows by
    effective degree, so degrees 1, 4, and 10 in one call must each
    resolve to the right value.
    """
    polys = [
        [1, -2],                      # x - 2, M = 2
        PHI_5,                        # M = 1
        LEHMER,                       # M = 1.17628...
        [1, 0, 0],                    # x^2, M = 1 (single root at 0, max(1,0)=1)
    ]
    out = mahler_measure_batch(polys)
    expected = np.array([mahler_measure(p) for p in polys])
    assert np.allclose(out, expected, atol=1e-10)


def test_edge_unknown_method_raises_value_error():
    """`method` outside the documented set -> ValueError."""
    with pytest.raises(ValueError, match="method must be one of"):
        mahler_measure_batch([LEHMER], method="fft")


def test_edge_chunked_invalid_chunk_size():
    """`chunk_size < 1` -> ValueError."""
    with pytest.raises(ValueError, match="chunk_size must be"):
        mahler_measure_batch_chunked([LEHMER], chunk_size=0)


def test_edge_padded_rejects_non_2d():
    """`mahler_measure_padded` rejects non-2-D arrays explicitly."""
    with pytest.raises(ValueError, match="2-D"):
        mahler_measure_padded(np.array([1, 2, 3]))


def test_edge_chunked_matches_unchunked():
    """Chunking does not alter output values or order.

    Edge: chunk_size smaller than n forces multiple inner calls; the
    concatenation must reproduce the unchunked batch result exactly.
    """
    polys = [LEHMER, PHI_5, [1, -1, -1], [1, -2], [1, 0, 0, -1]]
    out_full = mahler_measure_batch(polys)
    out_chunked = mahler_measure_batch_chunked(polys, chunk_size=2)
    assert np.allclose(out_full, out_chunked, atol=1e-12)


# ---------------------------------------------------------------------------
# 4. Composition tests (>= 2 required)
# ---------------------------------------------------------------------------

def test_composition_batch_then_sort_matches_sorted_scalars():
    """Sorting batch output reproduces sorting of per-poly scalar output.

    Composition: batch -> np.sort vs [scalar(c) for c] -> np.sort.
    This catches subtle ordering / index-mapping bugs that pass the
    elementwise property test but fail at the consumer end.
    """
    snap = _load_mossinghoff_snapshot()
    polys = [c for c, _ in snap]
    M_batch_sorted = np.sort(mahler_measure_batch(polys))
    M_scalar_sorted = np.sort(np.array([mahler_measure(p) for p in polys]))
    assert np.allclose(M_batch_sorted, M_scalar_sorted, atol=1e-10)


def test_composition_batch_then_filter_below_M_matches_scalar_pipeline():
    """Batch + filter_below_M agrees with the per-poly scalar pipeline.

    Composition: emulate the Charon Lehmer scan two ways --
    (a) compute M via batch, attach into dicts, then filter_below_M;
    (b) compute M via scalar in a Python loop into the dicts, then
        filter_below_M.

    The set of surviving entries (compared by their `id` payload)
    must be identical, and the surviving Mahler measures must match
    to 1e-9.
    """
    try:
        from prometheus_math.research.lehmer import filter_below_M
    except Exception:                                        # pragma: no cover
        pytest.skip("prometheus_math.research.lehmer unavailable")

    snap = _load_mossinghoff_snapshot()
    polys = [c for c, _ in snap]
    M_batch = mahler_measure_batch(polys)
    rows_batch = [
        {"id": i, "mahler_measure": float(M_batch[i])}
        for i in range(len(polys))
    ]
    rows_scalar = [
        {"id": i, "mahler_measure": float(mahler_measure(p))}
        for i, p in enumerate(polys)
    ]

    M_threshold = 1.30
    surv_batch = filter_below_M(rows_batch, M_threshold)
    surv_scalar = filter_below_M(rows_scalar, M_threshold)
    ids_batch = sorted(r["id"] for r in surv_batch)
    ids_scalar = sorted(r["id"] for r in surv_scalar)
    assert ids_batch == ids_scalar
    by_id_batch = {r["id"]: r["mahler_measure"] for r in surv_batch}
    by_id_scalar = {r["id"]: r["mahler_measure"] for r in surv_scalar}
    for i in ids_batch:
        assert abs(by_id_batch[i] - by_id_scalar[i]) < 1e-9


# ---------------------------------------------------------------------------
# Performance smoke test (not gated; informational).
# ---------------------------------------------------------------------------

def test_performance_batch_at_least_as_fast_as_individual_at_scale():
    """At the Charon Lehmer-scan operating point, batch >= individual.

    Not a strict speed assertion — CI hosts vary wildly — but the
    batch path must not be *slower* than the individual loop on a
    realistic 1000-poly degree-8 workload.  If this regresses we
    want to know.
    """
    res = benchmark_mahler_batch([8], 1000, seed=1)
    indiv = res["individual"]["time_total"]
    batch = res["companion_batch"]["time_total"]
    # Allow 20% slack for the random outlier; a real regression will
    # blow this out by 2x or more.
    assert batch <= indiv * 1.2, (
        f"batch ({batch:.4f}s) slower than individual ({indiv:.4f}s) "
        f"on 1000 deg-8 polys; expected speedup, got {indiv/batch:.2f}x"
    )
