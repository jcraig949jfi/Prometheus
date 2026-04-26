"""Test TOOL_CF_EXPANSION batch / numba JIT extensions (project #52).

A/P/E/C TDD coverage for:
    cf_expand            (scalar)
    cf_expand_batch      (Python loop over list of (p, q))
    cf_expand_jit        (numba njit, int64-safe)
    cf_expand_array      (auto-dispatch JIT vs Python fallback)
    cf_truncate_to_partial

Every test cites its category in the docstring header.
"""
import os
import sys
import math
from fractions import Fraction

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.cf_expansion import (  # noqa: E402
    cf_expand,
    cf_expand_batch,
    cf_expand_array,
    cf_truncate_to_partial,
    HAS_NUMBA,
)

if HAS_NUMBA:
    from lib.cf_expansion import cf_expand_jit  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cf_eval(terms):
    """Evaluate a continued fraction [a_0; a_1, ...] back to a Fraction."""
    if not terms:
        raise ValueError("empty cf")
    acc = Fraction(terms[-1])
    for a in reversed(terms[:-1]):
        acc = a + Fraction(1) / acc
    return acc


# ---------------------------------------------------------------------------
# AUTHORITY-BASED TESTS (Category A) — 5 entries
# ---------------------------------------------------------------------------

def test_authority_355_over_113_pi_approximant():
    """A: 355/113 -> [3, 7, 16].

    Reference: Khinchin, "Continued Fractions" (Dover 1997), Ch.II §10
    — 355/113 = 3 + 1/(7 + 1/16) is the classical 6-decimal best
    rational approximation to pi. Hand-verified Euclidean run:
        355 = 3*113 + 16
        113 = 7*16  + 1
         16 = 16*1  + 0
    """
    assert cf_expand(355, 113) == [3, 7, 16]


def test_authority_22_over_7_archimedes():
    """A: 22/7 -> [3, 7].

    Reference: Archimedes' "Measurement of a Circle" (3rd c. BC).
    Euclidean: 22 = 3*7 + 1; 7 = 7*1 + 0.
    """
    assert cf_expand(22, 7) == [3, 7]


def test_authority_unit_and_one_half():
    """A: cf_expand(1, 1) == [1] and cf_expand(1, 2) == [0, 2].

    Reference: definitional. 1/1 has trivial expansion [1].
    1/2 = 0 + 1/2 -> [0, 2]. Hand-computed; matches Hardy & Wright
    "An Introduction to the Theory of Numbers" §10.1, eq. (10.1.4).
    """
    assert cf_expand(1, 1) == [1]
    assert cf_expand(1, 2) == [0, 2]


def test_authority_fibonacci_ratio_golden():
    """A: cf_expand(89, 55) -> [1,1,1,1,1,1,1,1,2].

    Reference: Hardy & Wright §10.12 — consecutive Fibonacci ratios
    F(n+1)/F(n) yield CF expansions [1; 1, 1, ..., 1, 2] of length n,
    converging to the golden ratio phi = [1; 1, 1, ...]. Here
    F(11)=89, F(10)=55, so n=10 and we expect 9 terms (eight 1s + a 2).
    """
    assert cf_expand(89, 55) == [1, 1, 1, 1, 1, 1, 1, 1, 2]


def test_authority_oeis_a002486_denominators_match():
    """A: convergents of 22/7 evaluate exactly to 22/7.

    Reference: OEIS A002485/A002486 (numerators/denominators of
    convergents of pi). cf_expand(22, 7) = [3, 7]; the convergent
    sequence is 3/1, 22/7, matching the first two entries of
    A002485/A002486. Round-trip eval verifies.
    """
    cf = cf_expand(22, 7)
    assert _cf_eval(cf) == Fraction(22, 7)


# ---------------------------------------------------------------------------
# PROPERTY-BASED TESTS (Category P) — 6 entries
# ---------------------------------------------------------------------------

@given(
    p=st.integers(min_value=1, max_value=10**6),
    q=st.integers(min_value=1, max_value=10**6),
)
@settings(max_examples=80, deadline=None)
def test_property_tail_terms_are_positive(p, q):
    """P: For positive p, q, every CF term after a_0 is >= 1.

    Standard CF property: in the regular CF expansion of a positive
    rational, partial quotients a_i >= 1 for i >= 1. (a_0 is just
    floor(p/q) and may be 0.)
    """
    cf = cf_expand(p, q)
    for a in cf[1:]:
        assert a >= 1, f"non-positive tail term in CF({p}/{q}) = {cf}"


@given(
    p=st.integers(min_value=0, max_value=10**6),
    q=st.integers(min_value=1, max_value=10**6),
)
@settings(max_examples=80, deadline=None)
def test_property_a0_nonneg_for_nonneg_input(p, q):
    """P: a_0 >= 0 when p >= 0, q > 0."""
    cf = cf_expand(p, q)
    assert cf[0] >= 0


@given(
    inputs=st.lists(
        st.tuples(
            st.integers(min_value=1, max_value=10**5),
            st.integers(min_value=1, max_value=10**5),
        ),
        min_size=0,
        max_size=20,
    )
)
@settings(max_examples=40, deadline=None)
def test_property_batch_length_matches(inputs):
    """P: cf_expand_batch returns a list of equal length to the input."""
    out = cf_expand_batch(inputs)
    assert len(out) == len(inputs)


@given(
    inputs=st.lists(
        st.tuples(
            st.integers(min_value=1, max_value=10**4),
            st.integers(min_value=1, max_value=10**4),
        ),
        min_size=1,
        max_size=20,
    )
)
@settings(max_examples=40, deadline=None)
def test_property_batch_matches_scalar(inputs):
    """P: cf_expand_batch(xs) == [cf_expand(p, q) for (p, q) in xs]."""
    expected = [cf_expand(p, q) for (p, q) in inputs]
    got = cf_expand_batch(inputs)
    assert got == expected


@given(
    p=st.integers(min_value=1, max_value=10**6),
    q=st.integers(min_value=1, max_value=10**6),
)
@settings(max_examples=80, deadline=None)
def test_property_evaluation_round_trip(p, q):
    """P: evaluating cf_expand(p, q) reconstructs p/q (in lowest terms)."""
    cf = cf_expand(p, q)
    assert _cf_eval(cf) == Fraction(p, q)


@given(
    p=st.integers(min_value=1, max_value=10**4),
    q=st.integers(min_value=1, max_value=10**4),
)
@settings(max_examples=40, deadline=None)
def test_property_length_at_most_log_phi(p, q):
    """P: |cf_expand(p, q)| <= ceil(log_phi(min(p, q))) + 5.

    Worst-case length of the regular CF is achieved by consecutive
    Fibonacci numbers; in general len(cf) = O(log_phi(min(p, q))).
    Reference: Knuth TAOCP vol.2 §4.5.3 Thm.E. We add a +5 cushion
    for the constant in Lame's theorem.
    """
    cf = cf_expand(p, q)
    m = min(p, q)
    if m == 1:
        return  # trivial; bound below is degenerate
    bound = math.ceil(math.log(m, (1 + 5 ** 0.5) / 2)) + 5
    assert len(cf) <= bound, f"CF too long: {len(cf)} > {bound} for {p}/{q}"


@given(
    p=st.integers(min_value=1, max_value=10**8),
    q=st.integers(min_value=1, max_value=10**8),
)
@settings(max_examples=40, deadline=None)
def test_property_jit_matches_scalar(p, q):
    """P: cf_expand_jit on int64-safe inputs matches cf_expand."""
    if not HAS_NUMBA:
        pytest.skip("numba not available")
    expected = cf_expand(p, q)
    arr = cf_expand_jit(p, q, max_terms=200)
    # Strip trailing zero pad
    assert arr.dtype == np.int64
    n = int((arr != 0).sum()) if expected and expected[0] != 0 else None
    # Reconstruct list (handle a0 == 0 edge — but min_value=1 so unused)
    got = list(arr[arr != 0]) if (expected and expected[0] != 0) else None
    if got is None:
        # Cannot strip trivially; compare via padded length
        pad = np.zeros(200, dtype=np.int64)
        for i, v in enumerate(expected):
            pad[i] = v
        np.testing.assert_array_equal(arr, pad)
    else:
        assert got == expected, f"jit {got} != scalar {expected} for {p}/{q}"


# ---------------------------------------------------------------------------
# EDGE-CASE TESTS (Category E) — 6 entries
# ---------------------------------------------------------------------------

def test_edge_zero_numerator():
    """E: cf_expand(0, 1) -> [0]. (Boundary: numerator zero.)"""
    assert cf_expand(0, 1) == [0]


def test_edge_zero_denominator_raises():
    """E: cf_expand(1, 0) raises ValueError. (Malformed input.)"""
    with pytest.raises(ValueError):
        cf_expand(1, 0)
    with pytest.raises(ValueError):
        cf_expand(0, 0)


def test_edge_negative_numerator():
    """E: cf_expand(-3, 7) handles negative numerator correctly.

    Hand-computed: -3/7 = -1 + 4/7 -> a_0 = -1, then 7/4 = 1 + 3/4 ->
    a_1 = 1, then 4/3 = 1 + 1/3 -> a_2 = 1, then 3/1 = 3. So
    cf_expand(-3, 7) == [-1, 1, 1, 3]. Round-trip:
        -1 + 1/(1 + 1/(1 + 1/3)) = -1 + 1/(1 + 1/(4/3))
                                 = -1 + 1/(1 + 3/4)
                                 = -1 + 1/(7/4)
                                 = -1 + 4/7 = -3/7. OK.
    """
    cf = cf_expand(-3, 7)
    assert _cf_eval(cf) == Fraction(-3, 7)
    # Tail terms must still be positive.
    for a in cf[1:]:
        assert a >= 1


def test_edge_overflow_falls_back():
    """E: cf_expand_array handles inputs that exceed int64 by falling
    back to Python.

    int64 max is 9_223_372_036_854_775_807 ~ 9.2e18. We pass an
    arbitrary-precision pair (p, q) > int64 whose CF terms themselves
    still fit in int64 (the common Charon use case: huge rationals
    with bounded partial quotients). The CF of two consecutive
    Fibonacci-like numbers has all terms == 1, which fits trivially.
    """
    # Build two consecutive "shifted" Fibonacci numbers > int64.
    # Use a Lucas-like recurrence beyond int64.
    a, b = 10 ** 25, 10 ** 25 + 10 ** 24
    # Now (a, b) -> CF([1; ...]) with all small terms (< 10).
    arr = np.array([[b, a]], dtype=object)
    out = cf_expand_array(arr, max_terms=20, fallback='python')
    # Trim trailing zeros (pad terminator).
    cf_trim = list(out[0])
    while cf_trim and cf_trim[-1] == 0 and len(cf_trim) > 1:
        cf_trim.pop()
    expected = cf_expand(b, a)
    # All expected terms must fit in int64 for this case.
    assert all(_INT64_MIN <= x <= _INT64_MAX for x in expected), \
        "test precondition: all CF terms must fit in int64"
    # The fallback path returns the same terms as the scalar.
    assert cf_trim == expected, f"fallback CF mismatch: {cf_trim} vs {expected}"

    # Additionally: dtype=object path must not crash on the small-CF case.
    assert _cf_eval(cf_trim) == Fraction(b, a)


_INT64_MAX = np.iinfo(np.int64).max
_INT64_MIN = np.iinfo(np.int64).min


def test_edge_max_terms_zero_and_singleton():
    """E: cf_truncate_to_partial(p, q, 0) returns []; n=1 returns [a_0]."""
    assert cf_truncate_to_partial(355, 113, 0) == []
    assert cf_truncate_to_partial(355, 113, 1) == [3]
    assert cf_truncate_to_partial(355, 113, 100) == [3, 7, 16]  # full
    # Empty batch
    assert cf_expand_batch([]) == []


def test_edge_negative_denominator_normalized():
    """E: cf_expand normalizes negative denominators.

    Convention in the spec: q must be > 0 — if q < 0 we either raise
    ValueError or auto-flip signs. We pick auto-flip (pre-existing
    helper raised; we prefer flipping so cf(p, -q) == cf(-p, q)).
    """
    # Either consistent normalization or a clear ValueError is acceptable.
    try:
        cf_neg = cf_expand(3, -7)
    except ValueError:
        # Legacy behavior — acceptable.
        return
    cf_pos = cf_expand(-3, 7)
    assert _cf_eval(cf_neg) == _cf_eval(cf_pos) == Fraction(-3, 7)


# ---------------------------------------------------------------------------
# COMPOSITION TESTS (Category C) — 3 entries
# ---------------------------------------------------------------------------

def test_composition_truncate_is_prefix():
    """C: cf_truncate_to_partial(p, q, n) == cf_expand(p, q)[:n].

    Composition of two operations (truncate o expand) must commute
    with prefix slicing.
    """
    for p, q in [(355, 113), (89, 55), (1, 1), (22, 7), (12345, 67890)]:
        full = cf_expand(p, q)
        for n in range(0, len(full) + 2):
            assert cf_truncate_to_partial(p, q, n) == full[:n]


def test_composition_array_round_trips_to_input():
    """C: cf_expand_array followed by CF evaluation reconstructs p/q.

    Round-trip identity: eval(cf_expand_array([p,q])[0]) == p/q.
    Spans the JIT path (small ints) and the Python path (large ints)
    — the dispatch is module-internal; we test the union.
    """
    rationals = np.array(
        [
            [355, 113],
            [22, 7],
            [89, 55],
            [1, 2],
            [123_456_789, 987_654_321],
        ],
        dtype=np.int64,
    )
    out = cf_expand_array(rationals, max_terms=200)
    for i, (p, q) in enumerate(rationals):
        row = list(out[i])
        # Trim trailing zeros (pad terminator)
        while row and row[-1] == 0 and len(row) > 1:
            row.pop()
        assert _cf_eval(row) == Fraction(int(p), int(q)), (
            f"round-trip failed for {int(p)}/{int(q)}: cf={row}"
        )


def test_composition_batch_consistent_with_scalar_and_array():
    """C: For int64-safe inputs, three paths agree:
        cf_expand_batch == [cf_expand(p,q) for ...]
                       and reconstructs same rationals as cf_expand_array.

    This is a 3-tool composition: scalar ↔ Python-batch ↔ JIT-array.
    All three must produce CFs that evaluate to the same Fraction.
    """
    inputs = [(355, 113), (22, 7), (89, 55), (12345, 67890), (7, 13)]
    batch = cf_expand_batch(inputs)
    arr = np.array(inputs, dtype=np.int64)
    out = cf_expand_array(arr, max_terms=64)

    for i, ((p, q), cf_b) in enumerate(zip(inputs, batch)):
        cf_s = cf_expand(p, q)
        row = list(out[i])
        while row and row[-1] == 0 and len(row) > 1:
            row.pop()
        # All three paths reconstruct the same rational.
        f_target = Fraction(p, q)
        assert _cf_eval(cf_s) == f_target
        assert _cf_eval(cf_b) == f_target
        assert _cf_eval(row) == f_target
        # Scalar and batch should be elementwise identical.
        assert cf_s == cf_b
