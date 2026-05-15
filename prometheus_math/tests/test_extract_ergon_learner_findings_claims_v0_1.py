"""Smoke tests for the ergon_learner_findings claim-mining extractor (v0.1).

Per BL-T-003 in techne/BACKLOG.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prometheus_math.substrate_generation.claim_mining.extract_ergon_learner_findings_claims_v0_1 import (
    EXTRACTOR_VERSION,
    _ANCHOR_REGEXES,
    _CLAIM_INDICATORS,
    _RULE_D_NEGATIVE_INDICATORS,
    _detect_rule_d,
    _detect_section_for_offset,
    _numeric_hash_suffix,
    _paragraph_at,
    extract_claims_from_dir,
    extract_claims_from_file,
    stage_claims_per_category,
)


class TestAnchorRegexes:
    def test_bs_anchor(self):
        m = _ANCHOR_REGEXES["BS"].search("see BS-014 finding")
        assert m is not None
        assert m.group(1) == "014"

    def test_eec_anchor(self):
        m = _ANCHOR_REGEXES["EEC"].search("EEC-007 gap surfaced")
        assert m is not None
        assert m.group(1) == "007"

    def test_fm_anchor_2_or_3_digits(self):
        m = _ANCHOR_REGEXES["FM"].search("FM-12 demonstrated")
        assert m is not None and m.group(1) == "12"
        m = _ANCHOR_REGEXES["FM"].search("FM-105 verified")
        assert m is not None and m.group(1) == "105"

    def test_req_anchor(self):
        m = _ANCHOR_REGEXES["REQ"].search("REQ-029 closed")
        assert m is not None
        assert m.group(1) == "029"

    def test_no_arxiv_anchor(self):
        # Sanity: this corpus's extractor does NOT use arXiv pattern
        import re
        # Just confirm there's no "arxiv" in the regex set
        all_regex_strs = [r.pattern for r in _ANCHOR_REGEXES.values()]
        assert all("arxiv" not in r.lower() for r in all_regex_strs)


class TestNumericHashSuffix:
    def test_5_digits(self):
        s = _numeric_hash_suffix("BS-014:test")
        assert len(s) == 5 and s.isdigit()

    def test_deterministic(self):
        assert _numeric_hash_suffix("x") == _numeric_hash_suffix("x")


class TestExtractClaimsFromFile:
    def test_synthetic_ergon_doc_yields_substrate_self_claims(self, tmp_path):
        md = tmp_path / "synth.md"
        md.write_text(
            "# Test\n\n"
            "## §1 Findings\n\n"
            "BS-014 surfaced in tagging — silent-miss demonstrated when "
            "regex heuristic was used; explicit field needed.\n\n"
            "## §2 Failure modes\n\n"
            "FM-23 verified across 3 sessions; load-bearing for the next "
            "iteration.\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md, source_dir=tmp_path)
        assert len(claims) >= 2
        # All should be substrate_self category
        for c in claims:
            assert c["claim_category"] == "substrate_self"
            assert c["expected_verifier_primary"] == "manual_review"
        # Schema id pattern
        import re
        id_re = re.compile(r"^CLAIM-[a-z][a-zA-Z0-9_-]+-\d{4,5}$")
        for c in claims:
            assert id_re.match(c["id"]) is not None, f"id {c['id']!r}"

    def test_rule_d_caveat_emitted_for_negative_adjacency(self, tmp_path):
        md = tmp_path / "synth.md"
        md.write_text(
            "## §1 test\n\n"
            "BS-014 finding established but the regex heuristic was wrong; "
            "silent-miss demonstrated despite earlier fix attempt.\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md, source_dir=tmp_path)
        rule_d_claims = [c for c in claims if c.get("caveats", "").startswith("rule_d_candidate")]
        assert len(rule_d_claims) >= 1
        for c in rule_d_claims:
            assert c["expected_verdict"] == "falsified"
            assert c["trust_tier"] == "folklore"

    def test_no_claim_indicator_skipped(self, tmp_path):
        md = tmp_path / "synth.md"
        md.write_text(
            "## §1 test\n\nSee BS-014 for context. Nothing else.\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md, source_dir=tmp_path)
        assert len(claims) == 0

    def test_anchor_namespace_recorded_in_verifier_args(self, tmp_path):
        md = tmp_path / "synth.md"
        md.write_text(
            "## §1 test\n\nEEC-007 gap surfaced; needs Techne audit-prep.\n\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_file(md, source_dir=tmp_path)
        assert len(claims) >= 1
        assert claims[0]["verifier_args"]["anchor_namespace"] == "EEC"
        assert claims[0]["verifier_args"]["anchor_id"] == "EEC-007"


class TestExtractClaimsFromDir:
    def test_walks_dir_recursively(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "subdir" / "b.md"
        f2.parent.mkdir(parents=True)
        f1.write_text("## §1 test\n\nBS-001 demonstrates issue.\n", encoding="utf-8")
        f2.write_text("## §1 test\n\nFM-99 surfaced; needs review.\n", encoding="utf-8")
        claims, summary = extract_claims_from_dir(tmp_path)
        assert summary["files_scanned"] == 2
        assert summary["files_with_claims"] == 2
        assert len(claims) >= 2

    def test_missing_dir_returns_empty(self, tmp_path):
        claims, summary = extract_claims_from_dir(tmp_path / "nope")
        assert claims == []
        assert summary["files_missing"] == 1


class TestStageClaimsPerCategory:
    def test_writes_all_5_files_even_when_empty(self, tmp_path):
        counts = stage_claims_per_category([], tmp_path / "stage")
        for cat in ("frontier_survey", "calibration", "boundary", "substrate_self", "other"):
            assert (tmp_path / "stage" / f"{cat}.jsonl").exists()
            assert counts[cat] == 0
