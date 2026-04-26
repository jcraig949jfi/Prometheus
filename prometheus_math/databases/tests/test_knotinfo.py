"""Smoke tests for prometheus_math.databases.knotinfo.

These tests load the KnotInfo CSV via the `database_knotinfo` pip
package (preferred) or via direct CSV download. They skip cleanly if
neither is available.

Run directly with `python -m prometheus_math.databases.tests.test_knotinfo`
or under pytest.
"""
from __future__ import annotations

import pytest

from prometheus_math.databases import knotinfo


# ---------------------------------------------------------------------------
# Backend gate
# ---------------------------------------------------------------------------

def _backend_ok() -> bool:
    try:
        return knotinfo.probe(timeout=5.0)
    except Exception:
        return False


_OK = _backend_ok()
_skip_no_backend = pytest.mark.skipif(
    not _OK,
    reason="KnotInfo backend unavailable: install `database_knotinfo` pip "
           "package or ensure network access to knotinfo.math.indiana.edu.",
)


# ---------------------------------------------------------------------------
# Pure-Python tests (no I/O)
# ---------------------------------------------------------------------------

def test_canonical_name_low_crossing_variants():
    """3_1, 3.1, 3a1, K3_1 should all collapse to '3_1'."""
    c = knotinfo._canonical_knot_name
    assert c("3_1") == "3_1"
    assert c("3.1") == "3_1"
    assert c("K3_1") == "3_1"
    assert c("k3.1") == "3_1"


def test_canonical_name_high_crossing_variants():
    """11n34, 11n_34, K11n34 should all collapse to '11n_34'."""
    c = knotinfo._canonical_knot_name
    assert c("11n_34") == "11n_34"
    assert c("11n34") == "11n_34"
    assert c("K11n34") == "11n_34"
    assert c("11n.34") == "11n_34"
    # 11+ crossings without a class letter is ambiguous: reject.
    assert c("11_34") is None


def test_parse_alex_vector_trefoil():
    """Trefoil's '[0, 2, 1, -1, 1]' parses to coefficients [1, -1, 1]."""
    coeffs = knotinfo._parse_alex_vector("[0, 2, 1, -1, 1]")
    assert coeffs == [1, -1, 1]


def test_parse_alex_vector_figure8():
    """Figure-8's '[0, 2, 1, -3, 1]' -> [1, -3, 1]  (i.e. 1 - 3t + t^2)."""
    coeffs = knotinfo._parse_alex_vector("[0, 2, 1, -3, 1]")
    assert coeffs == [1, -3, 1]


def test_parse_yes_no():
    p = knotinfo._parse_yes_no
    assert p("Y") is True
    assert p("yes") is True
    assert p("N") is False
    assert p("no") is False
    assert p("") is None
    assert p(None) is None


# ---------------------------------------------------------------------------
# Live data tests (skip if no backend)
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_lookup_trefoil():
    """3_1 (trefoil): crossing=3, signature=-2, determinant=3, fibered, alt."""
    rec = knotinfo.lookup("3_1")
    assert rec is not None
    assert rec["name"] == "3_1"
    assert rec["crossing_number"] == 3
    assert rec["signature"] == -2
    assert rec["determinant"] == 3
    assert rec["fibered"] is True
    assert rec["alternating"] is True
    assert rec["three_genus"] == 1
    assert rec["genus"] == 1
    # Trefoil is not hyperbolic (it's a torus knot).
    assert rec["hyperbolic"] is False


@_skip_no_backend
def test_lookup_figure_eight():
    """4_1 (figure-8): crossing=4, sigma=0, det=5, hyperbolic w/ vol~2.0299."""
    rec = knotinfo.lookup("4_1")
    assert rec is not None
    assert rec["crossing_number"] == 4
    assert rec["signature"] == 0
    assert rec["determinant"] == 5
    assert rec["hyperbolic"] is True
    assert rec["hyperbolic_volume"] is not None
    assert 2.02 < rec["hyperbolic_volume"] < 2.04


@_skip_no_backend
def test_lookup_5_2():
    """5_2: crossing=5, signature=-2, determinant=7, hyperbolic."""
    rec = knotinfo.lookup("5_2")
    assert rec is not None
    assert rec["crossing_number"] == 5
    assert rec["signature"] == -2
    assert rec["determinant"] == 7


@_skip_no_backend
def test_lookup_name_aliases():
    """Variant names ('3.1', 'K3_1') resolve to the same knot."""
    a = knotinfo.lookup("3_1")
    b = knotinfo.lookup("3.1")
    c = knotinfo.lookup("K3_1")
    assert a is not None and b is not None and c is not None
    assert a["name"] == b["name"] == c["name"] == "3_1"


@_skip_no_backend
def test_lookup_high_crossing():
    """11n_34 should resolve via the 11-crossing class-letter convention."""
    rec_a = knotinfo.lookup("11n_34")
    rec_b = knotinfo.lookup("K11n34")
    assert rec_a is not None
    assert rec_b is not None
    assert rec_a["name"] == rec_b["name"] == "11n_34"
    assert rec_a["crossing_number"] == 11


@_skip_no_backend
def test_alexander_figure_eight():
    """Alexander polynomial of 4_1 is 1 - 3t + t^2 (or its negative)."""
    coeffs = knotinfo.alexander("4_1")
    assert coeffs is not None
    assert coeffs == [1, -3, 1] or coeffs == [-1, 3, -1]


@_skip_no_backend
def test_signature_trefoil():
    """signature(3_1) == -2."""
    assert knotinfo.signature("3_1") == -2


@_skip_no_backend
def test_jones_trefoil_nonempty():
    """jones(3_1) returns a non-empty Laurent-polynomial string."""
    j = knotinfo.jones("3_1")
    assert isinstance(j, str)
    assert len(j) > 0
    # Should mention 't' as a variable
    assert "t" in j


@_skip_no_backend
def test_is_l_space_trefoil():
    """The trefoil is an L-space knot."""
    assert knotinfo.is_l_space("3_1") is True


@_skip_no_backend
def test_is_l_space_figure_eight():
    """4_1 is NOT an L-space knot."""
    assert knotinfo.is_l_space("4_1") is False


@_skip_no_backend
def test_filter_crossing_number_4():
    """There is exactly one prime knot with 4 crossings: 4_1."""
    hits = knotinfo.filter(crossing_number=4)
    assert len(hits) == 1
    assert hits[0]["name"] == "4_1"


@_skip_no_backend
def test_all_knots_up_to_4():
    """Knots with crossing<=4: just 3_1 and 4_1 (we drop the unknot 0_1
    if it's there or keep it if it's there — accept either, but 3_1 and 4_1
    must be present)."""
    knots = knotinfo.all_knots(crossing_max=4)
    names = {k["name"] for k in knots}
    assert "3_1" in names
    assert "4_1" in names
    # Total should be small (2 or 3 — depends on whether unknot 0_1 is listed).
    assert len(knots) <= 3


@_skip_no_backend
def test_list_l_space_knots_includes_trefoil():
    """The trefoil must appear in the L-space knot list."""
    names = knotinfo.list_l_space_knots()
    assert "3_1" in names
    # All L-space knots should be a small set in the 13-crossing census.
    assert 1 <= len(names) <= 50


@_skip_no_backend
def test_lookup_unknown_returns_none():
    """A name with no possible match in the census returns None."""
    assert knotinfo.lookup("99x_999") is None
    assert knotinfo.lookup("garbage") is None


@_skip_no_backend
def test_cache_info_has_data():
    """After any lookup, cache_info() reports loaded rows."""
    knotinfo.lookup("3_1")
    info = knotinfo.cache_info()
    assert info["knots_loaded"] >= 100
    assert info["source"] in ("database_knotinfo", "csv-network")


# ---------------------------------------------------------------------------
# Self-runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = skipped = failed = 0
    failures: list[tuple[str, str]] = []
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  OK   {name}")
        except pytest.skip.Exception as e:  # type: ignore[attr-defined]
            skipped += 1
            print(f"  SKIP {name}: {e}")
        except Exception as e:
            failed += 1
            failures.append((name, traceback.format_exc()))
            print(f"  FAIL {name}: {type(e).__name__}: {e}")
    total = len(tests)
    print(f"\n{passed}/{total} OK ({skipped} skipped, {failed} failed)")
    if failed:
        for n, tb in failures:
            print(f"\n--- {n} ---\n{tb}")
        raise SystemExit(1)
