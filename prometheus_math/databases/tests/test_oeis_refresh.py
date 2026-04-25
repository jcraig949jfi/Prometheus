"""Tests for the OEIS mirror metadata + weekly refresh hook.

Authority + property + edge + composition tests for
``mirror_metadata()`` and ``update_mirror()``'s metadata-write contract,
introduced for project #11 (OEIS local mirror weekly refresh CI job).

These tests redirect the prometheus_math data dir to a per-test
``tmp_path`` via ``PROMETHEUS_DATA_DIR`` so they never touch the real
mirror on disk and never hit the network.
"""
from __future__ import annotations

import gzip
import importlib
import json
import os
import pathlib

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def isolated_oeis(tmp_path, monkeypatch):
    """Reload prometheus_math.databases.oeis against a sandbox data dir.

    Yields the freshly-imported module along with the sandbox base
    directory.  Module-level caches are zeroed so every test starts
    from a clean slate.
    """
    monkeypatch.setenv("PROMETHEUS_DATA_DIR", str(tmp_path))
    # Force _local._DATA_DIR to reset on next call.
    from prometheus_math.databases import _local as _l
    _l._DATA_DIR = None
    from prometheus_math.databases import oeis as _oeis
    importlib.reload(_oeis)
    # Defensive: zero in-memory caches the reload may have skipped.
    _oeis._OEIS_LOCAL_CACHE.clear()
    _oeis._OEIS_PREFIX_INDEX.clear()
    _oeis._OEIS_LOCAL_LOADED = False
    _oeis._OEIS_USE_LOCAL_FIRST = None
    yield _oeis, tmp_path
    # Cleanup: reset shared state so other test modules aren't poisoned.
    _l._DATA_DIR = None
    _oeis._OEIS_LOCAL_CACHE.clear()
    _oeis._OEIS_PREFIX_INDEX.clear()
    _oeis._OEIS_LOCAL_LOADED = False
    _oeis._OEIS_USE_LOCAL_FIRST = None


def _seed_minimal_mirror(tmp_path: pathlib.Path) -> pathlib.Path:
    """Lay down a tiny but valid stripped.gz / names.gz so the mirror
    autoload path can populate the in-memory cache without network."""
    base = tmp_path / "oeis"
    base.mkdir(parents=True, exist_ok=True)
    # 3 sequences chosen so the prefix scan in _local_find_sequence has
    # something to bite on without resembling real OEIS volume.
    stripped = (
        "# OEIS stripped (test fixture)\n"
        "A000045 ,0,1,1,2,3,5,8,13,21,34,\n"
        "A000027 ,1,2,3,4,5,6,7,8,9,10,\n"
        "A000040 ,2,3,5,7,11,13,17,19,23,29,\n"
    )
    names = (
        "# OEIS names (test fixture)\n"
        "A000045\tFibonacci numbers (test fixture).\n"
        "A000027\tThe positive integers (test fixture).\n"
        "A000040\tThe primes (test fixture).\n"
    )
    with gzip.open(base / "stripped.gz", "wt", encoding="utf-8") as fh:
        fh.write(stripped)
    with gzip.open(base / "names.gz", "wt", encoding="utf-8") as fh:
        fh.write(names)
    return base


# ---------------------------------------------------------------------------
# 1. Authority — required keys / structure
# ---------------------------------------------------------------------------

def test_authority_metadata_keys_present_after_refresh(isolated_oeis):
    """Authority: mirror_metadata() returns the documented dict shape.

    Reference: project #11 spec — the sidecar must carry
    {sequences, last_refresh_iso, files, size_bytes}.
    """
    oeis, tmp = isolated_oeis
    _seed_minimal_mirror(tmp)
    # Trigger a metadata write via the public refresh hook.
    out = oeis.update_mirror(force=False)
    assert "sequences_loaded" in out
    meta = oeis.mirror_metadata()
    for key in ("sequences", "last_refresh_iso", "files", "size_bytes"):
        assert key in meta, f"missing key {key} in {meta!r}"
    assert isinstance(meta["sequences"], int)
    assert isinstance(meta["files"], list)
    assert isinstance(meta["size_bytes"], int)
    assert meta["sequences"] >= 1
    assert "stripped.gz" in meta["files"]


def test_authority_sidecar_file_written(isolated_oeis):
    """Authority: update_mirror() writes a real .metadata.json on disk
    that round-trips through the json module verbatim."""
    oeis, tmp = isolated_oeis
    _seed_minimal_mirror(tmp)
    oeis.update_mirror(force=False)
    sidecar = tmp / "oeis" / ".metadata.json"
    assert sidecar.is_file(), f"sidecar not at {sidecar}"
    raw = json.loads(sidecar.read_text(encoding="utf-8"))
    assert raw["sequences"] == 3  # the three seeded sequences
    assert raw["last_refresh_iso"] is not None
    assert raw["last_refresh_iso"].endswith("+00:00")  # UTC ISO 8601


# ---------------------------------------------------------------------------
# 2. Property — invariants under update_mirror()
# ---------------------------------------------------------------------------

def test_property_metadata_count_equals_in_memory(isolated_oeis):
    """Property: after update_mirror(force=False), the persisted
    ``sequences`` count equals len(_OEIS_LOCAL_CACHE)."""
    oeis, tmp = isolated_oeis
    _seed_minimal_mirror(tmp)
    oeis.update_mirror(force=False)
    meta = oeis.mirror_metadata()
    assert meta["sequences"] == len(oeis._OEIS_LOCAL_CACHE)


def test_property_size_bytes_matches_local_inventory(isolated_oeis):
    """Property: reported size_bytes equals the os.walk-summed dataset
    size at the moment update_mirror() ran."""
    oeis, tmp = isolated_oeis
    _seed_minimal_mirror(tmp)
    oeis.update_mirror(force=False)
    meta = oeis.mirror_metadata()
    from prometheus_math.databases import _local
    on_disk = _local.mirror_size("oeis")
    # The metadata file itself is part of the directory now, so we
    # only require the recorded size to be bounded by reality.
    assert 0 < meta["size_bytes"] <= on_disk


# ---------------------------------------------------------------------------
# 3. Edge — empty / corrupt / missing
# ---------------------------------------------------------------------------

def test_edge_no_mirror_returns_empty_default(isolated_oeis):
    """Edge: with NO mirror on disk and nothing loaded in memory,
    mirror_metadata() returns the empty default rather than raising."""
    oeis, tmp = isolated_oeis
    # Sanity: dataset dir does not yet exist.
    assert not (tmp / "oeis").exists()
    meta = oeis.mirror_metadata()
    assert meta == {
        "sequences":        0,
        "last_refresh_iso": None,
        "files":            [],
        "size_bytes":       0,
    }


def test_edge_corrupt_sidecar_falls_back(isolated_oeis):
    """Edge: a malformed .metadata.json is tolerated — we fall back to
    the synthesized state and log, rather than blowing up CI."""
    oeis, tmp = isolated_oeis
    base = tmp / "oeis"
    base.mkdir(parents=True, exist_ok=True)
    (base / ".metadata.json").write_text("this is not json {{{",
                                         encoding="utf-8")
    meta = oeis.mirror_metadata()
    # Synthesized default has empty files (no stripped/names yet).
    assert meta["sequences"] == 0
    assert meta["files"] == []
    assert meta["last_refresh_iso"] is None


# ---------------------------------------------------------------------------
# 4. Composition — full lifecycle
# ---------------------------------------------------------------------------

def test_composition_lifecycle_delete_recompute(isolated_oeis):
    """Composition: seed mirror -> refresh -> delete sidecar ->
    force-refresh -> sidecar regenerated AND consistent with the
    second in-memory load.

    Chains: _seed_minimal_mirror + update_mirror + mirror_metadata
    + filesystem mutation + a second update_mirror.
    """
    oeis, tmp = isolated_oeis
    _seed_minimal_mirror(tmp)
    out1 = oeis.update_mirror(force=False)
    meta1 = oeis.mirror_metadata()
    sidecar = tmp / "oeis" / ".metadata.json"
    assert sidecar.is_file()
    first_iso = meta1["last_refresh_iso"]

    # Mutilate metadata; the cache is still loaded so synthesis works.
    sidecar.unlink()
    assert not sidecar.exists()
    synthesized = oeis.mirror_metadata()
    # Without a sidecar, synthesized count comes from _OEIS_LOCAL_CACHE
    # (still populated from the first load).
    assert synthesized["sequences"] == out1["sequences_loaded"]

    # Second refresh writes a fresh sidecar with a NEW timestamp.
    import time
    time.sleep(0.01)  # ensure ISO timestamp moves forward
    oeis.update_mirror(force=False)
    meta2 = oeis.mirror_metadata()
    assert sidecar.is_file()
    assert meta2["sequences"] == meta1["sequences"]
    assert meta2["last_refresh_iso"] != first_iso
    assert meta2["last_refresh_iso"] > first_iso  # ISO 8601 sorts lex


def test_composition_delta_arithmetic_for_ci(isolated_oeis):
    """Composition: simulates the CI delta computation.

    The CI workflow reads `prev = mirror_metadata()`, runs
    update_mirror, then reads `cur = mirror_metadata()` and commits iff
    `cur['sequences'] - prev['sequences'] > 0`.  Verify both the
    no-delta and the +N-delta branches behave correctly.
    """
    oeis, tmp = isolated_oeis
    base = _seed_minimal_mirror(tmp)
    oeis.update_mirror(force=False)
    prev = oeis.mirror_metadata()
    assert prev["sequences"] == 3

    # No-op refresh: delta should be 0 (already-fresh mirror).
    oeis.update_mirror(force=False)
    cur = oeis.mirror_metadata()
    assert cur["sequences"] - prev["sequences"] == 0

    # Now grow the mirror behind the cache and force-reparse to
    # simulate Sloane publishing a new sequence.
    extended = (
        "A000045 ,0,1,1,2,3,5,8,13,21,34,\n"
        "A000027 ,1,2,3,4,5,6,7,8,9,10,\n"
        "A000040 ,2,3,5,7,11,13,17,19,23,29,\n"
        "A000010 ,1,1,2,2,4,2,6,4,6,4,\n"   # phi: simulated new entry
    )
    with gzip.open(base / "stripped.gz", "wt", encoding="utf-8") as fh:
        fh.write(extended)
    # Force a re-parse of the on-disk dump.
    oeis._OEIS_LOCAL_LOADED = False
    oeis._OEIS_LOCAL_CACHE.clear()
    oeis._load_local_cache(base / "stripped.gz", base / "names.gz")
    oeis._OEIS_LOCAL_LOADED = True
    # Now write the metadata to reflect the new state.
    oeis.update_mirror(force=False)
    grown = oeis.mirror_metadata()
    delta = grown["sequences"] - prev["sequences"]
    assert delta == 1, f"expected +1, got {delta}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
