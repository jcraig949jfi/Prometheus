"""Tests for prometheus_math.encodings.large_cardinal_consistency.

Closes T-2026-05-07-T027 implementation per
`prometheus_math/encodings/large_cardinal_consistency_GAP.md`.
Mini contract-change window 2026-05-10 (orthogonal to Aporia Phase-2
5-meta-primitive plan; foundations/logic primitive doesn't fit any
of the 5 metas).

Two new frozen dataclasses:
  - FormalTheory: registered axiomatic theory with content-addressed
    axioms_hash + closed-enum axiomatization_lang
  - ConsistencyRelation: typed `Con(stronger) -> Con(weaker)` claim
    with closed-enum justification_method
"""
from __future__ import annotations

import dataclasses

import pytest

from prometheus_math.encodings.large_cardinal_consistency import (
    AxiomatizationLang,
    ConsistencyRelation,
    FormalTheory,
    JustificationMethod,
    VALID_AXIOMATIZATION_LANGS,
    VALID_JUSTIFICATION_METHODS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _zfc() -> FormalTheory:
    return FormalTheory(
        theory_id="ZFC",
        axioms_hash="0" * 64,
        axiomatization_lang="informal",
        chart_id="formal_theory:foundations",
    )


def _zfc_meas() -> FormalTheory:
    return FormalTheory(
        theory_id="ZFC + measurable cardinal exists",
        axioms_hash="1" * 64,
        axiomatization_lang="informal",
        chart_id="formal_theory:foundations",
    )


def _zfc_neg_sch() -> FormalTheory:
    return FormalTheory(
        theory_id="ZFC + ¬SCH",
        axioms_hash="2" * 64,
        axiomatization_lang="informal",
        chart_id="formal_theory:foundations",
    )


# ---------------------------------------------------------------------------
# FormalTheory contract
# ---------------------------------------------------------------------------


class TestFormalTheoryContract:
    def test_construction(self):
        t = _zfc()
        assert t.theory_id == "ZFC"
        assert t.axioms_hash == "0" * 64
        assert t.axiomatization_lang == "informal"

    def test_frozen(self):
        t = _zfc()
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.theory_id = "different"  # type: ignore

    def test_empty_theory_id_raises(self):
        with pytest.raises(ValueError):
            FormalTheory(theory_id="", axioms_hash="x", axiomatization_lang="informal",
                         chart_id="formal_theory:foundations")

    def test_non_string_theory_id_raises(self):
        with pytest.raises(ValueError):
            FormalTheory(theory_id=123, axioms_hash="x",  # type: ignore
                         axiomatization_lang="informal",
                         chart_id="formal_theory:foundations")

    def test_empty_axioms_hash_raises(self):
        with pytest.raises(ValueError):
            FormalTheory(theory_id="ZFC", axioms_hash="",
                         axiomatization_lang="informal",
                         chart_id="formal_theory:foundations")

    def test_unknown_axiomatization_lang_raises(self):
        with pytest.raises(ValueError):
            FormalTheory(theory_id="ZFC", axioms_hash="x",
                         axiomatization_lang="latex",  # not registered
                         chart_id="formal_theory:foundations")

    def test_empty_chart_id_raises(self):
        with pytest.raises(ValueError):
            FormalTheory(theory_id="ZFC", axioms_hash="x",
                         axiomatization_lang="informal", chart_id="")

    @pytest.mark.parametrize("lang", list(VALID_AXIOMATIZATION_LANGS))
    def test_all_registered_langs_accepted(self, lang: str):
        t = FormalTheory(theory_id="x", axioms_hash="y",
                         axiomatization_lang=lang,
                         chart_id="formal_theory:foundations")
        assert t.axiomatization_lang == lang


# ---------------------------------------------------------------------------
# ConsistencyRelation contract
# ---------------------------------------------------------------------------


class TestConsistencyRelationContract:
    def test_construction_strict(self):
        rel = ConsistencyRelation(
            stronger=_zfc_meas(),
            weaker=_zfc_neg_sch(),
            justification_ref="Magidor 1977 SCH failure",
            justification_method="forcing",
            chart_id="consistency_relation:foundations",
        )
        assert rel.stronger.theory_id == "ZFC + measurable cardinal exists"
        assert rel.weaker.theory_id == "ZFC + ¬SCH"
        assert rel.justification_method == "forcing"
        assert rel.is_strict is True

    def test_frozen(self):
        rel = ConsistencyRelation(
            stronger=_zfc_meas(), weaker=_zfc_neg_sch(),
            justification_ref="Magidor 1977",
            justification_method="forcing",
            chart_id="consistency_relation:foundations",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            rel.justification_method = "inner_model"  # type: ignore

    def test_non_FormalTheory_stronger_raises(self):
        with pytest.raises(TypeError):
            ConsistencyRelation(
                stronger="ZFC",  # type: ignore
                weaker=_zfc_neg_sch(),
                justification_ref="x", justification_method="forcing",
                chart_id="consistency_relation:foundations",
            )

    def test_non_FormalTheory_weaker_raises(self):
        with pytest.raises(TypeError):
            ConsistencyRelation(
                stronger=_zfc_meas(), weaker="ZFC + ¬SCH",  # type: ignore
                justification_ref="x", justification_method="forcing",
                chart_id="consistency_relation:foundations",
            )

    def test_empty_justification_ref_raises(self):
        with pytest.raises(ValueError):
            ConsistencyRelation(
                stronger=_zfc_meas(), weaker=_zfc_neg_sch(),
                justification_ref="",
                justification_method="forcing",
                chart_id="consistency_relation:foundations",
            )

    def test_unknown_justification_method_raises(self):
        with pytest.raises(ValueError):
            ConsistencyRelation(
                stronger=_zfc_meas(), weaker=_zfc_neg_sch(),
                justification_ref="x",
                justification_method="hand_waving",  # not registered
                chart_id="consistency_relation:foundations",
            )

    @pytest.mark.parametrize("method", list(VALID_JUSTIFICATION_METHODS))
    def test_all_registered_methods_accepted(self, method: str):
        rel = ConsistencyRelation(
            stronger=_zfc_meas(), weaker=_zfc(),
            justification_ref="x", justification_method=method,
            chart_id="consistency_relation:foundations",
        )
        assert rel.justification_method == method

    def test_is_strict_false_for_self_relation(self):
        """Reflexive Con(T) → Con(T) — structurally valid but
        content-empty. is_strict reports False so downstream consumers
        can filter."""
        zfc = _zfc()
        rel = ConsistencyRelation(
            stronger=zfc, weaker=zfc,
            justification_ref="reflexive (axiomatic_inclusion: T ⊆ T)",
            justification_method="axiomatic_inclusion",
            chart_id="consistency_relation:foundations",
        )
        assert rel.is_strict is False

    def test_is_strict_true_for_distinct_theories(self):
        rel = ConsistencyRelation(
            stronger=_zfc_meas(), weaker=_zfc_neg_sch(),
            justification_ref="Magidor 1977",
            justification_method="forcing",
            chart_id="consistency_relation:foundations",
        )
        assert rel.is_strict is True


# ---------------------------------------------------------------------------
# Worked example: SCH failure relative to measurable cardinal (Magidor 1977)
# ---------------------------------------------------------------------------


class TestWorkedExample:
    """The design doc's worked example: SCH failure consistent relative
    to a measurable cardinal."""

    def test_magidor_1977_encoding(self):
        zfc_meas = _zfc_meas()
        zfc_neg_sch = _zfc_neg_sch()
        rel = ConsistencyRelation(
            stronger=zfc_meas,
            weaker=zfc_neg_sch,
            justification_ref="Magidor 1977 SCH failure",
            justification_method="forcing",
            chart_id="consistency_relation:foundations",
        )
        # All fields recoverable + relation is strict
        assert rel.stronger is zfc_meas
        assert rel.weaker is zfc_neg_sch
        assert rel.is_strict
        assert rel.justification_method == "forcing"


# ---------------------------------------------------------------------------
# Cross-tier: ConsistencyRelation works inside an
# OperatorPortabilityCertificate (per design doc cross-ref)
# ---------------------------------------------------------------------------


class TestSubstrateIntegration:
    """Per the design doc: consistency-strength relations are operator-
    portability instances. The 'operator' is 'extends-by-axiom-X' and
    the chart is the foundation system."""

    def test_chart_id_is_foundations_namespace(self):
        """Both primitives default to a foundations:* chart_id, so
        substrate's CoordinateChart registry can scope them
        consistently."""
        t = _zfc()
        rel = ConsistencyRelation(
            stronger=_zfc_meas(), weaker=t,
            justification_ref="ZFC ⊆ ZFC + meas",
            justification_method="axiomatic_inclusion",
            chart_id="consistency_relation:foundations",
        )
        assert "foundations" in t.chart_id
        assert "foundations" in rel.chart_id

    def test_enum_classes_round_trip_through_str_value(self):
        """Both enums are str-based; passing the string value is
        equivalent to passing the enum member. Substrate-grade
        permissive-at-write for downstream callers that only see
        strings (e.g. JSON-loaded configs)."""
        t1 = FormalTheory(theory_id="x", axioms_hash="y",
                          axiomatization_lang=AxiomatizationLang.LEAN4.value,
                          chart_id="formal_theory:foundations")
        assert t1.axiomatization_lang == "lean4"
        rel = ConsistencyRelation(
            stronger=t1, weaker=_zfc(),
            justification_ref="x",
            justification_method=JustificationMethod.INNER_MODEL.value,
            chart_id="consistency_relation:foundations",
        )
        assert rel.justification_method == "inner_model"
