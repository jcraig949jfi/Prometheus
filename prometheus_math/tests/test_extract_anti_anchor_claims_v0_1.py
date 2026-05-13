"""Smoke tests for the anti_anchor-registry mining extractor (v0.1)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prometheus_math.substrate_generation.claim_mining.extract_anti_anchor_claims_v0_1 import (
    EXTRACTOR_VERSION,
    _build_couplet_claim,
    _numeric_hash_suffix,
    extract_claims_from_registry,
    stage_claims_per_category,
)


class TestBuildCoupletClaim:
    def _aa(self) -> dict:
        return {
            "id": "AA-001",
            "name": "GCT_OCCURRENCE_DEAD",
            "false_form": (
                "Bürgisser-Ikenmeyer-Panova killed GCT entirely; occurrence "
                "obstructions for det/padded-perm are still viable."
            ),
            "true_form": (
                "BIP 2019 killed occurrence obstructions specifically for "
                "(det_m, padded_perm_{n,m}); other obstructions remain."
            ),
            "citation": "arXiv:1604.06431 (BIP 2019 J. AMS)",
            "verification_source": "Wave 1 Gemini Deep Research",
        }

    def test_false_form_yields_falsified(self):
        c = _build_couplet_claim(self._aa(), form="false_form")
        assert c is not None
        assert c["expected_verdict"] == "falsified"
        assert c["claim_category"] == "frontier_survey"
        assert c["parent_block"] == "AA-001"
        assert "false_form" in c["source_report"]

    def test_true_form_yields_survived(self):
        c = _build_couplet_claim(self._aa(), form="true_form")
        assert c is not None
        assert c["expected_verdict"] == "survived"
        assert "true_form" in c["source_report"]

    def test_missing_form_returns_none(self):
        aa = {"id": "AA-001", "name": "X"}  # no false_form/true_form
        assert _build_couplet_claim(aa, form="false_form") is None
        assert _build_couplet_claim(aa, form="true_form") is None

    def test_short_text_returns_none(self):
        aa = {"id": "AA-001", "name": "X", "false_form": "too short"}
        assert _build_couplet_claim(aa, form="false_form") is None

    def test_non_AA_id_returns_none(self):
        aa = {"id": "X-001", "false_form": "long enough text here for the test"}
        assert _build_couplet_claim(aa, form="false_form") is None

    def test_id_matches_schema_pattern(self):
        import re
        c = _build_couplet_claim(self._aa(), form="false_form")
        assert c is not None
        id_re = re.compile(r"^CLAIM-[a-z][a-zA-Z0-9_-]+-\d{4,5}$")
        assert id_re.match(c["id"]) is not None, f"id {c['id']!r} fails regex"

    def test_invalid_form_arg_raises(self):
        with pytest.raises(ValueError):
            _build_couplet_claim(self._aa(), form="bogus")


class TestExtractClaimsFromRegistry:
    def test_yields_two_claims_per_entry(self, tmp_path):
        registry = tmp_path / "aa.jsonl"
        registry.write_text(
            json.dumps({
                "id": "AA-001", "name": "TEST",
                "false_form": "false claim text long enough for the test",
                "true_form": "true claim text long enough for the test",
                "citation": "arXiv:1604.06431",
            }) + "\n"
            + json.dumps({
                "id": "AA-002", "name": "TEST2",
                "false_form": "another false claim text long enough",
                "true_form": "another true claim text long enough",
                "citation": "arXiv:2509.15537",
            }) + "\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_registry(registry)
        assert len(claims) == 4  # 2 entries × 2 forms each
        ids = sorted(c["parent_block"] for c in claims)
        assert ids == ["AA-001", "AA-001", "AA-002", "AA-002"]

    def test_missing_registry_returns_empty(self, tmp_path):
        assert extract_claims_from_registry(tmp_path / "nope.jsonl") == []

    def test_malformed_line_skipped(self, tmp_path):
        registry = tmp_path / "aa.jsonl"
        registry.write_text(
            "not valid json\n" +
            json.dumps({
                "id": "AA-001", "name": "X",
                "false_form": "good false form text long enough",
                "true_form": "good true form text long enough",
            }) + "\n",
            encoding="utf-8",
        )
        claims = extract_claims_from_registry(registry)
        # Bad line skipped, good entry yields 2 claims
        assert len(claims) == 2


class TestCoupletOverridePreCheckShortCircuit:
    """Loop hour 14 optimization: anti_anchor_couplet_override pre-check
    moved BEFORE primary/fallback dispatch in run_claim. Network calls
    for citation_audit are skipped on couplet claims (parent_block
    + source_report markers determine verdict via the registry)."""

    def test_couplet_claim_does_not_dispatch_primary_verifier(self):
        """Run a couplet claim through run_claim; assert verifier_used is
        anti_anchor_couplet_override (not citation_audit), and runtime
        is sub-millisecond (no network roundtrip)."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import run_claim
        claim = {
            "_schema_version": "1.0.0",
            "id": "CLAIM-mined-aa-couplet-AA001-fal-abc123-12345",
            "claim_category": "frontier_survey",
            "claim_text": "Some false-form claim text long enough.",
            "expected_verifier_primary": "citation_audit",
            "expected_verdict": "falsified",
            "ground_truth_source": "arXiv:1604.06431",
            "trust_tier": "analytically_proven",
            "source_report": "AA-001 anti_anchor false_form (registry)",
            "parent_block": "AA-001",  # Registered AA in registry
        }
        result, records = run_claim(claim, kernel=None, emit_kernel_opcodes=False)
        assert result.verifier_used == "anti_anchor_couplet_override"
        assert result.actual_verdict == "decisive_contradicted"
        assert result.runtime_ms < 50  # sub-50ms; no network


class TestStageClaimsPerCategory:
    def test_writes_all_5_files(self, tmp_path):
        counts = stage_claims_per_category([], tmp_path / "stage")
        for cat in ("frontier_survey", "calibration", "boundary", "substrate_self", "other"):
            assert (tmp_path / "stage" / f"{cat}.jsonl").exists()
            assert counts[cat] == 0
