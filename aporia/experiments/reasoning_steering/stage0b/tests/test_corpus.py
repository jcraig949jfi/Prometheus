"""TDD tests for the in-band corpus loader (Stage 0b relational, v0.3)."""
import pytest

from aporia.experiments.reasoning_steering.stage0b.corpus import (
    load_in_band_states,
    InBandState,
    BAND_LOW,
    BAND_HIGH,
)

LEHMER = (1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1)


# 1. AUTHORITY
def test_authority_in_band_slice_contains_lehmer():
    """The in-band slice of MAHLER_TABLE contains Lehmer's polynomial (M~1.176, the
    canonical in-band state) and every member is strictly in (1.001, 1.18).
    Reference: MAHLER_TABLE (Lehmer 1933 entry)."""
    states = load_in_band_states()
    assert all(isinstance(s, InBandState) for s in states)
    assert all(BAND_LOW < s.mahler_measure < BAND_HIGH for s in states)
    assert any(s.coeffs == LEHMER for s in states)
    assert len(states) >= 8          # enough for a non-trivial comparison graph


# 2. PROPERTY
def test_property_deterministic_and_sorted():
    a = load_in_band_states()
    b = load_in_band_states()
    assert [s.coeffs for s in a] == [s.coeffs for s in b]            # deterministic
    assert a == sorted(a, key=lambda s: (s.mahler_measure, s.coeffs))  # sorted order
    for s in a:
        assert isinstance(s.coeffs, tuple) and len(s.coeffs) >= 2


# 3. EDGE CASES
def test_edge_cases():
    """Edges: empty band -> []; inverted band -> ValueError."""
    assert load_in_band_states(m_low=1.50, m_high=1.50001) == []
    with pytest.raises(ValueError):
        load_in_band_states(m_low=1.18, m_high=1.001)


# 4. COMPOSITION — count matches an independent re-filter of MAHLER_TABLE.
def test_composition_count_matches_independent_filter():
    from prometheus_math.databases import mahler as mdb
    indep = sum(
        1 for e in mdb.MAHLER_TABLE
        if e.get("mahler_measure") is not None and e.get("coeffs") is not None
        and BAND_LOW < float(e["mahler_measure"]) < BAND_HIGH
    )
    assert len(load_in_band_states()) == indep
