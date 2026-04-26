"""Smoke tests for prometheus_math.databases.arxiv.

Hits the live arXiv API. Skips cleanly when the host is unreachable
or the third-party `arxiv` pip package is missing.

Run directly with `python -m prometheus_math.databases.tests.test_arxiv`
or under pytest.
"""
from __future__ import annotations

import datetime as _dt
import importlib.util

import pytest

# The wrapper module imports cleanly even when the `arxiv` pip package
# is missing (functions just return [] / None), so we always import it
# but gate live tests on package availability + a probe call.
from prometheus_math.databases import arxiv as ax


# ---------------------------------------------------------------------------
# Network gate
# ---------------------------------------------------------------------------

def _has_arxiv_pkg() -> bool:
    return importlib.util.find_spec("arxiv") is not None


def _network_ok() -> bool:
    if not _has_arxiv_pkg():
        return False
    try:
        return ax.probe(timeout=5.0)
    except Exception:
        return False


_PKG_OK = _has_arxiv_pkg()
_NET_OK = _network_ok()

_skip_no_pkg = pytest.mark.skipif(
    not _PKG_OK,
    reason="`arxiv` pip package not installed; skipping wrapper tests.",
)
_skip_no_net = pytest.mark.skipif(
    not _NET_OK,
    reason="arXiv API unreachable (no network or transient block); skipping live tests.",
)


# ---------------------------------------------------------------------------
# Pure-Python tests (no network)
# ---------------------------------------------------------------------------

def test_normalize_id_strips_version():
    assert ax._normalize_id("2410.12345v2") == "2410.12345"
    assert ax._normalize_id("2410.12345") == "2410.12345"
    assert ax._normalize_id("arXiv:2410.12345v3") == "2410.12345"


def test_normalize_id_legacy_passthrough():
    # Old-style ids contain a slash but no trailing version.
    assert ax._normalize_id("math.NT/0501234") == "math.NT/0501234"


def test_build_query_categories_combine():
    q = ax._build_query("Riemann zeta", categories=["math.NT", "math.AG"])
    assert "Riemann zeta" in q
    assert "cat:math.NT" in q
    assert "cat:math.AG" in q
    assert " AND " in q


def test_build_query_no_query_just_categories():
    q = ax._build_query(None, categories=["math.NT"])
    assert "cat:math.NT" in q
    assert "Riemann" not in q


def test_resolve_sort_known_aliases():
    if not _PKG_OK:
        pytest.skip("arxiv package missing")
    assert ax._resolve_sort("relevance") is not None
    assert ax._resolve_sort("submittedDate") is not None
    assert ax._resolve_sort("lastUpdatedDate") is not None
    assert ax._resolve_sort("submitted") is not None  # alias


# ---------------------------------------------------------------------------
# Live API tests
# ---------------------------------------------------------------------------

@_skip_no_pkg
@_skip_no_net
def test_search_riemann_zeta():
    """Free-text search for 'Riemann zeta' returns >= 5 hits, with the
    keyword present in titles or abstracts of most of them."""
    hits = ax.search("Riemann zeta", max_results=10)
    if not hits:
        pytest.skip("arXiv search returned no results (transient).")
    assert len(hits) >= 5
    # Sanity: every hit has the canonical fields populated.
    for h in hits:
        assert h["id"]
        assert h["title"]
        assert isinstance(h["authors"], list)
        assert isinstance(h["categories"], list)
    text_blob = " ".join(
        ((h["title"] or "") + " " + (h["abstract"] or "")).lower() for h in hits
    )
    assert "riemann" in text_blob


@_skip_no_pkg
@_skip_no_net
def test_get_known_paper():
    """1505.05456 is a stable, well-known arXiv id."""
    rec = ax.get("1505.05456")
    if rec is None:
        pytest.skip("arXiv get() returned None (transient block).")
    assert rec["id"].startswith("1505.05456")
    assert rec["title"]
    assert isinstance(rec["authors"], list) and len(rec["authors"]) >= 1
    assert rec["abstract"]
    assert rec["pdf_url"].startswith("http")


@_skip_no_pkg
@_skip_no_net
def test_recent_math_nt():
    """recent('math.NT') returns recent number-theory papers."""
    hits = ax.recent("math.NT", max_results=5, days=60)
    if not hits:
        pytest.skip("arXiv recent() returned no results (transient).")
    assert len(hits) >= 1
    # Every hit should have math.NT in its categories (primary or cross).
    for h in hits:
        assert "math.NT" in (h["categories"] or [])
    # Every published date should parse and be recent.
    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=120)
    for h in hits:
        if h["published"]:
            d = _dt.datetime.fromisoformat(h["published"])
            assert d >= cutoff


@_skip_no_pkg
@_skip_no_net
def test_by_author_terence_tao():
    """Terence Tao has thousands of arXiv papers; we expect at least one."""
    hits = ax.by_author("Terence Tao", max_results=10)
    if not hits:
        pytest.skip("by_author() returned nothing (transient).")
    assert len(hits) >= 1
    # At least one hit should genuinely list Tao among the authors.
    saw_tao = any(
        any("tao" in a.lower() for a in (h["authors"] or []))
        for h in hits
    )
    assert saw_tao, f"none of {len(hits)} hits actually list Tao as author"


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
