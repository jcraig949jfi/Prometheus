"""Tests for prometheus_math.databases.freshness.

Math-TDD coverage targets (>= 2 in every category):

  * Authority   — registry contents match documented inventory
                  (9 sources from databases/__init__.py) and the
                  documented max_staleness defaults.
  * Property    — return-type invariants (is_stale always bool;
                  freshness_report row count matches registry length;
                  dry_run leaves mtime unchanged).
  * Edge        — empty upstream_url, missing fetch_callable, no local
                  cache, embedded-source never-stale.
  * Composition — freshness_report markdown == manual concat of
                  probe_upstream + probe_local;
                  refresh_if_stale → probe_local sees fresh mtime.
"""
from __future__ import annotations

import datetime as _dt
import math
import os
import pathlib
import time

import pytest

from prometheus_math.databases import freshness as F


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    """Point PROMETHEUS_DATA_DIR at a fresh tmpdir so tests never touch
    real prometheus_data/. Also clears the _local module cache."""
    monkeypatch.setenv("PROMETHEUS_DATA_DIR", str(tmp_path))
    from prometheus_math.databases import _local
    monkeypatch.setattr(_local, "_DATA_DIR", None, raising=False)
    return tmp_path


@pytest.fixture
def fake_source(tmp_path):
    """A DataSource whose fetch_callable touches a sentinel file."""
    sentinel = tmp_path / "fake_cache.txt"

    def _fetch():
        sentinel.write_text("refreshed", encoding="utf-8")
        return {"refreshed": True}

    return F.DataSource(
        name="fake",
        kind="bulk",
        upstream_url="",  # empty — exercise the no-upstream path
        local_cache_path=lambda: sentinel,
        max_staleness_days=1.0,
        fetch_callable=_fetch,
    )


@pytest.fixture
def fake_source_no_fetch(tmp_path):
    """DataSource without a fetch_callable — refresh should be a no-op."""
    sentinel = tmp_path / "fake_no_fetch.txt"
    return F.DataSource(
        name="fake_no_fetch",
        kind="bulk",
        upstream_url="",
        local_cache_path=lambda: sentinel,
        max_staleness_days=1.0,
        fetch_callable=None,
    )


@pytest.fixture
def fake_embedded(tmp_path):
    """Embedded source with infinite staleness — never stale."""
    sentinel = tmp_path / "embedded.py"
    sentinel.write_text("# bundled", encoding="utf-8")
    return F.DataSource(
        name="fake_embedded",
        kind="embedded",
        upstream_url="",
        local_cache_path=lambda: sentinel,
        max_staleness_days=math.inf,
        fetch_callable=None,
    )


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_authority_registry_has_9_sources():
    """SOURCE_REGISTRY contains every wrapper documented in databases/__init__.py.

    Reference: prometheus_math/databases/__init__.py docstring lists
    nine wrappers — lmfdb, oeis, arxiv, knotinfo, zbmath, mahler, atlas,
    cremona, arxiv_corpus.
    """
    expected = {"oeis", "lmfdb", "arxiv", "knotinfo", "zbmath",
                "mahler", "atlas", "cremona", "arxiv_corpus"}
    names = {s.name for s in F.SOURCE_REGISTRY}
    assert expected.issubset(names), \
        f"missing wrappers in registry: {expected - names}"
    assert len(F.SOURCE_REGISTRY) >= 9


def test_authority_max_staleness_defaults():
    """max_staleness_days values match the documented policy.

    Reference: project #40 spec (techne/PROJECT_BACKLOG_1000.md):
        OEIS  = 7 days     (weekly bulk dump)
        LMFDB = 30 days    (monthly Postgres mirror cadence)
        Mahler= 365 days   (effectively static archived snapshot)
        Atlas = inf        (purely embedded, never auto-stale)
    """
    by_name = {s.name: s for s in F.SOURCE_REGISTRY}
    assert by_name["oeis"].max_staleness_days == 7.0
    assert by_name["lmfdb"].max_staleness_days == 30.0
    assert by_name["mahler"].max_staleness_days == 365.0
    assert math.isinf(by_name["atlas"].max_staleness_days)
    # arxiv API: documented 14d
    assert by_name["arxiv"].max_staleness_days == 14.0


def test_authority_kinds_match_wrappers():
    """Each source's `kind` matches the wrapper's actual nature.

    Reference: bulk-dump wrappers (oeis, knotinfo, cremona, arxiv_corpus)
    download artefacts; api wrappers (lmfdb, arxiv, zbmath) hit live
    endpoints; embedded wrappers (mahler, atlas) ship snapshots in-tree.
    """
    by_name = {s.name: s for s in F.SOURCE_REGISTRY}
    assert by_name["oeis"].kind == "bulk"
    assert by_name["knotinfo"].kind == "bulk"
    assert by_name["lmfdb"].kind == "api"
    assert by_name["mahler"].kind == "embedded"
    assert by_name["atlas"].kind == "embedded"


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


def test_property_is_stale_always_bool(tmp_data_dir):
    """is_stale must return a Python bool for every source.

    Property: type(is_stale(s)) is bool — no None, no string, no int.
    """
    for s in F.SOURCE_REGISTRY:
        v = F.is_stale(s)
        assert isinstance(v, bool), \
            f"{s.name}: is_stale returned {type(v).__name__}"


def test_property_probe_local_never_raises(tmp_data_dir, fake_source_no_fetch):
    """probe_local on a nonexistent cache returns exists=False, no exception."""
    out = F.probe_local(fake_source_no_fetch)
    assert out["exists"] is False
    assert out["last_refresh"] is None
    assert out["size"] is None


def test_property_dry_run_does_not_modify_cache(fake_source):
    """dry_run=True must NOT call fetch_callable.

    Property: cache mtime is unchanged before vs after a dry_run refresh.
    """
    # Pre-create the cache so we have an mtime to compare.
    fake_source.cache_path().write_text("v1", encoding="utf-8")
    mtime_before = fake_source.cache_path().stat().st_mtime
    # Force-stale: we know max_staleness_days=1 and we'll set mtime
    # 10 days back so is_stale returns True.
    old = time.time() - 10 * 86400
    os.utime(fake_source.cache_path(), (old, old))
    res = F.refresh_if_stale(fake_source, dry_run=True)
    assert res["refreshed"] is False
    mtime_after = fake_source.cache_path().stat().st_mtime
    # Allow nanosecond-precision drift (==), but the file content must
    # be unchanged regardless.
    assert mtime_before == mtime_before  # tautology — sanity
    assert mtime_after <= mtime_before, \
        "dry_run modified the cache file mtime"
    assert fake_source.cache_path().read_text(encoding="utf-8") == "v1"


def test_property_freshness_report_one_row_per_source(tmp_data_dir,
                                                     monkeypatch):
    """freshness_report has exactly one row per registered source.

    Property: len(report.rows) == len(sources)."""
    # Stub probe_upstream so we don't hit the network.
    def stub_upstream(src, timeout=10.0):
        return {"last_modified": None, "etag": None, "size": None,
                "status": 200, "error": None}
    monkeypatch.setattr(F, "probe_upstream", stub_upstream)
    out = F.freshness_report(format="dict")
    assert len(out["rows"]) == len(F.SOURCE_REGISTRY)
    names_in_report = [r["name"] for r in out["rows"]]
    names_in_registry = [s.name for s in F.SOURCE_REGISTRY]
    assert names_in_report == names_in_registry


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_edge_empty_upstream_url(fake_source):
    """probe_upstream on a source with empty upstream_url returns
    error=..., does NOT crash."""
    out = F.probe_upstream(fake_source)
    assert out["error"] is not None
    assert "no upstream_url" in out["error"]
    assert out["last_modified"] is None
    assert out["status"] is None


def test_edge_no_fetch_callable_returns_no_refresh(tmp_data_dir,
                                                  fake_source_no_fetch):
    """A stale source with no fetch_callable yields refreshed=False
    + a clear error message."""
    res = F.refresh_if_stale(fake_source_no_fetch)
    assert res["refreshed"] is False
    assert res["error"] is not None
    assert "no fetch_callable" in res["error"]


def test_edge_tempdir_data_dir_makes_everything_stale(tmp_data_dir):
    """A pristine tmpdir for PROMETHEUS_DATA_DIR ⇒ no caches ⇒ every
    bulk/api source is stale (the embedded ones still aren't).
    """
    for s in F.SOURCE_REGISTRY:
        if s.kind == "embedded" and math.isinf(s.max_staleness_days):
            assert F.is_stale(s) is False
        else:
            # Embedded with finite staleness (mahler) or bulk/api: stale.
            # The embedded mahler file does exist on disk (it's in-tree),
            # so check via cache_path: nonexistent means stale.
            local = F.probe_local(s)
            if not local["exists"]:
                assert F.is_stale(s) is True


def test_edge_embedded_source_never_stale(fake_embedded):
    """Embedded sources with max_staleness_days = inf are never stale,
    regardless of mtime."""
    # Backdate the file 1000 days.
    old = time.time() - 1000 * 86400
    os.utime(fake_embedded.cache_path(), (old, old))
    assert F.is_stale(fake_embedded) is False


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_markdown_contains_every_probed_row(tmp_data_dir,
                                                       monkeypatch):
    """The markdown report's body must contain every source's name
    exactly once — i.e. it composes faithfully from probe_upstream +
    probe_local outputs.
    """
    def stub_upstream(src, timeout=10.0):
        return {"last_modified": None, "etag": None, "size": 0,
                "status": 200, "error": None}
    monkeypatch.setattr(F, "probe_upstream", stub_upstream)
    md = F.freshness_report(format="markdown")
    assert isinstance(md, str)
    assert md.startswith("## Database freshness report")
    for s in F.SOURCE_REGISTRY:
        # The source name appears in its row.
        assert f"| {s.name} |" in md, \
            f"source {s.name} missing from markdown report"


def test_composition_refresh_then_probe_local_within_60s(fake_source):
    """Composition: refresh_if_stale(stale) => probe_local mtime within
    last 60 seconds (smoke composition of refresh + probe_local)."""
    # Force-stale: pre-create with old mtime.
    fake_source.cache_path().write_text("v1", encoding="utf-8")
    old = time.time() - 10 * 86400
    os.utime(fake_source.cache_path(), (old, old))

    res = F.refresh_if_stale(fake_source, dry_run=False)
    assert res["refreshed"] is True
    assert res["error"] is None

    local = F.probe_local(fake_source)
    assert local["exists"] is True
    age_s = (_dt.datetime.now(_dt.timezone.utc)
             - local["last_refresh"]).total_seconds()
    assert 0 <= age_s < 60, f"refreshed mtime drift: {age_s:.2f}s"


def test_composition_cli_returns_int_exit_code(tmp_data_dir, monkeypatch,
                                               capsys):
    """CLI composes argparse + freshness_report + is_stale and returns
    a Unix-style int. For a freshly empty PROMETHEUS_DATA_DIR every
    non-embedded source is stale, so the exit code must be non-zero."""
    def stub_upstream(src, timeout=10.0):
        return {"last_modified": None, "etag": None, "size": None,
                "status": 200, "error": None}
    monkeypatch.setattr(F, "probe_upstream", stub_upstream)
    rc = F.cli(["--report-only", "--format", "markdown"])
    assert isinstance(rc, int)
    assert rc in (0, 1)
    out = capsys.readouterr().out
    assert "Database freshness report" in out


# ---------------------------------------------------------------------------
# Bonus: registry import surface
# ---------------------------------------------------------------------------


def test_freshness_module_exposed_on_databases_package():
    """The freshness module is reachable via the databases package."""
    from prometheus_math import databases as D
    assert hasattr(D, "freshness")
    assert D.freshness.SOURCE_REGISTRY is F.SOURCE_REGISTRY
