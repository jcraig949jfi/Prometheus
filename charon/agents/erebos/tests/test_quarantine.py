"""Synthetic-control tests for quarantine + applicable_plugins filter.

Per Erebos v3 Phase 0 ITER-28. Validates that quarantined plugins
are filtered out of production paths, that the emission cap raises,
and that the registry has the correct quarantine classes.
"""
from __future__ import annotations

import pytest

from charon.agents.erebos._quarantine import (
    LoaderDebtCapExceededError,
    MAX_PENDING_EMISSIONS,
    MAX_QUARANTINE_DAYS,
    QUARANTINE_RULES,
    QuarantineRule,
    all_quarantined_plugins,
    check_emission_cap,
    is_quarantined,
    quarantine_class_counts,
    quarantine_rule_for,
    restore_quarantine_state,
    unquarantine,
)


# ---------------------------------------------------------------------
# Registry shape
# ---------------------------------------------------------------------

def test_quarantine_registry_has_expected_count():
    """v0.33 state: 11 loader-less plugins quarantined (7 plain +
    3 infrastructure-blocked + 1 vacuous-by-design)."""
    assert len(QUARANTINE_RULES) == 11


def test_quarantine_class_counts_correct():
    counts = quarantine_class_counts()
    assert counts["loader_missing"] == 7
    assert counts["infrastructure_blocked"] == 3
    assert counts["vacuous_by_design"] == 1


def test_quarantine_includes_expected_plain_plugins():
    """Per v0.33 audit: G01, G05, G06, G12, G13, G14, G22 are
    loader-less and could ship Mahler-context loaders."""
    expected = {"g01_intersection", "g05_confound_swap", "g06_null_space",
                "g12_invariant_substitution", "g13_relation_weakening",
                "g14_relation_strengthening", "g22_subgraph_clique"}
    plain = {
        rule.plugin_id for rule in QUARANTINE_RULES.values()
        if rule.quarantine_class == "loader_missing"
    }
    assert plain == expected


def test_quarantine_includes_infrastructure_blocked_plugins():
    """Per v3 whitepaper §6: G07, G08, G21 are infrastructure-blocked."""
    expected = {"g07_analogy", "g08_dimensional_lift",
                "g21_isomorphism_functor"}
    blocked = {
        rule.plugin_id for rule in QUARANTINE_RULES.values()
        if rule.quarantine_class == "infrastructure_blocked"
    }
    assert blocked == expected


def test_quarantine_includes_vacuous_plugin():
    """G20 is vacuous-until-Lethe-v2."""
    vacuous = {
        rule.plugin_id for rule in QUARANTINE_RULES.values()
        if rule.quarantine_class == "vacuous_by_design"
    }
    assert vacuous == {"g20_instrument_disagreement"}


# ---------------------------------------------------------------------
# QuarantineRule construction validation
# ---------------------------------------------------------------------

def test_quarantine_rule_invalid_class_raises():
    with pytest.raises(ValueError, match="invalid quarantine_class"):
        QuarantineRule(
            plugin_id="g_test",
            quarantined_since="2026-05-27",
            unblock_criterion="test",
            quarantine_class="bogus_class",
        )


def test_quarantine_rule_empty_unblock_raises():
    with pytest.raises(ValueError, match="unblock_criterion cannot be empty"):
        QuarantineRule(
            plugin_id="g_test",
            quarantined_since="2026-05-27",
            unblock_criterion="",
            quarantine_class="loader_missing",
        )


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def test_is_quarantined_for_listed_plugin():
    assert is_quarantined("g01_intersection") is True
    assert is_quarantined("g05_confound_swap") is True
    assert is_quarantined("g20_instrument_disagreement") is True


def test_is_quarantined_for_unlisted_plugin():
    assert is_quarantined("g02_contrast") is False
    assert is_quarantined("g11_exception_miner") is False


def test_quarantine_rule_for_returns_rule():
    rule = quarantine_rule_for("g01_intersection")
    assert rule is not None
    assert rule.plugin_id == "g01_intersection"
    assert rule.quarantine_class == "loader_missing"


def test_quarantine_rule_for_unlisted_returns_none():
    assert quarantine_rule_for("g02_contrast") is None


def test_all_quarantined_plugins_sorted():
    plugins = all_quarantined_plugins()
    assert plugins == sorted(plugins)
    assert len(plugins) == 11


# ---------------------------------------------------------------------
# Emission cap enforcement
# ---------------------------------------------------------------------

def test_check_emission_cap_below_max_passes():
    """Below MAX_PENDING_EMISSIONS → no exception."""
    check_emission_cap("g_test_unquarantined", 50)
    check_emission_cap("g_test_unquarantined", MAX_PENDING_EMISSIONS)


def test_check_emission_cap_above_max_raises_for_unquarantined():
    """Plugin above cap and not yet quarantined → tells caller to
    ship loader or quarantine."""
    with pytest.raises(
        LoaderDebtCapExceededError, match="ship the loader or add a"
    ):
        check_emission_cap(
            "g_test_unquarantined", MAX_PENDING_EMISSIONS + 1
        )


def test_check_emission_cap_above_max_raises_for_quarantined():
    """Plugin already quarantined but somehow still emitting →
    investigate production path."""
    snapshot = dict(QUARANTINE_RULES)
    try:
        QUARANTINE_RULES["g_already_quarantined"] = QuarantineRule(
            plugin_id="g_already_quarantined",
            quarantined_since="2026-05-27",
            unblock_criterion="test",
            quarantine_class="loader_missing",
        )
        with pytest.raises(
            LoaderDebtCapExceededError, match="is QUARANTINED but emitted"
        ):
            check_emission_cap(
                "g_already_quarantined", MAX_PENDING_EMISSIONS + 1
            )
    finally:
        restore_quarantine_state(snapshot)


def test_max_pending_emissions_is_200():
    """v3 §4.8 hard cap."""
    assert MAX_PENDING_EMISSIONS == 200


def test_max_quarantine_days_is_30():
    """v3 §4.8 time cap."""
    assert MAX_QUARANTINE_DAYS == 30


# ---------------------------------------------------------------------
# applicable_plugins filter
# ---------------------------------------------------------------------

def test_applicable_plugins_excludes_quarantined_by_default():
    """Quarantined plugins do NOT appear in production runs."""
    from charon.agents.erebos.generators import applicable_plugins
    from charon.agents.erebos.tests._fixtures import empty_swarm_state

    state = empty_swarm_state()
    # Construct a state that would otherwise make a quarantined plugin
    # (g05) applicable
    state.stygian_substantive = [
        {
            "record_id": "s1",
            "canonical_claim_text": "promoted with coords",
            "verdict": "PROMOTED",
            "kill_pattern": None,
            "kill_vector": None,
            "generator_id": "stygian",
            "emitted_at": "2026-05-27T00:00:00+00:00",
            "claim_payload": {"degree": 12, "mahler": 1.20, "extra": 3.0},
            "extras": {},
        },
    ]
    plugins = applicable_plugins(state)
    ids = {p.id for p in plugins}
    # All quarantined plugins must be filtered out
    for qp in all_quarantined_plugins():
        assert qp not in ids, (
            f"Quarantined plugin {qp} appeared in production "
            f"applicable_plugins(state)"
        )


def test_applicable_plugins_include_quarantined_explicit_test_mode():
    """include_quarantined=True restores legacy behavior for tests."""
    from charon.agents.erebos.generators import applicable_plugins
    from charon.agents.erebos.tests._fixtures import empty_swarm_state

    state = empty_swarm_state()
    state.stygian_substantive = [
        {
            "record_id": "s1",
            "canonical_claim_text": "promoted",
            "verdict": "PROMOTED",
            "kill_pattern": None,
            "kill_vector": None,
            "generator_id": "stygian",
            "emitted_at": "2026-05-27T00:00:00+00:00",
            "claim_payload": {"a": 1.0, "b": 2.0},
            "extras": {},
        },
    ]
    test_mode_plugins = applicable_plugins(state, include_quarantined=True)
    test_mode_ids = {p.id for p in test_mode_plugins}
    prod_plugins = applicable_plugins(state)
    prod_ids = {p.id for p in prod_plugins}
    # Test mode is a superset of production mode
    assert prod_ids.issubset(test_mode_ids)


def test_unquarantine_removes_from_registry():
    snapshot = dict(QUARANTINE_RULES)
    try:
        assert is_quarantined("g01_intersection") is True
        unquarantine("g01_intersection")
        assert is_quarantined("g01_intersection") is False
    finally:
        restore_quarantine_state(snapshot)


def test_unquarantine_unknown_plugin_no_op():
    """Removing non-quarantined plugin is a no-op (not an error)."""
    snapshot = dict(QUARANTINE_RULES)
    try:
        unquarantine("g_never_was_quarantined")
    finally:
        restore_quarantine_state(snapshot)
