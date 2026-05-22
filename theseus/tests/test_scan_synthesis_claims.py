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
