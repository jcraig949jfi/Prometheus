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
        # 2026-05-13 hour 7: 6 of 7 verifiers wired. Only manual_review
        # remains stubbed (needs human-in-the-loop infrastructure design).
        from prometheus_math.substrate_generation.tier_1_claim_runner import get_verifier
        result = get_verifier("manual_review")({"id": "CLAIM-test-00001"})
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


class TestCatalogLookupVerifier:
    """Track 2 Verifier 2 (2026-05-13). MVP: tensor catalog T#NN entry
    existence lookup. Non-tensor catalogs return inconclusive for now."""

    def test_extract_t_entry_id_from_claim_id(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _extract_t_entry_id,
        )
        assert _extract_t_entry_id({"id": "CLAIM-boundary-T4-00001"}) == "T#4"
        assert _extract_t_entry_id({"id": "CLAIM-boundary-T56-00001"}) == "T#56"
        assert _extract_t_entry_id({"id": "CLAIM-frontier-00001"}) is None
        assert _extract_t_entry_id({"id": "CLAIM-calibration-knots-00001"}) is None

    def test_extract_t_entry_id_from_verifier_args(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _extract_t_entry_id,
        )
        # Explicit verifier_args.entry_id overrides claim_id pattern
        assert (
            _extract_t_entry_id({
                "id": "CLAIM-frontier-00001",
                "verifier_args": {"entry_id": "T#22"},
            })
            == "T#22"
        )

    def test_no_t_entry_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_catalog_lookup,
        )
        result = _verifier_catalog_lookup({"id": "CLAIM-calibration-bsd-00001"})
        assert result.outcome_class == "decisive_inconclusive"
        assert "no_t_entry_id_extractable" in result.evidence_blob["reason"]

    def test_existing_t_entry_returns_inconclusive_with_evidence(self):
        """T#1 (matrix multiplication exponent ω) is well-established in
        the tensor catalog."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_catalog_lookup,
        )
        result = _verifier_catalog_lookup({"id": "CLAIM-boundary-T1-00001"})
        assert result.outcome_class == "decisive_inconclusive"
        assert result.evidence_blob["entry_id"] == "T#1"
        assert result.evidence_blob["entry_body_chars"] > 100
        assert "entry_confirmed" in result.evidence_blob["reason"]

    def test_missing_t_entry_returns_contradicted(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_catalog_lookup,
        )
        # T#9999 won't exist in the catalog
        result = _verifier_catalog_lookup({
            "id": "CLAIM-boundary-T9999-00001",
        })
        assert result.outcome_class == "decisive_contradicted"
        assert result.evidence_blob["entry_id"] == "T#9999"
        assert "catalog_entry_missing" in result.evidence_blob["reason"]

    def test_registry_points_at_real_verifier(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            VERIFIER_REGISTRY, _verifier_catalog_lookup,
        )
        assert VERIFIER_REGISTRY["catalog_lookup"] is _verifier_catalog_lookup


class TestMpmathComputeVerifier:
    """Track 2 Verifier 3 (2026-05-13). MVP scope: Mahler-measure family
    via calibration table keyed by claim_id."""

    def test_unknown_claim_id_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_mpmath_compute,
        )
        result = _verifier_mpmath_compute({"id": "CLAIM-test-99999"})
        assert result.outcome_class == "decisive_inconclusive"
        assert "no_calibration_entry" in result.evidence_blob["reason"]

    def test_lehmer_smoke_target_verifies(self):
        """Aporia's CLAIM-calibration-mahler-00001 — the canonical smoke
        target. M(Lehmer) = 1.176280818259917506544... at dps=30."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_mpmath_compute,
        )
        result = _verifier_mpmath_compute({
            "id": "CLAIM-calibration-mahler-00001",
            "verifier_args": {"dps": 30, "tolerance": "1e-25"},
        })
        assert result.outcome_class == "decisive_verified"
        assert result.evidence_blob["dps"] == 30
        # Diff should be << tolerance
        assert "diff" in result.evidence_blob

    def test_compute_mahler_measure_matches_known_value(self):
        """Direct numerical check on _compute_mahler_measure."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _compute_mahler_measure,
        )
        coeffs = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]  # Lehmer descending
        import mpmath as mp
        saved = mp.mp.dps
        mp.mp.dps = 35
        try:
            computed = _compute_mahler_measure(coeffs, 30)
            expected = mp.mpf("1.17628081825991750654407033847")
            assert abs(computed - expected) < mp.mpf("1e-25")
        finally:
            mp.mp.dps = saved

    def test_invalid_tolerance_returns_permanent_failure(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_mpmath_compute,
        )
        result = _verifier_mpmath_compute({
            "id": "CLAIM-calibration-mahler-00001",
            "verifier_args": {"tolerance": "not-a-float"},
        })
        assert result.outcome_class == "verifier_permanent_failure"

    def test_registry_points_at_real_verifier(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            VERIFIER_REGISTRY, _verifier_mpmath_compute,
        )
        assert VERIFIER_REGISTRY["mpmath_compute"] is _verifier_mpmath_compute


class TestSubstrateSelfCheckVerifier:
    """Track 2 Verifier 4 (2026-05-13). Dispatches via
    verifier_args.invariant_name."""

    def test_no_invariant_name_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_substrate_self_check,
        )
        result = _verifier_substrate_self_check({"id": "X"})
        assert result.outcome_class == "decisive_inconclusive"
        assert "no_invariant_name" in result.evidence_blob["reason"]
        assert len(result.evidence_blob["available_invariants"]) >= 4

    def test_unknown_invariant_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_substrate_self_check,
        )
        result = _verifier_substrate_self_check({
            "id": "X",
            "verifier_args": {"invariant_name": "not_registered"},
        })
        assert result.outcome_class == "decisive_inconclusive"
        assert "unknown_invariant_name" in result.evidence_blob["reason"]

    def test_known_holding_invariant_verifies(self):
        """verifier_outcome_classes_size_5 holds: 5 enum values."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_substrate_self_check,
        )
        result = _verifier_substrate_self_check({
            "id": "CLAIM-substrate-self-00001",
            "verifier_args": {"invariant_name": "verifier_outcome_classes_size_5"},
        })
        assert result.outcome_class == "decisive_verified"
        assert result.evidence_blob["holds"] is True

    def test_kill_signature_invariant_holds(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_substrate_self_check,
        )
        for inv_name in (
            "kill_signature_survived_for_none",
            "kill_signature_survived_for_empty_string",
        ):
            result = _verifier_substrate_self_check({
                "id": "CLAIM-substrate-self-test",
                "verifier_args": {"invariant_name": inv_name},
            })
            assert result.outcome_class == "decisive_verified", (
                f"invariant {inv_name} should hold"
            )

    def test_known_verifiers_size_7(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_substrate_self_check,
        )
        result = _verifier_substrate_self_check({
            "id": "X",
            "verifier_args": {"invariant_name": "known_verifiers_size_7"},
        })
        assert result.outcome_class == "decisive_verified"

    def test_loop_hour_6_runtime_invariants_hold(self):
        """Per Day-3 substrate_self batch (loop hour 6): runtime invariants
        added for VERIFIER_REGISTRY consistency, calibration tables, T#
        bound checkers, and anti_anchor registry sanity."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_substrate_self_check,
        )
        new_invariants = [
            "verifier_registry_matches_known_verifiers",
            "mpmath_calibration_table_has_lehmer_entry",
            "sympy_calibration_table_has_trefoil_entry",
            "sympy_calibration_table_has_jones_entry",
            "t_bound_checkers_have_t1_t4_t56",
            "anti_anchor_registry_has_aa001",
            "anti_anchor_registry_nonempty",
            "t1_omega_lower_is_2",
            "t4_m3_upper_is_23",
        ]
        for inv in new_invariants:
            result = _verifier_substrate_self_check({
                "id": "X",
                "verifier_args": {"invariant_name": inv},
            })
            assert result.outcome_class == "decisive_verified", (
                f"invariant {inv!r} should hold but returned {result.outcome_class}"
            )

    def test_registry_points_at_real_verifier(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            VERIFIER_REGISTRY, _verifier_substrate_self_check,
        )
        assert VERIFIER_REGISTRY["substrate_self_check"] is _verifier_substrate_self_check


class TestTriangulationVerifier:
    """Loop hour 7 2026-05-13. Meta-verifier dispatching multiple
    verifiers and aggregating into agreement/disagreement."""

    def test_unanimous_verified_agreement(self):
        """When all dispatched verifiers return decisive_verified,
        triangulation returns decisive_verified."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_triangulation, VerifierResult, VERIFIER_REGISTRY,
        )
        # Stub the registry temporarily — both return verified
        orig_a = VERIFIER_REGISTRY.get("citation_audit")
        orig_b = VERIFIER_REGISTRY.get("catalog_lookup")
        VERIFIER_REGISTRY["citation_audit"] = lambda p: VerifierResult(
            outcome_class="decisive_verified", method_used="citation_audit",
        )
        VERIFIER_REGISTRY["catalog_lookup"] = lambda p: VerifierResult(
            outcome_class="decisive_verified", method_used="catalog_lookup",
        )
        try:
            result = _verifier_triangulation({"id": "X"})
            assert result.outcome_class == "decisive_verified"
            assert result.evidence_blob["agreement"] == "unanimous"
        finally:
            VERIFIER_REGISTRY["citation_audit"] = orig_a
            VERIFIER_REGISTRY["catalog_lookup"] = orig_b

    def test_unanimous_contradicted_agreement(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_triangulation, VerifierResult, VERIFIER_REGISTRY,
        )
        orig_a = VERIFIER_REGISTRY.get("citation_audit")
        orig_b = VERIFIER_REGISTRY.get("catalog_lookup")
        VERIFIER_REGISTRY["citation_audit"] = lambda p: VerifierResult(
            outcome_class="decisive_contradicted", method_used="citation_audit",
        )
        VERIFIER_REGISTRY["catalog_lookup"] = lambda p: VerifierResult(
            outcome_class="decisive_contradicted", method_used="catalog_lookup",
        )
        try:
            result = _verifier_triangulation({"id": "X"})
            assert result.outcome_class == "decisive_contradicted"
        finally:
            VERIFIER_REGISTRY["citation_audit"] = orig_a
            VERIFIER_REGISTRY["catalog_lookup"] = orig_b

    def test_mixed_decisive_flags_disagreement(self):
        """When verifiers disagree (one verified, one contradicted),
        triangulation returns decisive_inconclusive with disagreement
        evidence — a substrate-grade finding."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_triangulation, VerifierResult, VERIFIER_REGISTRY,
        )
        orig_a = VERIFIER_REGISTRY.get("citation_audit")
        orig_b = VERIFIER_REGISTRY.get("catalog_lookup")
        VERIFIER_REGISTRY["citation_audit"] = lambda p: VerifierResult(
            outcome_class="decisive_verified", method_used="citation_audit",
        )
        VERIFIER_REGISTRY["catalog_lookup"] = lambda p: VerifierResult(
            outcome_class="decisive_contradicted", method_used="catalog_lookup",
        )
        try:
            result = _verifier_triangulation({"id": "X"})
            assert result.outcome_class == "decisive_inconclusive"
            assert result.evidence_blob["agreement"] == "mixed_decisive"
            assert "substrate_verifier_disagreement" in result.evidence_blob["reason"]
        finally:
            VERIFIER_REGISTRY["citation_audit"] = orig_a
            VERIFIER_REGISTRY["catalog_lookup"] = orig_b

    def test_all_inconclusive_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_triangulation, VerifierResult, VERIFIER_REGISTRY,
        )
        orig_a = VERIFIER_REGISTRY.get("citation_audit")
        orig_b = VERIFIER_REGISTRY.get("catalog_lookup")
        VERIFIER_REGISTRY["citation_audit"] = lambda p: VerifierResult(
            outcome_class="decisive_inconclusive", method_used="citation_audit",
        )
        VERIFIER_REGISTRY["catalog_lookup"] = lambda p: VerifierResult(
            outcome_class="decisive_inconclusive", method_used="catalog_lookup",
        )
        try:
            result = _verifier_triangulation({"id": "X"})
            assert result.outcome_class == "decisive_inconclusive"
            assert result.evidence_blob["agreement"] == "no_decisive_signal"
        finally:
            VERIFIER_REGISTRY["citation_audit"] = orig_a
            VERIFIER_REGISTRY["catalog_lookup"] = orig_b

    def test_self_recursion_filter(self):
        """triangulation must not recurse into itself."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_triangulation,
        )
        result = _verifier_triangulation({
            "id": "X",
            "verifier_args": {"verifiers": ["triangulation"]},
        })
        # After self-filter the list is empty -> permanent_failure
        assert result.outcome_class == "verifier_permanent_failure"

    def test_unknown_verifier_in_list_records_permanent_failure(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_triangulation,
        )
        result = _verifier_triangulation({
            "id": "X",
            "verifier_args": {"verifiers": ["not_a_real_verifier"]},
        })
        # All inconclusive -> aggregate inconclusive
        assert result.outcome_class == "decisive_inconclusive"
        unknown_entries = [
            e for e in result.evidence_blob["per_verifier"]
            if e.get("reason") == "unknown_verifier"
        ]
        assert len(unknown_entries) == 1

    def test_registry_points_at_real_verifier(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            VERIFIER_REGISTRY, _verifier_triangulation,
        )
        assert VERIFIER_REGISTRY["triangulation"] is _verifier_triangulation


class TestAntiAnchorCoupletOverride:
    """Loop hour 5 2026-05-13. Anti-anchor couplet logic — handles
    fundamental citation_audit limitation (verifies existence not
    semantic alignment)."""

    def test_no_parent_block_returns_none(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _check_anti_anchor_couplet_override,
        )
        assert _check_anti_anchor_couplet_override({"id": "X"}) is None

    def test_non_AA_parent_block_returns_none(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _check_anti_anchor_couplet_override,
        )
        result = _check_anti_anchor_couplet_override({
            "id": "X", "parent_block": "T#1", "source_report": "false_form",
        })
        assert result is None

    def test_no_form_marker_returns_none(self):
        """parent_block matches but source_report doesn't tag false/true_form."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _check_anti_anchor_couplet_override,
        )
        result = _check_anti_anchor_couplet_override({
            "id": "X",
            "parent_block": "AA-001",
            "source_report": "general note",
        })
        assert result is None

    def test_unregistered_aa_id_returns_none(self):
        """Even with form marker + AA-NNN shape, unregistered IDs defer."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _check_anti_anchor_couplet_override,
        )
        result = _check_anti_anchor_couplet_override({
            "id": "X",
            "parent_block": "AA-9999",
            "source_report": "AA-9999 anti_anchor false_form",
        })
        assert result is None

    def test_false_form_registered_aa_yields_contradicted(self):
        """AA-001 is registered + source_report tags false_form -> override."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _check_anti_anchor_couplet_override,
        )
        result = _check_anti_anchor_couplet_override({
            "id": "CLAIM-frontier-00001",
            "parent_block": "AA-001",
            "source_report": "AA-001 anti_anchor false_form",
            "paired_claim_id": "CLAIM-frontier-00002",
        })
        assert result is not None
        assert result.outcome_class == "decisive_contradicted"
        assert result.evidence_blob["parent_block"] == "AA-001"

    def test_true_form_registered_aa_yields_verified(self):
        """true_form override resolves the multi-citation Saxl case."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _check_anti_anchor_couplet_override,
        )
        result = _check_anti_anchor_couplet_override({
            "id": "CLAIM-frontier-00006",
            "parent_block": "AA-004",
            "source_report": "AA-004 anti_anchor true_form",
        })
        assert result is not None
        assert result.outcome_class == "decisive_verified"

    def test_run_claim_applies_override(self):
        """End-to-end: false_form claim with citation_audit-verified citation
        should be overridden to decisive_contradicted."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            run_claim,
        )
        # Use a claim shape Aporia would author
        claim = {
            "_schema_version": "1.0.0",
            "id": "CLAIM-frontier-00001",
            "claim_category": "frontier_survey",
            "claim_text": (
                "Bürgisser-Ikenmeyer-Panova killed GCT entirely; occurrence "
                "obstructions for det/padded-perm are still a viable path."
            ),
            # Use sympy_factor (returns inconclusive on no-calibration-entry)
            # to keep the test offline; couplet override should still fire.
            "expected_verifier_primary": "sympy_factor",
            "expected_verdict": "falsified",
            "ground_truth_source": "arXiv:1604.06431",
            "trust_tier": "analytically_proven",
            "source_report": "AA-001 anti_anchor false_form",
            "parent_block": "AA-001",
        }
        result, _records = run_claim(claim, kernel=None, emit_kernel_opcodes=False)
        assert result.actual_verdict == "decisive_contradicted"
        assert result.verifier_used == "anti_anchor_couplet_override"
        assert result.expected_actual_match is True


class TestTBoundCheckers:
    """Per-T# numeric bound comparison closures wired into catalog_lookup,
    loop hour 4 2026-05-13."""

    def test_t1_omega_upper_bound_implication(self):
        """ω < 2.371339 follows from established upper bound."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t1_omega_bound_check,
        )
        result = _t1_omega_bound_check("The matrix multiplication exponent ω satisfies ω < 2.371339.")
        assert result is not None
        outcome, _caveats = result
        assert outcome == "decisive_verified"

    def test_t1_omega_below_lower_bound_contradicts(self):
        """ω = 1.9 violates trivial lower bound ω >= 2."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t1_omega_bound_check,
        )
        result = _t1_omega_bound_check("The matrix multiplication exponent ω equals 1.9 (i.e., ω < 2).")
        assert result is not None
        outcome, _caveats = result
        assert outcome == "decisive_contradicted"

    def test_t1_omega_equals_2_open(self):
        """ω = 2 is within range but unproven; inconclusive.

        Note: extractor regex requires the `=` symbol, not the word
        'equals'. Aporia's actual CLAIM-boundary-T1-00002 uses the
        word form ('ω equals 2 exactly'), which falls through to the
        outer catalog_lookup's 'entry confirmed but extraction failed'
        path — also returning decisive_inconclusive at the verifier
        level. Either way, expected=open matches.
        """
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t1_omega_bound_check,
        )
        result = _t1_omega_bound_check("Claim: ω = 2 exactly.")
        assert result is not None
        outcome, _caveats = result
        assert outcome == "decisive_inconclusive"

    def test_t1_no_omega_mention_returns_none(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t1_omega_bound_check,
        )
        assert _t1_omega_bound_check("Some unrelated text about tensors.") is None

    def test_t4_m3_rank_at_upper_bound_verifies(self):
        """R(M<3>) <= 23 is implied by Laderman 1976."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t4_m3_rank_bound_check,
        )
        result = _t4_m3_rank_bound_check("R(M<3>) <= 23.")
        assert result is not None
        outcome, _caveats = result
        assert outcome == "decisive_verified"

    def test_t4_m3_rank_below_lower_bound_contradicts(self):
        """R(M<3>) <= 18 violates Landsberg lower bound 19."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t4_m3_rank_bound_check,
        )
        result = _t4_m3_rank_bound_check("R(M<3>) <= 18.")
        assert result is not None
        outcome, _caveats = result
        assert outcome == "decisive_contradicted"

    def test_t4_m3_rank_equality_in_range(self):
        """R(M<3>) = 20 is within [19,23]; inconclusive (exact value open)."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t4_m3_rank_bound_check,
        )
        result = _t4_m3_rank_bound_check("Claim: R(M<3>) = 20.")
        assert result is not None
        outcome, _caveats = result
        assert outcome == "decisive_inconclusive"

    def test_catalog_lookup_uses_t_bound_checker_when_registered(self):
        """End-to-end: catalog_lookup dispatches T#1 to its bound checker."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_catalog_lookup,
        )
        result = _verifier_catalog_lookup({
            "id": "CLAIM-boundary-T1-00001",
            "claim_text": "ω < 2.371339",
        })
        assert result.outcome_class == "decisive_verified"
        assert result.evidence_blob["entry_id"] == "T#1"
        assert result.evidence_blob.get("bound_check") == "T#-specific-closure"

    def test_t_bound_checker_registry_has_t1_t4_t56(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _T_BOUND_CHECKERS,
        )
        assert "T#1" in _T_BOUND_CHECKERS
        assert "T#4" in _T_BOUND_CHECKERS
        assert "T#56" in _T_BOUND_CHECKERS

    def test_t56_sym_rank_in_p_contradicted(self):
        """Claim of polynomial-time decidability for symmetric tensor rank
        over Q contradicts Shitov 2016 NP-hardness."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t56_sym_rank_complexity_check,
        )
        result = _t56_sym_rank_complexity_check(
            "The symmetric tensor rank computation over the rationals is decidable in polynomial time."
        )
        assert result is not None
        outcome, _ = result
        assert outcome == "decisive_contradicted"

    def test_t56_handles_line_wrapped_claim_text(self):
        """Aporia's CLAIM-boundary-T56-00001 has 'decidable in\\npolynomial time'.
        Whitespace normalization in the checker must handle this."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t56_sym_rank_complexity_check,
        )
        result = _t56_sym_rank_complexity_check(
            "The symmetric tensor rank computation over the rationals is decidable in\npolynomial time."
        )
        assert result is not None
        outcome, _ = result
        assert outcome == "decisive_contradicted"

    def test_t56_np_hard_claim_verified(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t56_sym_rank_complexity_check,
        )
        result = _t56_sym_rank_complexity_check(
            "Symmetric tensor rank over Q is NP-hard."
        )
        assert result is not None
        outcome, _ = result
        assert outcome == "decisive_verified"

    def test_t56_unrelated_claim_returns_none(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _t56_sym_rank_complexity_check,
        )
        assert _t56_sym_rank_complexity_check("Some unrelated text about tensors.") is None


class TestSympyFactorVerifier:
    """sympy_factor verifier wired 2026-05-13 hour 3."""

    def test_unknown_claim_id_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_sympy_factor,
        )
        result = _verifier_sympy_factor({"id": "CLAIM-test-99999"})
        assert result.outcome_class == "decisive_inconclusive"
        assert "no_calibration_entry" in result.evidence_blob["reason"]

    def test_trefoil_alexander_verifies(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_sympy_factor,
        )
        result = _verifier_sympy_factor({
            "id": "CLAIM-calibration-knots-00001",
            "claim_text": (
                "The Alexander polynomial of the trefoil knot (3_1) is "
                "Δ(t) = t^2 - t + 1\nin canonical form."
            ),
        })
        assert result.outcome_class == "decisive_verified"
        assert result.evidence_blob["match"] is True

    def test_figure_eight_jones_verifies(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_sympy_factor,
        )
        result = _verifier_sympy_factor({
            "id": "CLAIM-calibration-jones-00001",
            "claim_text": (
                "The Jones polynomial of the figure-eight knot 4_1 is "
                "V(t) = t^{-2} - t^{-1} + 1 - t + t^2."
            ),
        })
        assert result.outcome_class == "decisive_verified"

    def test_mismatched_polynomial_contradicts(self):
        """If the claim_text says the wrong polynomial, must contradict."""
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_sympy_factor,
        )
        result = _verifier_sympy_factor({
            "id": "CLAIM-calibration-knots-00001",
            "claim_text": (
                # Wrong polynomial — t^2 + t + 1 instead of t^2 - t + 1
                "The Alexander polynomial of the trefoil knot (3_1) is "
                "Δ(t) = t^2 + t + 1\nin canonical form."
            ),
        })
        assert result.outcome_class == "decisive_contradicted"
        assert "polynomial_mismatch" in result.evidence_blob["reason"]

    def test_unparseable_claim_text_returns_inconclusive(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            _verifier_sympy_factor,
        )
        result = _verifier_sympy_factor({
            "id": "CLAIM-calibration-knots-00001",
            "claim_text": "some text with no = sign at all",
        })
        assert result.outcome_class == "decisive_inconclusive"

    def test_registry_points_at_real_verifier(self):
        from prometheus_math.substrate_generation.tier_1_claim_runner import (
            VERIFIER_REGISTRY, _verifier_sympy_factor,
        )
        assert VERIFIER_REGISTRY["sympy_factor"] is _verifier_sympy_factor


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
            # Use a still-stubbed verifier so this test stays deterministic
            # offline. As of 2026-05-13 hour 7: only manual_review remains
            # stubbed; the other 6 are wired (live).
            "expected_verifier_primary": "manual_review",
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
        assert result.verifier_used == "manual_review"
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
                # As of hour 7 2026-05-13, only manual_review remains stubbed
                # — all 6 others are wired (live). Keep tests offline.
                "expected_verifier_primary": "manual_review",
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
