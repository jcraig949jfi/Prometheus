"""Tests for clio_quality (Clio v0.4)."""
import json
import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import clio_quality  # noqa: E402


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_pct_safe_on_zero_denom():
    assert clio_quality._pct(5, 0) == 0.0
    assert clio_quality._pct(0, 0) == 0.0


def test_pct_basic():
    assert clio_quality._pct(1, 4) == 25.0
    assert clio_quality._pct(3, 4) == 75.0
    assert clio_quality._pct(7, 11) == 63.64  # rounded


def test_round_or_none():
    assert clio_quality._round_or_none(None) is None
    assert clio_quality._round_or_none(1.234567) == 1.235
    assert clio_quality._round_or_none(1.234567, ndigits=1) == 1.2
    assert clio_quality._round_or_none("not-a-number") is None


def test_percentiles_empty_input():
    out = clio_quality._percentiles([])
    assert out == {"p25": None, "p50": None, "p75": None}


def test_percentiles_single_value():
    out = clio_quality._percentiles([0.5])
    assert out["p25"] == 0.5
    assert out["p50"] == 0.5
    assert out["p75"] == 0.5


def test_percentiles_known_values():
    out = clio_quality._percentiles([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    # numpy linear-interp default: p50 of 1..10 = 5.5
    assert out["p50"] == 5.5
    # p25 of 1..10 should be 3.25
    assert out["p25"] == 3.25
    # p75 of 1..10 should be 7.75
    assert out["p75"] == 7.75


def test_percentiles_skips_nones():
    out = clio_quality._percentiles([None, 1, None, 5, 9, None])
    # Effectively percentiles of [1, 5, 9]
    assert out["p50"] == 5.0


def test_gini_empty_returns_none():
    assert clio_quality._gini([]) is None
    assert clio_quality._gini([7]) is None
    assert clio_quality._gini([0, 0, 0]) is None  # total == 0


def test_gini_perfectly_even():
    # Equal counts -> Gini near 0
    g = clio_quality._gini([10, 10, 10, 10])
    assert g is not None
    assert abs(g) < 0.01


def test_gini_concentrated():
    # All weight on one bucket -> high Gini
    g = clio_quality._gini([1, 1, 1, 100])
    assert g is not None
    assert g > 0.5


# ---------------------------------------------------------------------------
# render_snapshot — pure
# ---------------------------------------------------------------------------

SAMPLE_SNAPSHOT = {
    "computed_at": "2026-05-18T12:00:00Z",
    "window_hours": 24,
    "papers_24h": 200,
    "claims_extracted_24h": 540,
    "claims_submitted_24h": 530,
    "papers_attempted_24h": 200,
    "papers_with_zero_claims_pct": 5.0,
    "claims_per_paper_mean": 2.7,
    "claims_per_paper_p25": 2,
    "claims_per_paper_p50": 3,
    "claims_per_paper_p75": 3,
    "claim_type_known_pct": 96.0,
    "paradigm_hint_pct": 78.0,
    "open_problem_hint_pct": 22.0,
    "falsifiable_pct": 88.0,
    "confidence_mean": 0.84,
    "confidence_p25": 0.75,
    "confidence_p50": 0.85,
    "confidence_p75": 0.92,
    "claim_text_length_mean": 142.3,
    "paradigm_coverage_count": 18,
    "paradigm_distribution": {"P15": 87, "P22": 60, "P04": 41, "P01": 33, "P16": 27, "P30": 25},
    "paradigm_distribution_gini": 0.41,
    "sigma_submission_error_count": 2,
    "sigma_submission_error_pct": 0.38,
    "theorem_claims_submitted_24h": 210,
    "theorem_with_counterexample_kill_path_pct": 100.0,
    "query_yield": [
        {"query": "tensor decomposition", "papers": 20, "claims": 55, "claims_per_paper": 2.75},
    ],
}


def test_render_includes_headline_numbers():
    text = clio_quality.render_snapshot(SAMPLE_SNAPSHOT)
    assert "papers_24h:          200" in text
    assert "claims_extracted_24h: 540" in text
    assert "paradigm_coverage_count: 18 / 30" in text


def test_render_surfaces_theorem_kill_path_canary():
    text = clio_quality.render_snapshot(SAMPLE_SNAPSHOT)
    assert "theorem_with_counterexample_kill_path_pct" in text
    assert "canary" in text.lower()


def test_render_handles_empty_snapshot():
    empty = {"computed_at": "now", "window_hours": 24}
    text = clio_quality.render_snapshot(empty)
    assert "papers_24h:          0" in text
    assert "paradigm_coverage_count: 0" in text


# ---------------------------------------------------------------------------
# compute_quality_snapshot with mocked connection
# ---------------------------------------------------------------------------

class FakeCursor:
    """Records queries; returns canned results in sequence."""

    def __init__(self, results: list):
        self._results = list(results)
        self.executed: list[tuple] = []
        self._last = None

    def execute(self, sql, params=()):
        self.executed.append((sql.strip()[:80], params))
        self._last = self._results.pop(0) if self._results else None

    def fetchone(self):
        if isinstance(self._last, list):
            return self._last[0] if self._last else None
        return self._last

    def fetchall(self):
        return self._last if isinstance(self._last, list) else []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeConn:
    def __init__(self, results):
        self._cursor = FakeCursor(results)

    def cursor(self, **kw):
        return self._cursor

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_compute_quality_snapshot_with_mocks():
    """Verify the snapshot dict has all expected top-level keys with mocked DB."""
    # Result sequence matches the order of cur.execute calls in
    # compute_quality_snapshot via the four collector helpers.
    results = [
        # _collect_volume — 3 scalar SELECT COUNT
        [(200,)],
        [(540,)],
        [(530,)],
        # _collect_yield — papers with claim counts
        [(1, 3), (2, 2), (3, 0), (4, 4)],
        # _collect_specificity — rows of (claim_type, paradigm, open_p, falsifiable, conf, text_len)
        [
            ("theorem", "P15", None, True, 0.9, 140),
            ("conjecture", "P22", "RH-adjacent", True, 0.7, 110),
            ("empirical", None, None, False, 0.5, 80),
        ],
        # _collect_diversity — paradigm rows
        [("P15", 5), ("P22", 3), ("P04", 1)],
        # _collect_diversity — query rows
        [("query A", 10, 25), ("query B", 8, 16)],
        # _collect_failure_modes — sigma errors / submitted / theorem-counterex / theorem-submitted
        [(2,)],
        [(530,)],
        [(210,)],
        [(210,)],
    ]

    def connect_fn():
        return FakeConn(results)

    snap = clio_quality.compute_quality_snapshot(window_hours=24, connect_fn=connect_fn)

    # Headline keys present
    assert snap["window_hours"] == 24
    assert "computed_at" in snap
    assert snap["papers_24h"] == 200
    assert snap["claims_extracted_24h"] == 540
    assert snap["claims_submitted_24h"] == 530

    # Yield
    assert snap["papers_attempted_24h"] == 4
    assert snap["claims_per_paper_mean"] is not None
    # papers with zero claims: paper id 3 -> 0 claims; 1 of 4
    assert snap["papers_with_zero_claims_pct"] == 25.0

    # Specificity (3 claims; 2 with paradigm; 2 falsifiable)
    assert snap["paradigm_hint_pct"] == round(100 * 2 / 3, 2)
    assert snap["falsifiable_pct"] == round(100 * 2 / 3, 2)
    assert snap["confidence_mean"] is not None
    assert snap["claim_type_known_pct"] == 100.0  # all 3 have a type

    # Diversity
    assert snap["paradigm_coverage_count"] == 3
    assert snap["paradigm_distribution"]["P15"] == 5
    assert isinstance(snap["query_yield"], list)
    assert snap["query_yield"][0]["papers"] == 10

    # Failure-mode canary
    assert snap["sigma_submission_error_count"] == 2
    assert snap["theorem_claims_submitted_24h"] == 210
    assert snap["theorem_with_counterexample_kill_path_pct"] == 100.0


# ---------------------------------------------------------------------------
# Postgres integration test — seed + compute + rollback
# ---------------------------------------------------------------------------

def _pg_reachable() -> bool:
    if not clio_quality.HAS_PG:
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
def test_quality_snapshot_against_real_postgres_with_seeded_data():
    """Seed a few rows in a savepoint, compute, assert headline numbers, rollback.

    Uses a savepoint to isolate from live data: paper/extraction inserts roll
    back cleanly. The compute_quality_snapshot uses its own connection so we
    can't reuse our seeding connection — but the seeded rows are committed
    via the savepoint window; we use a marker query_matched value to scope
    our reads and then DELETE them at the end as a safety net.
    """
    import agora_persist

    marker = f"clio_quality_test_{uuid.uuid4().hex[:8]}"
    # Insert two papers under the marker, one with claims, one without
    with agora_persist._connect() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.clio_papers (source, external_id, title, abstract, url,
                                                   authors, query_matched, arxiv_categories,
                                                   pub_date, cycle_id, raw_json)
                    VALUES ('arxiv', %s, 'Test paper with claims', 'abstract',
                            'http://x.test', %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (f"{marker}_a", ["A. Author"], marker, ["math.NT"], "2026-01-01",
                      str(uuid.uuid4()), json.dumps({"marker": marker})))
                p1 = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO agora.clio_papers (source, external_id, title, abstract, url,
                                                   authors, query_matched, arxiv_categories,
                                                   pub_date, cycle_id, raw_json)
                    VALUES ('arxiv', %s, 'Test paper no claims', 'abstract',
                            'http://x.test', %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (f"{marker}_b", ["B. Author"], marker, ["math.NT"], "2026-01-01",
                      str(uuid.uuid4()), json.dumps({"marker": marker})))
                p2 = cur.fetchone()[0]
                # Two claims on p1: one theorem with paradigm, one conjecture without
                cur.execute("""
                    INSERT INTO agora.clio_claim_extractions
                        (paper_id, claim_index, claim_text, claim_type, paradigm_hint,
                         falsifiable, confidence, extractor_model, raw_llm_response)
                    VALUES (%s, 0, 'Test theorem claim X', 'theorem', 'P15', true, 0.9, 'mock', '{}'),
                           (%s, 1, 'Test conjecture claim Y', 'conjecture', NULL, true, 0.7, 'mock', '{}')
                """, (p1, p1))
                # p2 has no claims (zero-claim case)
            conn.commit()

            # Compute snapshot. The compute query uses a 24h window; our seeded
            # rows are within that. The marker lets us assert specific numbers
            # by filtering, but compute_quality_snapshot is global. So we make
            # narrower assertions: it ran without error and our rows are
            # included (papers_24h >= 2, etc.).
            snap = clio_quality.compute_quality_snapshot(window_hours=24)

            assert snap["papers_24h"] >= 2
            assert snap["claims_extracted_24h"] >= 2
            # Paradigm coverage at least includes P15 (or matches what we inserted)
            assert snap["paradigm_coverage_count"] >= 1
            assert "P15" in (snap.get("paradigm_distribution") or {})

            # Confidence statistics must be in expected range
            assert snap["confidence_mean"] is not None
            assert 0.0 <= snap["confidence_mean"] <= 1.0

            # The query_yield list should reference our marker
            yields = snap.get("query_yield") or []
            matched = [y for y in yields if y["query"].startswith(marker)]
            assert len(matched) == 1
            assert matched[0]["papers"] == 2
            assert matched[0]["claims"] == 2
            assert matched[0]["claims_per_paper"] == 1.0
        finally:
            # Cleanup — DELETE our marker rows
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM agora.clio_claim_extractions "
                        "WHERE paper_id IN (SELECT id FROM agora.clio_papers WHERE query_matched = %s)",
                        (marker,),
                    )
                    cur.execute(
                        "DELETE FROM agora.clio_papers WHERE query_matched = %s",
                        (marker,),
                    )
                conn.commit()
            except Exception:
                conn.rollback()


@pytest.mark.skipif(not _pg_reachable(), reason="Postgres unreachable")
def test_quality_snapshot_roundtrip_via_persistence():
    """Persist a fake snapshot, read it back, verify shape."""
    import agora_persist
    marker = f"qtest-{uuid.uuid4().hex[:8]}"
    fake = {"marker": marker, "papers_24h": 999, "claims_extracted_24h": 0}
    sid = agora_persist.write_clio_quality_snapshot(window_hours=24, metrics=fake)
    assert sid is not None
    rows = agora_persist.read_recent_clio_quality_snapshots(limit=10)
    matched = [r for r in rows if (r["metrics"] if isinstance(r["metrics"], dict)
                                   else json.loads(r["metrics"])).get("marker") == marker]
    assert len(matched) == 1
    # Cleanup
    with agora_persist._connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM agora.clio_quality_snapshots WHERE id = %s", (sid,))
        conn.commit()
