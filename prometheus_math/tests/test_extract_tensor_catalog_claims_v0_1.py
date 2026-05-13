"""Smoke tests for the tensor-catalog claim-mining extractor (v0.1)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prometheus_math.substrate_generation.claim_mining.extract_tensor_catalog_claims_v0_1 import (
    EXTRACTOR_VERSION,
    _ENTRY_HEADER_RE,
    _detect_rule_d,
    _entry_status_verdict,
    _numeric_hash_suffix,
    _split_entries,
    extract_claims_from_catalog,
    stage_claims_per_category,
)


class TestSplitEntries:
    def test_finds_entries_by_header(self):
        text = (
            "## Heading\n\n"
            "### 1. Matrix multiplication exponent\n"
            "Bounds: 2 ≤ ω ≤ 2.371.\n"
            "**Class.** Algebraic.\n\n"
            "### 4. M⟨3⟩ rank\n"
            "Bounds: 19 ≤ R ≤ 23.\n"
        )
        entries = _split_entries(text)
        assert len(entries) == 2
        assert entries[0][0] == "T#1"
        assert entries[0][1].startswith("Matrix multiplication")
        assert entries[1][0] == "T#4"

    def test_entry_body_excludes_next_header(self):
        text = "### 1. Foo\nbody1\n\n### 2. Bar\nbody2\n"
        entries = _split_entries(text)
        assert "Bar" not in entries[0][2]
        assert "body1" in entries[0][2]


class TestEntryStatusVerdict:
    def test_open_status(self):
        assert _entry_status_verdict("This problem remains open as of 2026.") == "open"
        assert _entry_status_verdict("The exact value is unknown.") == "open"

    def test_settled_status(self):
        assert _entry_status_verdict("Settled by Shitov 2016.") == "survived"
        assert _entry_status_verdict("Established via the substitution method theorem.") == "survived"

    def test_falsified_status(self):
        assert _entry_status_verdict("Shitov 2019 disproved this.") == "falsified"
        assert _entry_status_verdict("Withdrawn 2025-12-20.") == "falsified"


class TestDetectRuleD:
    def test_negative_adjacency_flagged(self):
        text = "arXiv:1234.56789 was WITHDRAWN soon after."
        import re
        m = re.search(r"\barXiv:(\d{4}\.\d{4,5})\b", text)
        assert m is not None
        assert _detect_rule_d(text, (m.start(), m.end())) is True

    def test_no_negative_not_flagged(self):
        text = "arXiv:1604.06431 establishes the result correctly."
        import re
        m = re.search(r"\barXiv:(\d{4}\.\d{4,5})\b", text)
        assert _detect_rule_d(text, (m.start(), m.end())) is False


class TestNumericHashSuffix:
    def test_5_digits(self):
        for t in ("foo", "T#1:bar", "arXiv:1234.56789"):
            s = _numeric_hash_suffix(t)
            assert len(s) == 5 and s.isdigit()

    def test_deterministic(self):
        assert _numeric_hash_suffix("same") == _numeric_hash_suffix("same")


class TestExtractClaimsFromCatalog:
    def test_synthetic_catalog_yields_claims(self, tmp_path):
        catalog = tmp_path / "synth_catalog.md"
        catalog.write_text(
            "# Open Problems\n\n"
            "## I. Foundations\n\n"
            "### 1. Matrix multiplication exponent ω\n"
            "Bounds: 2 ≤ ω ≤ 2.371. Established via "
            "Alman-Duan-VW-Xu-Xu-Zhou 2024 (arXiv:2404.16349). Open: "
            "ω = 2 conjectured.\n"
            "**Class.** Algebraic.\n"
            "**Refs.** arXiv:2404.16349 main.\n\n"
            "### 2. Hillar-Lim conjecture\n"
            "Theorem proven: symmetric rank over Q is NP-hard "
            "(Shitov 2016, arXiv:1611.01559). Settled.\n"
            "**Refs.** arXiv:1611.01559.\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_catalog(catalog)
        # At least 2 boundary claims (one per entry) + arXiv-anchored claims
        boundary = [c for c in claims if c["claim_category"] == "boundary"]
        frontier = [c for c in claims if c["claim_category"] == "frontier_survey"]
        assert len(boundary) == 2
        assert len(frontier) >= 2  # at least the cited arXiv IDs
        # All IDs match schema pattern
        import re as _re
        id_re = _re.compile(r"^CLAIM-[a-z][a-zA-Z0-9_-]+-\d{4,5}$")
        for c in claims:
            assert id_re.match(c["id"]) is not None, f"id {c['id']!r}"

    def test_entry_with_open_status_marked_open(self, tmp_path):
        catalog = tmp_path / "synth.md"
        catalog.write_text(
            "### 99. Open problem X\n"
            "Bounds known but exact value remains open as of 2026.\n"
            "**Refs.** none yet.\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_catalog(catalog)
        boundary = [c for c in claims if c["claim_category"] == "boundary"]
        assert len(boundary) == 1
        assert boundary[0]["expected_verdict"] == "open"


class TestStageClaimsPerCategory:
    def test_writes_all_5_files(self, tmp_path):
        counts = stage_claims_per_category([], tmp_path / "stage")
        for cat in ("frontier_survey", "calibration", "boundary", "substrate_self", "other"):
            assert (tmp_path / "stage" / f"{cat}.jsonl").exists()
            assert counts[cat] == 0
