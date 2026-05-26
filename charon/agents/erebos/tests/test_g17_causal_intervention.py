"""TDD tests for G17 Causal-Intervention."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g17_causal_intervention import (
    CORRELATION_FIELDS,
    CausalInterventionGenerator,
    DECOUPLING_THRESHOLD,
    _find_correlation_field,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _pollux_row(rid: str, corr: float) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"Pollux pair {rid}",
        "verdict": "PROMOTED",
        "kill_pattern": None,
        "kill_vector": {"corr_raw": corr},
        "generator_id": "pollux",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {},
        "extras": {"composition_payload": {"corr_raw": corr}},
    }


@pytest.fixture
def gen():
    return CausalInterventionGenerator()


def test_find_correlation_field_picks_high_magnitude():
    row = _pollux_row("r1", 0.85)
    out = _find_correlation_field(row)
    assert out is not None
    field, value = out
    assert field == "corr_raw"
    assert value == 0.85


def test_find_correlation_field_skips_below_threshold():
    row = _pollux_row("r1", 0.05)  # below decoupling threshold
    assert _find_correlation_field(row) is None


def test_g17_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g17_not_applicable_without_correlation(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_pollux_row("r1", 0.0)]
    assert gen.applicable(state) is False


def test_g17_applicable_with_promoted_correlation(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_pollux_row("r1", 0.85)]
    assert gen.applicable(state) is True


def test_g17_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_pollux_row("r1", 0.75)]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "correlation_survives_intervention"


def test_g17_metadata():
    g = CausalInterventionGenerator()
    assert g.id == "g17_causal_intervention"
    assert g.feasibility_tier == "B"
    assert g.reasoning_tier == "R5"


def test_g17_composed_id_format(gen):
    state = empty_swarm_state()
    state.pollux_substantive = [_pollux_row("r1", 0.85)]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G17-intervene_")
