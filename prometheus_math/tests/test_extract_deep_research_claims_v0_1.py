"""Smoke tests for the Day-1 claim-mining extractor (deep_research_reports source).

Per Aporia BUILD-unblock 2026-05-13 + Techne ACK ticket
T-2026-05-13-techne-to-aporia-build-unblock-ack-day1-deep-research-extractor.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prometheus_math.substrate_generation.claim_mining.extract_deep_research_claims_v0_1 import (
    EXTRACTOR_VERSION,
    _ARXIV_RE,
    _CLAIM_INDICATORS,
    _MAX_CLAIM_TEXT_LEN,
    _MIN_CLAIM_TEXT_LEN,
    _RULE_D_NEGATIVE_INDICATORS,
    _SECTION_RE,
    _TENSOR_CAT_RE,
    _detect_rule_d_candidate,
    _detect_section_for_offset,
    _numeric_hash_suffix,
    _paragraph_at,
    _section_letter_to_claim_category,
    _section_letter_to_expected_verdict,
    extract_claims_from_file,
    stage_claims_to_per_category_jsonl,
)


class TestNumericHashSuffix:
    def test_returns_5_digits(self):
        for text in ("foo", "arXiv:1604.06431", "long claim text here"):
            s = _numeric_hash_suffix(text)
            assert len(s) == 5
            assert s.isdigit()

    def test_deterministic(self):
        assert _numeric_hash_suffix("test") == _numeric_hash_suffix("test")

    def test_different_inputs_differ(self):
        # Probabilistic but ~99.999% reliable
        assert _numeric_hash_suffix("foo") != _numeric_hash_suffix("bar")


class TestRegexPrimitives:
    def test_arxiv_re_matches_canonical(self):
        m = _ARXIV_RE.search("citing arXiv:1604.06431 in context")
        assert m is not None
        assert m.group(1) == "1604.06431"

    def test_arxiv_re_matches_at_end(self):
        m = _ARXIV_RE.search("arXiv:2509.15537")
        assert m is not None
        assert m.group(1) == "2509.15537"

    def test_arxiv_re_no_match_on_partial(self):
        assert _ARXIV_RE.search("arxiv:1234.56") is None  # case + len
        assert _ARXIV_RE.search("arXiv:123.4567") is None  # wrong-len prefix

    def test_tensor_cat_re_matches(self):
        m = _TENSOR_CAT_RE.search("T#1 catalog entry")
        assert m is not None
        assert m.group(1) == "1"
        m = _TENSOR_CAT_RE.search("references T#56 and not T#abc")
        assert m is not None
        assert m.group(1) == "56"

    def test_section_re_matches_lowercase_letters(self):
        text = "## (a) PRIMARY SOURCE CONFIRMATION\n\n## (b) FOLLOW-ON WORK"
        sections = list(_SECTION_RE.finditer(text))
        assert len(sections) == 2
        assert sections[0].group(1) == "a"
        assert sections[1].group(1) == "b"


class TestDetectRuleDCandidate:
    def test_withdrawn_near_arxiv_id_flagged(self):
        para = "The Lee 2025 paper (arXiv:2512.15035) was WITHDRAWN within 3 days."
        m = _ARXIV_RE.search(para)
        assert m is not None
        assert _detect_rule_d_candidate(para, (m.start(), m.end())) is True

    def test_distant_negative_not_flagged(self):
        # arXiv ID at start, "withdrawn" far away (>80 chars)
        para = "arXiv:1234.56789 cited; " + ("filler text. " * 20) + "withdrawn far away"
        m = _ARXIV_RE.search(para)
        assert m is not None
        assert _detect_rule_d_candidate(para, (m.start(), m.end())) is False

    def test_no_negative_indicator(self):
        para = "arXiv:1604.06431 establishes the result via the substitution method."
        m = _ARXIV_RE.search(para)
        assert _detect_rule_d_candidate(para, (m.start(), m.end())) is False


class TestDetectSectionForOffset:
    def test_finds_most_recent_section(self):
        text = (
            "## (a) PRIMARY SOURCE CONFIRMATION\n"
            "Some prose.\n\n"
            "## (b) FOLLOW-ON WORK\n"
            "more prose. arXiv:1234.56789 cited here."
        )
        arxiv_offset = text.find("arXiv:")
        assert _detect_section_for_offset(text, arxiv_offset) == "b"

    def test_no_section_above(self):
        text = "arXiv:1234.56789 before any section header."
        assert _detect_section_for_offset(text, 0) is None


class TestParagraphAt:
    def test_extracts_paragraph_around_offset(self):
        text = "first para.\n\nsecond para with arXiv:1234.56789 in it.\n\nthird para."
        offset = text.find("arXiv:")
        para, start, end = _paragraph_at(text, offset)
        assert "second para" in para
        assert "first para" not in para
        assert "third para" not in para


class TestSectionLetterMappings:
    def test_categories(self):
        assert _section_letter_to_claim_category("a") == "frontier_survey"
        assert _section_letter_to_claim_category("b") == "frontier_survey"
        assert _section_letter_to_claim_category("c") == "frontier_survey"
        assert _section_letter_to_claim_category("d") == "substrate_self"
        assert _section_letter_to_claim_category(None) == "other"
        assert _section_letter_to_claim_category("z") == "other"

    def test_verdicts(self):
        # Default: survived for true-form sections; falsified for (c) false-form
        assert _section_letter_to_expected_verdict("a", False) == "survived"
        assert _section_letter_to_expected_verdict("c", False) == "falsified"
        # Rule D flag overrides to falsified regardless of section
        assert _section_letter_to_expected_verdict("a", True) == "falsified"


class TestExtractClaimsFromFile:
    def test_real_substrate_shaped_pilot_file_yields_claims(self, tmp_path):
        # Write a small synthetic report exercising both arXiv + T# anchors
        md = tmp_path / "test_report.md"
        md.write_text(
            "# Synthetic test\n\n"
            "## (a) PRIMARY SOURCE CONFIRMATION\n\n"
            "Filip Rupniewski established the safe zone via arXiv:2209.11040 (peer-"
            "reviewed in LAA Vol 698), demonstrating that tensor rank additivity "
            "holds for R <= 7.\n\n"
            "## (c) FALSE-FORM RECURRENCE\n\n"
            "The false form asserts the bound established for tensor rank "
            "extends to border rank R-bar, which is wrong per Schönhage 1981 "
            "theorem (T#1 catalog entry).\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md, source_dir=tmp_path)
        assert len(claims) >= 2  # at least one arXiv + one T#
        # IDs all match schema pattern (4-5 digit suffix)
        import re
        id_pattern = re.compile(r"^CLAIM-[a-z][a-zA-Z0-9_-]+-\d{4,5}$")
        for c in claims:
            assert id_pattern.match(c["id"]) is not None, f"id {c['id']!r} fails regex"
        # The (c) section false-form claim should have expected_verdict=falsified
        false_form_claims = [
            c for c in claims if c["expected_verdict"] == "falsified"
        ]
        assert len(false_form_claims) >= 1

    def test_claim_text_length_capped(self, tmp_path):
        md = tmp_path / "long_para.md"
        # Construct a paragraph longer than _MAX_CLAIM_TEXT_LEN
        long_filler = "This proven theorem ".replace(" ", " " * 50) * 30
        md.write_text(
            f"## (a) test\n\narXiv:1234.56789 {long_filler}\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md, source_dir=tmp_path)
        for c in claims:
            assert len(c["claim_text"]) <= _MAX_CLAIM_TEXT_LEN

    def test_no_claim_indicator_skipped(self, tmp_path):
        md = tmp_path / "no_indicator.md"
        # Paragraph has arXiv ID but no claim-indicator word
        md.write_text(
            "## (a) test\n\nSee arXiv:1234.56789 for details. Nothing to assert.\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md, source_dir=tmp_path)
        # 'shown'/'established'/etc. not present → no claim emitted
        assert len(claims) == 0


class TestStageClaimsToPerCategoryJsonl:
    def test_writes_all_5_category_files_even_when_empty(self, tmp_path):
        out_dir = tmp_path / "stage"
        counts = stage_claims_to_per_category_jsonl([], out_dir)
        for cat in ("frontier_survey", "calibration", "boundary", "substrate_self", "other"):
            f = out_dir / f"{cat}.jsonl"
            assert f.exists()
            assert f.read_text() == ""
            assert counts[cat] == 0

    def test_routes_by_category(self, tmp_path):
        out_dir = tmp_path / "stage"
        claims = [
            {"id": "CLAIM-test-arxiv-00001", "claim_category": "frontier_survey",
             "claim_text": "x", "expected_verifier_primary": "citation_audit",
             "expected_verdict": "survived", "ground_truth_source": "arXiv:1234.56789",
             "trust_tier": "analytically_proven", "source_report": "test",
             "_schema_version": "1.0.0"},
            {"id": "CLAIM-test-boundary-T1-00002", "claim_category": "boundary",
             "claim_text": "x", "expected_verifier_primary": "catalog_lookup",
             "expected_verdict": "falsified", "ground_truth_source": "T#1",
             "trust_tier": "analytically_proven", "source_report": "test",
             "_schema_version": "1.0.0"},
        ]
        counts = stage_claims_to_per_category_jsonl(claims, out_dir)
        assert counts["frontier_survey"] == 1
        assert counts["boundary"] == 1
        assert counts["calibration"] == 0
