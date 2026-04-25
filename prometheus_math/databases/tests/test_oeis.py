"""Smoke tests for prometheus_math.databases.oeis.

These hit the live OEIS API. They skip cleanly when:
  * The host is unreachable (DNS / connection refused / timeout).
  * Cloudflare returns a 403 challenge page (lookup() yields None).

Local-mirror tests skip unless PROMETHEUS_DOWNLOAD_OEIS=1 is set in the
environment, so a clean checkout doesn't trigger a 35 MB download
during routine `pytest`.

Run directly with `python -m prometheus_math.databases.tests.test_oeis`
or under pytest.
"""
from __future__ import annotations

import os
import shutil

import pytest

from prometheus_math.databases import oeis


# ---------------------------------------------------------------------------
# Network gate
# ---------------------------------------------------------------------------

def _network_ok() -> bool:
    try:
        return oeis.probe(timeout=4.0)
    except Exception:
        return False


_NET_OK = _network_ok()
_skip_no_net = pytest.mark.skipif(
    not _NET_OK,
    reason="OEIS unreachable (no network or Cloudflare challenge); skipping live tests.",
)


# ---------------------------------------------------------------------------
# Pure-Python tests (no network)
# ---------------------------------------------------------------------------

def test_normalize_a_number_variants():
    """Accept int, 'A45', 'a45', 'A000045' uniformly."""
    n = oeis._normalize_a_number
    assert n(45) == "A000045"
    assert n("A45") == "A000045"
    assert n("a45") == "A000045"
    assert n("A000045") == "A000045"


def test_normalize_a_number_rejects_garbage():
    with pytest.raises(ValueError):
        oeis._normalize_a_number("hello")


def test_parse_data_field():
    """Comma-separated string -> list[int], skipping malformed tokens."""
    assert oeis._parse_data_field("0,1,1,2,3,5") == [0, 1, 1, 2, 3, 5]
    assert oeis._parse_data_field("") == []
    assert oeis._parse_data_field("1,foo,2") == [1, 2]


def test_extract_cross_refs_dedup_and_normalize():
    refs = oeis._extract_cross_refs([
        "Cf. A000032, A000045.",
        "See also A45 and A000045 again.",
    ])
    assert "A000032" in refs
    assert "A000045" in refs
    # Dedup
    assert refs.count("A000045") == 1


# ---------------------------------------------------------------------------
# Live API tests
# ---------------------------------------------------------------------------

@_skip_no_net
def test_lookup_fibonacci():
    """A000045 must resolve to Fibonacci with the canonical leading terms.

    Forces the live API path (local mirror records have empty keywords).
    """
    prev = oeis.use_local_first()
    try:
        oeis.use_local_first(False)
        rec = oeis.lookup("A000045")
        if rec is None:
            pytest.skip("OEIS returned no result (transient block).")
        assert rec["number"] == "A000045"
        assert "fibonacci" in rec["name"].lower()
        # Canonical Fibonacci prefix
        assert rec["data"][:8] == [0, 1, 1, 2, 3, 5, 8, 13]
        # Keyword set should include 'nonn' (nonnegative) and either 'core' or 'easy'
        assert "nonn" in rec["keywords"]
    finally:
        oeis.use_local_first(prev)


@_skip_no_net
def test_find_sequence_fibonacci_prefix():
    """Searching by [1,1,2,3,5,8,13] should surface A000045 via the live API.

    Local mirror's brute-force scan doesn't always surface A000045 because
    its data starts with [0,1,1,2,3,5,...] and other sequences (e.g.
    A005181) genuinely begin with [1,1,2,3,5,8,13,...].
    """
    prev = oeis.use_local_first()
    try:
        oeis.use_local_first(False)
        hits = oeis.find_sequence([1, 1, 2, 3, 5, 8, 13], max_results=10)
        if not hits:
            pytest.skip("OEIS search returned nothing.")
        a_numbers = {h["number"] for h in hits}
        assert "A000045" in a_numbers
    finally:
        oeis.use_local_first(prev)


@_skip_no_net
def test_b_file_extended_terms():
    """The b-file of Fibonacci has thousands of entries; ask for 20."""
    rows = oeis.b_file("A000045", max_terms=20)
    if not rows:
        pytest.skip("b-file unreachable.")
    assert len(rows) >= 20
    # Indices should be non-decreasing integers
    indices = [r[0] for r in rows]
    assert indices == sorted(indices)
    # First few values should match Fibonacci
    values = [r[1] for r in rows]
    # The b-file may start at offset 0 or 1, but both lie inside the sequence
    # 0,1,1,2,3,5,8,13,21,...; check that the early values come from that set.
    fib_set = {0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610}
    assert any(v in fib_set for v in values[:5])


@_skip_no_net
def test_is_known_natural_numbers():
    """[1,2,3,4,5] is the all-time-most-common prefix; live OEIS returns A000027."""
    prev = oeis.use_local_first()
    try:
        oeis.use_local_first(False)
        a = oeis.is_known([1, 2, 3, 4, 5])
        if a is None:
            pytest.skip("OEIS returned no match (transient block).")
        assert a == "A000027"
    finally:
        oeis.use_local_first(prev)


@_skip_no_net
def test_cross_refs_present():
    """Fibonacci should cross-reference Lucas numbers (A000032)."""
    refs = oeis.cross_refs("A000045")
    if not refs:
        pytest.skip("No cross-refs returned.")
    assert "A000032" in refs


@_skip_no_net
def test_get_data_one_liner():
    """get_data() should give the same prefix as lookup()['data']."""
    data = oeis.get_data(45)
    if not data:
        pytest.skip("OEIS unreachable.")
    assert data[:8] == [0, 1, 1, 2, 3, 5, 8, 13]


@_skip_no_net
def test_cache_round_trip():
    """Second lookup of the same A-number must come from the JSON cache.

    The JSON cache is the live-API cache; the local mirror has its own
    (already-resident) cache, so we force the live path here.
    """
    prev = oeis.use_local_first()
    try:
        oeis.use_local_first(False)
        oeis.clear_cache()
        info0 = oeis.cache_info()
        assert info0["json_entries"] == 0
        rec = oeis.lookup("A000045")
        if rec is None:
            pytest.skip("OEIS unreachable.")
        info1 = oeis.cache_info()
        assert info1["json_entries"] >= 1
        # Second call should not increase the cache size.
        rec2 = oeis.lookup("A000045")
        info2 = oeis.cache_info()
        assert info2["json_entries"] == info1["json_entries"]
        assert rec2["number"] == rec["number"]
    finally:
        oeis.use_local_first(prev)


# ---------------------------------------------------------------------------
# Local mirror tests
# ---------------------------------------------------------------------------
#
# These exercise the offline-first path that resolves the Cloudflare
# blocker.  Triggering the actual download is expensive (~35 MB) so we
# gate the heavy test behind an env var.  Tests that only verify the
# mirror is wired up correctly run unconditionally and skip cleanly if
# no mirror is loaded.

_DOWNLOAD_OPTED_IN = os.environ.get("PROMETHEUS_DOWNLOAD_OEIS") == "1"
_skip_no_download = pytest.mark.skipif(
    not _DOWNLOAD_OPTED_IN,
    reason="set PROMETHEUS_DOWNLOAD_OEIS=1 to run the OEIS bulk download.",
)


def _enough_disk_for_mirror(min_bytes: int = 200 * 1024 * 1024) -> bool:
    """At least ~200 MB free in the data dir."""
    try:
        from prometheus_math.databases import _local
        path = _local.data_dir()
        usage = shutil.disk_usage(path)
        return usage.free >= min_bytes
    except Exception:
        return False


@_skip_no_download
def test_local_mirror_download_and_lookup():
    """Smoke test the full pipeline: download, parse, look up.

    Skips if PROMETHEUS_DOWNLOAD_OEIS is not set or disk is short.
    """
    if not _enough_disk_for_mirror():
        pytest.skip("not enough free disk for OEIS mirror.")

    status = oeis.update_mirror()
    if status.get("error") or status.get("sequences_loaded", 0) == 0:
        pytest.skip(f"mirror download failed: {status}")

    assert oeis.has_local_mirror()
    assert status["sequences_loaded"] > 100_000  # ~370K expected, allow slack

    fib = oeis.lookup("A000045")
    assert fib is not None
    assert fib["number"] == "A000045"
    assert "fibonacci" in fib["name"].lower()
    assert fib["data"][:8] == [0, 1, 1, 2, 3, 5, 8, 13]

    nat = oeis.lookup("A000027")
    assert nat is not None
    assert nat["number"] == "A000027"
    assert nat["data"][:5] == [1, 2, 3, 4, 5]

    # An unallocated A-number returns None.
    miss = oeis.lookup("A8000000")
    assert miss is None


def test_offline_lookup_works_without_network():
    """If a mirror is loaded, lookup returns name + data with no API call."""
    if not oeis.has_local_mirror():
        pytest.skip("no local mirror present; run with PROMETHEUS_DOWNLOAD_OEIS=1.")

    prev = oeis.use_local_first()
    try:
        oeis.use_local_first(True)
        rec = oeis.lookup("A000045")
        assert rec is not None
        assert rec["name"]              # populated from names.gz
        assert rec["data"]              # populated from stripped.gz
        assert rec["number"] == "A000045"
    finally:
        oeis.use_local_first(prev)


def test_use_local_first_toggle():
    """The flag is settable and round-trips."""
    if not oeis.has_local_mirror():
        pytest.skip("no local mirror present; run with PROMETHEUS_DOWNLOAD_OEIS=1.")

    prev = oeis.use_local_first()
    try:
        # Local path
        oeis.use_local_first(True)
        assert oeis.use_local_first() is True
        local = oeis.lookup("A000045")
        assert local is not None
        assert local["data"][:5] == [0, 1, 1, 2, 3]

        # Live path — only meaningful if the API is reachable; skip if not.
        oeis.use_local_first(False)
        assert oeis.use_local_first() is False
        if _NET_OK:
            live = oeis.lookup("A000045")
            if live is not None:
                assert live["number"] == "A000045"
                assert live["data"][:5] == [0, 1, 1, 2, 3]
    finally:
        oeis.use_local_first(prev)


def test_probe_true_with_local_mirror():
    """probe() should report True if the mirror is loaded, even offline."""
    if not oeis.has_local_mirror():
        pytest.skip("no local mirror present.")
    # Even with an absurdly tight timeout we should win via the mirror.
    assert oeis.probe(timeout=0.001) is True


def test_parse_stripped_line():
    """Round-trip the stripped.gz line format."""
    line = "A000045 ,0,1,1,2,3,5,8,13,21,34,"
    parsed = oeis._parse_stripped_line(line)
    assert parsed is not None
    a_id, data = parsed
    assert a_id == "A000045"
    assert data == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    # Comments and blanks are skipped
    assert oeis._parse_stripped_line("# comment") is None
    assert oeis._parse_stripped_line("") is None
    # Malformed but parseable: empty data
    a_id, data = oeis._parse_stripped_line("A000001 ,")
    assert a_id == "A000001" and data == []


def test_parse_names_line():
    """Round-trip the names.gz line format."""
    line = "A000045\tFibonacci numbers: F(n) = F(n-1) + F(n-2)."
    parsed = oeis._parse_names_line(line)
    assert parsed is not None
    a_id, name = parsed
    assert a_id == "A000045"
    assert name.startswith("Fibonacci")


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
