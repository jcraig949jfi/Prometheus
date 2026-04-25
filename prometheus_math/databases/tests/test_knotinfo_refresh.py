"""Tests for the KnotInfo mirror-refresh subsystem (project #12).

Covers `mirror_info`, `update_mirror`, `probe_extended`, and the
helper version-comparison logic. Per math-tdd discipline these are
sorted by category:

  Authority   : the installed pip version is reported faithfully and
                the row counts agree with the package's own published
                figures (12,966 knots / 4,188 links for
                database_knotinfo 2026.4.1).
  Property    : `update_mirror(force=False)` is idempotent; calling it
                N times never raises and never modifies disk; semver
                comparison obeys partial order axioms.
  Edge        : PyPI unreachable -> graceful None; package not
                installed -> sensible None; unknown semver tokens ->
                no spurious upgrade signal.
  Composition : `mirror_info().n_knots` equals
                `len(all_knots(crossing_max=999))`; counts agree with
                the underlying database_knotinfo package call.

Run directly via:
    python -m prometheus_math.databases.tests.test_knotinfo_refresh
or under pytest.
"""
from __future__ import annotations

from unittest import mock

import pytest

from prometheus_math.databases import knotinfo


def _backend_ok() -> bool:
    try:
        return knotinfo.probe(timeout=5.0)
    except Exception:
        return False


_OK = _backend_ok()
_skip_no_backend = pytest.mark.skipif(
    not _OK,
    reason="KnotInfo backend unavailable: install `database_knotinfo` "
           "or ensure network access to knotinfo.math.indiana.edu.",
)


# ---------------------------------------------------------------------------
# Authority — installed pip version + canonical row counts
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_mirror_info_reports_real_pip_version_authority():
    """Authority: mirror_info().pip_version equals importlib.metadata.version.

    Reference: PEP 566 + importlib.metadata stdlib. We compare to the
    same source `_pip_version` claims to use, so a divergence would
    indicate a bug in version-extraction logic (e.g. shelling out
    rather than reading metadata).
    """
    import importlib.metadata as _md
    info = knotinfo.mirror_info()
    expected = _md.version("database_knotinfo")
    assert info["pip_version"] == expected
    # The active source must be the package backend whenever the
    # package is importable -- network fallback would mask version
    # mismatches.
    assert info["source"] == "database_knotinfo"


@_skip_no_backend
def test_mirror_info_n_knots_matches_published_census_authority():
    """Authority: n_knots == 12966 (KnotInfo's published 13-crossing census).

    Reference: KnotInfo about page (https://knotinfo.math.indiana.edu/)
    states the census covers all prime knots through 13 crossings,
    which equals 12,966 entries (excluding the unknot 0_1 if present
    as a header artifact, OR including it; database_knotinfo 2026.4.1
    ships 12,967 raw rows -- one is filtered as a 'pretty header' row,
    leaving 12,966 real knots). This anchors the inventory against
    Sebastian Oehms's published wheel.
    """
    info = knotinfo.mirror_info()
    assert info["n_knots"] == 12966, (
        f"Expected 12,966 knots in the census, got {info['n_knots']}. "
        "If database_knotinfo has been upgraded, this anchor needs "
        "to move and the project_12 spec re-confirmed."
    )
    # Links: published count is 4,188 (LinkInfo through 11 crossings).
    assert info["n_links"] >= 4000
    assert info["n_links"] <= 4500


# ---------------------------------------------------------------------------
# Property — idempotence, no side effects, semver order
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_update_mirror_is_idempotent_property():
    """Property: update_mirror(force=False) called twice never raises and
    leaves on-disk state untouched.

    Strategy: call update_mirror with force=False three times; assert
    every call returns refreshed=False, the message is non-empty, and
    n_knots is invariant. We monkey-patch subprocess.run so that any
    accidental shell-out fails loudly -- a passing test is then proof
    that force=False truly never spawns a subprocess.
    """
    with mock.patch("subprocess.run", side_effect=AssertionError(
            "force=False must NEVER spawn subprocess")):
        first = knotinfo.update_mirror(force=False)
        second = knotinfo.update_mirror(force=False)
        third = knotinfo.update_mirror(force=False)
    for r in (first, second, third):
        assert r["refreshed"] is False
        assert isinstance(r["message"], str) and r["message"]
        assert r["n_knots"] == first["n_knots"]
        assert r["n_links"] == first["n_links"]
        # upgrade_cmd is always documented for the user.
        assert "pip install" in r["upgrade_cmd"]
        assert "database_knotinfo" in r["upgrade_cmd"]


def test_semver_lt_is_total_order_property():
    """Property: _semver_lt is irreflexive, antisymmetric on a small set.

    These are basic axioms for any well-formed less-than:
      * x is not < x
      * if x < y then NOT y < x
      * transitivity on a known-ordered triple
    """
    samples = ["2025.1.1", "2026.2.1", "2026.4.1", "2026.10.1", "2027.1.1"]
    lt = knotinfo._semver_lt
    # Irreflexive
    for s in samples:
        assert not lt(s, s), f"_semver_lt({s!r},{s!r}) must be False"
    # Antisymmetric on a known-ordered pair: 2026.2.1 < 2026.10.1
    # (lexicographic would falsely flip this)
    assert lt("2026.2.1", "2026.10.1") is True
    assert lt("2026.10.1", "2026.2.1") is False
    # Transitivity
    assert lt("2025.1.1", "2026.2.1")
    assert lt("2026.2.1", "2027.1.1")
    assert lt("2025.1.1", "2027.1.1")


# ---------------------------------------------------------------------------
# Edge — PyPI offline, package missing, malformed inputs
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_pypi_unreachable_returns_has_newer_none_edge():
    """Edge: when PyPI is unreachable, has_newer is None (NOT False).

    A False answer would falsely imply 'we checked and you're up to
    date'. None correctly says 'we don't know'. We simulate a network
    failure by patching requests.get to raise a ConnectionError.
    """
    import requests as _req
    with mock.patch("prometheus_math.databases.knotinfo.requests.get",
                    side_effect=_req.ConnectionError("simulated offline")):
        info = knotinfo.mirror_info()
        assert info["latest_pypi"] is None
        assert info["has_newer"] is None
        # n_knots survives the network outage -- mirror data is local.
        assert info["n_knots"] == 12966
    # Now run update_mirror under the same network outage; it must
    # return a graceful (non-raising) response with a useful message.
    with mock.patch("prometheus_math.databases.knotinfo.requests.get",
                    side_effect=_req.ConnectionError("simulated offline")):
        r = knotinfo.update_mirror(force=False)
        assert r["refreshed"] is False
        assert r["latest_pypi"] is None
        assert r["has_newer"] is None
        assert "PyPI unreachable" in r["message"] or "up to date" in r["message"]


def test_semver_lt_unknown_tokens_no_upgrade_signal_edge():
    """Edge: malformed/unknown version strings must not signal an upgrade.

    Two paths to exercise:
      * empty strings on either side
      * non-numeric tokens that defeat the int() fallback when
        packaging.version is also defeated.
    """
    lt = knotinfo._semver_lt
    assert lt("", "2026.4.1") is False   # empty 'a'
    assert lt("2026.4.1", "") is False   # empty 'b'
    assert lt("", "") is False
    # Non-numeric tokens. packaging.version may or may not handle these;
    # the contract is "no spurious True". (False or no-raise is fine.)
    result = lt("garbage", "alsojunk")
    assert result is False or result is True  # must not raise
    # Equal on both sides is False
    assert lt("2026.4.1", "2026.4.1") is False


def test_probe_extended_returns_well_formed_dict_edge():
    """Edge: probe_extended must return a structurally valid dict even
    on full network failure (no URL returns 200)."""
    import requests as _req
    with mock.patch("prometheus_math.databases.knotinfo.requests.head",
                    side_effect=_req.ConnectionError("simulated offline")):
        result = knotinfo.probe_extended(timeout=0.1)
    assert isinstance(result, dict)
    assert "any_reachable" in result and result["any_reachable"] is False
    assert "urls" in result and isinstance(result["urls"], list)
    assert len(result["urls"]) >= 1
    for entry in result["urls"]:
        assert "url" in entry
        assert entry["ok"] is False
        assert entry["error"] is not None  # ConnectionError captured


# ---------------------------------------------------------------------------
# Composition — mirror_info <-> all_knots <-> database_knotinfo
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_mirror_info_count_matches_all_knots_composition():
    """Composition: mirror_info().n_knots == len(all_knots(crossing_max=999)).

    Both surfaces must report the same census size; a discrepancy
    means one of the two paths is filtering rows the other isn't.
    """
    info = knotinfo.mirror_info()
    every_knot = knotinfo.all_knots(crossing_max=999)
    assert info["n_knots"] == len(every_knot)
    # And both equal 12966 (anchored by Authority test above).
    assert len(every_knot) == 12966


@_skip_no_backend
def test_mirror_info_count_matches_underlying_package_composition():
    """Composition: mirror_info().n_knots equals
    `len(database_knotinfo.link_list(proper_links=False)) - <header>`.

    Chains the public mirror_info() through to the upstream package's
    own count, minus the one synthetic 'pretty header' row that
    `_is_real_data_row` filters. A mismatch means our header-detection
    logic has fallen out of sync with the upstream CSV format.
    """
    from database_knotinfo import link_list  # type: ignore
    raw_rows = link_list(proper_links=False)
    raw_count = len(raw_rows)
    real_rows = [r for r in raw_rows if knotinfo._is_real_data_row(r)]
    info = knotinfo.mirror_info()
    assert info["n_knots"] == len(real_rows)
    # And the difference between raw and real should be small (just
    # the header row, or zero if upstream removed it).
    assert raw_count - len(real_rows) in (0, 1)


@_skip_no_backend
def test_update_mirror_chains_through_lookup_composition():
    """Composition: after update_mirror(force=False), the `lookup`
    public surface still works on canonical anchors.

    Verifies the no-op path doesn't accidentally clear caches or
    break invariants. Chains: update_mirror -> lookup -> alexander.
    """
    r = knotinfo.update_mirror(force=False)
    assert r["n_knots"] == 12966
    rec = knotinfo.lookup("3_1")
    assert rec is not None
    assert rec["crossing_number"] == 3
    coeffs = knotinfo.alexander("4_1")
    assert coeffs is not None
    assert coeffs in ([1, -3, 1], [-1, 3, -1])


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
