"""Tests for Tier-1 substrate generation enrichment.

Per Ergon discussion `ergon/learner/v1_0_plans/substrate_quality_for_learner_discussion.md`
+ Techne reply 2026-05-11. Covers:
  - learner_enrichment.py (Dim 1, 4, 6, 9 enrichment fields)
  - survivor_seed_pool.py (Dim 7 decoy interleaving)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pytest

from prometheus_math.substrate_generation.learner_enrichment import (
    DECOY_KINDS,
    EPISODE_PHASES,
    LearnerRecord,
    OUTCOME_CLASSES,
    VERIFICATION_TIERS,
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
