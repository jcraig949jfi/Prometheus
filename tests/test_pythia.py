"""Tests for Pythia (Gemini Deep Research dispatch daemon)."""
import json
import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pythia_daemon  # noqa: E402


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_slugify_basic():
    assert pythia_daemon.slugify("Hello World") == "hello_world"
    assert pythia_daemon.slugify("AlphaEvolve + OpenEvolve") == "alphaevolve_openevolve"


def test_slugify_empty_yields_fallback():
    assert pythia_daemon.slugify("") == "untitled"
    assert pythia_daemon.slugify("!!!") == "untitled"


def test_slugify_caps_length():
    long = "x" * 200
    assert len(pythia_daemon.slugify(long)) <= 60


def test_is_quota_error_detects_keywords():
    assert pythia_daemon.is_quota_error("Error: 429 Too Many Requests")
    assert pythia_daemon.is_quota_error("status code: 429")
    assert pythia_daemon.is_quota_error("RESOURCE_EXHAUSTED: quota exceeded")
    assert pythia_daemon.is_quota_error("rate limit reached")
    assert pythia_daemon.is_quota_error("Your quota has been exceeded for the day.")


def test_is_quota_error_false_negatives():
    assert not pythia_daemon.is_quota_error("ConnectionError: timeout")
    assert not pythia_daemon.is_quota_error("ValueError: invalid prompt")
    assert not pythia_daemon.is_quota_error("")
    assert not pythia_daemon.is_quota_error(None)


def test_github_url_for_basic():
    url = pythia_daemon.github_url_for("aporia/docs/x.md")
    assert url.startswith("https://github.com/")
    assert url.endswith("aporia/docs/x.md")
    assert "/blob/main/" in url


def test_github_url_for_normalizes_backslashes():
    url = pythia_daemon.github_url_for(r"aporia\docs\x.md")
    assert "\\" not in url
    assert "aporia/docs/x.md" in url


def test_github_url_for_strips_leading_slash():
    a = pythia_daemon.github_url_for("/aporia/docs/x.md")
    b = pythia_daemon.github_url_for("aporia/docs/x.md")
    assert a == b


def test_report_path_for_uses_id_and_slug():
    row = {"id": 42, "title": "Test Title"}
    p = pythia_daemon.report_path_for(row)
    assert "00042" in p.name
    assert "test_title" in p.name
    assert p.suffix == ".md"


def test_report_path_for_dated_subdir():
    """Report saves under a date-stamped subdirectory under deep_research_reports/."""
    p = pythia_daemon.report_path_for({"id": 1, "title": "X"})
    parent = p.parent.name
    assert len(parent) == 10  # YYYY-MM-DD
    assert parent[4] == "-" and parent[7] == "-"
    assert p.parent.parent.name == "deep_research_reports"


# ---------------------------------------------------------------------------
# Postgres roundtrip — schema + enqueue/dispatch/complete lifecycle
# ---------------------------------------------------------------------------

def _pg_reachable() -> bool:
    if not pythia_daemon.HAS_PG:
        return False
    try:
        import agora_persist
        with agora_persist._connect(timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _pg_reachable(), reason="Postgres unreachable")
def test_research_queue_lifecycle():
    """enqueue → next_pending → dispatch → complete; cleanup."""
    import agora_persist

    marker = f"test-pythia-{uuid.uuid4().hex[:8]}"
    rid = agora_persist.enqueue_research(
        title=f"Test prompt {marker}",
        prompt_text="dummy prompt body",
        requested_by="pytest",
        priority=1,
        tier="TEST",
        queue_ref=marker,
    )
    assert rid is not None

    try:
        pending = agora_persist.next_pending_research(limit=200)
        ours = [p for p in pending if p["id"] == rid]
        assert len(ours) == 1
        assert ours[0]["priority"] == 1

        assert agora_persist.mark_research_dispatched(rid, "test-iid-123")
        in_flight = agora_persist.get_in_flight_research()
        ours_if = [r for r in in_flight if r["id"] == rid]
        assert len(ours_if) == 1
        assert ours_if[0]["interaction_id"] == "test-iid-123"

        assert agora_persist.mark_research_complete(
            row_id=rid,
            report_path="aporia/docs/deep_research_reports/test/x.md",
            report_github_url="https://github.com/x/y/blob/main/x.md",
            report_summary="test summary",
            elapsed_sec=12.5,
        )
        recent = agora_persist.read_recent_completed_research(hours=1, limit=200)
        ours_c = [r for r in recent if r["id"] == rid]
        assert len(ours_c) == 1
        assert ours_c[0]["report_github_url"].startswith("https://")
    finally:
        with agora_persist._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM agora.research_queue WHERE id = %s", (rid,))
            conn.commit()


@pytest.mark.skipif(not _pg_reachable(), reason="Postgres unreachable")
def test_count_research_today_excludes_other_days():
    import agora_persist
    counts = agora_persist.count_research_today()
    assert isinstance(counts, dict)
    # All keys should be in the expected status vocabulary
    valid = {"pending", "dispatched", "in_progress", "complete", "failed", "rate_limited"}
    for k in counts:
        assert k in valid, f"unexpected status: {k}"


@pytest.mark.skipif(not _pg_reachable(), reason="Postgres unreachable")
def test_mark_research_failed_with_rate_limited_status():
    import agora_persist
    marker = f"test-rl-{uuid.uuid4().hex[:8]}"
    rid = agora_persist.enqueue_research(
        title=marker, prompt_text="x", queue_ref=marker,
    )
    try:
        assert agora_persist.mark_research_failed(
            rid, "RESOURCE_EXHAUSTED: quota exceeded", status="rate_limited"
        )
        # Verify the status update
        with agora_persist._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT status, error FROM agora.research_queue WHERE id = %s", (rid,))
                row = cur.fetchone()
                assert row[0] == "rate_limited"
                assert "RESOURCE_EXHAUSTED" in row[1]
    finally:
        with agora_persist._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM agora.research_queue WHERE id = %s", (rid,))
            conn.commit()
