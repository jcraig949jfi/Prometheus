"""Tests for Tier-1 substrate generation enrichment.

Per Ergon discussion `ergon/learner/v1_0_plans/substrate_quality_for_learner_discussion.md`
+ Techne reply 2026-05-11. Covers:
  - learner_enrichment.py (Dim 1, 4, 6, 9 enrichment fields)
  - survivor_seed_pool.py (Dim 7 decoy interleaving)
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

import pytest

from prometheus_math.substrate_generation.learner_enrichment import (
    DECOY_KINDS,
    EPISODE_PHASES,
    LearnerRecord,
    OUTCOME_CLASSES,
    VERIFICATION_TIERS,
    VERIFIER_OUTCOME_CLASSES,
    derive_kill_signature,
    enrich,
    lookup_verification_tier,
    normalize_outcome_class,
)
from prometheus_math.substrate_generation.survivor_seed_pool import (
    get_deg12_survivors,
    interleave_decoys,
    iter_seeded_survivors,
)


# ---------------------------------------------------------------------------
# Helpers — fake DiscoveryRecord (avoid importing the heavy real one)
# ---------------------------------------------------------------------------


@dataclass
class _FakeDiscoveryRecord:
    candidate_hash: str = "abc123"
    coeffs: tuple = (1, 0, 0)
    mahler_measure: float = 1.1
    terminal_state: str = "REJECTED"
    kill_pattern: Optional[str] = "out_of_band:M=1.45_outside_(1.001,1.18)"


# ---------------------------------------------------------------------------
# derive_kill_signature (Dim 9 anti-leakage)
# ---------------------------------------------------------------------------


class TestDeriveKillSignature:
    def test_none_pattern_is_survived(self):
        assert derive_kill_signature(None) == ("survived",)

    def test_empty_string_is_survived(self):
        assert derive_kill_signature("") == ("survived",)

    def test_out_of_band(self):
        sig = derive_kill_signature("out_of_band:M=1.4521_outside_(1.001,1.18)")
        # Must not contain literal numeric 1.4521 (anti-leakage)
        assert sig == ("out_of_band",)
        for elem in sig:
            assert "1.4521" not in elem
            assert "1.001" not in elem

    def test_reducible_one_factor(self):
        sig = derive_kill_signature("reducible:reducible: (x**2 + 1)^1")
        assert sig[0] == "reducible"
        assert any("n_factors" in s for s in sig)

    def test_reducible_multi_factor(self):
        sig = derive_kill_signature(
            "reducible:reducible: (x**2 + 1)^1; (x**10 - x**9 + 1)^1; (x + 1)^2"
        )
        assert sig[0] == "reducible"
        # Should report 3 factors
        assert any("n_factors=3" in s for s in sig)
        # Must not contain the literal coefficient strings (anti-leakage)
        for elem in sig:
            assert "x**" not in elem
            assert "+ 1" not in elem

    def test_f_gate_kill(self):
        for prefix in ("F1", "F6", "F9", "F11"):
            sig = derive_kill_signature(f"{prefix}:rationale text")
            assert sig == (f"{prefix.lower()}_killed",)

    def test_catalog_hit(self):
        sig = derive_kill_signature("catalog_hit:Mossinghoff")
        assert sig[0] == "catalog_hit"
        assert "Mossinghoff" in sig

    def test_unknown_prefix(self):
        sig = derive_kill_signature("brand_new_prefix:whatever")
        assert sig[0] == "other"
        assert "brand_new_prefix" in sig


# ---------------------------------------------------------------------------
# normalize_outcome_class
# ---------------------------------------------------------------------------


class TestNormalizeOutcomeClass:
    def test_rejected(self):
        assert normalize_outcome_class("REJECTED") == "rejected"

    def test_survived(self):
        assert normalize_outcome_class("SURVIVED") == "survived"

    def test_promoted(self):
        assert normalize_outcome_class("PROMOTED") == "promoted"

    def test_error(self):
        assert normalize_outcome_class("ERROR") == "errored"

    def test_none(self):
        assert normalize_outcome_class(None) == "errored"

    def test_unknown_lowercases(self):
        assert normalize_outcome_class("WAT") == "wat"


# ---------------------------------------------------------------------------
# lookup_verification_tier (Dim 4)
# ---------------------------------------------------------------------------


class TestLookupVerificationTier:
    def test_no_chart_id_returns_unknown(self):
        tier, used = lookup_verification_tier(None)
        assert tier == "unknown"
        assert used is None

    def test_unregistered_chart_returns_unknown(self):
        tier, used = lookup_verification_tier("never_registered:nowhere")
        assert tier == "unknown"

    def test_malformed_chart_id_returns_unknown(self):
        tier, used = lookup_verification_tier("nocolon")
        assert tier == "unknown"


# ---------------------------------------------------------------------------
# enrich() top-level
# ---------------------------------------------------------------------------


class TestEnrich:
    def test_basic_rejected(self):
        rec = _FakeDiscoveryRecord(
            candidate_hash="hashA", terminal_state="REJECTED",
            kill_pattern="reducible:reducible: (x + 1)^2",
        )
        lr = enrich(rec)
        assert lr.underlying_record_hash == "hashA"
        assert lr.episode_id == "hashA"  # 1:1 in Tier-1
        assert lr.episode_phase == "evaluate"
        assert lr.outcome_class == "rejected"
        assert lr.kill_signature[0] == "reducible"
        assert lr.decoy_kind is None
        assert lr.verification_tier == "unknown"

    def test_seeded_survivor_decoy(self):
        rec = _FakeDiscoveryRecord(
            candidate_hash="seedB", terminal_state="SURVIVED",
            kill_pattern=None,
        )
        lr = enrich(rec, decoy_kind="seeded_survivor")
        assert lr.decoy_kind == "seeded_survivor"
        assert lr.outcome_class == "survived"
        assert lr.kill_signature == ("survived",)

    def test_invalid_decoy_kind_raises(self):
        rec = _FakeDiscoveryRecord()
        with pytest.raises(ValueError):
            enrich(rec, decoy_kind="bogus")

    def test_invalid_episode_phase_raises(self):
        rec = _FakeDiscoveryRecord()
        with pytest.raises(ValueError):
            enrich(rec, episode_phase="bogus")

    def test_all_episode_phases_valid(self):
        rec = _FakeDiscoveryRecord()
        for phase in EPISODE_PHASES:
            lr = enrich(rec, episode_phase=phase)
            assert lr.episode_phase == phase

    def test_all_decoy_kinds_valid(self):
        rec = _FakeDiscoveryRecord()
        for dk in DECOY_KINDS:
            lr = enrich(rec, decoy_kind=dk)
            assert lr.decoy_kind == dk


class TestLearnerRecordFrozen:
    def test_frozen(self):
        import dataclasses
        rec = _FakeDiscoveryRecord()
        lr = enrich(rec)
        with pytest.raises(dataclasses.FrozenInstanceError):
            lr.episode_id = "different"  # type: ignore


# ---------------------------------------------------------------------------
# survivor_seed_pool — get_deg12_survivors
# ---------------------------------------------------------------------------


class TestSurvivorPool:
    def test_pool_has_at_least_3_entries(self):
        pool = get_deg12_survivors()
        assert len(pool) >= 3

    def test_pool_entries_are_deg12(self):
        for coeffs, m, label in get_deg12_survivors():
            assert len(coeffs) == 13  # deg-12 -> 13 coefficients

    def test_pool_entries_in_band(self):
        for coeffs, m, label in get_deg12_survivors():
            assert 1.001 < m < 1.18, f"{label}: M={m} not in Lehmer band"

    def test_pool_entries_palindromic(self):
        for coeffs, m, label in get_deg12_survivors():
            assert coeffs == list(reversed(coeffs)), (
                f"{label}: not palindromic"
            )

    def test_pool_returns_shallow_copies(self):
        """Mutating a returned entry must not affect subsequent reads."""
        p1 = get_deg12_survivors()
        p1[0][0][0] = 999  # mutate
        p2 = get_deg12_survivors()
        assert p2[0][0][0] != 999


class TestIterSeededSurvivors:
    def test_no_repeat_yields_pool_size(self):
        entries = list(iter_seeded_survivors(degree=12, repeat=False))
        assert len(entries) == len(get_deg12_survivors())

    def test_repeat_yields_first_pool_then_cycles(self):
        it = iter_seeded_survivors(degree=12, repeat=True)
        first_n = [next(it) for _ in range(10)]
        # Pool has 3 entries; with repeat=True we should have cycled
        assert len(first_n) == 10

    def test_unknown_degree_returns_empty(self):
        entries = list(iter_seeded_survivors(degree=99, repeat=False))
        assert entries == []


# ---------------------------------------------------------------------------
# survivor_seed_pool — interleave_decoys
# ---------------------------------------------------------------------------


class TestInterleaveDecoys:
    def test_decoy_rate_zero_no_injection(self):
        natural = iter([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        out = list(interleave_decoys(natural, decoy_rate=0.0))
        assert all(marker == "" for _, marker in out)
        assert len(out) == 3

    def test_decoy_rate_half_injects_some(self):
        natural = iter([[i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, i]
                        for i in range(20)])
        out = list(interleave_decoys(natural, decoy_rate=0.5, degree=12))
        markers = [m for _, m in out]
        n_decoys = markers.count("seeded_survivor")
        n_natural = markers.count("")
        # 20 natural + decoy injection ratio ~50% -> some decoys present
        assert n_natural == 20
        assert n_decoys > 0

    def test_decoy_rate_invalid_raises(self):
        natural = iter([])
        with pytest.raises(ValueError):
            list(interleave_decoys(natural, decoy_rate=1.5))
        with pytest.raises(ValueError):
            list(interleave_decoys(natural, decoy_rate=-0.1))

    def test_decoys_are_palindromic_deg12(self):
        natural = iter([[1] + [0] * 12])  # 1 natural candidate
        # Force high decoy rate to ensure injection
        out = list(interleave_decoys(natural, decoy_rate=0.5, degree=12))
        decoys = [c for c, m in out if m == "seeded_survivor"]
        for c in decoys:
            assert len(c) == 13
            assert c == list(reversed(c))


# ===========================================================================
# Claim-stack pipeline (Aporia adjudication 2026-05-12)
# ===========================================================================


class TestVerifierOutcomeClassesEnum:
    """Per Aporia Mod 2: 5-value enum on LearnerRecord."""

    def test_enum_has_five_values(self):
        assert len(VERIFIER_OUTCOME_CLASSES) == 5

    def test_two_decisive_pass_outcomes_present(self):
        assert "decisive_verified" in VERIFIER_OUTCOME_CLASSES
        assert "decisive_contradicted" in VERIFIER_OUTCOME_CLASSES

    def test_inconclusive_separate_from_failure(self):
        # The whole point of Aporia Mod 2: real Learner signal vs missing data
        assert "decisive_inconclusive" in VERIFIER_OUTCOME_CLASSES
        assert "verifier_transient_failure" in VERIFIER_OUTCOME_CLASSES
        assert "verifier_permanent_failure" in VERIFIER_OUTCOME_CLASSES


class TestEnrichVerifierOutcomeClassParameter:

    def test_default_is_none(self):
        rec = enrich(_FakeDiscoveryRecord())
        assert rec.verifier_outcome_class is None

    def test_accepts_each_known_value(self):
        for v in VERIFIER_OUTCOME_CLASSES:
            rec = enrich(_FakeDiscoveryRecord(), verifier_outcome_class=v)
            assert rec.verifier_outcome_class == v

    def test_explicit_none_is_accepted(self):
        rec = enrich(_FakeDiscoveryRecord(), verifier_outcome_class=None)
        assert rec.verifier_outcome_class is None

    def test_unknown_value_raises(self):
        with pytest.raises(ValueError):
            enrich(_FakeDiscoveryRecord(), verifier_outcome_class="bogus_outcome")

    def test_underscore_separated_typo_raises(self):
        # Common typo: 'decisive verified' (space) — must reject
        with pytest.raises(ValueError):
            enrich(_FakeDiscoveryRecord(), verifier_outcome_class="decisive verified")


class TestClaimRunnerVerifierStubs:
    """Day-1: all 7 verifiers return verifier_permanent_failure with not_yet_implemented."""

    def test_known_verifiers_count(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import KNOWN_VERIFIERS
        assert len(KNOWN_VERIFIERS) == 7

    def test_each_verifier_in_registry(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            KNOWN_VERIFIERS, VERIFIER_REGISTRY,
        )
        for name in KNOWN_VERIFIERS:
            assert name in VERIFIER_REGISTRY
            assert callable(VERIFIER_REGISTRY[name])

    def test_get_verifier_unknown_raises(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import get_verifier
        with pytest.raises(ValueError):
            get_verifier("not_a_real_verifier")

    def test_stub_returns_not_yet_implemented(self):
        # Track 2 2026-05-13: citation_audit is no longer stubbed; use sympy_factor
        # (still stubbed). Same behavior applies to the remaining stubs.
        from prometheus_math.substrate_generation.tier_1_claim_runner import get_verifier
        result = get_verifier("sympy_factor")({"id": "CLAIM-test-00001"})
        assert result.outcome_class == "verifier_permanent_failure"
        assert result.evidence_blob["flag"] == "not_yet_implemented"
        assert result.evidence_blob["claim_id"] == "CLAIM-test-00001"


class TestVerifierDispatchWrapper:
    """Per Aporia Mod 2: transient retries once, permanent fails immediately."""

    def _make_payload(self):
        return {
            "id": "CLAIM-test-00001",
            "claim_category": "frontier_survey",
            "expected_verifier_primary": "citation_audit",
            "expected_verdict": "falsified",
        }

    def test_decisive_outcome_passes_through(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            VerifierResult, _dispatch_verifier,
        )
        def good_verifier(_payload):
            return VerifierResult(outcome_class="decisive_verified")
        result = _dispatch_verifier(good_verifier, self._make_payload())
        assert result.outcome_class == "decisive_verified"

    def test_invalid_outcome_class_returns_permanent_failure(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            VerifierResult, _dispatch_verifier,
        )
        def bad_verifier(_payload):
            return VerifierResult(outcome_class="not_a_real_outcome")
        result = _dispatch_verifier(bad_verifier, self._make_payload())
        assert result.outcome_class == "verifier_permanent_failure"

    def test_non_verifier_result_return_returns_permanent_failure(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _dispatch_verifier
        def wrong_return_type(_payload):
            return {"this": "is not a VerifierResult"}
        result = _dispatch_verifier(wrong_return_type, self._make_payload())
        assert result.outcome_class == "verifier_permanent_failure"

    def test_value_error_is_permanent(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _dispatch_verifier
        def value_err(_payload):
            raise ValueError("bad input shape")
        result = _dispatch_verifier(value_err, self._make_payload())
        assert result.outcome_class == "verifier_permanent_failure"
        assert "ValueError" in result.error_text

    def test_timeout_error_is_transient_retried_once(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _dispatch_verifier
        call_count = [0]
        def transient_then_succeed(_payload):
            call_count[0] += 1
            if call_count[0] == 1:
                raise TimeoutError("network timed out")
            from prometheus_math.substrate_generation.tier_1_claim_runner import VerifierResult
            return VerifierResult(outcome_class="decisive_verified")
        result = _dispatch_verifier(transient_then_succeed, self._make_payload())
        assert result.outcome_class == "decisive_verified"
        assert call_count[0] == 2  # one retry happened

    def test_persistent_transient_returns_transient_failure(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _dispatch_verifier
        def always_timeout(_payload):
            raise TimeoutError("persistent timeout")
        result = _dispatch_verifier(always_timeout, self._make_payload())
        assert result.outcome_class == "verifier_transient_failure"


class TestCitationAuditVerifier:
    """Track 2 Verifier 1 (2026-05-13). Offline-only tests — the network-
    bound paths (arxiv.org HEAD + abstract fetch) are exercised at smoke
    time, not in pytest."""

    def test_no_ground_truth_source_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_citation_audit,
        )
        result = _verifier_citation_audit({"id": "X"})
        assert result.outcome_class == "decisive_inconclusive"
        assert "no_ground_truth_source" in result.evidence_blob["reason"]

    def test_empty_ground_truth_source_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_citation_audit,
        )
        result = _verifier_citation_audit({"id": "X", "ground_truth_source": ""})
        assert result.outcome_class == "decisive_inconclusive"

    def test_non_arxiv_citation_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_citation_audit,
        )
        result = _verifier_citation_audit({
            "id": "X",
            "ground_truth_source": "Shitov 2021 SIAGA 5(4); Boij-Teitler 2019",
        })
        assert result.outcome_class == "decisive_inconclusive"
        assert "no_arxiv_id_extractable" in result.evidence_blob["reason"]

    def test_arxiv_id_with_parenthetical_context_extracts(self):
        """Aporia's batch uses 'arXiv:1604.06431 (BIP 2019 J. AMS)' shape."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _ARXIV_EXTRACT_RE,
        )
        m = _ARXIV_EXTRACT_RE.search("arXiv:1604.06431 (BIP 2019 J. AMS)")
        assert m is not None
        assert m.group(1) == "1604.06431"

    def test_arxiv_id_at_end_of_string_extracts(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _ARXIV_EXTRACT_RE,
        )
        m = _ARXIV_EXTRACT_RE.search("Lee 2025 arXiv:2512.15035 WITHDRAWN")
        assert m is not None
        assert m.group(1) == "2512.15035"

    def test_no_arxiv_id_returns_none(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _ARXIV_EXTRACT_RE,
        )
        assert _ARXIV_EXTRACT_RE.search("KnotInfo 2024-12 snapshot") is None

    def test_registry_points_at_real_verifier_not_stub(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            VERIFIER_REGISTRY, _verifier_citation_audit,
        )
        assert VERIFIER_REGISTRY["citation_audit"] is _verifier_citation_audit


class TestLearnerRecordClaimExtensionFields:
    """Per Track 1 prompt 2026-05-13: claim_id, claim_category, actual_verdict
    carry through from CLAIM payload to LearnerRecord."""

    def test_defaults_are_none(self):
        rec = enrich(_FakeDiscoveryRecord())
        assert rec.claim_id is None
        assert rec.claim_category is None
        assert rec.actual_verdict is None

    def test_pass_through_via_enrich(self):
        rec = enrich(
            _FakeDiscoveryRecord(),
            claim_id="CLAIM-test-00001",
            claim_category="frontier_survey",
            actual_verdict="decisive_verified",
        )
        assert rec.claim_id == "CLAIM-test-00001"
        assert rec.claim_category == "frontier_survey"
        assert rec.actual_verdict == "decisive_verified"


class TestRunClaim:

    def _payload(self, **overrides):
        base = {
            "_schema_version": "1.0.0",
            "id": "CLAIM-test-00001",
            "claim_category": "frontier_survey",
            "claim_text": "Sample claim long enough to pass the 20-char minimum.",
            # Use a stubbed verifier so this test stays deterministic offline
            # (citation_audit is wired against arxiv.org as of 2026-05-13).
            "expected_verifier_primary": "sympy_factor",
            "expected_verdict": "falsified",
            "ground_truth_source": "arXiv:1604.06431",
            "trust_tier": "analytically_proven",
            "source_report": "test fixture",
        }
        base.update(overrides)
        return base

    def test_stubbed_verifier_yields_permanent_failure(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import run_claim
        result, records = run_claim(self._payload())
        assert result.actual_verdict == "verifier_permanent_failure"
        assert result.verifier_used == "sympy_factor"
        assert result.expected_actual_match is False  # failure never matches expected
        assert len(records) == 1
        assert records[0].verifier_outcome_class == "verifier_permanent_failure"
        # Track 1 2026-05-13: claim_id / claim_category / actual_verdict carry through
        assert records[0].claim_id == "CLAIM-test-00001"
        assert records[0].claim_category == "frontier_survey"
        assert records[0].actual_verdict == "verifier_permanent_failure"

    def test_verdict_match_mapping(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _verdict_match
        assert _verdict_match("survived", "decisive_verified") is True
        assert _verdict_match("falsified", "decisive_contradicted") is True
        assert _verdict_match("open", "decisive_inconclusive") is True
        assert _verdict_match("conditional", "decisive_inconclusive") is True
        assert _verdict_match("survived", "decisive_contradicted") is False
        assert _verdict_match("falsified", "verifier_permanent_failure") is False

    def test_kill_signature_anti_leakage(self):
        # Permanent verifier failure should produce a categorical
        # kill_pattern, not literal claim_text content
        from prometheus_math.substrate_generation.tier_1_claim_runner import run_claim
        _result, records = run_claim(self._payload())
        sig = records[0].kill_signature
        # No literal claim_text content in the signature
        assert all("Sample" not in s for s in sig)
        assert all("arXiv" not in s for s in sig)


class TestClaimBatchQualityRules:
    """Per claim_stack_design §5: Rules A (diversity) / B (verdicts) / C (trust)."""

    def _claim(self, idx, **overrides):
        base = {
            "_schema_version": "1.0.0",
            "id": f"CLAIM-test-{idx:05d}",
            "claim_category": "frontier_survey",
            "claim_text": "Sample claim long enough to pass the 20-char minimum.",
            "expected_verifier_primary": "citation_audit",
            "expected_verdict": "falsified",
            "ground_truth_source": "arXiv:1604.06431",
            "trust_tier": "analytically_proven",
            "source_report": "test fixture",
        }
        base.update(overrides)
        return base

    def test_empty_batch_rejected(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _enforce_quality_rules
        with pytest.raises(ValueError, match="empty"):
            _enforce_quality_rules([])

    def test_small_batch_uniform_categories_allowed(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _enforce_quality_rules
        # 5 claims, all same category — Rule A only kicks in at >=10
        _enforce_quality_rules([self._claim(i) for i in range(5)])

    def test_large_batch_requires_3_categories(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _enforce_quality_rules
        # 10 claims, all frontier_survey — must fail Rule A
        with pytest.raises(ValueError, match="Rule A"):
            _enforce_quality_rules([self._claim(i) for i in range(10)])

    def test_rule_c_ml_predicted_over_10pct_rejected(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _enforce_quality_rules
        # 10 claims, 2 ml_predicted (20%) — must fail Rule C
        # Spread categories + verdicts to clear Rules A & B first
        claims = [self._claim(i) for i in range(8)]
        for i, c in enumerate(claims):
            c["claim_category"] = ["frontier_survey", "calibration", "boundary"][i % 3]
            c["expected_verdict"] = ["falsified", "survived"][i % 2]
            if c["claim_category"] == "calibration":
                c["prompt_template"] = "answer this please"
        ml_claims = [self._claim(i + 100, trust_tier="ml_predicted") for i in range(2)]
        for i, c in enumerate(ml_claims):
            c["claim_category"] = ["frontier_survey", "calibration"][i % 2]
            c["expected_verdict"] = "open"
            if c["claim_category"] == "calibration":
                c["prompt_template"] = "answer this please"
        with pytest.raises(ValueError, match="Rule C"):
            _enforce_quality_rules(claims + ml_claims)

    def test_well_balanced_batch_passes(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import _enforce_quality_rules
        claims = []
        for i in range(12):
            c = self._claim(
                i,
                claim_category=["frontier_survey", "calibration", "boundary"][i % 3],
                expected_verdict=["falsified", "survived", "open"][i % 3],
            )
            if c["claim_category"] == "calibration":
                c["prompt_template"] = "answer this please"
            claims.append(c)
        # All analytically_proven → 100% proven, 0% ml_predicted; passes Rule C
        # 3 categories, 3 verdicts; passes A and B
        _enforce_quality_rules(claims)


class TestRunClaimBatch:
    """End-to-end: load batch → dispatch all stubs → emit summary."""

    def test_batch_run_with_stubs(self, tmp_path):
        from prometheus_math.substrate_generation.tier_1_claim_runner import run_claim_batch

        # Build a minimal batch (3 claims, mixed categories, all proven)
        batch_path = tmp_path / "batch.jsonl"
        claims = [
            {
                "_schema_version": "1.0.0",
                "id": f"CLAIM-test-{i:05d}",
                "claim_category": ["frontier_survey", "boundary", "substrate_self"][i],
                "claim_text": "Sample claim long enough to pass the 20-char minimum.",
                # sympy_factor still stubbed; citation_audit now wired (network).
                "expected_verifier_primary": "sympy_factor",
                "expected_verdict": ["falsified", "survived", "open"][i],
                "ground_truth_source": "arXiv:1604.06431",
                "trust_tier": "analytically_proven",
                "source_report": "test fixture",
            }
            for i in range(3)
        ]
        batch_path.write_text(
            "\n".join(json.dumps(c) for c in claims), encoding="utf-8",
        )

        out_jsonl = tmp_path / "records.jsonl"
        out_summary = tmp_path / "summary.json"
        summary = run_claim_batch(
            batch_path,
            out_jsonl=out_jsonl,
            out_summary=out_summary,
            kernel=None,
            enforce_quality_rules=False,  # 3 claims < diversity threshold anyway
        )

        assert summary["n_claims"] == 3
        assert summary["n_learner_records"] == 3
        assert summary["permanent_failure_count"] == 3  # all stubs fail
        assert summary["expected_actual_match_rate"] == 0.0
        assert out_jsonl.exists()
        assert out_summary.exists()
        # Each emitted record carries the verifier_outcome_class
        for line in out_jsonl.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            assert rec["verifier_outcome_class"] == "verifier_permanent_failure"
