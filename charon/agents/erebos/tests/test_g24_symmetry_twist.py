"""TDD tests for G24 Symmetry/Twist."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g24_symmetry_twist import (
    SymmetryTwistGenerator,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _row(text: str, rid: str = "r1", verdict: str = "PROMOTED") -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": text,
        "verdict": verdict,
        "kill_pattern": None,
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {},
        "extras": {},
    }


@pytest.fixture
def gen():
    return SymmetryTwistGenerator()


def test_g24_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g24_not_applicable_without_mahler_context(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("some unrelated claim")]
    assert gen.applicable(state) is False


def test_g24_applicable_with_mahler_indicator(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("BL-C-001 / Lehmer Mahler measure")]
    assert gen.applicable(state) is True


def test_g24_applicable_with_salem_indicator(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("Salem-class polynomial test")]
    assert gen.applicable(state) is True


def test_g24_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("BL-C-001 Lehmer test")]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)


def test_g24_expected_kill_pattern(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("Lehmer Mahler claim")]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "symmetry_breaking"


def test_g24_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("Mahler measure test")]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G24-symmetry_")


def test_g24_six_field_compliance(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_row("Lehmer test")]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()


def test_g24_metadata():
    g = SymmetryTwistGenerator()
    assert g.id == "g24_symmetry_twist"
    assert g.feasibility_tier == "A"
    assert g.reasoning_tier == "R3"
