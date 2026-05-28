"""Synthetic-control tests for kill_pattern_registry.

Per Erebos v3 Phase 0 ITER-26. Validates the 27-row routing table
from v3 amendment §4 + the public API for substrate routing.
"""
from __future__ import annotations

import pytest

from charon.agents.erebos._kill_pattern_registry import (
    KILL_PATTERN_REGISTRY,
    KillPatternSpec,
    VALID_PROVENANCE,
    VALID_REPAIR_CLASSES,
    all_registered_kill_patterns,
    assignment_provenance_for,
    confusion_class_for,
    kill_patterns_by_repair_class,
    observable_signature_for,
    repair_class_for,
    routing_action_for,
)


# ---------------------------------------------------------------------
# Registry shape
# ---------------------------------------------------------------------

def test_registry_has_27_entries():
    """Per v3 amendment §4 routing table — exactly 27 rows."""
    assert len(KILL_PATTERN_REGISTRY) == 27


def test_registry_keys_match_dataclass_name_field():
    """Each spec's name field must equal its registry key."""
    for key, spec in KILL_PATTERN_REGISTRY.items():
        assert spec.name == key, (
            f"Mismatch: key={key!r}, spec.name={spec.name!r}"
        )


def test_all_entries_have_valid_repair_class():
    for kp, spec in KILL_PATTERN_REGISTRY.items():
        assert spec.repair_class in VALID_REPAIR_CLASSES, (
            f"{kp}: invalid repair_class {spec.repair_class}"
        )


def test_all_entries_have_valid_provenance():
    for kp, spec in KILL_PATTERN_REGISTRY.items():
        assert spec.assignment_provenance in VALID_PROVENANCE, (
            f"{kp}: invalid provenance {spec.assignment_provenance}"
        )


def test_all_entries_have_non_empty_observable_signature():
    for kp, spec in KILL_PATTERN_REGISTRY.items():
        assert spec.observable_signature, (
            f"{kp}: empty observable_signature"
        )


def test_all_entries_have_non_empty_routing_action():
    for kp, spec in KILL_PATTERN_REGISTRY.items():
        assert spec.routing_action, (
            f"{kp}: empty routing_action"
        )


# ---------------------------------------------------------------------
# Construction validation
# ---------------------------------------------------------------------

def test_spec_construction_invalid_repair_class_raises():
    with pytest.raises(ValueError, match="invalid repair_class"):
        KillPatternSpec(
            name="test_kp",
            repair_class="F99",  # not in VALID_REPAIR_CLASSES
            routing_action="test_action",
            confusion_class=(),
            observable_signature="test signature",
            assignment_provenance="loader",
        )


def test_spec_construction_invalid_provenance_raises():
    with pytest.raises(ValueError, match="invalid assignment_provenance"):
        KillPatternSpec(
            name="test_kp",
            repair_class="F3",
            routing_action="test_action",
            confusion_class=(),
            observable_signature="test signature",
            assignment_provenance="wizard_intuition",  # not in VALID
        )


def test_spec_construction_empty_signature_raises():
    with pytest.raises(ValueError, match="observable_signature cannot be empty"):
        KillPatternSpec(
            name="test_kp",
            repair_class="F3",
            routing_action="test_action",
            confusion_class=(),
            observable_signature="",
            assignment_provenance="loader",
        )


# ---------------------------------------------------------------------
# Live production kill_patterns coverage
# ---------------------------------------------------------------------

# The 14 directional kill_patterns the v0.26 substrate emits in
# production. Each must be registered post-v3.
LIVE_DIRECTIONAL_KILL_PATTERNS = [
    "permutation_null",
    "metaphor_collapse",
    "overfitting_goodharting",
    "smooth_degradation",
    "error_term_does_not_decay",
    "correlation_survives_intervention",
    "conjecture_survives_adversarial_attack",
    "region_R_exhausted_without_counterexample",
    "sub_claim_falsified",
    "instrument_clash_detected",
    "functor_breaks",
    "out_of_sample_failure",
    "sharp_boundary_detected",
    "decay_faster_than_1_over_N",
]


def test_all_live_directional_kill_patterns_registered():
    """v1 substrate's 14 directional labels all have v3 routing entries."""
    for kp in LIVE_DIRECTIONAL_KILL_PATTERNS:
        assert kp in KILL_PATTERN_REGISTRY, (
            f"Live kill_pattern {kp!r} missing from v3 registry"
        )


def test_live_kill_patterns_have_concrete_routing_actions():
    """Live kill_patterns must route to a non-stub plugin."""
    for kp in LIVE_DIRECTIONAL_KILL_PATTERNS:
        action = routing_action_for(kp)
        assert action is not None
        assert action != ""


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def test_routing_action_for_known_kp():
    action = routing_action_for("permutation_null")
    assert action == "g02_with_westfall_young"


def test_routing_action_for_unknown_kp_returns_none():
    assert routing_action_for("nonexistent_kill_pattern_xyz") is None


def test_confusion_class_for_boundary_collapse():
    cc = confusion_class_for("boundary_collapse")
    assert "weakening_too_strict" in cc


def test_confusion_class_for_unknown_returns_empty():
    assert confusion_class_for("nonexistent_kp") == ()


def test_repair_class_for_known_kp():
    assert repair_class_for("sub_claim_falsified") == "F3"
    assert repair_class_for("complete_signal_collapse") == "F6"
    assert repair_class_for("tautological_pass") == "F8"


def test_repair_class_for_unknown_raises():
    with pytest.raises(KeyError, match="not in registry"):
        repair_class_for("nonexistent_kp")


def test_assignment_provenance_for_known_kp():
    assert assignment_provenance_for("permutation_null") == "loader"
    assert assignment_provenance_for("tautological_pass") == "substrate_derived"


def test_observable_signature_for_known_kp():
    sig = observable_signature_for("permutation_null")
    assert "observed_divergence" in sig
    assert "null_p95" in sig


def test_all_registered_kill_patterns_sorted():
    kps = all_registered_kill_patterns()
    assert kps == sorted(kps)
    assert len(kps) == 27


def test_kill_patterns_by_repair_class_F3():
    """F3 (local repair) should contain at least permutation_null,
    residual_survival, smooth_degradation, uncorrelated_residual_failures,
    sub_claim_falsified per v3 amendment §4 routing table."""
    f3 = kill_patterns_by_repair_class("F3")
    assert "permutation_null" in f3
    assert "residual_survival" in f3
    assert "smooth_degradation" in f3
    assert "sub_claim_falsified" in f3


def test_kill_patterns_by_repair_class_F8_epistemic():
    """F8 (epistemic repair) contains the substrate self-audit
    kill_patterns: instrument_clash, symmetry_breaking, tautological_pass."""
    f8 = kill_patterns_by_repair_class("F8")
    assert "instrument_clash_detected" in f8
    assert "symmetry_breaking" in f8
    assert "tautological_pass" in f8


def test_kill_patterns_by_repair_class_unknown_returns_empty():
    assert kill_patterns_by_repair_class("F99") == []


# ---------------------------------------------------------------------
# Substrate-level integrity
# ---------------------------------------------------------------------

def test_confusion_classes_reference_only_registered_patterns():
    """Every entry in a confusion_class must itself be a registered
    kill_pattern. Catches typos."""
    for kp, spec in KILL_PATTERN_REGISTRY.items():
        for confused_with in spec.confusion_class:
            assert confused_with in KILL_PATTERN_REGISTRY, (
                f"{kp}: confusion_class references unregistered "
                f"{confused_with!r}"
            )


def test_confusion_symmetric_or_documented():
    """If A's confusion_class contains B, B's confusion_class should
    typically contain A. Asymmetries are allowed but should be rare.
    This test surfaces asymmetries for review."""
    asymmetries = []
    for kp_a, spec_a in KILL_PATTERN_REGISTRY.items():
        for kp_b in spec_a.confusion_class:
            spec_b = KILL_PATTERN_REGISTRY.get(kp_b)
            if spec_b is None:
                continue
            if kp_a not in spec_b.confusion_class:
                asymmetries.append((kp_a, kp_b))
    # 8 asymmetries are documented + expected: permutation_null and
    # boundary_collapse are central "looks like X" attractors for
    # several siblings (strict_threshold_violation, complete_signal
    # _collapse, out_of_sample_failure, etc.) but the converse isn't
    # symmetric — those niche failure modes look like permutation_null
    # before triage, but permutation_null itself isn't confused with
    # all of them at observation time. If the count grows past 10,
    # surface for review.
    assert len(asymmetries) <= 10, (
        f"Too many asymmetric confusion entries: {asymmetries}"
    )
