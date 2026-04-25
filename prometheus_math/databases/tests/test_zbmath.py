"""Smoke tests for prometheus_math.databases.zbmath.

Hits the live zbMATH Open API. Skips cleanly when the host is unreachable
(no network, transient block, or firewall).

Run directly with `python -m prometheus_math.databases.tests.test_zbmath`
or under pytest.
"""
from __future__ import annotations

import pytest

from prometheus_math.databases import zbmath as zb


# ---------------------------------------------------------------------------
# Network gate
# ---------------------------------------------------------------------------

def _network_ok() -> bool:
    try:
        return zb.probe(timeout=5.0)
    except Exception:
        return False


_NET_OK = _network_ok()

_skip_no_net = pytest.mark.skipif(
    not _NET_OK,
    reason="zbMATH Open API unreachable (no network or transient block); skipping live tests.",
)


# ---------------------------------------------------------------------------
# Pure-Python tests (no network)
# ---------------------------------------------------------------------------

def test_msc_codes():
    """msc_codes() returns ~200 (code, description) pairs."""
    codes = zb.msc_codes()
    assert isinstance(codes, list)
    assert len(codes) >= 100, f"expected >=100 MSC codes, got {len(codes)}"
    # Spot-check format and content.
    for entry in codes[:20]:
        assert isinstance(entry, tuple) and len(entry) == 2
        code, desc = entry
        assert isinstance(code, str) and code
        assert isinstance(desc, str) and desc
    # Famous codes that must be present.
    code_index = {c: d for c, d in codes}
    assert "11-XX" in code_index
    assert "14-XX" in code_index
    assert "11G" in code_index  # arithmetic algebraic geometry section
    assert "number theory" in code_index["11-XX"].lower()


def test_build_search_string_combinations():
    """The internal search-string builder honors all kwargs."""
    s = zb._build_search_string(query="zeta", author="Wiles", msc="11G05")
    assert "zeta" in s
    assert "au:Wiles" in s
    assert "cc:11G05" in s

    s2 = zb._build_search_string(year_range=(1990, 2000), author="Tao")
    assert "py:1990-2000" in s2
    assert "au:Tao" in s2

    s3 = zb._build_search_string(year=2020, msc="14H")
    assert "py:2020" in s3
    assert "cc:14H" in s3

    # No kwargs -> empty
    assert zb._build_search_string() == ""


# ---------------------------------------------------------------------------
# Live API tests
# ---------------------------------------------------------------------------

@_skip_no_net
def test_probe():
    """Should return True when network is reachable (gate already passed)."""
    assert zb.probe(timeout=10.0) is True


@_skip_no_net
def test_search_basic():
    """Free-text query for a famous theorem should return at least 1 hit
    with a populated title."""
    hits = zb.search(query="fermat last theorem", max_results=5)
    if not hits:
        pytest.skip("zbMATH search returned no results (transient).")
    assert len(hits) >= 1
    for h in hits:
        assert isinstance(h, dict)
        assert "title" in h and "authors" in h and "msc_codes" in h
    # At least one hit should mention "fermat" in title or keywords.
    blob = " ".join(
        ((h.get("title") or "") + " " + " ".join(h.get("keywords") or [])).lower()
        for h in hits
    )
    assert "fermat" in blob


@_skip_no_net
def test_search_msc():
    """Searching by MSC code 11G05 (elliptic curves over global fields)
    should yield many results."""
    hits = zb.by_msc("11G05", max_results=20)
    if not hits:
        pytest.skip("zbMATH MSC search returned no results (transient).")
    assert len(hits) >= 5
    # At least most of them should carry 11G05 (or a sibling 11G code).
    has_11g = sum(
        1 for h in hits
        if any((c or "").startswith("11G") for c in h.get("msc_codes") or [])
    )
    assert has_11g >= max(1, len(hits) // 2), \
        f"only {has_11g}/{len(hits)} hits had an 11G* MSC tag"


@_skip_no_net
def test_search_by_author():
    """by_author('Wiles') should return at least one paper, and at least one
    of those should genuinely list Wiles as an author."""
    hits = zb.by_author("Wiles", max_results=10)
    if not hits:
        pytest.skip("zbMATH by_author() returned no results (transient).")
    assert len(hits) >= 1
    saw_wiles = any(
        any("wiles" in a.lower() for a in h.get("authors") or [])
        for h in hits
    )
    assert saw_wiles, f"none of {len(hits)} hits actually list Wiles as author"


@_skip_no_net
def test_get_doc():
    """Fetch a known zbMATH ID — Wiles 1995 FLT proof, Zbl 0823.11029."""
    rec = zb.get("0823.11029")
    if rec is None:
        pytest.skip("zbMATH get() returned None (transient block).")
    assert isinstance(rec, dict)
    assert rec.get("zbmath_id") == "0823.11029"
    assert rec.get("title")
    assert isinstance(rec.get("authors"), list) and len(rec["authors"]) >= 1
    assert any("wiles" in a.lower() for a in rec["authors"])
    # Year should parse and look right.
    assert rec.get("year") in (1995, 1994, 1996)  # robust to slight variations


@_skip_no_net
def test_reviews_known_paper():
    """The Wiles paper has a famous Faltings review attached."""
    rev = zb.reviews("0823.11029")
    if rev is None:
        pytest.skip("zbMATH reviews() returned None (closed or transient).")
    assert isinstance(rev, dict)
    assert "review_text" in rev and rev["review_text"]
    assert isinstance(rev["review_text"], str)
    assert len(rev["review_text"]) > 50  # reviews are usually paragraphs


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
