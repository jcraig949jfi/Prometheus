"""Tests for prometheus_math.cross_machine_audit (T-2026-05-07-T013)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from prometheus_math.cross_machine_audit import (
    SUBSTRATE_VERSION_FOR_AUDIT,
    CanonicalHashInput,
    CrossMachineAuditReport,
    canonical_hash,
    canonical_hash_corpus,
    compare_against_remote_report,
    render_audit_report,
)
from prometheus_math.kill_vector import (
    ALL_COMPONENT_NAMES,
    KillComponent,
    KillVector,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kv(
    *,
    candidate_hash: str = "h_default",
    triggered_components: List[str] = None,
    operator_class: str = "TestOperator@v1",
    region_meta: dict = None,
    timestamp: float = 0.0,
) -> KillVector:
    triggered_components = triggered_components or ["F1_permutation_null"]
    comps = tuple(
        KillComponent(falsifier_name=name, triggered=True, margin=0.5, margin_unit="absolute")
        for name in triggered_components
    )
    return KillVector(
        components=comps,
        candidate_hash=candidate_hash,
        operator_class=operator_class,
        region_meta=region_meta or {"degree": 14},
        timestamp=timestamp,
    )


def _input(kv: KillVector, **kwargs) -> CanonicalHashInput:
    return CanonicalHashInput(kill_record=kv, **kwargs)


# ---------------------------------------------------------------------------
# Property: hash determinism (same input -> same hash)
# ---------------------------------------------------------------------------


class TestCanonicalHashDeterminism:
    def test_same_input_yields_same_hash(self):
        kv = _make_kv()
        h1 = canonical_hash(_input(kv))
        h2 = canonical_hash(_input(kv))
        assert h1 == h2

    def test_two_independently_constructed_kvs_yield_same_hash(self):
        kv_a = _make_kv()
        kv_b = _make_kv()
        h_a = canonical_hash(_input(kv_a))
        h_b = canonical_hash(_input(kv_b))
        assert h_a == h_b


# ---------------------------------------------------------------------------
# Property: hash STABLE under no-op transformations (acceptance #3)
# ---------------------------------------------------------------------------


class TestHashStableUnderNoOpTransformations:
    """Acceptance criterion #3: stable under relabeling, permutation of
    independent fields."""

    def test_timestamp_change_does_not_affect_hash(self):
        """timestamp is wall-clock; the audit hash explicitly drops it."""
        kv1 = _make_kv(timestamp=1000.0)
        kv2 = _make_kv(timestamp=9999.0)
        assert canonical_hash(_input(kv1)) == canonical_hash(_input(kv2))

    def test_region_meta_key_reordering_does_not_affect_hash(self):
        """Mapping key order should not enter identity. JSON sort_keys=True
        canonicalizes this."""
        kv1 = _make_kv(region_meta={"a": 1, "b": 2, "c": 3})
        kv2 = _make_kv(region_meta={"c": 3, "a": 1, "b": 2})
        assert canonical_hash(_input(kv1)) == canonical_hash(_input(kv2))

    def test_components_permutation_does_not_affect_hash(self):
        """Per acceptance #3: permutation of independent fields is a
        no-op. The audit hash sorts components by falsifier_name before
        hashing so order does not enter identity."""
        comps_forward = (
            KillComponent(falsifier_name="F1_permutation_null", triggered=True, margin=0.1, margin_unit="absolute"),
            KillComponent(falsifier_name="F6_base_rate", triggered=True, margin=0.2, margin_unit="absolute"),
        )
        comps_reverse = (
            KillComponent(falsifier_name="F6_base_rate", triggered=True, margin=0.2, margin_unit="absolute"),
            KillComponent(falsifier_name="F1_permutation_null", triggered=True, margin=0.1, margin_unit="absolute"),
        )
        kv_forward = KillVector(
            components=comps_forward, candidate_hash="h_perm", operator_class="op",
        )
        kv_reverse = KillVector(
            components=comps_reverse, candidate_hash="h_perm", operator_class="op",
        )
        assert canonical_hash(_input(kv_forward)) == canonical_hash(_input(kv_reverse))


# ---------------------------------------------------------------------------
# Property: hash UNSTABLE under semantic transformations (acceptance #4)
# ---------------------------------------------------------------------------


class TestHashUnstableUnderSemanticTransformations:
    """Acceptance criterion #4: hash unstable under semantic transformations
    (validates sensitivity)."""

    def test_triggered_flip_changes_hash(self):
        kv1 = _make_kv()
        # Construct a vector where the same component is NOT triggered.
        comp_off = KillComponent(falsifier_name="F1_permutation_null", triggered=False)
        kv2 = KillVector(
            components=(comp_off,),
            candidate_hash=kv1.candidate_hash,
            operator_class=kv1.operator_class,
            region_meta=dict(kv1.region_meta),
            timestamp=0.0,
        )
        assert canonical_hash(_input(kv1)) != canonical_hash(_input(kv2))

    def test_margin_change_changes_hash(self):
        comp_a = KillComponent(falsifier_name="F1_permutation_null", triggered=True, margin=0.5, margin_unit="absolute")
        comp_b = KillComponent(falsifier_name="F1_permutation_null", triggered=True, margin=0.7, margin_unit="absolute")
        kv_a = KillVector(components=(comp_a,), candidate_hash="h_m", operator_class="op")
        kv_b = KillVector(components=(comp_b,), candidate_hash="h_m", operator_class="op")
        assert canonical_hash(_input(kv_a)) != canonical_hash(_input(kv_b))

    def test_candidate_hash_change_changes_hash(self):
        kv_a = _make_kv(candidate_hash="hash_a")
        kv_b = _make_kv(candidate_hash="hash_b")
        assert canonical_hash(_input(kv_a)) != canonical_hash(_input(kv_b))

    def test_substrate_version_change_changes_hash(self):
        kv = _make_kv()
        h_a = canonical_hash(_input(kv, substrate_version="v2.3.0"))
        h_b = canonical_hash(_input(kv, substrate_version="v2.4.0"))
        assert h_a != h_b

    def test_transformation_chain_change_changes_hash(self):
        kv = _make_kv()
        h_empty = canonical_hash(_input(kv, transformation_chain=()))
        h_one = canonical_hash(_input(kv, transformation_chain=("relabel",)))
        h_two = canonical_hash(_input(kv, transformation_chain=("relabel", "permute")))
        assert h_empty != h_one
        assert h_one != h_two
        assert h_empty != h_two

    def test_transformation_chain_order_matters(self):
        """[A, B] must hash differently from [B, A] — chain is a sequence,
        not a set."""
        kv = _make_kv()
        h_ab = canonical_hash(_input(kv, transformation_chain=("A", "B")))
        h_ba = canonical_hash(_input(kv, transformation_chain=("B", "A")))
        assert h_ab != h_ba

    def test_operator_class_change_changes_hash(self):
        kv_a = _make_kv(operator_class="OperatorA@v1")
        kv_b = _make_kv(operator_class="OperatorB@v1")
        assert canonical_hash(_input(kv_a)) != canonical_hash(_input(kv_b))

    def test_region_meta_value_change_changes_hash(self):
        kv_a = _make_kv(region_meta={"degree": 14})
        kv_b = _make_kv(region_meta={"degree": 12})
        assert canonical_hash(_input(kv_a)) != canonical_hash(_input(kv_b))


# ---------------------------------------------------------------------------
# Construction validation
# ---------------------------------------------------------------------------


class TestCanonicalHashInputValidation:
    def test_non_killvector_raises(self):
        with pytest.raises(TypeError, match="kill_record"):
            CanonicalHashInput(kill_record="not a kv")  # type: ignore

    def test_empty_substrate_version_raises(self):
        kv = _make_kv()
        with pytest.raises(ValueError, match="substrate_version"):
            CanonicalHashInput(kill_record=kv, substrate_version="")

    def test_non_tuple_transformation_chain_raises(self):
        kv = _make_kv()
        with pytest.raises(TypeError, match="transformation_chain"):
            CanonicalHashInput(kill_record=kv, transformation_chain=["a", "b"])  # type: ignore

    def test_non_string_chain_entry_raises(self):
        kv = _make_kv()
        with pytest.raises(TypeError, match="transformation_chain entries"):
            CanonicalHashInput(kill_record=kv, transformation_chain=("ok", 42))  # type: ignore


# ---------------------------------------------------------------------------
# Cross-machine comparison
# ---------------------------------------------------------------------------


class TestCompareAgainstRemoteReport:
    def test_all_matching_yields_zero_diverging(self):
        kv1 = _make_kv(candidate_hash="h1")
        kv2 = _make_kv(candidate_hash="h2")
        inputs = [_input(kv1), _input(kv2)]
        local = canonical_hash_corpus(inputs)
        # Remote = perfect copy of local
        report = compare_against_remote_report(inputs, dict(local))
        assert report.n_compared == 2
        assert report.n_matching == 2
        assert report.n_diverging == 0
        assert report.n_only_local == 0
        assert report.n_only_remote == 0
        assert report.diverging == ()

    def test_diverging_pair_surfaces(self):
        kv = _make_kv(candidate_hash="hX")
        inputs = [_input(kv)]
        # Remote reports a different hash for the same candidate
        bogus_remote = {"hX": "deadbeef" * 8}
        report = compare_against_remote_report(inputs, bogus_remote)
        assert report.n_compared == 1
        assert report.n_diverging == 1
        assert len(report.diverging) == 1
        d = report.diverging[0]
        assert d.candidate_hash == "hX"
        assert d.local_canonical_hash != "deadbeef" * 8
        assert d.remote_canonical_hash == "deadbeef" * 8
        assert d.matches is False

    def test_only_local_records_reported(self):
        kv = _make_kv(candidate_hash="local_only")
        inputs = [_input(kv)]
        report = compare_against_remote_report(inputs, {})
        assert report.n_only_local == 1
        assert "local_only" in report.only_local

    def test_only_remote_records_reported(self):
        report = compare_against_remote_report([], {"remote_only": "deadbeef"})
        assert report.n_only_remote == 1
        assert "remote_only" in report.only_remote


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


class TestRenderAuditReport:
    def test_all_matching_renders_no_divergence_message(self):
        kv = _make_kv(candidate_hash="h_ok")
        inputs = [_input(kv)]
        local = canonical_hash_corpus(inputs)
        report = compare_against_remote_report(inputs, dict(local))
        md = render_audit_report(report)
        assert "Cross-Machine Determinism Audit" in md
        assert "No substrate-level cross-machine divergence detected" in md
        assert "Substrate finding" not in md  # no divergence section

    def test_diverging_renders_substrate_finding_section(self):
        kv = _make_kv(candidate_hash="h_div")
        inputs = [_input(kv)]
        report = compare_against_remote_report(inputs, {"h_div": "wrong" * 12})
        md = render_audit_report(report)
        assert "Substrate finding: divergent records" in md
        assert "h_div" in md
        assert "1 record(s) produce different canonical hashes" in md

    def test_only_local_only_remote_renders_orchestration_section(self):
        kv = _make_kv(candidate_hash="local_only_h")
        inputs = [_input(kv)]
        report = compare_against_remote_report(inputs, {"remote_only_h": "x" * 64})
        md = render_audit_report(report)
        assert "Coverage gaps" in md
        assert "record(s) only on local" in md
        assert "local_only_h" in md
        assert "record(s) only on remote" in md
        assert "remote_only_h" in md

    def test_empty_intersection_renders_orchestration_gap_message(self):
        report = compare_against_remote_report([], {})
        md = render_audit_report(report)
        assert "No records to compare" in md or "intersection" in md


# ---------------------------------------------------------------------------
# Coverage: spans all 20 KillVector v2 component types
# ---------------------------------------------------------------------------


class TestCoverageAcrossAllComponentTypes:
    def test_canonical_hash_works_across_all_20_component_types(self):
        """Sanity: hash computation runs cleanly across ALL_COMPONENT_NAMES;
        each yields a distinct hash (different candidate_hash per component)."""
        hashes = set()
        for name in ALL_COMPONENT_NAMES:
            kv = _make_kv(
                candidate_hash=f"h_cov_{name}",
                triggered_components=[name],
            )
            h = canonical_hash(_input(kv))
            assert isinstance(h, str)
            assert len(h) == 64  # SHA256 hex digest
            hashes.add(h)
        # All 20 produce distinct hashes (different candidate_hash + name).
        assert len(hashes) == 20
