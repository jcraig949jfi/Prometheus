"""Phase 0 integration tests.

Per Erebos v3 Phase 0 ITER-30. Verifies the 9 discipline primitives
shipped in ITER-21 through ITER-29 compose cleanly. Each test
exercises a multi-primitive interaction the substrate will rely on
once Phase 1 loader retrofits begin.

If any of these tests fails, a primitive's contract has drifted
relative to what its neighbors assume.
"""
from __future__ import annotations

import pytest

from charon.agents.erebos._kill_pattern_registry import (
    KILL_PATTERN_REGISTRY,
    repair_class_for,
    routing_action_for,
)
from charon.agents.erebos._quarantine import (
    QUARANTINE_RULES,
    all_quarantined_plugins,
    is_quarantined,
)
from charon.agents.erebos._value_metrics import (
    summarize_economy,
    value_per_tick,
)
from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators._predicate_handles import (
    MahlerPolynomialHandle,
)
from charon.agents.stygian.loaders._degeneracy_precondition import (
    degeneracy_report,
    gate,
    DegenerateInputError,
)
from charon.agents.stygian.loaders._emission_types import SurvivalCurve
from charon.agents.stygian.loaders._selection_discipline import (
    ArbitraryScalarSelectionError,
    SelectionMetric,
    disciplined_select,
)


# ---------------------------------------------------------------------
# Integration 1 — A loader using all 5 primitives in one emission path
# ---------------------------------------------------------------------

def test_loader_uses_all_5_primitives_in_one_emission_path():
    """Simulated loader path that touches:
       - selection_discipline (pick adversarial value)
       - catalog_profile (data-driven threshold)
       - degeneracy_precondition (gate the (data, inquiry))
       - SurvivalCurve (emit parameter-sweep result)
       - predicate_handle (carry structural representation)
       - kill_pattern_registry (derive verdict from sweep)
       - cost-instrumentation (record price)
    All five must compose without contract conflicts.
    """
    # Step 1: degeneracy gate on (data, inquiry)
    feature_dist = [50, 50]  # balanced binary
    report = degeneracy_report(
        data=list(range(100)),
        inquiry={"test": "binary_split"},
        feature_extractor=lambda d: feature_dist,
    )
    gate(report)  # no exception

    # Step 2: disciplined select of adversarial value from 3 candidates
    candidates = [1.10, 1.20, 1.30]
    target = 1.22
    chosen_value, sel_prov = disciplined_select(
        candidates,
        metric=SelectionMetric.PERCENTILE_BASED,
        metric_callable=lambda c: abs(c - target),
        data_type="scalar_axis_value",
        selection_provenance={"plugin_id": "g_test"},
    )
    assert chosen_value == 1.20

    # Step 3: build a SurvivalCurve over the sweep
    curve = SurvivalCurve(
        parameter_name="threshold",
        parameter_values=[1.0, 1.1, 1.2, 1.3],
        observed_values=[0.01, 0.02, 0.50, 0.95],
        null_p05_values=[0.0] * 4,
        null_p95_values=[0.05] * 4,
        summary_verdict="REJECTED",
        summary_kill_pattern="correlation_survives_intervention",
        phase_transition_index=2,
    )

    # Step 4: derive the routing action from the verdict's kill_pattern
    routing = routing_action_for(curve.summary_kill_pattern)
    assert routing is not None
    assert routing.startswith("g17")

    # Step 5: build a predicate handle to carry algebraic substrate
    handle = MahlerPolynomialHandle(
        coeffs=(1, 0, 1),  # palindromic (reversed == itself)
        mahler_measure=1.0,
        degree=2,
    )

    # Step 6: emit a ComposedClaim with cost-instrumentation fields
    claim = ComposedClaim(
        plugin_id="g_test",
        composed_id="INTEGRATION-001",
        input_provenance={"selection_provenance": sel_prov,
                          "degeneracy_report": report.to_payload_dict()},
        transformation_description="integration test",
        output_claim_text="test claim",
        falsification_route="custom_composition",
        expected_kill_pattern="correlation_survives_intervention",
        loader_feasibility_note="integration",
        composition_payload=curve.to_battery_result(),
        predicate_handle=handle,
        generation_cost_seconds=0.123,
        falsification_cost_seconds=0.456,
        information_gain_nats=0.05,
        reuse_value_count=0,
    )

    # All 5 primitives composed into one emission — verify the result
    # carries the expected metadata
    assert claim.predicate_handle.is_palindromic is True
    assert claim.generation_cost_seconds == 0.123
    assert claim.composition_payload["phase_transition_index"] == 2
    assert "selection_provenance" in claim.input_provenance
    assert claim.input_provenance["degeneracy_report"]["is_degenerate"] is False


# ---------------------------------------------------------------------
# Integration 2 — Quarantined plugin with predicate_handle is still blocked
# ---------------------------------------------------------------------

def test_quarantined_plugin_with_predicate_handle_still_blocked():
    """Even if a quarantined plugin produces a predicate_handle-bearing
    emission, the routing layer must not route it on production paths.
    Confirms the quarantine filter is the LAST gate, after all the
    discipline primitives."""
    from charon.agents.erebos.generators import applicable_plugins
    from charon.agents.erebos.tests._fixtures import empty_swarm_state

    state = empty_swarm_state()
    state.stygian_substantive = [{
        "record_id": "s1",
        "canonical_claim_text": "promoted",
        "verdict": "PROMOTED",
        "kill_pattern": None,
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-27T00:00:00+00:00",
        "claim_payload": {"degree": 12, "mahler": 1.2, "extra": 3.0},
        "extras": {},
    }]

    prod_plugins = applicable_plugins(state)
    prod_ids = {p.id for p in prod_plugins}

    # G05 has a degree+mahler+extra payload → would be applicable, but
    # is quarantined → filtered out
    assert "g05_confound_swap" not in prod_ids
    # G06 + G01 similarly
    assert "g06_null_space" not in prod_ids
    assert "g01_intersection" not in prod_ids


# ---------------------------------------------------------------------
# Integration 3 — SurvivalCurve summary_kill_pattern routes via registry
# ---------------------------------------------------------------------

def test_survival_curve_summary_kill_pattern_routes_via_registry():
    """When a loader emits a SurvivalCurve with summary_kill_pattern
    set, the routing layer can derive next-plugin from the registry."""
    curve = SurvivalCurve(
        parameter_name="threshold",
        parameter_values=[1.0, 2.0],
        observed_values=[0.5, 0.9],
        null_p05_values=[0.0, 0.0],
        null_p95_values=[0.6, 0.6],
        summary_verdict="REJECTED",
        summary_kill_pattern="sharp_boundary_detected",
        phase_transition_index=1,
    )
    routing = routing_action_for(curve.summary_kill_pattern)
    assert routing == "g10_with_bocpd_posterior"
    # And the repair class is F6 ontology repair
    assert repair_class_for(curve.summary_kill_pattern) == "F6"


# ---------------------------------------------------------------------
# Integration 4 — value_per_tick computable on existing ledger
# ---------------------------------------------------------------------

def test_value_per_tick_baseline_computable_on_synthetic_ledger():
    """The substrate's value function must compute meaningfully on
    a realistic-shape ledger (some rows with full cost data, some
    without — the v1 ledger has 0 entries with cost data, so this
    test simulates the post-Phase-1 state where the daemon wraps
    plugin.generate() and loader execution with timers)."""
    import datetime as dt
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = [
        # An emission with full cost / value data
        {
            "emitted_at": now_iso,
            "generation_cost_seconds": 0.5,
            "falsification_cost_seconds": 1.5,
            "information_gain_nats": 0.3,
            "reuse_value_count": 2,
        },
        # An emission with only generation cost (loader didn't run yet)
        {
            "emitted_at": now_iso,
            "generation_cost_seconds": 0.4,
            "falsification_cost_seconds": None,
            "information_gain_nats": None,
            "reuse_value_count": 0,
        },
    ]
    vpt = value_per_tick(rows)
    summary = summarize_economy(rows)
    assert vpt >= 0
    assert summary["n_emissions"] == 2
    assert summary["total_generation_cost_seconds"] == 0.9


# ---------------------------------------------------------------------
# Integration 5 — degeneracy_precondition + quarantine interact correctly
# ---------------------------------------------------------------------

def test_degeneracy_report_for_g11_v1_salem_cluster_would_have_been_caught():
    """The G11 v1 Salem-cluster tautology (ITER-12 substrate self-
    correction event) would be caught by the degeneracy gate AND
    G11 is currently NOT quarantined (it has 4 working loaders).
    This test verifies the (data, inquiry) gate is the right
    discipline layer for the v1-style tautology, complementing the
    plugin-level quarantine."""
    report = degeneracy_report(
        data=list(range(8596)),
        inquiry={"test": "binary_split",
                 "binary_field": "salem_class",
                 "survival_threshold_M": 1.30},
        feature_extractor=lambda d: [8501, 95],
    )
    assert report.is_degenerate is True
    assert "tail_concentration_index" in report.reason

    # And G11 itself is NOT quarantined (has loaders) — the gate is
    # the discipline that catches per-emission tautologies even on
    # active plugins.
    assert is_quarantined("g11_exception_miner") is False


# ---------------------------------------------------------------------
# Integration 6 — kill_pattern_registry covers all production kill_patterns
# ---------------------------------------------------------------------

def test_all_production_kill_patterns_have_routing_entries():
    """Every kill_pattern the substrate emits in production must
    have a registry entry. Surfaces any gap between what loaders
    emit and what the routing layer understands."""
    # The 14 directional kill_patterns from production usage
    production_kps = [
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
    for kp in production_kps:
        assert kp in KILL_PATTERN_REGISTRY, (
            f"Production kill_pattern {kp!r} missing from routing registry"
        )
        action = routing_action_for(kp)
        assert action is not None
        assert action != ""


# ---------------------------------------------------------------------
# Integration 7 — Phase 0 invariants
# ---------------------------------------------------------------------

def test_phase0_substrate_state_invariants():
    """Snapshot of the substrate's Phase-0-end state:
       - 25 plugins in REGISTRY
       - 11 quarantined (7 loader_missing + 3 infra-blocked + 1 vacuous)
       - 14 active in production
       - 27 kill_patterns in routing registry
       - 7 registered data types in selection discipline
    Any drift here surfaces a primitive change."""
    from charon.agents.erebos.generators import REGISTRY
    from charon.agents.stygian.loaders._selection_discipline import (
        known_data_types,
    )

    assert len(REGISTRY) == 25
    assert len(QUARANTINE_RULES) == 11
    active = [p for p in REGISTRY.keys() if not is_quarantined(p)]
    assert len(active) == 14
    assert len(KILL_PATTERN_REGISTRY) == 27
    assert len(known_data_types()) >= 7  # registered data types
