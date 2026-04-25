"""Tests for prometheus_math.databases.arxiv_corpus.

The corpus is a local on-disk cache; the tests fabricate a synthetic
corpus under ``tmp_path`` (via ``PROMETHEUS_DATA_DIR``) so they never
hit the network and never touch the user's real corpus directory.

Live downloads run only when ``PROMETHEUS_DOWNLOAD_ARXIV_CORPUS=1`` is
set in the environment.

Test coverage by math-tdd category (target >= 2 each):

    Authority:   - corpus_stats matches authoritative hand-counted truth
                   over a synthetic corpus we wrote ourselves.
                 - get_by_id with the canonical version-stripping
                   convention is checked against arXiv's documented id
                   format.
                 - search ranks an FV-keyword paper above a control
                   paper (authority on the curated query intent).
                 - tags_index agrees with the ground-truth categories
                   we hand-wrote into the synthetic corpus.

    Property:    - search results are ordered by score descending.
                 - search is case-insensitive.
                 - get_by_id is consistent with the stored record
                   (round-trip).
                 - update_corpus's curated query string is
                   well-formed (idempotent under repeat calls).

    Edge:        - empty corpus dir: stats / search / tags_index all
                   degrade cleanly (no exception).
                 - get_by_id with bogus / empty / version-suffixed id.
                 - search with empty query, zero limit, year_range that
                   excludes everything.
                 - corrupt JSON file is ignored, not raised.

    Composition: - search -> get_by_id round-trip preserves data.
                 - tags_index keys are exactly the set of paper ids
                   reachable via get_by_id (and stats agree on count).
                 - probe() returns True once any paper exists
                   (composes file-system state with availability).
"""
from __future__ import annotations

import importlib
import json
import os
import pathlib

import pytest


# ---------------------------------------------------------------------------
# Fixture: synthetic corpus under tmp_path
# ---------------------------------------------------------------------------

_FAKE_PAPERS: list[dict] = [
    {
        "id": "2401.00001",
        "title": "A Lean formalization of the prime number theorem",
        "authors": ["Alice Lean", "Bob Mathlib"],
        "abstract": (
            "We present a complete formal proof of the prime number theorem "
            "in the Lean theorem prover, building on mathlib. Our development "
            "highlights modular arithmetic and analytic number theory."
        ),
        "categories": ["math.NT", "cs.LO"],
        "published": "2024-01-15T00:00:00+00:00",
        "updated": "2024-02-01T00:00:00+00:00",
        "pdf_url": "https://arxiv.org/pdf/2401.00001",
    },
    {
        "id": "2402.00002",
        "title": "Coq proof of quadratic reciprocity",
        "authors": ["Carol Coq"],
        "abstract": (
            "A formalization in Coq of Gauss's law of quadratic reciprocity. "
            "We compare the proof with prior Lean and Isabelle developments."
        ),
        "categories": ["math.NT", "math.LO"],
        "published": "2024-02-20T00:00:00+00:00",
        "updated": "2024-02-20T00:00:00+00:00",
        "pdf_url": "https://arxiv.org/pdf/2402.00002",
    },
    {
        "id": "2103.99999",
        "title": "On L-functions of elliptic curves",
        "authors": ["Dan Diamond"],
        "abstract": (
            "We study the analytic continuation of L-functions attached to "
            "elliptic curves over number fields. No formal verification is "
            "discussed."
        ),
        "categories": ["math.NT"],
        "published": "2021-03-10T00:00:00+00:00",
        "updated": "2021-03-10T00:00:00+00:00",
        "pdf_url": "https://arxiv.org/pdf/2103.99999",
    },
    {
        "id": "1907.12345",
        "title": "Type theory and dependent types in Isabelle",
        "authors": ["Eve Isabelle"],
        "abstract": (
            "A discussion of dependent type theory implementations in the "
            "Isabelle proof assistant, with comparisons to Lean and Coq."
        ),
        "categories": ["cs.LO", "math.LO"],
        "published": "2019-07-04T00:00:00+00:00",
        "updated": "2019-07-04T00:00:00+00:00",
        "pdf_url": "https://arxiv.org/pdf/1907.12345",
    },
]


def _reload_module():
    """Force a fresh import after PROMETHEUS_DATA_DIR has been monkey-patched.

    The :mod:`prometheus_math.databases._local` module caches the
    resolved data dir in a module-level global. We blow away that cache
    AND reload the corpus module so its ``_corpus_dir`` resolves under
    the new env var.
    """
    from prometheus_math.databases import _local
    _local._DATA_DIR = None
    import prometheus_math.databases.arxiv_corpus as ac
    importlib.reload(ac)
    return ac


@pytest.fixture
def corpus(tmp_path: pathlib.Path, monkeypatch):
    """Materialize ``_FAKE_PAPERS`` on disk, return the reloaded module."""
    monkeypatch.setenv("PROMETHEUS_DATA_DIR", str(tmp_path))
    ac = _reload_module()
    base = pathlib.Path(ac._corpus_dir())
    for p in _FAKE_PAPERS:
        with (base / f"{p['id']}.json").open("w", encoding="utf-8") as fh:
            json.dump(p, fh)
    return ac


@pytest.fixture
def empty_corpus(tmp_path: pathlib.Path, monkeypatch):
    """Empty (but resolvable) corpus directory."""
    monkeypatch.setenv("PROMETHEUS_DATA_DIR", str(tmp_path))
    return _reload_module()


# ---------------------------------------------------------------------------
# Authority-based tests
# ---------------------------------------------------------------------------

def test_authority_corpus_stats_matches_hand_count(corpus):
    """corpus_stats over our hand-built fixture must match its ground truth.

    Reference: ``_FAKE_PAPERS`` defined above. Hand-counted:
      - n_papers = 4
      - 'math.NT' appears in papers 2401.00001, 2402.00002, 2103.99999
        -> count 3
      - 'cs.LO' in 2401.00001 and 1907.12345 -> count 2
      - 'math.LO' in 2402.00002 and 1907.12345 -> count 2
      - years: 2024 -> 2, 2021 -> 1, 2019 -> 1
    """
    s = corpus.corpus_stats()
    assert s["n_papers"] == 4
    assert s["by_category"]["math.NT"] == 3
    assert s["by_category"]["cs.LO"] == 2
    assert s["by_category"]["math.LO"] == 2
    assert s["by_year"][2024] == 2
    assert s["by_year"][2021] == 1
    assert s["by_year"][2019] == 1
    assert s["total_size_bytes"] > 0


def test_authority_tags_index_matches_ground_truth(corpus):
    """tags_index should reproduce the categories we hand-wrote.

    Authoritative reference: ``_FAKE_PAPERS`` is the source of truth
    for this synthetic corpus.
    """
    idx = corpus.tags_index()
    assert set(idx.keys()) == {p["id"] for p in _FAKE_PAPERS}
    for paper in _FAKE_PAPERS:
        assert sorted(idx[paper["id"]]) == sorted(paper["categories"])


def test_authority_search_ranks_lean_paper_first(corpus):
    """A query matching FV keywords must rank the FV paper above a control.

    Authoritative intent of the curated corpus is to surface
    formal-verification papers. The "L-functions" paper (2103.99999)
    deliberately disclaims FV in its abstract; querying 'Lean' should
    NOT return it ahead of the actual Lean paper (2401.00001).
    """
    hits = corpus.search("Lean", limit=5)
    assert len(hits) >= 1
    assert hits[0]["id"] == "2401.00001"
    # The L-functions paper shouldn't surface for 'Lean' at all.
    assert all(h["id"] != "2103.99999" for h in hits)


def test_authority_get_by_id_strips_arxiv_version(corpus):
    """arXiv documents 'NNNN.NNNNN' as the canonical id and 'vN' as the
    optional version suffix. get_by_id must accept both forms.

    Reference: https://arxiv.org/help/arxiv_identifier
    """
    rec = corpus.get_by_id("2401.00001v3")
    assert rec is not None
    assert rec["id"] == "2401.00001"
    rec2 = corpus.get_by_id("arXiv:2401.00001")
    assert rec2 is not None
    assert rec2["id"] == "2401.00001"


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------

def test_property_search_results_sorted_by_score_desc(corpus):
    """Property: search results must be in non-increasing score order."""
    hits = corpus.search("Lean Coq Isabelle", limit=10)
    assert len(hits) >= 2
    for a, b in zip(hits, hits[1:]):
        assert a["score"] >= b["score"], (
            f"out-of-order: {a['id']}={a['score']} < {b['id']}={b['score']}"
        )


def test_property_search_case_insensitive(corpus):
    """Property: query case must not change the result set."""
    lower = [h["id"] for h in corpus.search("lean", limit=10)]
    upper = [h["id"] for h in corpus.search("LEAN", limit=10)]
    mixed = [h["id"] for h in corpus.search("LeAn", limit=10)]
    assert lower == upper == mixed
    assert len(lower) >= 1


def test_property_round_trip_preserves_record(corpus):
    """Property: get_by_id(rec['id']) returns the same canonical fields."""
    for paper in _FAKE_PAPERS:
        got = corpus.get_by_id(paper["id"])
        assert got is not None, f"missing {paper['id']}"
        for k in ("id", "title", "abstract", "pdf_url"):
            assert got[k] == paper[k]
        assert sorted(got["categories"]) == sorted(paper["categories"])
        assert sorted(got["authors"]) == sorted(paper["authors"])


def test_property_curated_query_is_well_formed(corpus):
    """Property: the curated query is non-empty, mentions every requested
    category, and includes at least one formal-verification keyword.
    Calling the builder repeatedly with the same input is idempotent.
    """
    q1 = corpus._build_curated_query(["math.LO", "math.NT"])
    q2 = corpus._build_curated_query(["math.LO", "math.NT"])
    assert q1 == q2  # idempotent
    assert "cat:math.LO" in q1
    assert "cat:math.NT" in q1
    assert "Lean" in q1
    # Default fallback when given empty input
    q3 = corpus._build_curated_query([])
    for c in corpus.DEFAULT_CATEGORIES:
        assert f"cat:{c}" in q3


def test_property_year_range_filters_results(corpus):
    """Property: year_range=(lo, hi) excludes everything published outside
    [lo, hi]; the count inside the window is monotone in the window size.
    """
    narrow = corpus.search("formal", limit=10, year_range=(2024, 2024))
    wide = corpus.search("formal", limit=10, year_range=(2019, 2024))
    for h in narrow:
        assert int(h["published"][:4]) == 2024
    assert len(wide) >= len(narrow)


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_empty_corpus_returns_empty_results(empty_corpus):
    """Edges:
      - corpus_stats over an empty dir: 0 papers, 0 bytes.
      - search returns [].
      - tags_index returns {}.
      - get_by_id returns None.
      - probe returns whatever the live arxiv check says — but must not
        raise.
    """
    stats = empty_corpus.corpus_stats()
    assert stats["n_papers"] == 0
    assert stats["by_category"] == {}
    assert stats["by_year"] == {}
    assert empty_corpus.search("anything", limit=5) == []
    assert empty_corpus.tags_index() == {}
    assert empty_corpus.get_by_id("nonexistent.id") is None
    # probe must not raise even when offline.
    _ = empty_corpus.probe(timeout=0.1)


def test_edge_get_by_id_bogus_inputs(corpus):
    """Edges for get_by_id: empty string, None-ish, with version, missing."""
    assert corpus.get_by_id("") is None
    assert corpus.get_by_id(None) is None
    assert corpus.get_by_id("not-an-id") is None
    # Version-stripped lookup of a missing id stays None.
    assert corpus.get_by_id("9999.99999v2") is None
    # Real id with version works.
    assert corpus.get_by_id("2401.00001v17") is not None


def test_edge_search_pathological_inputs(corpus):
    """Edges for search:
      - empty query -> []
      - whitespace-only query -> []
      - limit=0 -> []
      - year_range that excludes everything -> []
      - no-match query -> []
    """
    assert corpus.search("", limit=10) == []
    assert corpus.search("   ", limit=10) == []
    assert corpus.search("Lean", limit=0) == []
    assert corpus.search("Lean", limit=10, year_range=(3000, 3001)) == []
    assert corpus.search("zzzqxxxnotaword", limit=10) == []


def test_edge_corrupt_json_is_ignored(corpus, tmp_path):
    """A corrupt JSON file must NOT crash search or stats."""
    base = pathlib.Path(corpus._corpus_dir())
    (base / "9999.99998.json").write_text("{not valid json", encoding="utf-8")
    # Reading a paper missing required fields also tolerated.
    (base / "9999.99997.json").write_text(json.dumps({"id": "x"}),
                                          encoding="utf-8")
    # Should still return the 4 valid papers, ignoring the 2 broken ones.
    assert corpus.corpus_stats()["n_papers"] == 4
    assert len(corpus.search("Lean", limit=10)) >= 1


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------

def test_composition_search_then_get_by_id_round_trip(corpus):
    """Composition: every search hit must resolve via get_by_id, and the
    underlying record (excluding the synthesized 'score' field) must be
    bit-equal between the two paths.
    """
    hits = corpus.search("Lean", limit=5)
    assert len(hits) >= 1
    for h in hits:
        rec = corpus.get_by_id(h["id"])
        assert rec is not None, f"search returned {h['id']} but get_by_id missed it"
        # Drop the synthesized score before comparing.
        h_no_score = {k: v for k, v in h.items() if k != "score"}
        assert rec == h_no_score


def test_composition_tags_index_agrees_with_stats_and_get_by_id(corpus):
    """Composition across tags_index, corpus_stats, and get_by_id.

      - len(tags_index) == corpus_stats['n_papers']
      - every key in tags_index resolves via get_by_id
      - every category count in corpus_stats equals the number of papers
        in tags_index whose category list contains that category.
    """
    idx = corpus.tags_index()
    stats = corpus.corpus_stats()
    assert len(idx) == stats["n_papers"]
    for aid in idx:
        assert corpus.get_by_id(aid) is not None
    for cat, expected in stats["by_category"].items():
        actual = sum(1 for cats in idx.values() if cat in cats)
        assert actual == expected, f"mismatch on {cat}: stats={expected} idx={actual}"


def test_composition_probe_is_true_when_corpus_nonempty(corpus):
    """Composition of file-system state with the probe contract.

    By construction the fixture wrote 4 JSONs, so probe must return True
    purely from the on-disk check (i.e. without needing the network).
    """
    # Sanity: the fixture really did write papers.
    assert any(pathlib.Path(corpus._corpus_dir()).glob("*.json"))
    assert corpus.probe(timeout=0.0) is True


def test_composition_probe_falls_back_to_live_when_empty(empty_corpus,
                                                         monkeypatch):
    """When the corpus is empty, probe consults the live arxiv module
    (if available). We monkey-patch its .probe to a known value and
    confirm composition: empty corpus + live=True -> True; empty
    corpus + live=False -> False.
    """
    if empty_corpus._live_arxiv is None:
        pytest.skip("arxiv pip pkg not installed; live fallback unreachable")
    monkeypatch.setattr(empty_corpus._live_arxiv, "probe",
                        lambda timeout=3.0: True)
    assert empty_corpus.probe(timeout=0.0) is True
    monkeypatch.setattr(empty_corpus._live_arxiv, "probe",
                        lambda timeout=3.0: False)
    assert empty_corpus.probe(timeout=0.0) is False


# ---------------------------------------------------------------------------
# Live-download tests (gated)
# ---------------------------------------------------------------------------

_DL_FLAG = os.environ.get("PROMETHEUS_DOWNLOAD_ARXIV_CORPUS") == "1"

_skip_no_dl = pytest.mark.skipif(
    not _DL_FLAG,
    reason="PROMETHEUS_DOWNLOAD_ARXIV_CORPUS != 1; skipping live download",
)


@_skip_no_dl
def test_live_update_corpus_downloads_some_papers(tmp_path, monkeypatch):
    """Smoke test for the live updater. Pulls a tiny slice (5 papers).

    Gated behind PROMETHEUS_DOWNLOAD_ARXIV_CORPUS=1 so CI doesn't hammer
    arXiv. Cleans up by writing into a tmp_path corpus dir.
    """
    monkeypatch.setenv("PROMETHEUS_DATA_DIR", str(tmp_path))
    ac = _reload_module()
    status = ac.update_corpus(force=False, max_papers=5, since_year=2018)
    if status.get("errors"):
        pytest.skip(f"arxiv download failed: {status.get('error')}")
    # We expect at least some additions OR some skips (if cached).
    assert status["added"] + status["skipped"] >= 1
    assert ac.corpus_stats()["n_papers"] >= status["added"]
