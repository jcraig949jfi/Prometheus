"""TDD tests for G16 Anti-Anchor."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g16_anti_anchor import (
    ADVERSARIAL_MULT_HIGH,
    ADVERSARIAL_MULT_LOW,
    AntiAnchorGenerator,
    _harvest_numeric_params,
    _is_anchor,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _promoted(rid: str, payload: dict) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"PROMOTED parent {rid}",
        "verdict": "PROMOTED",
        "kill_pattern": None,
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": payload,
        "extras": {},
    }


def _rejected(rid: str, payload: dict) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"REJECTED row {rid}",
        "verdict": "REJECTED",
        "kill_pattern": "stygian_f17_failed",
        "kill_vector": None,
        "generator_id": "stygian",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": payload,
        "extras": {},
    }


def _lethe_anti_anchor(rid: str, payload: dict) -> dict:
    return {
        "record_id": rid,
        "canonical_claim_text": f"Lethe candidate {rid}",
        "verdict": "REJECTED",
        "kill_pattern": "lethe_anti_anchor_candidate",
        "kill_vector": None,
        "generator_id": "lethe",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": payload,
        "extras": {},
    }


@pytest.fixture
def gen():
    return AntiAnchorGenerator()


def test_is_anchor_promoted():
    assert _is_anchor({"verdict": "PROMOTED"}) is True


def test_is_anchor_rejected_not_anchor():
    assert _is_anchor({"verdict": "REJECTED"}) is False


def test_is_anchor_lethe_anti_anchor():
    row = {"verdict": "REJECTED", "kill_pattern": "lethe_anti_anchor_candidate"}
    assert _is_anchor(row) is True


def test_harvest_skips_bools():
    row = {"claim_payload": {"degree": 12, "is_cm": True, "rank": 1}}
    p = _harvest_numeric_params(row)
    assert "pl.degree" in p
    assert "pl.is_cm" not in p
    assert "pl.rank" in p


def test_g16_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g16_not_applicable_when_only_rejected(gen):
    """G16 needs PROMOTED anchors to invert; REJECTED isn't an anchor."""
    state = empty_swarm_state()
    state.stygian_substantive = [_rejected("r1", {"degree": 10})]
    assert gen.applicable(state) is False


def test_g16_applicable_with_promoted_and_params(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"degree": 10})]
    assert gen.applicable(state) is True


def test_g16_applicable_with_lethe_anti_anchor(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_lethe_anti_anchor("r1", {"degree": 10})]
    assert gen.applicable(state) is True


def test_g16_generates_composed_claim(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"degree": 10.0})]
    claim = gen.generate(state)
    assert isinstance(claim, ComposedClaim)
    assert claim.expected_kill_pattern == "conjecture_survives_adversarial_attack"


def test_g16_adversarial_value_high(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"degree": 10.0})]
    claim = gen.generate(state)
    # First direction tried is HIGH → 10 * 10 = 100
    assert claim.composition_payload["adversarial_value"] == 100.0
    assert claim.composition_payload["direction"] == "HIGH"


def test_g16_skips_zero_valued_params(gen):
    """Zero-valued params can't be pushed multiplicatively; skip them."""
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"only_zero": 0.0})]
    assert gen.applicable(state) is False


def test_g16_metadata():
    g = AntiAnchorGenerator()
    assert g.id == "g16_anti_anchor"
    assert g.feasibility_tier == "C"
    assert g.reasoning_tier == "R5"


def test_g16_composed_id_format(gen):
    state = empty_swarm_state()
    state.stygian_substantive = [_promoted("r1", {"degree": 10.0})]
    claim = gen.generate(state)
    assert claim.composed_id.startswith("EREBOS-G16-anti_anchor_")
