"""Tests for theseus.scripts.scan_synthesis_claims."""
from __future__ import annotations

import json
from pathlib import Path

from theseus.scripts.scan_synthesis_claims import (
    _claim_id,
    _classify_pattern,
    _extract_claims_from_text,
    scan,
)


def test_claim_id_stable_for_same_text():
    assert _claim_id("foo") == _claim_id("foo")


def test_claim_id_differs_for_different_text():
    assert _claim_id("foo") != _claim_id("bar")


def test_classify_pattern_conjecture():
    assert _classify_pattern("We conjecture that X.") == "conjecture"
    assert _classify_pattern("We predict the limit is 5.") == "conjecture"


def test_classify_pattern_implication():
    assert _classify_pattern("This implies that Y.") == "implication"
    assert _classify_pattern("This shows the bound.") == "implication"


def test_classify_pattern_percentage():
    assert _classify_pattern("Rate of 80% on the set.") == "rate_or_percentage"


def test_classify_pattern_magnitude():
    assert _classify_pattern("A 10x improvement here.") == "magnitude_change"


def test_classify_pattern_numeric_bound():
    assert _classify_pattern("The value is ≥ 5 always.") == "numeric_bound"
    assert _classify_pattern("Less than K when X > 0.") == "numeric_bound"


def test_extract_claims_picks_up_conjecture(tmp_path):
    text = (
        "Background prose. We conjecture that the rate exceeds 50% for "
        "all primes considered in this experiment."
    )
    claims = _extract_claims_from_text(text, tmp_path / "doc.md")
    assert any(c["pattern_kind"] == "conjecture" for c in claims)


def test_extract_claims_dedupes_within_file(tmp_path):
    line = (
        "We conjecture that the rate exceeds 50% for all primes in this "
        "experiment."
    )
    text = f"{line} {line}"
    claims = _extract_claims_from_text(text, tmp_path / "doc.md")
    # Same canonical text → dedup within single scan.
    conjectures = [c for c in claims if c["pattern_kind"] == "conjecture"]
    assert len(conjectures) == 1


def test_scan_writes_jsonl(tmp_path, monkeypatch):
    # Fake a synthesis doc the scanner would find
    from theseus.scripts import scan_synthesis_claims as ssc
    fake_repo = tmp_path / "repo"
    pivot = fake_repo / "pivot"
    pivot.mkdir(parents=True)
    (pivot / "techne_demo.md").write_text(
        "Intro prose for the demo synthesis doc. We conjecture that the "
        "rate exceeds 50% for all primes encountered. This implies the "
        "bound holds across the full sample. Concluding remarks follow.",
        encoding="utf-8",
    )
    monkeypatch.setattr(ssc, "REPO_ROOT", fake_repo)

    output_path = tmp_path / "out.jsonl"
    summary = scan(output_path)
    assert summary["n_files_scanned"] >= 1
    assert summary["n_claims_extracted"] >= 1
    lines = output_path.read_text(encoding="utf-8").strip().split("\n")
    parsed = [json.loads(l) for l in lines if l]
    assert all("claim_id" in c for c in parsed)
    assert all("source_path" in c for c in parsed)
    assert all("pattern_kind" in c for c in parsed)


def test_aporia_filter_rejects_prometheus_internal():
    """Internal-only claim with no external math anchor → rejected."""
    from theseus.scripts.scan_synthesis_claims import _passes_aporia_filters
    claim = "Techne fire #34 ships 7 new algorithms; substrate v2.3 is stable."
    assert _passes_aporia_filters(claim) is False


def test_aporia_filter_accepts_externally_anchored():
    """Claim referencing Lehmer / theorem / arXiv passes."""
    from theseus.scripts.scan_synthesis_claims import _passes_aporia_filters
    assert _passes_aporia_filters(
        "We expect Lehmer enumerations are ~99% in-band uninformative."
    )
    assert _passes_aporia_filters(
        "The Riemann hypothesis remains open for ζ(s)."
    )
    assert _passes_aporia_filters(
        "Per arXiv:2401.12345 the bound is 5 < n < 100."
    )


def test_aporia_filter_internal_marker_with_external_anchor_survives():
    """Techne mentioned but core math is external → strip + accept."""
    from theseus.scripts.scan_synthesis_claims import _passes_aporia_filters
    claim = (
        "Per Techne fire #34, the Riemann hypothesis ζ(s) zeros constrain "
        "Lehmer's conjecture to 95% of cases."
    )
    assert _passes_aporia_filters(claim) is True


def test_aporia_filter_no_anchor_rejected_even_when_clean():
    """Pure workflow claim with NO Prometheus markers AND no external anchor
    → still rejected. We want external substantiation, not just clean text."""
    from theseus.scripts.scan_synthesis_claims import _passes_aporia_filters
    claim = "We plan to ship 5 new modules over the next 2 weeks."
    assert _passes_aporia_filters(claim) is False


def test_scan_excludes_meta_analysis_docs(tmp_path, monkeypatch):
    """meta_analysis_* and feedback_* docs should be excluded — they're
    ABOUT Techne work, not Techne claims."""
    from theseus.scripts import scan_synthesis_claims as ssc
    fake_repo = tmp_path / "repo"
    pivot = fake_repo / "pivot"
    pivot.mkdir(parents=True)
    (pivot / "meta_analysis_techne.md").write_text(
        "We conjecture the meta thing.", encoding="utf-8"
    )
    (pivot / "feedback_techne.md").write_text(
        "We conjecture the feedback thing.", encoding="utf-8"
    )
    monkeypatch.setattr(ssc, "REPO_ROOT", fake_repo)

    output_path = tmp_path / "out.jsonl"
    summary = scan(output_path)
    # Both meta and feedback docs excluded
    assert summary["n_files_scanned"] == 0
