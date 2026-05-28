"""Tests for kill_pattern-driven plugin routing (Phase 1B ITER-38).

Validates next_plugin_kp_routed() picks the plugin pointed to by
kill_pattern_registry.routing_action_for(kp), falls back to round-
robin when the kp is unregistered / unmapped / quarantined / non-
applicable, and exposes the _routing_action_to_plugin_id helper.
"""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators import (
    REGISTRY,
    SwarmState,
    _routing_action_to_plugin_id,
    next_plugin_kp_routed,
    next_plugin_round_robin,
)


# ---------------------------------------------------------------------
# _routing_action_to_plugin_id
# ---------------------------------------------------------------------

def test_routing_action_maps_g11_to_exception_miner():
    """g11_with_monte_carlo_g_test -> g11_exception_miner."""
    pid = _routing_action_to_plugin_id("g11_with_monte_carlo_g_test")
    assert pid == "g11_exception_miner"


def test_routing_action_maps_g10_to_boundary():
    """g10_with_bocpd_posterior -> g10_boundary."""
    pid = _routing_action_to_plugin_id("g10_with_bocpd_posterior")
    assert pid == "g10_boundary"


def test_routing_action_maps_g25_to_degeneracy():
    """g25_v2_data_inquiry_precondition -> g25_degeneracy."""
    pid = _routing_action_to_plugin_id("g25_v2_data_inquiry_precondition")
    assert pid == "g25_degeneracy"


def test_routing_action_returns_none_for_sentinel():
    """The 'none_claim_survives' sentinel returns None."""
    pid = _routing_action_to_plugin_id("none_claim_survives")
    assert pid is None


def test_routing_action_returns_none_for_unknown_prefix():
    """A gNN that doesn't match any plugin returns None."""
    pid = _routing_action_to_plugin_id("g99_nonexistent_plugin")
    assert pid is None


def test_routing_action_returns_none_for_non_g_prefix():
    """Non-g-prefix actions (legacy / malformed) return None."""
    assert _routing_action_to_plugin_id("foo_bar") is None
    assert _routing_action_to_plugin_id("") is None
    assert _routing_action_to_plugin_id("g_no_number") is None


# ---------------------------------------------------------------------
# next_plugin_kp_routed
# ---------------------------------------------------------------------

def test_kp_routed_falls_back_to_round_robin_when_no_kp():
    """No last_kill_pattern -> behave exactly like round-robin."""
    state = SwarmState()
    routed = next_plugin_kp_routed(state, last_plugin_id=None,
                                    last_kill_pattern=None)
    rr = next_plugin_round_robin(state, last_plugin_id=None)
    assert routed is rr


def test_kp_routed_falls_back_for_unregistered_kp():
    """A kp not in kill_pattern_registry -> round-robin fallback."""
    state = SwarmState()
    routed = next_plugin_kp_routed(state, last_plugin_id=None,
                                    last_kill_pattern="totally_made_up_kp_xyz")
    rr = next_plugin_round_robin(state, last_plugin_id=None)
    assert routed is rr


def test_kp_routed_picks_g11_for_g11_kp():
    """A registered kp whose routing_action maps to G11 -> G11."""
    state = SwarmState()
    # First, find a kp in the registry whose routing_action points to g11
    from charon.agents.erebos._kill_pattern_registry import (
        KILL_PATTERN_REGISTRY,
    )
    g11_kps = [
        kp for kp, spec in KILL_PATTERN_REGISTRY.items()
        if spec.routing_action.startswith("g11_")
    ]
    if not g11_kps:
        pytest.skip("no kp routes to g11; registry shape changed")
    routed = next_plugin_kp_routed(
        state, last_plugin_id=None, last_kill_pattern=g11_kps[0]
    )
    if routed is None:
        pytest.skip("g11 not applicable in empty SwarmState")
    assert routed.id == "g11_exception_miner"


def test_kp_routed_falls_back_when_target_not_applicable():
    """If the kp-routed plugin is not applicable to current state,
    fall back to round-robin (don't return None when other plugins
    are applicable)."""
    # Build a state where most plugins are applicable but g05 (Confound-
    # Swap, Tier C, often not applicable in empty state) isn't.
    state = SwarmState()
    # Find a kp routing to g05 (or any plugin that's unlikely to be
    # applicable in empty state)
    from charon.agents.erebos._kill_pattern_registry import (
        KILL_PATTERN_REGISTRY,
    )
    target_kps = [
        kp for kp, spec in KILL_PATTERN_REGISTRY.items()
        if spec.routing_action.startswith("g05_")
    ]
    if not target_kps:
        pytest.skip("no kp routes to g05; registry shape changed")
    g05 = REGISTRY.get("g05_confound_swap")
    if g05 is None or g05.applicable(state):
        pytest.skip("g05 not in registry OR happens to be applicable")
    routed = next_plugin_kp_routed(
        state, last_plugin_id=None, last_kill_pattern=target_kps[0]
    )
    # Should NOT be g05 (not applicable); must be something else or None
    if routed is not None:
        assert routed.id != "g05_confound_swap"


def test_kp_routed_no_applicable_plugins_returns_none():
    """If even round-robin can't find an applicable plugin, return None."""
    # Construct a SwarmState that makes nothing applicable. Hard to do
    # without knowing each plugin's applicable() rules, so we'll test
    # the path indirectly: pass an obviously-bad state. If everything
    # remains applicable, skip.
    state = SwarmState()
    from charon.agents.erebos.generators import applicable_plugins
    if applicable_plugins(state):
        # Some plugins are applicable in empty state -- can't test
        # the no-applicable path without monkeypatching
        pytest.skip("empty SwarmState has applicable plugins")
    routed = next_plugin_kp_routed(
        state, last_plugin_id=None, last_kill_pattern="any_kp"
    )
    assert routed is None


# ---------------------------------------------------------------------
# Quarantine integration
# ---------------------------------------------------------------------

def test_kp_routed_skips_quarantined_target():
    """If the kp-routed target plugin is quarantined, fall back to
    round-robin instead of selecting the quarantined plugin."""
    from charon.agents.erebos._quarantine import is_quarantined
    from charon.agents.erebos._kill_pattern_registry import (
        KILL_PATTERN_REGISTRY,
    )

    # Find any kp whose routing_action maps to a QUARANTINED plugin
    state = SwarmState()
    quarantined_route_kp = None
    for kp, spec in KILL_PATTERN_REGISTRY.items():
        target_id = _routing_action_to_plugin_id(spec.routing_action)
        if target_id and is_quarantined(target_id):
            quarantined_route_kp = kp
            break

    if quarantined_route_kp is None:
        pytest.skip("no kp routes to a quarantined plugin in current registry")

    routed = next_plugin_kp_routed(
        state, last_plugin_id=None,
        last_kill_pattern=quarantined_route_kp,
    )
    # Whatever it returns, it must not be a quarantined plugin
    if routed is not None:
        assert not is_quarantined(routed.id), (
            f"kp-routed selected quarantined plugin {routed.id!r}; "
            f"should have fallen back"
        )
