"""Smoke tests for prometheus_math.databases.mahler.

Covers the embedded Mossinghoff snapshot:

* ``test_lehmer_witness`` -- the deg-10 Lehmer entry is present and
  reports M near 1.17628.
* ``test_smallest_known_by_degree`` -- known entries at degrees 8, 10,
  12 are returned in ascending Mahler order.
* ``test_lookup_polynomial`` -- Lehmer's coefficients round-trip.
* ``test_all_below_smyth`` -- entries with M < Smyth's bound are flagged
  Salem (or are the Lehmer witness).
* ``test_M_cross_check`` -- every embedded entry's stored M matches a
  fresh ``mahler_measure(coeffs)`` recomputation to 1e-6.
* ``test_x_flip_invariance`` -- looking up the x -> -x reflected
  coefficients still finds the original entry.
* ``test_probe`` -- always True (embedded data, no network).
* ``test_degree_minima_keys`` -- minima dict has expected degrees.
* ``test_smyth_extremal_M`` -- Smyth's polynomial reports M near 1.32472.
* ``test_lookup_by_M`` -- looking up by M near Lehmer's constant finds
  the Lehmer witness.

Run directly with ``pytest`` or
``python -m prometheus_math.databases.tests.test_mahler``.
"""

from __future__ import annotations

import pytest

from prometheus_math.databases import mahler


# ---------------------------------------------------------------------------
# Backend gate (always True for embedded snapshots, but still expressed
# so the test file pattern matches the other database wrappers).
# ---------------------------------------------------------------------------

def _backend_ok() -> bool:
    try:
        return mahler.probe(timeout=1.0)
    except Exception:
        return False


_OK = _backend_ok()
_skip_no_backend = pytest.mark.skipif(
    not _OK,
    reason="Mossinghoff embedded snapshot unavailable (this should never happen).",
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_lehmer_witness():
    """Lehmer's polynomial is degree 10 with M ~ 1.17628."""
    e = mahler.lehmer_witness()
    assert e["degree"] == 10
    assert abs(e["mahler_measure"] - 1.176280818259918) < 1e-9
    assert e["lehmer_witness"] is True
    assert e["salem_class"] is True
    # Coefficients should be the canonical Lehmer ascending list.
    assert e["coeffs"] == [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]


@_skip_no_backend
def test_smallest_known_by_degree():
    """Each of degrees 8, 10, 12 must have at least one catalog entry,
    sorted ascending by Mahler measure."""
    for d in (8, 10, 12):
        rows = mahler.smallest_known(degree=d, limit=10)
        assert len(rows) >= 1, f"no entries at degree {d}"
        # Ascending order.
        for a, b in zip(rows, rows[1:]):
            assert a["mahler_measure"] <= b["mahler_measure"]
        # All filtered to the requested degree.
        assert all(r["degree"] == d for r in rows)
    # Smallest at degree 10 should be Lehmer's polynomial.
    top10 = mahler.smallest_known(degree=10, limit=1)
    assert top10[0]["lehmer_witness"] is True


@_skip_no_backend
def test_lookup_polynomial():
    """Looking up Lehmer's coefficients finds Lehmer's polynomial."""
    coeffs = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    e = mahler.lookup_polynomial(coeffs)
    assert e is not None
    assert e["lehmer_witness"] is True
    # And a clearly bogus polynomial returns None.
    assert mahler.lookup_polynomial([1, 0, 0, 0, 0, 0, 99]) is None


@_skip_no_backend
def test_all_below_smyth():
    """Every entry strictly below Smyth's constant must be Salem-class
    (the Smyth bound is the infimum for non-reciprocal polynomials)."""
    rows = mahler.all_below(mahler.SMYTH_CONSTANT)
    assert len(rows) >= 3, "expected several catalog entries below Smyth"
    for r in rows:
        # Pure cyclotomics with M = 1 are below Smyth but are not Salem
        # (no off-circle roots at all).  Allow them through.
        if r["mahler_measure"] <= 1.0 + 1e-9:
            continue
        assert r["salem_class"] is True, (
            f"entry below Smyth must be Salem-class: {r['name']}"
        )


@_skip_no_backend
def test_M_cross_check():
    """Stored M must match a fresh recomputation to 1e-6 for every
    embedded entry.  This is the strongest sanity test on the snapshot."""
    from techne.lib.mahler_measure import mahler_measure
    table = mahler.smallest_known(limit=1000)
    assert len(table) >= 15
    for e in table:
        desc = list(reversed(e["coeffs"]))
        M_fresh = mahler_measure(desc)
        assert abs(M_fresh - e["mahler_measure"]) < 1e-6, (
            f"stored M does not match recomputation for {e['name']}: "
            f"stored={e['mahler_measure']}, computed={M_fresh}"
        )


@_skip_no_backend
def test_x_flip_invariance():
    """M(p(x)) = M(p(-x)).  Looking up the sign-flipped coefficients
    should find the same entry."""
    # Lehmer's: ascending = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    # x -> -x flips every odd-index coefficient:
    flipped = [1, -1, 0, 1, -1, 1, -1, 1, 0, -1, 1]
    e = mahler.lookup_polynomial(flipped)
    assert e is not None
    assert e["lehmer_witness"] is True


@_skip_no_backend
def test_probe():
    """Probe is unconditionally True for the embedded snapshot."""
    assert mahler.probe() is True
    # Argument is accepted for API uniformity.
    assert mahler.probe(timeout=0.001) is True


@_skip_no_backend
def test_degree_minima_keys():
    """degree_minima() must include at least Lehmer's degree (10),
    Smyth's degree (3), and the golden-ratio degree (2)."""
    minima = mahler.degree_minima()
    assert 10 in minima
    assert minima[10]["lehmer_witness"] is True
    assert 3 in minima
    assert minima[3]["is_smyth_extremal"] is True
    assert 2 in minima  # golden ratio


@_skip_no_backend
def test_smyth_extremal_M():
    """Smyth-extremal entries report M = SMYTH_CONSTANT to high
    precision."""
    extremals = mahler.smyth_extremal()
    assert len(extremals) >= 1
    for e in extremals:
        assert e["is_smyth_extremal"] is True
        assert abs(e["mahler_measure"] - mahler.SMYTH_CONSTANT) < 1e-9


@_skip_no_backend
def test_lookup_by_M():
    """Looking up M near Lehmer's constant finds the Lehmer witness
    among the matches."""
    rows = mahler.lookup_by_M(mahler.LEHMER_CONSTANT, tol=1e-6)
    assert len(rows) >= 1
    assert any(r.get("lehmer_witness") for r in rows)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
