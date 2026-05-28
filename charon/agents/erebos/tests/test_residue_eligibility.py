"""Tests for the residue-eligibility seam primitive.

Per Erebos v3 Phase 1B ITER-35. Validates the four-criterion
eligibility contract on synthetic scenarios + cross-criterion
combinations + integration with kill_pattern_registry routing
and Phase 1A verdict shapes (BOCPD / bootstrap-CI / MC G-test).
"""
from __future__ import annotations

import pytest

from charon.agents.erebos._residue_eligibility import (
    ALL_CRITERIA,
    CRITERION_ADDS_TENSOR_RANK,
    CRITERION_BOUNDARY_LOCALIZED,
    CRITERION_FALSIFIES_PRIOR,
    CRITERION_ROUTING_CHANGE,
    EligibilityVerdict,
    LedgerContext,
    assess_residue_eligibility,
)


# ---------------------------------------------------------------------
# Empty ledger / cold-start
# ---------------------------------------------------------------------

def test_empty_ledger_first_kp_is_eligible():
    """First emission against an empty ledger must always be eligible
    (it changes routing distribution by definition + adds rank)."""
    verdict = assess_residue_eligibility(
        plugin_id="g11_exception_miner",
        new_kill_pattern="catalog_flag_inconsistent",
        verdict={"verdict": "REJECTED"},
        domain="mahler_non_cyclotomic",
        ledger_context=LedgerContext.empty(),
    )
    assert verdict.eligible is True
    # Empty ledger: routing change + rank both fire
    assert CRITERION_ROUTING_CHANGE in verdict.criteria_met
    assert CRITERION_ADDS_TENSOR_RANK in verdict.criteria_met


def test_empty_ledger_promoted_verdict_is_eligible_by_rank():
    """PROMOTED on a never-seen (plugin, domain) is still rank-adding."""
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern=None,  # PROMOTED
        verdict={"verdict": "PROMOTED"},
        domain="mahler_non_cyclotomic",
        ledger_context=LedgerContext.empty(),
    )
    assert v.eligible is True
    assert CRITERION_ADDS_TENSOR_RANK in v.criteria_met
    # PROMOTED has no routing implication
    assert CRITERION_ROUTING_CHANGE not in v.criteria_met


# ---------------------------------------------------------------------
# CRITERION_ROUTING_CHANGE
# ---------------------------------------------------------------------

def test_routing_change_fires_on_novel_kp():
    """A kp not present in the ledger fires the routing-change criterion."""
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"existing_kp"}),
        routing_distribution={"existing_kp": 1.0},
        prior_kps_by_input_signature={},
        known_plugin_domain_kp_triples=frozenset(
            {("g02_contrast", "mahler_non_cyclotomic", "existing_kp")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="brand_new_kp_never_seen",
        verdict={"verdict": "REJECTED"},
        domain="mahler_non_cyclotomic",
        ledger_context=ctx,
    )
    assert CRITERION_ROUTING_CHANGE in v.criteria_met
    assert v.routing_change_detail["is_novel_kp"] is True


def test_routing_change_does_not_fire_on_same_action_kp():
    """A kp whose routing_action matches the current dominant action
    does NOT fire routing-change (assuming the kp is also non-novel)."""
    # Use two real kps from kill_pattern_registry that map to the same
    # routing action so we can simulate "different kp, same action."
    # The simpler way: register the same kp as both prior and new
    # (impossible to satisfy "novel kp" then). Test with non-novel kp:
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"sharp_boundary_detected"}),
        routing_distribution={"sharp_boundary_detected": 1.0},
        prior_kps_by_input_signature={},
        known_plugin_domain_kp_triples=frozenset(
            {("g10_boundary", "mahler", "sharp_boundary_detected")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g10_boundary",
        new_kill_pattern="sharp_boundary_detected",
        verdict={"verdict": "REJECTED"},
        domain="mahler",
        ledger_context=ctx,
    )
    # Non-novel kp, matching dominant action — routing does NOT fire
    assert CRITERION_ROUTING_CHANGE not in v.criteria_met


def test_routing_change_does_not_fire_on_promoted_verdict():
    """PROMOTED has no routing implication."""
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"some_kp"}),
        routing_distribution={"some_kp": 1.0},
    )
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern=None,
        verdict={"verdict": "PROMOTED"},
        domain="mahler",
        ledger_context=ctx,
    )
    assert CRITERION_ROUTING_CHANGE not in v.criteria_met
    assert v.routing_change_detail["fires"] is False


# ---------------------------------------------------------------------
# CRITERION_BOUNDARY_LOCALIZED
# ---------------------------------------------------------------------

def test_boundary_localized_fires_on_bocpd_interior_spike():
    """G10 v2 BOCPD output's interior_spike_threshold localizes
    a boundary."""
    bocpd_verdict = {
        "verdict": "REJECTED",
        "interior_spike_threshold": 1.30,
        "interior_spike_value": 0.499,
    }
    v = assess_residue_eligibility(
        plugin_id="g10_boundary",
        new_kill_pattern="sharp_boundary_detected_bocpd",
        verdict=bocpd_verdict,
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    assert CRITERION_BOUNDARY_LOCALIZED in v.criteria_met
    assert "interior_spike_threshold" in v.boundary_detail["fields_present"]


def test_boundary_localized_fires_on_bootstrap_ci():
    """G23 v2 bootstrap CI bounds localize."""
    ci_verdict = {
        "verdict": "REJECTED",
        "slope_ci_lower": -0.294,
        "slope_ci_upper": -0.081,
    }
    v = assess_residue_eligibility(
        plugin_id="g23_asymptotic_limit",
        new_kill_pattern="error_term_does_not_decay_bootstrap",
        verdict=ci_verdict,
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    assert CRITERION_BOUNDARY_LOCALIZED in v.criteria_met


def test_boundary_localized_fires_on_mc_p_value():
    """G11 v5 MC G-test p-value localizes."""
    v = assess_residue_eligibility(
        plugin_id="g11_exception_miner",
        new_kill_pattern=None,
        verdict={"verdict": "PROMOTED", "p_value_mc": 0.0},
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    assert CRITERION_BOUNDARY_LOCALIZED in v.criteria_met


def test_boundary_not_localized_on_bare_verdict():
    """A verdict dict with no boundary fields does NOT fire."""
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="some_kp",
        verdict={"verdict": "REJECTED", "reason": "categorical fail"},
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    assert CRITERION_BOUNDARY_LOCALIZED not in v.criteria_met
    assert v.boundary_detail["fields_present"] == []


def test_boundary_not_localized_when_field_is_none():
    """A boundary field present-but-None should not fire."""
    v = assess_residue_eligibility(
        plugin_id="g10_boundary",
        new_kill_pattern=None,
        verdict={
            "verdict": "PROMOTED",
            "interior_spike_threshold": None,  # absent signal
        },
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    assert CRITERION_BOUNDARY_LOCALIZED not in v.criteria_met


def test_boundary_not_localized_when_verdict_not_dict():
    """Non-dict verdict (e.g., legacy plain-text) doesn't crash."""
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="kp",
        verdict="REJECTED: text only",  # type: ignore[arg-type]
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    assert CRITERION_BOUNDARY_LOCALIZED not in v.criteria_met
    assert v.boundary_detail["verdict_is_dict"] is False


# ---------------------------------------------------------------------
# CRITERION_FALSIFIES_PRIOR
# ---------------------------------------------------------------------

def test_falsifies_prior_fires_when_new_kp_differs_from_priors():
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"prior_kp_A"}),
        routing_distribution={"prior_kp_A": 1.0},
        prior_kps_by_input_signature={"sig:lehmer_x_phi16": ["prior_kp_A"]},
        known_plugin_domain_kp_triples=frozenset(
            {("g02_contrast", "mahler", "prior_kp_A")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="conflicting_new_kp",
        verdict={"verdict": "REJECTED"},
        domain="mahler",
        ledger_context=ctx,
        input_signature="sig:lehmer_x_phi16",
    )
    assert CRITERION_FALSIFIES_PRIOR in v.criteria_met


def test_falsifies_prior_does_not_fire_on_matching_kp():
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"stable_kp"}),
        routing_distribution={"stable_kp": 1.0},
        prior_kps_by_input_signature={
            "sig:salem_low_M": ["stable_kp", "stable_kp"]
        },
        known_plugin_domain_kp_triples=frozenset(
            {("g10_boundary", "mahler", "stable_kp")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g10_boundary",
        new_kill_pattern="stable_kp",
        verdict={"verdict": "REJECTED"},
        domain="mahler",
        ledger_context=ctx,
        input_signature="sig:salem_low_M",
    )
    assert CRITERION_FALSIFIES_PRIOR not in v.criteria_met


def test_falsifies_prior_without_input_signature_returns_false():
    """No input_signature -> the falsification check returns False
    cleanly (does not crash)."""
    ctx = LedgerContext(
        prior_kps_by_input_signature={"some_sig": ["k"]},
    )
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="different_k",
        verdict={"verdict": "REJECTED"},
        domain="mahler",
        ledger_context=ctx,
        input_signature=None,
    )
    assert CRITERION_FALSIFIES_PRIOR not in v.criteria_met
    assert v.prior_falsification_detail["input_signature"] is None


def test_falsifies_prior_fires_when_prior_was_promoted_and_new_is_rejected():
    """Prior PROMOTED -> new REJECTED on same input is a falsification."""
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"new_kp"}),
        prior_kps_by_input_signature={"sig:x": [None]},  # PROMOTED previously
        known_plugin_domain_kp_triples=frozenset(
            {("g02_contrast", "mahler", "PROMOTED")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="new_kp",
        verdict={"verdict": "REJECTED"},
        domain="mahler",
        ledger_context=ctx,
        input_signature="sig:x",
    )
    assert CRITERION_FALSIFIES_PRIOR in v.criteria_met


# ---------------------------------------------------------------------
# CRITERION_ADDS_TENSOR_RANK
# ---------------------------------------------------------------------

def test_rank_fires_on_novel_plugin_domain_kp_triple():
    ctx = LedgerContext(
        known_plugin_domain_kp_triples=frozenset(
            {("g02_contrast", "mahler", "existing_kp")}
        ),
        known_kill_patterns=frozenset({"existing_kp"}),
        routing_distribution={"existing_kp": 1.0},
    )
    v = assess_residue_eligibility(
        plugin_id="g23_asymptotic_limit",  # different plugin
        new_kill_pattern="existing_kp",
        verdict={"verdict": "REJECTED"},
        domain="mahler",
        ledger_context=ctx,
    )
    assert CRITERION_ADDS_TENSOR_RANK in v.criteria_met


def test_rank_does_not_fire_on_repeat_triple():
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"kp"}),
        routing_distribution={"kp": 1.0},
        known_plugin_domain_kp_triples=frozenset(
            {("g02_contrast", "mahler", "kp")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="kp",
        verdict={"verdict": "REJECTED"},
        domain="mahler",
        ledger_context=ctx,
    )
    assert CRITERION_ADDS_TENSOR_RANK not in v.criteria_met


def test_rank_fires_on_same_plugin_kp_but_new_domain():
    """A (plugin, kp) pair already seen but in a new domain is
    rank-adding."""
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"kp"}),
        routing_distribution={"kp": 1.0},
        known_plugin_domain_kp_triples=frozenset(
            {("g02_contrast", "mahler", "kp")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="kp",
        verdict={"verdict": "REJECTED"},
        domain="BSD",  # new domain
        ledger_context=ctx,
    )
    assert CRITERION_ADDS_TENSOR_RANK in v.criteria_met


# ---------------------------------------------------------------------
# Exhaust (zero criteria fire) — the WHOLE point of the gate
# ---------------------------------------------------------------------

def test_exhaust_returns_not_eligible():
    """A verdict matching prior signature exactly, with no boundary
    fields, on a non-novel triple, with matching routing action
    -> exhaust."""
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"sharp_boundary_detected"}),
        routing_distribution={"sharp_boundary_detected": 1.0},
        prior_kps_by_input_signature={
            "sig:repeat_input": ["sharp_boundary_detected"]
        },
        known_plugin_domain_kp_triples=frozenset(
            {("g10_boundary", "mahler", "sharp_boundary_detected")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g10_boundary",
        new_kill_pattern="sharp_boundary_detected",
        verdict={"verdict": "REJECTED"},  # no boundary fields
        domain="mahler",
        ledger_context=ctx,
        input_signature="sig:repeat_input",
    )
    assert v.eligible is False
    assert v.criteria_met == ()
    assert "exhaust" in v.notes.lower()


def test_exhaust_promoted_verdict_with_no_signal():
    """PROMOTED verdict on a previously-known (plugin, domain, kp=PROMOTED)
    with no boundary fields and a matching prior is exhaust."""
    ctx = LedgerContext(
        known_kill_patterns=frozenset({"some_kp"}),
        routing_distribution={"some_kp": 1.0},
        prior_kps_by_input_signature={"sig:identical": [None]},
        known_plugin_domain_kp_triples=frozenset(
            {("g02_contrast", "mahler", "PROMOTED")}
        ),
    )
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern=None,
        verdict={"verdict": "PROMOTED"},
        domain="mahler",
        ledger_context=ctx,
        input_signature="sig:identical",
    )
    assert v.eligible is False


# ---------------------------------------------------------------------
# Multi-criterion: ensure ALL fired criteria are listed
# ---------------------------------------------------------------------

def test_multiple_criteria_listed_in_order():
    """A verdict that triggers routing-change + boundary + rank
    should list all three in criteria_met."""
    v = assess_residue_eligibility(
        plugin_id="g10_boundary",
        new_kill_pattern="sharp_boundary_detected_bocpd",
        verdict={
            "verdict": "REJECTED",
            "interior_spike_threshold": 1.30,
        },
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    assert v.eligible is True
    assert CRITERION_ROUTING_CHANGE in v.criteria_met
    assert CRITERION_BOUNDARY_LOCALIZED in v.criteria_met
    assert CRITERION_ADDS_TENSOR_RANK in v.criteria_met
    # All entries in criteria_met are valid criterion names
    for c in v.criteria_met:
        assert c in ALL_CRITERIA


# ---------------------------------------------------------------------
# Verdict surface area / immutability
# ---------------------------------------------------------------------

def test_eligibility_verdict_is_frozen():
    """EligibilityVerdict is a frozen dataclass — cannot be mutated
    after construction."""
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="kp",
        verdict={},
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    with pytest.raises((AttributeError, Exception)):
        v.eligible = False  # type: ignore[misc]


def test_all_four_details_always_present_in_verdict():
    """Even for verdicts where a criterion didn't fire, the per-
    criterion detail dict is present so audit reads don't KeyError."""
    v = assess_residue_eligibility(
        plugin_id="g02_contrast",
        new_kill_pattern="kp",
        verdict={"verdict": "REJECTED"},
        domain="mahler",
        ledger_context=LedgerContext.empty(),
    )
    assert isinstance(v.routing_change_detail, dict)
    assert isinstance(v.boundary_detail, dict)
    assert isinstance(v.prior_falsification_detail, dict)
    assert isinstance(v.tensor_rank_detail, dict)
    # Each detail has a 'fires' boolean for downstream filtering
    for d in (
        v.routing_change_detail,
        v.boundary_detail,
        v.prior_falsification_detail,
        v.tensor_rank_detail,
    ):
        assert "fires" in d
        assert isinstance(d["fires"], bool)
