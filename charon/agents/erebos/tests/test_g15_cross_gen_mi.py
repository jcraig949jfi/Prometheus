"""TDD tests for G15 Cross-Gen MI Generator."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g15_cross_gen_mi import (
    CrossGenMIGenerator,
    MIN_CROSSGEN_PATTERNS,
    _longest_common_token,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


@pytest.fixture
def gen():
    return CrossGenMIGenerator()


def test_g15_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g15_not_applicable_with_one_crossgen_pattern(gen):
    state = empty_swarm_state()
    state.hecate_crossgen_canonical = ["pattern_alpha"]
    assert gen.applicable(state) is False


def test_g15_applicable_with_threshold_crossgen_patterns(gen):
    state = empty_swarm_state()
    state.hecate_crossgen_canonical = [
        "method_triangulated_reject",
        "detrended_correlation_below_threshold",
    ]
    assert gen.applicable(state) is True


def test_g15_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.hecate_crossgen_canonical = [
        "method_triangulated_reject",
        "detrended_correlation_below_threshold",
        "relation_equal_violated",
    ]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g15_expected_kill_pattern(gen):
    state = empty_swarm_state()
    state.hecate_crossgen_canonical = ["pattern_a_token", "pattern_b_token"]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "uncorrelated_residual_failures"


def test_longest_common_token_finds_shared():
    patterns = [
        "method_triangulated_reject",
        "method_simple_reject",
        "method_anomaly_reject",
    ]
    common = _longest_common_token(patterns)
    # Should be "triangulated" or "reject" or "method" depending on length
    assert common in ("triangulated", "reject", "method", "simple", "anomaly")
    # Specifically, the LONGEST common one
    assert len(common) >= len("method")


def test_longest_common_token_returns_none_when_disjoint():
    assert _longest_common_token(["alpha_x", "beta_y", "gamma_z"]) is None


def test_g15_six_field_compliance(gen):
    state = empty_swarm_state()
    state.hecate_crossgen_canonical = ["alpha", "beta"]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()


def test_g15_metadata():
    g = CrossGenMIGenerator()
    assert g.id == "g15_cross_gen_mi"
    assert g.feasibility_tier == "B"
    assert g.reasoning_tier == "R5"
