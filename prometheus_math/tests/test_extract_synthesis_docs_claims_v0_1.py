"""Smoke tests for the synthesis_docs claim-mining extractor (v0.1).

Per BL-T-002 in techne/BACKLOG.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prometheus_math.substrate_generation.claim_mining.extract_synthesis_docs_claims_v0_1 import (
    EXTRACTOR_VERSION,
    _ARXIV_RE,
    _CLAIM_INDICATORS,
    _RULE_D_NEGATIVE_INDICATORS,
    _SECTION_RE,
    _TENSOR_CAT_RE,
    _detect_rule_d,
    _detect_section_for_offset,
    _numeric_hash_suffix,
    _paragraph_at,
    extract_claims_from_file,
    extract_claims_from_paths,
    stage_claims_per_category,
)


class TestNumericHashSuffix:
    def test_returns_5_digits(self):
        for text in ("foo", "T#1:bar", "arXiv:1604.06431"):
            s = _numeric_hash_suffix(text)
            assert len(s) == 5
            assert s.isdigit()

    def test_deterministic(self):
        assert _numeric_hash_suffix("test") == _numeric_hash_suffix("test")


class TestRegexPrimitives:
    def test_arxiv_match(self):
        m = _ARXIV_RE.search("citing arXiv:2411.05721 cleanly")
        assert m is not None
        assert m.group(1) == "2411.05721"

    def test_t_cat_match(self):
        m = _TENSOR_CAT_RE.search("update T#86 catalog entry")
        assert m is not None
        assert m.group(1) == "86"

    def test_section_re_matches_numeric_section(self):
        text = "## 1. Executive summary\n\n## 2. Catalog updates required"
        sections = list(_SECTION_RE.finditer(text))
        assert len(sections) == 2
        assert sections[0].group(1) == "1"
        assert sections[1].group(1) == "2"


class TestDetectRuleD:
    def test_negative_adjacency_flagged(self):
        text = "arXiv:2512.15035 was withdrawn after gap discovery."
        m = _ARXIV_RE.search(text)
        assert m is not None
        assert _detect_rule_d(text, (m.start(), m.end())) is True

    def test_no_negative_not_flagged(self):
        text = "arXiv:1604.06431 establishes the result via the substitution method."
        m = _ARXIV_RE.search(text)
        assert _detect_rule_d(text, (m.start(), m.end())) is False


class TestDetectSection:
    def test_finds_most_recent_section(self):
        text = (
            "## 1. Executive summary\n\nSome prose.\n\n"
            "## 2. Catalog updates\n\nmore prose. arXiv:1234.56789 here."
        )
        offset = text.find("arXiv:")
        assert _detect_section_for_offset(text, offset) == "2"


class TestExtractClaimsFromFile:
    def test_synthetic_synthesis_doc_yields_claims(self, tmp_path):
        md = tmp_path / "synth.md"
        md.write_text(
            "# Synthesis\n\n"
            "## 1. Executive summary\n\n"
            "Mańdziuk-Ventura proven (arXiv:2411.05721) that border Comon's "
            "conjecture holds for n <= d+1 in the minimal-border-rank regime. "
            "T#20 catalog entry should reflect this.\n\n"
            "## 2. Anti-anchor candidates\n\n"
            "Lee 2025 (arXiv:2512.15035) was withdrawn within 3 days; "
            "established that the proof gap was substantive.\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md)
        # Expect at least one frontier_survey (arXiv-anchored) + one boundary (T#20)
        assert len(claims) >= 2
        cats = sorted({c["claim_category"] for c in claims})
        assert "frontier_survey" in cats
        assert "boundary" in cats
        # Schema id pattern
        import re
        id_re = re.compile(r"^CLAIM-[a-z][a-zA-Z0-9_-]+-\d{4,5}$")
        for c in claims:
            assert id_re.match(c["id"]) is not None, f"id {c['id']!r}"

    def test_rule_d_caveat_emitted(self, tmp_path):
        md = tmp_path / "synth.md"
        md.write_text(
            "## 1. test\n\n"
            "Lee 2025 (arXiv:2512.15035) was WITHDRAWN; established gap.\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md)
        rule_d_claims = [c for c in claims if c.get("caveats", "").startswith("rule_d_candidate")]
        assert len(rule_d_claims) >= 1
        # rule_d should flip verdict to falsified
        for c in rule_d_claims:
            assert c["expected_verdict"] == "falsified"
            assert c["trust_tier"] == "folklore"

    def test_no_claim_indicator_skipped(self, tmp_path):
        md = tmp_path / "synth.md"
        md.write_text(
            "## 1. test\n\nSee arXiv:1234.56789 for details. Nothing to assert.\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md)
        assert len(claims) == 0  # no claim_indicator word


class TestExtractClaimsFromPaths:
    def test_walks_multiple_files(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text(
            "## 1. test\n\nProven by arXiv:1234.56789 that bound holds.\n",
            encoding="utf-8",
        )
        f2.write_text(
            "## 1. test\n\nT#42 catalog entry shown to be open via theorem.\n",
            encoding="utf-8",
        )
        claims, summary = extract_claims_from_paths((f1, f2))
        assert summary["files_scanned"] == 2
        assert summary["files_with_claims"] == 2
        assert summary["files_missing"] == 0
        assert len(claims) >= 2

    def test_missing_file_warned(self, tmp_path):
        # Mix of one real + one missing
        real = tmp_path / "real.md"
        real.write_text("## 1. test\n\nProven theorem at arXiv:1111.22222.\n", encoding="utf-8")
        missing = tmp_path / "missing.md"
        claims, summary = extract_claims_from_paths((real, missing))
        assert summary["files_missing"] == 1
        assert summary["files_scanned"] == 2


class TestStageClaimsPerCategory:
    def test_writes_all_5_files_even_when_empty(self, tmp_path):
        counts = stage_claims_per_category([], tmp_path / "stage")
        for cat in ("frontier_survey", "calibration", "boundary", "substrate_self", "other"):
            f = tmp_path / "stage" / f"{cat}.jsonl"
            assert f.exists()
            assert counts[cat] == 0
