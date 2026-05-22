"""Tests for the GeneratorRole taxonomy + discovery-stats exclusion.

Per advisory board Fire #53: c4 (generalization) is tautology by
construction, f1 (Monte Carlo) is null-baseline by design. Both
should NOT count toward substrate discoveries, but should stay
active (c4 as alive-monitor, f1 as calibration anchor).
"""
from __future__ import annotations

from theseus.emit.record_schema import (
    TheseusRecord, ClaimKind, Verdict,
)
from theseus.generators.base import GeneratorRole, NON_DISCOVERY_ROLES
from theseus.generators.c4_generalization import C4GeneralizationGenerator
from theseus.generators.f1_monte_carlo_random_pairs import (
    F1MonteCarloRandomPairsGenerator,
)
from theseus.generators.a1_catalog_cross_product import (
    A1CatalogCrossProductGenerator,
)


def test_c4_role_is_tautology_control():
    assert C4GeneralizationGenerator.role == GeneratorRole.TAUTOLOGY_CONTROL


def test_f1_role_is_null_baseline():
    assert F1MonteCarloRandomPairsGenerator.role == GeneratorRole.NULL_BASELINE


def test_a1_role_default_is_discovery():
    """Generators that don't override role default to DISCOVERY."""
    assert A1CatalogCrossProductGenerator.role == GeneratorRole.DISCOVERY


def test_non_discovery_roles_contains_expected():
    assert GeneratorRole.NULL_BASELINE in NON_DISCOVERY_ROLES
    assert GeneratorRole.TAUTOLOGY_CONTROL in NON_DISCOVERY_ROLES
    assert GeneratorRole.INFRA_DIAGNOSTIC in NON_DISCOVERY_ROLES
    assert GeneratorRole.DISCOVERY not in NON_DISCOVERY_ROLES
    assert GeneratorRole.FALSIFICATION not in NON_DISCOVERY_ROLES


def test_registry_lookups_role_correctly():
    """The registry-based role check used by maybe_emit_discoveries."""
    from theseus.registry import REGISTRY
    assert REGISTRY["c4"].role == GeneratorRole.TAUTOLOGY_CONTROL
    assert REGISTRY["f1"].role == GeneratorRole.NULL_BASELINE
    assert REGISTRY["a1"].role == GeneratorRole.DISCOVERY


def test_maybe_emit_discoveries_skips_non_discovery_role():
    """A c4-emitted record (TAUTOLOGY_CONTROL) is excluded from
    discovery emission even with high training_weight."""
    from theseus.orchestration import telemetry

    # If telemetry isn't available, function returns 0; that's fine
    if not telemetry.HAS_TELEMETRY:
        return

    rid = TheseusRecord.compute_record_id("test claim", "c4")
    c4_rec = TheseusRecord(
        record_id=rid, generator_id="c4", batch_id="t",
        emitted_at="2026-05-22T00:00:00Z",
        claim_kind=ClaimKind.MUTATION.value,
        claim_payload={"relation": "equal", "holds": True},
        canonical_claim_text="test claim",
        verdict=Verdict.SHADOW_CATALOG.value,
    )

    # Patch session_telemetry.emit_discovery to count calls without
    # actually firing
    import theseus.orchestration.telemetry as tel
    original_st = tel.session_telemetry
    calls: list = []

    class _Fake:
        @staticmethod
        def emit_discovery(**kwargs):
            calls.append(kwargs)
            return True

    tel.session_telemetry = _Fake
    try:
        n = telemetry.maybe_emit_discoveries(
            [c4_rec], weight_threshold=0.0, max_per_batch=20,
        )
    finally:
        tel.session_telemetry = original_st

    # c4 record was excluded → no emit calls, n_emitted == 0
    assert n == 0
    assert len(calls) == 0


def test_maybe_emit_discoveries_includes_discovery_role():
    """An a1-emitted record (DISCOVERY) IS eligible for emission."""
    from theseus.orchestration import telemetry

    if not telemetry.HAS_TELEMETRY:
        return

    rid = TheseusRecord.compute_record_id("test claim", "a1")
    a1_rec = TheseusRecord(
        record_id=rid, generator_id="a1", batch_id="t",
        emitted_at="2026-05-22T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y",
            "relation": "equal", "holds": False,
        },
        canonical_claim_text="test claim",
        verdict=Verdict.REJECTED.value,
        kill_pattern="a1_relation_equal_violated_specific",
    )

    import theseus.orchestration.telemetry as tel
    original_st = tel.session_telemetry
    calls: list = []

    class _Fake:
        @staticmethod
        def emit_discovery(**kwargs):
            calls.append(kwargs)
            return True

    tel.session_telemetry = _Fake
    try:
        n = telemetry.maybe_emit_discoveries(
            [a1_rec], weight_threshold=0.0, max_per_batch=20,
        )
    finally:
        tel.session_telemetry = original_st

    # a1 record was eligible; emit_discovery called once
    assert n == 1
    assert len(calls) == 1
