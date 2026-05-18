"""Tests for Clio paper-mining daemon (v0.1).

Cover the testable seams:
  - load_config: required-field validation
  - PaperIndex: fingerprint logic + persist/reload + dedup
  - _build_arxiv_url: query encoding
  - _parse_arxiv_atom: Atom feed parsing (pure, no I/O)
  - scan_arxiv_query: composition with injected fetcher
  - run_cycle: end-to-end with mock fetcher + mock persister

Postgres roundtrip is exercised only if PG is reachable; otherwise skipped.
"""
import json
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import clio_daemon  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ARXIV_ATOM_SAMPLE = b'''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2605.01234v1</id>
    <title>A new tensor decomposition algorithm for the cap-set problem</title>
    <summary>We present a polynomial-method-based tensor decomposition
that improves the cap-set bound.</summary>
    <published>2026-05-10T00:00:00Z</published>
    <author><name>Jane Smith</name></author>
    <author><name>Bob Jones</name></author>
    <category term="math.CO" />
    <category term="math.NT" />
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2605.05678v2</id>
    <title>Mahler measure of Lehmer-type polynomials</title>
    <summary>We study Mahler measures of a family of polynomials.</summary>
    <published>2026-05-11T00:00:00Z</published>
    <author><name>Alice Brown</name></author>
    <category term="math.NT" />
  </entry>
</feed>'''


@pytest.fixture
def tmp_config(tmp_path):
    """Minimal config that load_config will accept."""
    cfg_yaml = textwrap.dedent('''
        agent_name: "Clio-test"
        machine: "M1"
        scan_interval_sec: 3600
        paper_index_path: "data/clio_test/paper_index.json"
        arxiv_queries:
          - query: 'all:"tensor decomposition" AND cat:math.NA'
            max_results: 5
            priority: 1
        arxiv_min_interval_sec: 0.0
        http_timeout_sec: 30
    ''').strip()
    p = tmp_path / "clio_config.yaml"
    p.write_text(cfg_yaml, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------

def test_config_loads(tmp_config):
    cfg = clio_daemon.load_config(tmp_config)
    assert cfg["agent_name"] == "Clio-test"
    assert len(cfg["arxiv_queries"]) == 1
    assert cfg["arxiv_queries"][0]["query"].startswith("all:")


def test_config_rejects_missing_queries(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("agent_name: Clio\nscan_interval_sec: 3600\n", encoding="utf-8")
    with pytest.raises(ValueError, match="arxiv_queries"):
        clio_daemon.load_config(p)


def test_config_rejects_empty_queries(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("arxiv_queries: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="arxiv_queries"):
        clio_daemon.load_config(p)


# ---------------------------------------------------------------------------
# URL builder tests
# ---------------------------------------------------------------------------

def test_build_arxiv_url_encodes_query():
    url = clio_daemon._build_arxiv_url('all:"tensor decomposition"', max_results=20)
    assert "export.arxiv.org/api/query" in url
    # Query string must be URL-encoded (spaces -> +, quotes -> %22)
    assert "tensor+decomposition" in url or "tensor%20decomposition" in url
    assert "max_results=20" in url
    assert "sortBy=submittedDate" in url
    assert "sortOrder=descending" in url


def test_build_arxiv_url_respects_max_results():
    url = clio_daemon._build_arxiv_url("all:foo", max_results=5)
    assert "max_results=5" in url


# ---------------------------------------------------------------------------
# XML parser tests (pure, no I/O)
# ---------------------------------------------------------------------------

def test_parse_arxiv_atom_returns_list():
    papers = clio_daemon._parse_arxiv_atom(ARXIV_ATOM_SAMPLE)
    assert isinstance(papers, list)
    assert len(papers) == 2


def test_parse_arxiv_atom_extracts_fields():
    papers = clio_daemon._parse_arxiv_atom(ARXIV_ATOM_SAMPLE)
    p = papers[0]
    assert p["source"] == "arxiv"
    assert p["external_id"] == "2605.01234v1"
    assert "tensor decomposition" in p["title"].lower()
    assert "polynomial-method" in p["abstract"].lower()
    assert p["pub_date"] == "2026-05-10"
    assert "Jane Smith" in p["authors"]
    assert "Bob Jones" in p["authors"]
    assert "math.CO" in p["arxiv_categories"]
    assert "math.NT" in p["arxiv_categories"]


def test_parse_arxiv_atom_handles_malformed():
    papers = clio_daemon._parse_arxiv_atom(b"<not-xml>")
    assert papers == []


def test_parse_arxiv_atom_normalizes_whitespace_in_title():
    papers = clio_daemon._parse_arxiv_atom(ARXIV_ATOM_SAMPLE)
    for p in papers:
        # No double spaces, no leading/trailing whitespace
        assert "  " not in p["title"]
        assert p["title"] == p["title"].strip()


# ---------------------------------------------------------------------------
# PaperIndex tests
# ---------------------------------------------------------------------------

def test_paper_index_dedupes_by_external_id(tmp_path):
    idx = clio_daemon.PaperIndex(tmp_path / "idx.json")
    paper = {"external_id": "2605.01234v1", "title": "X", "authors": ["A"], "pub_date": "2026-01"}
    assert not idx.is_known(paper)
    idx.add(paper)
    assert idx.is_known(paper)


def test_paper_index_dedupes_by_title_author_year_when_no_external_id(tmp_path):
    idx = clio_daemon.PaperIndex(tmp_path / "idx.json")
    p1 = {"title": "On the X conjecture", "authors": ["Smith"], "pub_date": "2026-05-10"}
    p2 = {"title": "On the X Conjecture", "authors": ["Smith"], "pub_date": "2026-05-15"}  # same year
    idx.add(p1)
    assert idx.is_known(p2)  # fingerprint normalization should match


def test_paper_index_persists_and_reloads(tmp_path):
    idx_path = tmp_path / "idx.json"
    idx1 = clio_daemon.PaperIndex(idx_path)
    paper = {"external_id": "abs.X", "title": "T"}
    idx1.add(paper)
    idx1.save()

    idx2 = clio_daemon.PaperIndex(idx_path)
    assert idx2.is_known(paper)
    assert len(idx2.index) == 1


def test_paper_index_increments_seen_count(tmp_path):
    idx = clio_daemon.PaperIndex(tmp_path / "idx.json")
    paper = {"external_id": "abs.X", "title": "T"}
    idx.add(paper)
    idx.add(paper)
    entry = idx.index[clio_daemon.PaperIndex.fingerprint(paper)]
    assert entry["seen_count"] == 2


# ---------------------------------------------------------------------------
# scan_arxiv_query — composition with injected fetcher
# ---------------------------------------------------------------------------

def test_scan_arxiv_query_uses_injected_fetcher():
    called_with = {}

    def fake_fetcher(url):
        called_with["url"] = url
        return ARXIV_ATOM_SAMPLE

    papers = clio_daemon.scan_arxiv_query("all:foo", max_results=5, fetcher=fake_fetcher)
    assert "all:foo" in called_with["url"] or "all%3Afoo" in called_with["url"]
    assert len(papers) == 2


def test_scan_arxiv_query_returns_empty_on_fetcher_error():
    def bad_fetcher(url):
        raise RuntimeError("network down")
    papers = clio_daemon.scan_arxiv_query("all:foo", max_results=5, fetcher=bad_fetcher)
    assert papers == []


# ---------------------------------------------------------------------------
# run_cycle end-to-end with injected fetcher + persister
# ---------------------------------------------------------------------------

def test_run_cycle_persists_new_papers_only(tmp_path, tmp_config):
    cfg = clio_daemon.load_config(tmp_config)
    idx = clio_daemon.PaperIndex(tmp_path / "idx.json")
    persisted = []

    def fake_persister(paper, query, cycle_id):
        persisted.append((paper["external_id"], query, cycle_id))
        return True

    def fake_fetcher(url):
        return ARXIV_ATOM_SAMPLE

    stats = clio_daemon.run_cycle(
        cfg, paper_index=idx, fetcher=fake_fetcher, persister=fake_persister,
    )
    assert stats["queries_run"] == 1
    assert stats["papers_found"] == 2
    assert stats["papers_new"] == 2
    assert len(persisted) == 2
    assert all(t[1] == cfg["arxiv_queries"][0]["query"] for t in persisted)


def test_run_cycle_skips_known_papers(tmp_path, tmp_config):
    cfg = clio_daemon.load_config(tmp_config)
    idx = clio_daemon.PaperIndex(tmp_path / "idx.json")
    # Pre-populate the index with one of the sample papers
    idx.add({"external_id": "2605.01234v1", "title": "..."})

    persisted = []

    def fake_persister(paper, query, cycle_id):
        persisted.append(paper["external_id"])
        return True

    def fake_fetcher(url):
        return ARXIV_ATOM_SAMPLE

    stats = clio_daemon.run_cycle(
        cfg, paper_index=idx, fetcher=fake_fetcher, persister=fake_persister,
    )
    # One paper was known, only the other should be persisted
    assert stats["papers_found"] == 2
    assert stats["papers_new"] == 1
    assert persisted == ["2605.05678v2"]


def test_run_cycle_returns_per_query_stats(tmp_path, tmp_config):
    cfg = clio_daemon.load_config(tmp_config)
    idx = clio_daemon.PaperIndex(tmp_path / "idx.json")

    def fake_fetcher(url):
        return ARXIV_ATOM_SAMPLE

    def noop_persister(p, q, c):
        return True

    stats = clio_daemon.run_cycle(cfg, paper_index=idx, fetcher=fake_fetcher, persister=noop_persister)
    assert "per_query" in stats
    assert len(stats["per_query"]) == 1
    assert stats["per_query"][0]["found"] == 2
    assert stats["per_query"][0]["new"] == 2


def test_run_cycle_has_cycle_id_and_timing(tmp_path, tmp_config):
    cfg = clio_daemon.load_config(tmp_config)
    idx = clio_daemon.PaperIndex(tmp_path / "idx.json")

    def fake_fetcher(url):
        return ARXIV_ATOM_SAMPLE

    def noop_persister(p, q, c):
        return True

    stats = clio_daemon.run_cycle(cfg, paper_index=idx, fetcher=fake_fetcher, persister=noop_persister)
    assert "cycle_id" in stats
    assert len(stats["cycle_id"]) == 36  # UUID
    assert stats["duration_sec"] >= 0


# ---------------------------------------------------------------------------
# Postgres roundtrip — only if reachable
# ---------------------------------------------------------------------------

def _pg_reachable() -> bool:
    if not clio_daemon.HAS_PG:
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


@pytest.mark.skipif(not _pg_reachable(), reason="Postgres unreachable from this machine")
def test_postgres_clio_papers_roundtrip():
    """Insert a marker paper, read it back via the recent-papers query, clean up."""
    import agora_persist
    import uuid

    marker_ext = f"test-clio-{uuid.uuid4().hex[:8]}"
    ok = agora_persist.write_clio_paper(
        source="arxiv",
        external_id=marker_ext,
        title="TEST-CLIO marker",
        abstract="test abstract",
        url=f"http://example.test/{marker_ext}",
        authors=["Test, A."],
        query_matched="test_query",
        arxiv_categories=["test.X"],
        pub_date="2026-05-18",
        cycle_id=str(uuid.uuid4()),
        raw_json={"marker": marker_ext},
    )
    assert ok

    found = agora_persist.read_recent_clio_papers(hours=1, limit=200)
    titles = [p.get("title") for p in found]
    assert "TEST-CLIO marker" in titles

    # Cleanup
    with agora_persist._connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM agora.clio_papers WHERE external_id = %s", (marker_ext,))
        conn.commit()
